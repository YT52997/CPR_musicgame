from distutils.command.sdist import sdist
import os
from turtle import left
import pygame
from rabboni import *
import numpy as np
import time

#先宣告一個物件
rabbo = Rabboni(mode = "USB") 
#連結上rabboni，若沒插上會報錯
rabbo.connect()
print ("Status:",rabbo.Status)

# 幾秒提醒一次
processing_time = 5
# 取樣頻率幾赫茲
fs=200
# 整個程式要跑幾分鐘
test_time = 10
# 一次要抓的資料數
N=int(processing_time*fs)
# 取樣時間間隔
dt=1/fs
# 奈奎斯特頻率
fnq=fs/2
# 頻率解析度F
df=fs/N
# 1/頻率解析度
T=1/df
# 濾波器截止頻率
cutoff_low = 10
# 畫面FPS
FPS=60

# 遊戲背景色
bg_color = (0,38,75)
## 設定加速度跟陀螺儀的最大範圍與取樣頻率跟count threshold
rabbo. set_sensor_config(acc_scale = 16, gyr_scale = 2000,rate = fs,threshold=100000) 

# 實現低通濾波器的函數
def filter(data, cutoff_low,fs=fs, cutoff_high=None, order=4):
    # 將訊號做快速傅立葉轉換
    k = np.fft.fft(data)
    f = np.fft.fftfreq(len(data),1/fs)
    # 只取頻率<=截止頻率的成分，其他令為零
    filtered_spectrum = k*(np.absolute(f)<cutoff_low)
    # 將訊號做逆傅立葉轉換，得到濾波後的訊號
    y = np.fft.ifft(filtered_spectrum)
    return y

# 找出訊號中的波峰、波谷並傳回
def extreme_finding(x,t):
    # 用來裝波峰、波谷所在的index的串列
    peaks=[]
    valleys=[]

    # last_point_type 紀錄上一筆紀錄到的資料是波峰還是波谷，確保不會連續抓到兩個波峰或兩個波谷
    last_point_type = "N"

    for i in range(1,len(x)-2):
        # 若值太小，則忽略
        if(abs(x[i]) < 0.1):
            continue

        # 情況1: 該值比周遭值都大
        if x[i]>x[i-1] and x[i]>x[i+1] and x[i] >0 and last_point_type:
            if last_point_type == "P":
                if x[i] > peaks[-1]:
                    peaks.append(i)
                    last_point_type = "P"
            else:
                peaks.append(i)
                last_point_type = "P"
        # 情況2: 該值比周遭值都小
        elif x[i]<x[i-1] and x[i]<x[i+1] and x[i]<0:
            if last_point_type == "V":
                if x[i] > valleys[-1]:
                    valleys.append(i)
                    last_point_type = "V"
            else:
                valleys.append(i)
                last_point_type = "V"

        # 情況3: 該值和鄰近的值相等，但仍處於波峰或波谷
        # -> 有一段區域的比周遭值還大，但該區域中的數值都相等
        # > 最後會記錄該段區域的中間項

        #   i  i+1
        #i-1*  * i+2
        #  *    *
        # *       *
        #           *
        if(x[i]==x[i+1]):
            # 計算高峰上有幾個數相等
            num_equal=2
            #print("!!equal value!!")

            # 找出此段範圍的長度
            k=i+2
            next_loop = False
            while x[k] == x[k-1]:
                num_equal+=1
                k+=1
                if k==len(x):
                    next_loop=True
                    break
            if next_loop:
                continue

            # 若此段為波峰，則將其填入peaks
            if(x[i-1]<x[i] and x[i+num_equal] < x[i+num_equal-1]) and x[i]>0:
                # 避免連續兩個波峰被記錄
                if last_point_type == "P":
                    if x[i] > peaks[-1]:
                        peaks[-1]=(i+int(num_equal/2))
                        last_point_type = "P"
                else:
                    peaks.append(i+int(num_equal/2))
                    last_point_type = "P"
                
            # 若此段為波谷，則將其填入valleys
            elif(x[i-1]>x[i] and x[i+num_equal] > x[i+num_equal-1]) and x[i]<0:
                # 避免連續兩個波谷被記錄
                if last_point_type == "V":
                    if x[i] < valleys[-1]:
                        valleys[-1]=(i+int(num_equal/2))
                        last_point_type = "V"
                else:
                    valleys.append(i+int(num_equal/2))
                    last_point_type = "V"

    # 波峰和波谷的索引值由小到大排列
    peaks.sort()
    valleys.sort()

    # 裝波峰發生的時間
    tp=[]
    # 裝波谷發生的時間
    tv=[]
    # 裝波峰值
    xp=[]
    # 裝波谷值
    xv=[]

    for i in range(len(peaks)):
        tp.append(t[peaks[i]])
        xp.append(x[peaks[i]])
    for i in range(len(valleys)):
        tv.append(t[valleys[i]])
        xv.append(x[valleys[i]])

    val = (np.array(tp),np.array(xp),np.array(tv),np.array(xv),peaks,valleys)
    return val

# 將a做積分，得到的資料長度為N
def integrate(a,N,dt,v0):
    v=[v0]
    while len(v) < N:
        new_v = v[len(v)-1] + (a[len(v)] + a[len(v)-1])*dt/2
        v.append(new_v)
    return np.array(v)

# 繞x軸旋轉theta弧度的旋轉矩陣
def Rx(theta):
  return np.matrix([[ 1, 0           , 0           ],
                   [ 0, np.cos(theta),-np.sin(theta)],
                   [ 0, np.sin(theta), np.cos(theta)]])
  
# 繞y軸旋轉theta弧度的旋轉矩陣
def Ry(theta):
  return np.matrix([[ np.cos(theta), 0, np.sin(theta)],
                   [ 0           , 1, 0           ],
                   [-np.sin(theta), 0, np.cos(theta)]])
  
# 繞z軸旋轉theta弧度的旋轉矩陣
def Rz(theta):
  return np.matrix([[ np.cos(theta), -np.sin(theta), 0 ],
                   [ np.sin(theta), np.cos(theta) , 0 ],
                   [ 0           , 0            , 1 ]])

# 由繞x、y、z軸的轉動組成三維旋轉矩陣
def Rotation_matrix(theta_x,theta_y,theta_z):
    m = Rz(theta_z) @ Ry(theta_y)
    return np.array(m @ Rx(theta_x))

# 得到每次下壓的位移
# 回傳: np.array(t_val),np.array(v_val),np.array(x_val),np.real(delta_x)
# 積分區間的時間(陣列),積分所得的速度(陣列),積分所得的位移(陣列),每次下壓位移的平均值(數值)
def get_displacement(acc,t,peaks,valleys):

    # 調整peaks、valleys，使其長度到一樣
    length=min(len(peaks),len(valleys))
    peaks=peaks[0:length]
    valleys=valleys[0:length]

    # 若沒有找到任何波峰和波谷，則回傳-1，代表沒有位移
    if len(peaks)==0 or len(valleys)==0:
        return np.array([-1]),np.array([-1]),np.array([-1]),-1

    # 檢查在時間上是波峰還是波谷最早出現
    peak_first = t[peaks[0]] < t[valleys[0]]

    # 裝每次積分的時間區間
    t_val=[]
    # 裝每次積分所得的速度
    v_val=[]
    # 裝每次積分所得的位置
    x_val = []
    # 用來計算位移的平均值
    delta_x=0
    
    for i in range(length):
        # 若波峰先出現，則積分區間始於波峰，終於波谷
        if peak_first:
            t_integral = t[peaks[i]:valleys[i]+1]
            a_integral = acc[peaks[i]:valleys[i]+1]
        # 若波谷先出現，則積分區間始於波谷，終於波峰
        else:
            t_integral = t[valleys[i]:peaks[i]+1]
            a_integral = acc[valleys[i]:peaks[i]+1]

        # 由於感測器的運動類似簡諧運動，加速度波峰或波谷發生的時候，速度應趨近於零，所以每次積分時都假設初速為零
        v_integral = integrate(a_integral,len(t_integral),dt,0)
        # 我們只關心位移，方便起見，初位置皆設為0
        x_integral = integrate(v_integral,len(v_integral),dt,0)

        # 將資料存入t_val、v_val、x_val中
        for j in range(len(t_integral)):
            t_val.append(t_integral[j])
            v_val.append(v_integral[j])
            x_val.append(abs(x_integral[j]))
    
    # 將 x_val sort之後再去頭去尾，只留中間的3/5，以去除極值
    x_for_delta_x = sorted(x_val)
    while len(x_for_delta_x) > int(len(x_val)*3/5):
        x_for_delta_x.pop(-1)
        if len(x_for_delta_x) <= int(len(x_val)*3/5):
            break
        x_for_delta_x.pop(0)

    # 算出位移平均
    delta_x = np.average(np.array(x_for_delta_x))
    # 將位移單位轉成公分
    delta_x *= 9.8*100

    return np.array(t_val),np.array(v_val),np.array(x_val),np.real(delta_x)

# 傳入: fft之後所得的頻譜值(陣列),頻率(陣列)
# 回傳一個tuple: (分數,偏移正確頻率的比例(有正負之分))
def score_DFT(A,f):
    if(np.linalg.norm(A)/(len(A))**0.5 < 0.001):
        # 若讀值過小，回傳偏移率為零、頻率分數為零，頻率值為-1(表示讀值過小)
        return (0,0,-1)

    # 考慮範圍 0<--[100bpm,120bpm]-->2
    else:
        # 找出頻譜最大值所在的頻率
        max_idx = list(A).index(max(A))
        f_max = f[max_idx]
        print("max frequency=")
        print(f_max)

        # 將頻率換成bpm
        # 若bpm落在[100bpm,120bpm]中，或者邊界的正負5%之內，則視為滿分
        bpm=f_max*60
        # 頻率偏移了多少
        shift = None
        # 頻率的最大偏移輛
        max_shift = None
        if 100*0.95<=bpm and bpm<=120*1.05:
            return (100,0,f_max)
        # 假設一般人做cpr最快只會壓到4赫茲，因此max_shift = 2
        elif f_max>2:
            shift = f[max_idx]-2.0
            max_shift = 2
        # 假設一般人做cpr最慢只會壓到0.5赫茲，因此max_shift = 1.5
        else:
            shift = f[max_idx]-100/60
            max_shift = 1.5

        # 用頻率的偏移率算百分制的分數
        val=100*(1-abs(shift)/max_shift)
        if val<0:
            val=0
        return (val,shift/max_shift,f_max)

# 寫一個把文字印出的函式
def draw_text(surf, text,size,x,y,color):
    font = pygame.font.Font("msjh.ttc", size)
    text_surface = font.render(text,True,color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surf.blit(text_surface,text_rect)

print("Please don't move the sensor")
rabbo.read_data()

# 首先進入初始畫面
gamestate = 0

# 初始化遊戲
pygame.init()
# 初始化音效
pygame.mixer.init()


# 載入音效
deeper = pygame.mixer.Sound(os.path.join("audio","deeper.wav"))
excellent = pygame.mixer.Sound(os.path.join("audio","great.wav"))

factor = 5
# 顯示畫面
WIDTH = 408
HIGHT = 612
# pygame 的座標
#--------> +x
#|
#|
#|
#+y

# 傳入一個tuple: (畫面寬度,高度)
screen=pygame.display.set_mode((WIDTH,HIGHT))

# 載入圖片，換成pygame易讀取的格式
# 資料夾,圖檔名
img_side = int(WIDTH*3/5)
pink_shark = pygame.image.load(os.path.join("img","pink_shark.PNG"))
pink_shark.set_colorkey((0,0,0))
pink_shark.convert_alpha()
pink_shark = pygame.transform.scale(pink_shark,(img_side,img_side))

bg_img = pygame.image.load(os.path.join("img","bg_img.jpg")).convert()

# Set the caption of the pygame window
pygame.display.set_caption("CPR verification test")

# Clock for the game
# pygame.time.Clock() 回傳的物件可管理時間
clock = pygame.time.Clock()


#遊戲迴圈
running = True

# Class declaration

# 對 rabboni 的資料進行運算的class
class sensorData(pygame.sprite.Sprite):
    # constructor
    # 收集感測器的初始值和offset
    # 此時感測器必須是靜止的
    def __init__(self):
        # call the constructor of sprite
        pygame.sprite.Sprite.__init__(self)

        # 給使用者的關於頻率的提示(壓快一點、慢一點)
        self.freqRank = "- - -"
        # 給使用者的關於深度的提示(壓深一點、淺一點)
        self.displacementRank = "- - -"
        # 印在頻率數值的視窗的文字
        self.freq_msg = "---"
        # 印在位移數值的視窗的文字
        self.deltax_msg="---"
        # 存放加速度資料
        self.acc = np.array([])
        # 在收集資料過程中是否被中斷
        self.interupt=False

        # 先抓一秒鐘的資料
        self.initial_data_num = fs*1
        print("Collecting initial data...")
        data_num0 = rabbo.data_num
        while rabbo.data_num-data_num0 < self.initial_data_num:

            if rabbo.Status ==0:
                print("DISCONNECT")
                raise ValueError
            
            for event in pygame.event.get():
                #若使用者按下關閉視窗的X，則停止收集資料
                if event.type == pygame.QUIT:
                    #跳出while
                    self.interupt = True
                    # 關閉 rabboni
                    print('Shut done!')
                    break
            if self.interupt:
                break

            print(rabbo.data_num-data_num0,end="\r")
        print(rabbo.data_num-data_num0)

        # 利用加速度的初值計算感測器的初角度
        self.GZ_START=np.average(rabbo.Accz_list)
        self.GY_START=np.average(rabbo.Accy_list)
        self.GX_START=np.average(rabbo.Accx_list)
        self.G_START = np.array([self.GX_START,self.GY_START,self.GZ_START])
        self.GNORM_START = np.linalg.norm(self.G_START)

        # 抓gryx、gryy、gryz的offset
        self.gryx_offset = np.average(rabbo.Gyrx_list)
        self.gryy_offset = np.average(rabbo.Gyry_list)
        self.gryz_offset = np.average(rabbo.Gyrz_list)

        # 算出theta_x、theta_y、theta_z初值
        # 計算初始角度
        # 以一開始的z軸轉角為零度
        self.theta0_x = np.arctan(self.G_START[1]/self.G_START[2])
        RX_G = np.array(Rx(self.theta0_x)).dot(self.G_START)
        self.theta0_y = np.arctan(-RX_G[0]/RX_G[2])
        self.theta0_z=0

        # 用來累計平均分數
        self.ave_score=[]

    # 得到 acc_result，並存入self.acc
    def get_data(self):
        data_num0 = rabbo.data_num
        print("Num of data to be collected=",end=" ")
        print(N+data_num0)

        # 收集接下來processing_time秒的資料
        while True:
            #印出收集資料進度
            print(rabbo.data_num,end="\r")
            if rabbo.Status ==0:
                print("DISCONNECT!!")
                raise ValueError

            for event in pygame.event.get():
                #若使用者按下關閉視窗的X，則停止收集資料
                if event.type == pygame.QUIT:
                    self.interupt=True
                    print('Shut done!')
                    return None

            if rabbo.data_num >= N+ data_num0:
                break
        
        print(rabbo.data_num)

        # 把0~N 映射到 0~processing_time
        t=np.linspace(0,processing_time,N)
        # 加速度raw data
        raw_az_data=np.array(rabbo.Accz_list)
        raw_ay_data=np.array(rabbo.Accy_list)
        raw_ax_data=np.array(rabbo.Accx_list)

        # 角加速度全部先減去offset，再轉成rad/s
        gryx=(np.array(rabbo.Gyrx_list)-self.gryx_offset)*np.pi/180
        gryy=(np.array(rabbo.Gyry_list)-self.gryy_offset)*np.pi/180
        gryz=(np.array(rabbo.Gyrz_list)-self.gryz_offset)*np.pi/180

        # 角速度濾波
        gryx = filter(gryx,3000)[data_num0:data_num0+N]
        gryy = filter(gryy,3000)[data_num0:data_num0+N]
        gryz = filter(gryz,3000)[data_num0:data_num0+N]

        # 加速度濾波
        ax = filter(raw_ax_data,cutoff_low)[data_num0:data_num0+N]
        ay = filter(raw_ay_data,cutoff_low)[data_num0:data_num0+N]
        az = filter(raw_az_data,cutoff_low)[data_num0:data_num0+N]
        print("filter")

        # 積分算出各時間點下的角度
        theta_x = integrate(gryx,N,dt,self.theta0_x)
        theta_y = integrate(gryy,N,dt,self.theta0_y)
        theta_z = integrate(gryz,N,dt,self.theta0_z)
        print("intergrate theta")

        # 將每個時間點下測得的三維加速度，由感測器的參考系轉換到地面的參考系，並把z方向扣掉g之後存入self.acc
        acc_result=[]
        for i in range(N):
            trans_matrix = Rotation_matrix(theta_x[i],theta_y[i],theta_z[i])
            acc_iner = trans_matrix.dot(np.array([ax[i],ay[i],az[i]]))
            acc_result.append(acc_iner[2] - self.GNORM_START)
        self.acc = np.array(acc_result)

    # 得到頻率、位移的分數和提示訊息
    # 回傳: 位移提示訊息,頻率提示訊息,位移值,頻率值
    def get_rank(self):

        # FFT
        f=np.linspace(0,fnq,int(N/2))[1:]
        A=np.fft.fft(self.acc)
        A=np.abs((A)*2/N)
        A[0]/=2
        A=A[1:int(N/2)]
        # 得到頻率分數、頻率偏移率、此訊號最主要的頻率值
        freq_score,shift_rate,f_max = score_DFT(A,f)
        print("score_DFT")

        # 回傳的頻率值
        freq=f_max
        # 回傳的位移值
        deltax=None
        # 回傳的位移分數
        deltax_score = None

        print("val declared")

        # 若頻率分數非滿分
        if(freq_score<100):
            if(shift_rate > 0):
                # 壓太快
                self.freqRank="Slower!!!"
            elif(shift_rate < 0):
                # 壓太慢
                self.freqRank="Faster!!!"
            else:
                # 讀值過小
                print("讀值過小")
                self.freqRank="No movement!!"
                self.displacementRank = "No movement!!"
                # 位移和頻率回傳-1，表示讀值過小
                freq = -1
                deltax=-1
                deltax_score=0
                # 將頻率和位移分數平均，存入self.ave_score
                self.ave_score.append((freq_score+deltax_score)/2)
                print(self.displacementRank,self.freqRank,deltax,freq,deltax_score,freq_score)
                
                return self.displacementRank,self.freqRank,deltax,freq
        else:
            # 落在正確範圍，繼續保持
            self.freqRank="Keep this rate"

        print("freq score")

        t=np.linspace(0,processing_time,N)
        tpa,ap,tva,av,peaks,valleys = extreme_finding(self.acc,t)
        t_val,v_val,x_val,delta_x=get_displacement(self.acc,t,peaks,valleys)
        print("displacements=")
        print(100*9.8*abs(x_val))
        print("average displacement = ")
        print(delta_x)

        # 計算加速度訊號中有幾個>=1.45g的波峰
        count = 0
        for i in range(len(ap)):
            if ap[i] >= 1.45 - self.GNORM_START:
                count += 1
        print("-------")
        print("$: ap =",end=" ")
        print(ap)
        print("$: count of points >= 1.45:",end=" ")
        print(count)
        print("--------")

        # 若無波峰，則判定讀值過小
        if len(ap) == 0:
            self.displacementRank = "No movement!!"
            deltax = -1
            deltax_score = 0
        # 若有3/5的波峰>=1.45，則辦定為位移達到5公分
        elif count >= int(len(ap)*3/5):
            self.displacementRank = "keep this depth"
            deltax = 5
            deltax_score = 100
        # 否則判定位移小於5公分
        else:
            self.displacementRank = "Press deeper!!"
            deltax = 0
            deltax_score = 50

        self.ave_score.append((freq_score+deltax_score)/2)
        return self.displacementRank,self.freqRank,deltax,freq

    # 算出總平均分數
    def get_ave_score(self):
        if len(self.ave_score)==0:
            return -1
        return np.average(np.array(self.ave_score))

    # 印出遊戲畫面上的頻率、位移訊息
    def print_Msg(self,freq_color,deltax_color):
        # Print self.displacementRank,self.freqRank,deltax,freq
        window_w = 160
        window_h = 200

        # 頻率、位移值的視窗
        freq_value_win = pygame.Surface((window_w ,window_h ))  # the size of your rect
        freq_value_win.set_alpha(int(128))                # alpha level
        freq_value_win.fill((0,112,168))           # this fills the entire surface

        deltax_value_win = pygame.Surface((window_w ,window_h ))  # the size of your rect
        deltax_value_win.set_alpha(int(128))                # alpha level
        deltax_value_win.fill((0,112,168))           # this fills the entire surface

        # 印有"BPM"和"Depth"字樣的視窗
        win_h = 30
        freq_win = pygame.Surface((window_w ,win_h))  # the size of your rect
        #freq_win.set_alpha(int(128))                # alpha level
        freq_win.fill((1,15,150))           # this fills the entire surface

        deltax_win = pygame.Surface((window_w ,win_h))  # the size of your rect
        #deltax_win.set_alpha(int(128))                # alpha level
        deltax_win.fill((1,15,150))           # this fills the entire surface

        # 顯示提示訊息的視窗
        rank_win_h = 30
        freq_rank_win = pygame.Surface((window_w ,rank_win_h))  # the size of your rect
        #freq_rank_win.set_alpha(int(128))                # alpha level
        freq_rank_win.fill((1,15,150))           # this fills the entire surface

        deltax_rank_win = pygame.Surface((window_w ,rank_win_h))  # the size of your rect
        #deltax_rank_win.set_alpha(int(128))                # alpha level
        deltax_rank_win.fill((1,15,150))           # this fills the entire surface

        # 提示改進
        draw_text(freq_rank_win,self.freqRank,20,window_w/2,rank_win_h/2,freq_color)
        draw_text(deltax_rank_win,self.displacementRank,20,window_w/2,rank_win_h/2,deltax_color)

        # 印出項目名
        draw_text(freq_win,"BPM",20,window_w/2,win_h/2,(255,255,255))
        draw_text(deltax_win,"Depth(cm)",20,window_w/2,win_h/2,(255,255,255))

        # 印出各視窗
        screen.blit(freq_value_win, (WIDTH/3-window_w/5-window_w/2,HIGHT/2-window_h/2))
        screen.blit(deltax_value_win, (WIDTH*2/3+window_w/5-window_w/2,HIGHT/2-window_h/2))

        screen.blit(freq_win, (WIDTH/3-window_w/5-window_w/2,HIGHT/2-window_h/2-win_h/2))
        screen.blit(deltax_win, (WIDTH*2/3+window_w/5-window_w/2,HIGHT/2-window_h/2-win_h/2))
        
        screen.blit(freq_rank_win, (WIDTH/3-window_w/5-window_w/2,HIGHT/2+window_h/2+rank_win_h/3))
        screen.blit(deltax_rank_win, (WIDTH*2/3+window_w/5-window_w/2,HIGHT/2+window_h/2+rank_win_h/3))

        # 印出bpm、位移數值
        draw_text(screen,self.freq_msg,40,WIDTH/3-window_w/5,HIGHT/2,(255,255,255))
        draw_text(screen,self.deltax_msg,40,WIDTH*2/3+window_w/5,HIGHT/2,(255,255,255))

    def update(self):

        print("\n")
        print("===============")
        print("theta0_x = "+str(self.theta0_x))
        print("theta0_y = "+str(self.theta0_y))
        print("theta0_z = "+str(self.theta0_z))
        print("===============")
        print("\n")

        # 先抓資料
        self.get_data()
        print("get data end")

        # 若抓資料過程中關閉遊戲，此函數到此中止
        if rabbo.Status ==0:
            print("DISCONNECT")
            raise ValueError
        if self.interupt:
            print("self.interupt")
            return None

        # 得出提示訊息和回傳的頻率、位移
        self.displacementRank,self.freqRank,deltax,freq = self.get_rank()
        print("get rank")

        # 先將頻率轉為BPM
        self.freq_msg=str(int(freq*60))

        freq_color = None
        deltax_color = None

        # 若頻率讀值過小，用白字顯示"---"
        if freq == -1:
            self.freq_msg = "---"
            freq_color = (255,255,255)
        # 若頻率落在標準範圍中，用綠字顯示"Keep this rate"
        elif self.freqRank == "Keep this rate":
            freq_color = (0,255,0)
        # 否則用紅字顯示"Faster"或"Slower
        else:
            freq_color = (255,0,0)

        # 若位移讀值過小，用白字顯示"None"
        if deltax == -1:
            self.deltax_msg="None"
            deltax_color = (255,255,255)
        # 若位移達5公分，用綠字顯示">=5cm
        elif deltax == 5:
            self.deltax_msg=">=5cm"
            deltax_color=(0,255,0)
        # 若位移未達5公分，用紅字顯示"<5cm
        else:
            self.deltax_msg="<5cm"
            deltax_color=(255,0,0)
        # 印出遊戲畫面
        self.print_Msg(freq_color,deltax_color)

        # 播放提示音效
        if self.displacementRank == "Press deeper!!":
            pygame.mixer.music.set_volume(0.1)
            deeper.play()
            pygame.mixer.music.set_volume(0.78)
        elif self.displacementRank == "keep this depth":
            pygame.mixer.music.set_volume(0.1)
            excellent.play()
            pygame.mixer.music.set_volume(0.78)


# 遊戲畫面上的文字方塊
class block(pygame.sprite.Sprite):
    def __init__(self,cen_x,cen_y,w,h,text,text_size,block_color,text_color=(255,255,255),alpha=255):
        pygame.sprite.Sprite.__init__(self)
        self.cen_x = cen_x
        self.cen_y = cen_y
        self.w = w
        self.h = h
        self.text = text
        self.text_size = text_size
        self.block_color = block_color
        self.text_color = text_color
        #　方塊透明度
        self.alpha = alpha

        # 創建一個長方形作為其image
        img = pygame.Surface((self.w ,self.h))  # the size of your rect
        img.set_alpha(self.alpha)                # alpha level
        img.fill(self.block_color)           # this fills the entire surface
        self.image = img

    #　設定方塊上的文字
    def set_text(self,new_text):
        self.text = new_text

    # 畫出文字方塊
    def draw_block(self):
        screen.blit(self.image,(self.cen_x-self.w/2,self.cen_y-self.h/2))
        draw_text(screen,self.text,self.text_size,self.cen_x,self.cen_y-2.5,self.text_color)

    def update(self):
        self.draw_block()

class button(block):
    def __init__(self,cen_x,cen_y,w,h,text,text_size,button_color,text_color=(255,255,255),alpha=255):
        super().__init__(cen_x,cen_y,w,h,text,text_size,button_color,text_color,alpha)

    # 判斷滑鼠游標是否有放在按鈕上
    def hover(self):
            x,y = pygame.mouse.get_pos()
            inside_button= x>self.cen_x-self.w/2 and x<self.cen_x+self.w/2 and y>self.cen_y-self.h/2 and y<self.cen_y+self.h/2
            return inside_button
    # 判斷滑鼠是否被按下
    def pressed(self):
        event=pygame.event.get()
        val = pygame.mouse.get_pressed()[0]

        # 等到滑鼠放開後，再執行按鈕功能
        while pygame.mouse.get_pressed()[0] and self.hover():
            event=pygame.event.get()
        return self.hover() and val

    # 畫出按鈕
    def draw_button(self):
        # 若滑鼠有放在按鈕上，按鈕就膨脹
        if not self.hover():
            super().draw_block()
        else:
            button_big = pygame.Rect(self.cen_x-1.1*self.w/2,self.cen_y-1.1*self.h/2,self.w*1.1,self.h*1.1)
            pygame.draw.rect(screen,self.block_color,button_big)
            draw_text(screen,self.text,round(self.text_size*1.1),self.cen_x,self.cen_y-2.5,self.text_color)

    def update(self):
        self.draw_button()

music_end = {"Baby shark":95,"學貓叫":104,"妖怪手錶":85}
music_start = {"Baby shark":11,"學貓叫":7,"妖怪手錶":5}

# 儲存音樂的資料的class
class backGroundMusic():
    def __init__(self,music_name="Baby shark"):
        self.music_name = music_name
        self.end_time = music_end[music_name]
        self.music = pygame.mixer.music.load(os.path.join("audio",self.music_name+".mp3"))
        self.start_time = music_start[music_name]

# 存放所有sprite的地方
all_sprites = None
# 待會用來乘載sensorData物件的變數
sd = None
# 紀錄遊戲開始的時間
game_start_time = None

#設定各個按鈕的位置、大小
# start
start_w = 130
start_h = 50
start_cenx = int(WIDTH/2)
start_ceny = int(HIGHT*3/4)

# back
back_w = 130
back_h = 50
back_cenx = int(WIDTH/2)
back_ceny = int(HIGHT/2)+80

# music_win
mw_w = 200
mw_h = 40
mw_cenx = WIDTH/2
mw_ceny = HIGHT/2+60

# left
left_w = 40
left_h = mw_h
left_cenx = WIDTH/2 - mw_w*1.3/2
left_ceny = mw_ceny

#right
right_w = 40
right_h = mw_h
right_cenx = WIDTH/2 + mw_w*1.3/2
right_ceny = mw_ceny 

# 遊戲背景音樂
bgm = None
# 撥放哪個背景音樂
music_idx = 0

try:
    while(running):
        # 此迴圈最多1秒執行60次
        if gamestate != 1:
            clock.tick(FPS)

        print("enter game state",end=" ")
        print(gamestate)

        # 預防 rabboni 斷線
        if rabbo.Status ==0:
            print("DISCONNECT")
            raise ValueError

        # 若玩家關閉遊戲視窗，則跳出迴圈
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                print('Shut done!')
                break
        if running == False:
            continue
        print("check shutdown")

        # loading 畫面
        if gamestate == -1:
            # 印出背景
            screen.fill(bg_color)
            # 印出鯊魚圖片
            screen.blit(pink_shark,(WIDTH/2-img_side/2,20))
            # 印出背景文字
            draw_text(screen,"Keep Your Brain SHARK",22,int(WIDTH/2),int(HIGHT/2)-10,(255,255,255))
            draw_text(screen,"NCTU Baby Makers",15,int(WIDTH/2),HIGHT*19/20,(255,255,255))
            draw_text(screen,"Loading...",30,int(WIDTH/2),HIGHT/2+80,(255,255,255))

            # 顯示畫面
            pygame.display.update()
            print("Loading drawn")

            # declare a sensorData object
            sd=sensorData()
            # 若玩家按下關閉視窗的按鍵，則跳出迴圈
            if sd.interupt:
                running = False
                continue
            print("sensor data declared!!")

            #創建一個裝有所有sprite的group
            all_sprites = pygame.sprite.Group()
            # 把sd加入all_sprite
            all_sprites.add(sd)
            print("all sprite finished!!")
            # 下次迴圈進入遊戲畫面
            gamestate = 1

            # 畫出背景畫面
            screen.blit(bg_img,(0,0))
            pygame.display.update()
            
            # 撥放背景音樂
            pygame.mixer.music.play(1)
            # 設定音量(輸入0~1之間的值)
            pygame.mixer.music.set_volume(0.78)
            # 紀錄遊戲開始時間
            game_start_time = time.time()

        # 初始畫面
        elif gamestate == 0:
            # 填滿背景顏色
            screen.fill((bg_color))
            print("Bckground filled")
            # 畫出鯊魚圖片
            screen.blit(pink_shark,(WIDTH/2-img_side/2,20))
            # 印出背景文字
            draw_text(screen,"Keep Your Brain SHARK",22,int(WIDTH/2),int(HIGHT/2)-10,(255,255,255))
            draw_text(screen,"NCTU Baby Makers",15,int(WIDTH/2),HIGHT*19/20,(255,255,255))
            draw_text(screen,"Press to start",15,start_cenx,start_ceny+start_h/2+20,(255,255,255))

            # 畫出start按鈕
            start_button = button(start_cenx,start_ceny,start_w,start_h,"START",30,(0,255,0))
            start_button.draw_button()
            # 畫出向左、右鍵
            left_button = button(left_cenx,left_ceny,left_w,left_h,"<",30,(0,0,255))
            left_button.draw_button()
            right_button = button(right_cenx,right_ceny,right_w,right_h,">",30,(0,0,255))
            right_button.draw_button()

            # select music
            music_arr = ["Baby shark","學貓叫","妖怪手錶"]
            
            if left_button.pressed():
                music_idx -= 1
                if music_idx < 0:
                    music_idx += len(music_arr)     
            elif right_button.pressed():
                music_idx += 1
                if music_idx >= len(music_arr):
                    music_idx -= len(music_arr)

            # 音樂選單
            music_win = block(mw_cenx,mw_ceny,mw_w,mw_h,music_arr[music_idx],30,(125,125,125))
            music_win.draw_block()

            pygame.display.update()
            print("music selected")

            # start is pressed
            if start_button.pressed():
                # 宣告 backGroundMusic 物件
                bgm = backGroundMusic(music_arr[music_idx])
                # 進入loading 畫面
                gamestate = -1

            print("Event checked")

        # 遊戲進行中
        elif gamestate == 1:
            # display
            #update game data
            # 執行all_sprite中每個物件的update函式
            # -->每個物件都要寫update()

            # 遊戲時間到，結算分數
            if time.time() - game_start_time >= bgm.end_time:
                print("$: game stop!!")
                pygame.mixer.music.stop()
                gamestate = 2
                continue

            # 前奏
            elif time.time() - game_start_time < bgm.start_time:
                print("前奏")
                screen.blit(bg_img,(0,0))
                draw_text(screen,"Ready...",50,WIDTH/2,HIGHT/3,(255,255,255))

                x = int((time.time() - game_start_time) + 1)
                if x > bgm.start_time:
                    x=bgm.start_time
                x=bgm.start_time+1-x
                # 顯示倒數計時
                draw_text(screen,str(x),50,WIDTH/2,HIGHT/2,(255,255,255))
                pygame.display.update()
                continue

            # 在 sd 第一次計算資料結束之前，先顯示視窗
            if time.time() - game_start_time < bgm.start_time + processing_time:
                screen.blit(bg_img,(0,0))
                sd.print_Msg((255,255,255),(255,255,255))
                pygame.display.update()

            # 更新顯示
            screen.blit(bg_img,(0,0))
            all_sprites.update()
            print("update")

            # 若玩家按下關閉視窗鍵，就跳出迴圈
            if sd.interupt:
                running = False
                continue

            pygame.display.update()
            print("display update")


        # 遊戲結束，顯示評分和"Time's up"
        elif gamestate == 2:
            # 顯示背景音樂
            screen.blit(bg_img,(0,0))

            # 算出平均
            original_ave=sd.get_ave_score()
            print("original_ave =",end=" ")
            print(original_ave)

            # 避免平均超過100
            if original_ave<0 or original_ave>100:
                print("Invalid original_ave",end=" ")
                print(original_ave)
                raise ValueError
            
            # 顯示文字
            draw_text(screen,str("Time's up!"),50,int(WIDTH*1/2),HIGHT/2-HIGHT/6,(255,255,255))
            draw_text(screen,str("You scored"),20,int(WIDTH*1/3),HIGHT/2,(255,255,255))
            draw_text(screen,str(round(original_ave,1)),50,int(WIDTH*1/2)+50,HIGHT/2,(255,255,255))
            print("text drawn")

            # 畫出按鈕
            back_button = button(back_cenx,back_ceny,back_w,back_h,"Back",30,(0,255,0))
            back_button.draw_button()

            pygame.display.update()

            # Back is pressed
            if back_button.pressed():
                # 跳到初始畫面
                gamestate = 0
            print("event checked")
            
        else:
            print("Invalid gamestate",end=" ")
            print(gamestate)
            raise ValueError


    #關閉遊戲
    pygame.quit()
    rabbo.stop()
    print('Game closed')

except KeyboardInterrupt:
    pygame.quit()
    rabbo.stop()
