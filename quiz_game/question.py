import pygame
import os 

#constant
FPS = 20
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
BLACK_BLUE = (0, 0, 51)
PINK_BLUE =(100, 170, 255) 
YELLOW = (255,255,0)
BLACK = (0,0,0)
WIDTH = 400
HEIGHT = 600
QUESTION_HEIGHT = 200

#初始化
pygame.init() #pygame內的東東初始化
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH , HEIGHT)) #創建視窗and 視窗大小
pygame.display.set_caption("Quiz Game") # 遊戲名稱
clock = pygame.time.Clock() #物件對時間的管理

#因為question可能很長，所以我們要給他一個surface(因為後面有def blit_text可以把一行字拆開(因為pygame輸出讀不到換行符號))
quetion = pygame.Surface((WIDTH - 100 , QUESTION_HEIGHT - 50))
quetion = quetion.convert()
quetion.fill(WHITE)
quetion.set_alpha(200)


#載入圖片
background = pygame.image.load(os.path.join("img","bakground.jpg")).convert()
pink_fish = pygame.image.load(os.path.join("img","pink1.png")).convert()
pink_fish.set_colorkey((0,0,0))
pink_fish.convert_alpha()
pink_fish = pygame.transform.scale(pink_fish,(400,600))
#載入音樂
background_music = pygame.mixer.music.load(os.path.join("audio","Baby shark.mp3"))

# 載入字體
#font_name = pygame.font.match_font("arial")
font = pygame.font.Font("msjh.ttc", 35)
font1 = pygame.font.Font("msjh.ttc", 25)
font2 = pygame.font.Font("msjh.ttc", 30)
# 寫一個把文字印出的函式
def draw_text(surf, text,size,x,y,color):
    font = pygame.font.Font("msjh.ttc",size)
    text_surface = font.render(text,True,color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surf.blit(text_surface,text_rect)

#一個可以把文字拆開的函示
def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

#可以劃出一個框框，然後可以填字
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
        self.alpha = alpha

        img = pygame.Surface((self.w ,self.h))  # the size of your rect
        img.set_alpha(self.alpha)                # alpha level
        img.fill(self.block_color)           # this fills the entire surface
        self.image = img

    def draw_block(self):
        screen.blit(self.image,(self.cen_x-self.w/2,self.cen_y-self.h/2))
        draw_text(screen,self.text,self.text_size,self.cen_x,self.cen_y - 2.5,self.text_color)
    def update(self):
        self.draw_block()

#畫出按鍵
class button(block):
    def __init__(self,cen_x,cen_y,w,h,text,text_size,button_color,text_color=(255,255,255),alpha=255):
        super().__init__(cen_x,cen_y,w,h,text,text_size,button_color,text_color,alpha)

    def hover(self):
            x,y = pygame.mouse.get_pos()
            inside_button= x>self.cen_x-self.w/2 and x<self.cen_x+self.w/2 and y>self.cen_y-self.h/2 and y<self.cen_y+self.h/2
            return inside_button
    
    def pressed(self):
        event=pygame.event.get()
        val = pygame.mouse.get_pressed()[0]
        
        while pygame.mouse.get_pressed()[0] and self.hover():
            event=pygame.event.get()
        
        return self.hover() and val

    def draw_button(self):
        if not self.hover():
            super().draw_block()
        else:
            button_big = pygame.Rect(self.cen_x-1.1*self.w/2,self.cen_y-1.1*self.h/2,self.w*1.1,self.h*1.1)
            pygame.draw.rect(screen,self.block_color,button_big)
            draw_text(screen,self.text,self.text_size + 2,self.cen_x,self.cen_y - 2.5,self.text_color)

    def update(self):
        self.draw_button()



#QUETION AND CHOICE(情境模擬題)
quetion1 = "當您看到有人突然倒地 請問您的第一個想法是?"
quetion1_a = "趕緊避開避免責任"
quetion1_b = "拿出手機圍觀"
quetion1_c = "確認他的意識與呼吸"
quetion1_d = "嘲笑他突然跌倒"

quetion2 = "該怎麼判斷 正常呼吸和脈搏呢?"
quetion2_a = "透過頸動脈、肱動脈判斷脈搏"
quetion2_b = "默念一千零一到一千零七(10秒)"
quetion2_c = "趴下觀察胸口起伏"
quetion2_d = "以上皆是"

quetion3 = "假如那人無意識且 無正常呼吸時我們應該?"
quetion3_a = "大聲呼叫病人並求救"
quetion3_b = "開始準備CPR"
quetion3_c = "請求他人尋找AED"
quetion3_d = "以上皆是"

quetion4 = "有關高品質CPR 下列何者錯誤?"
quetion4_a = "按壓位置為兩乳頭中央"
quetion4_b = "為了快速按壓可以不用等待回彈"
quetion4_c = "速度維持在100-120/min"
quetion4_d = "深度必須要5cm以上"

quetion5 = "關於CPR姿勢的描述 下列何者錯誤？"
quetion5_a = "讓傷患平躺硬板上"
quetion5_b = "不可移動手的位置，雙肘勿彎曲"
quetion5_c = "累的話可以休息一下"
quetion5_d = "成人按壓位置為兩乳頭連線中間"

quetion6 = "關於CPR的知識 下列何者錯誤?"
quetion6_a = "按壓時確保呼吸道暢通"
quetion6_b = "AED電擊時也需要邊CPR"
quetion6_c = "可以喊出節奏，確保速度"
quetion6_d = "在沒力時可以請求身邊人員換手"

quetion7 = "關於AED實施 下列何者錯誤?"
quetion7_a = "只要貼上貼片都會被電擊"
quetion7_b = "可以判斷心臟有無亂跳或顫抖"
quetion7_c = "需依照裝置上的提示貼貼片"
quetion7_d = "可以非常有效提高存活率"

quetion8 = "當AED顯示不須電擊 但他還沒恢復呼吸 我們應該"
quetion8_a = "不用理他了"
quetion8_b = "等待AED的再次判斷"
quetion8_c = "繼續CPR"
quetion8_d = "幫他擺成復甦姿勢"

quetion9 = "關於AED的資訊 下列何者錯誤"
quetion9_a = "要是體毛太多可以使用貼片黏掉"
quetion9_b = "可以直接貼在衣服上進行"
quetion9_c = "通常置放在公共場合"
quetion9_d = "電擊時必須遠離病患"

quetion10 = "哪一個是CPR的 救命口訣呢?"
quetion10_a = "內外夾弓大立腕"
quetion10_b = "叫叫CABD"
quetion10_c = "濕搓沖捧擦"
quetion10_d = "叫叫伸拋滑"

#QUETION AND CHOICE(解答疑惑題)
quetion11 = "為什麼要幫忙急救？ 不能打119就好了嗎？"
quetion11_a = "119在撥打後4-6分鐘內才能到達"
quetion11_b = "僅靠醫護人員絕對來不及"
quetion11_c = "初步的急救其實不困難"
quetion11_d = "以上皆是"

quetion12 = "為什麼 我要學會CPR？"
quetion12_a = "台灣急救存活率僅21%有待加強"
quetion12_b = "一生中會遇到3.48次緊急事件"
quetion12_c = "維持患者生命徵象和避免二度傷害"
quetion12_d = "有備無患且以上皆是"

quetion13 = "關於什麼時候進行CPR 何者錯誤？"
quetion13_a = "溺水、昏迷、心肌梗塞等"
quetion13_b = "確認患者沒有呼吸及心跳"
quetion13_c = "直接衝上去進行急救就對了"
quetion13_d = "確保周遭環境安全"

quetion14 = "我不敢CPR 現場又只有我一個人 該怎麼辦？"
quetion14_a = "逃跑"
quetion14_b = "為患者祈禱"
quetion14_c = "去找別人幫忙"
quetion14_d = "打119並遵從人員指示"

quetion15 = "不敢做 人工呼吸怎麼辦?"
quetion15_a = "這樣就沒有急救的意義了"
quetion15_b = "可以只進行胸部按壓+AED"
quetion15_c = "口對口人工呼吸一定要做"
quetion15_d = "停止CPR找別人幫忙"

quetion16 = "出手急救 會不會有法律責任？"
quetion16_a = "出手救援的民眾有責"
quetion16_b = "跟隨的醫護人員有責"
quetion16_c = "看患者家屬是否提告"
quetion16_d = "適用緊急避難的法律而免責"

quetion17 = "在急救中 壓斷患者的肋骨 我會被告嗎？"
quetion17_a = "不會，急救中可能七成以上肋骨會斷"
quetion17_b = "不會，CPR的深度肋骨不會斷"
quetion17_c = "會，屬於過失傷害罪"
quetion17_d = "會，屬於非告訴乃論之罪名"

#sprites
all_sprites = pygame.sprite.Group()
button1 = button(WIDTH / 2,HEIGHT / 2 + 100,170,50,"情境模擬題",30,PINK_BLUE,WHITE,255)
button2 = button(WIDTH / 2,HEIGHT / 2 + 170,170,50,"解答疑惑題",30,PINK_BLUE,WHITE,255)
all_sprites.add(button1)
all_sprites.add(button2)

b = 75
c = 2 * b
d = 3 * b

#結束頁面
end = pygame.sprite.Group()
button3 = button(WIDTH / 2,HEIGHT / 2 +200,150,50,"Restart",30,PINK_BLUE,WHITE,255)
end.add(button3)

#結果
Answer = pygame.sprite.Group()
next = button(WIDTH / 2, 300, 200, 50, "next" ,20,WHITE, BLACK, 255)
Answer.add(next)

#問題1
Quetion1 = pygame.sprite.Group()
q1_button1 = button(WIDTH / 2, 250, 200, 50, quetion1_a ,20,WHITE, BLACK, 255)
q1_button2 = button(WIDTH / 2, 250 + b, 200, 50, quetion1_b ,20,WHITE, BLACK, 255)
q1_button3 = button(WIDTH / 2, 250 + c, 200, 50, quetion1_c ,20,WHITE, BLACK, 255)
q1_button4 = button(WIDTH / 2, 250 + d, 200, 50, quetion1_d ,20,WHITE, BLACK, 255)
Quetion1.add(q1_button1)
Quetion1.add(q1_button2)
Quetion1.add(q1_button3)
Quetion1.add(q1_button4)

#問題2
Quetion2 = pygame.sprite.Group()
q2_button1 = button(WIDTH / 2, 250, 300, 50, quetion2_a ,20,WHITE, BLACK, 255)
q2_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion2_b ,20,WHITE, BLACK, 255)
q2_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion2_c ,20,WHITE, BLACK, 255)
q2_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion2_d ,20,WHITE, BLACK, 255)
Quetion2.add(q2_button1)
Quetion2.add(q2_button2)
Quetion2.add(q2_button3)
Quetion2.add(q2_button4)

#問題3
Quetion3 = pygame.sprite.Group()
q3_button1 = button(WIDTH / 2, 250, 200, 50, quetion3_a ,20,WHITE, BLACK, 255)
q3_button2 = button(WIDTH / 2, 250 + b, 200, 50, quetion3_b ,20,WHITE, BLACK, 255)
q3_button3 = button(WIDTH / 2, 250 + c, 200, 50, quetion3_c ,20,WHITE, BLACK, 255)
q3_button4 = button(WIDTH / 2, 250 + d, 200, 50, quetion3_d ,20,WHITE, BLACK, 255)
Quetion3.add(q3_button1)
Quetion3.add(q3_button2)
Quetion3.add(q3_button3)
Quetion3.add(q3_button4)

#問題4
Quetion4 = pygame.sprite.Group()
q4_button1 = button(WIDTH / 2, 250, 300, 50, quetion4_a ,20,WHITE, BLACK, 255)
q4_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion4_b ,20,WHITE, BLACK, 255)
q4_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion4_c ,20,WHITE, BLACK, 255)
q4_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion4_d ,20,WHITE, BLACK, 255)
Quetion4.add(q4_button1)
Quetion4.add(q4_button2)
Quetion4.add(q4_button3)
Quetion4.add(q4_button4)

#問題5
Quetion5 = pygame.sprite.Group()
q5_button1 = button(WIDTH / 2, 250, 300, 50, quetion5_a ,20,WHITE, BLACK, 255)
q5_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion5_b ,20,WHITE, BLACK, 255)
q5_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion5_c ,20,WHITE, BLACK, 255)
q5_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion5_d ,20,WHITE, BLACK, 255)
Quetion5.add(q5_button1)
Quetion5.add(q5_button2)
Quetion5.add(q5_button3)
Quetion5.add(q5_button4)

#問題6
Quetion6 = pygame.sprite.Group()
q6_button1 = button(WIDTH / 2, 250, 300, 50, quetion6_a ,20,WHITE, BLACK, 255)
q6_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion6_b ,20,WHITE, BLACK, 255)
q6_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion6_c ,20,WHITE, BLACK, 255)
q6_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion6_d ,20,WHITE, BLACK, 255)
Quetion6.add(q6_button1)
Quetion6.add(q6_button2)
Quetion6.add(q6_button3)
Quetion6.add(q6_button4)

#問題7
Quetion7 = pygame.sprite.Group()
q7_button1 = button(WIDTH / 2, 250, 300, 50, quetion7_a ,20,WHITE, BLACK, 255)
q7_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion7_b ,20,WHITE, BLACK, 255)
q7_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion7_c ,20,WHITE, BLACK, 255)
q7_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion7_d ,20,WHITE, BLACK, 255)
Quetion7.add(q7_button1)
Quetion7.add(q7_button2)
Quetion7.add(q7_button3)
Quetion7.add(q7_button4)

#問題8
Quetion8 = pygame.sprite.Group()
q8_button1 = button(WIDTH / 2, 250, 300, 50, quetion8_a ,20,WHITE, BLACK, 255)
q8_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion8_b ,20,WHITE, BLACK, 255)
q8_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion8_c ,20,WHITE, BLACK, 255)
q8_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion8_d ,20,WHITE, BLACK, 255)
Quetion8.add(q8_button1)
Quetion8.add(q8_button2)
Quetion8.add(q8_button3)
Quetion8.add(q8_button4)

#問題9
Quetion9 = pygame.sprite.Group()
q9_button1 = button(WIDTH / 2, 250, 300, 50, quetion9_a ,20,WHITE, BLACK, 255)
q9_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion9_b ,20,WHITE, BLACK, 255)
q9_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion9_c ,20,WHITE, BLACK, 255)
q9_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion9_d ,20,WHITE, BLACK, 255)
Quetion9.add(q9_button1)
Quetion9.add(q9_button2)
Quetion9.add(q9_button3)
Quetion9.add(q9_button4)

#問題10
Quetion10 = pygame.sprite.Group()
q10_button1 = button(WIDTH / 2, 250, 300, 50, quetion10_a ,20,WHITE, BLACK, 255)
q10_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion10_b ,20,WHITE, BLACK, 255)
q10_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion10_c ,20,WHITE, BLACK, 255)
q10_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion10_d ,20,WHITE, BLACK, 255)
Quetion10.add(q10_button1)
Quetion10.add(q10_button2)
Quetion10.add(q10_button3)
Quetion10.add(q10_button4)

#問題11
Quetion11 = pygame.sprite.Group()
q11_button1 = button(WIDTH / 2, 250, 300, 50, quetion11_a ,20,WHITE, BLACK, 255)
q11_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion11_b ,20,WHITE, BLACK, 255)
q11_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion11_c ,20,WHITE, BLACK, 255)
q11_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion11_d ,20,WHITE, BLACK, 255)
Quetion11.add(q11_button1)
Quetion11.add(q11_button2)
Quetion11.add(q11_button3)
Quetion11.add(q11_button4)

#問題12
Quetion12 = pygame.sprite.Group()
q12_button1 = button(WIDTH / 2, 250, 300, 50, quetion12_a ,20,WHITE, BLACK, 255)
q12_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion12_b ,20,WHITE, BLACK, 255)
q12_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion12_c ,20,WHITE, BLACK, 255)
q12_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion12_d ,20,WHITE, BLACK, 255)
Quetion12.add(q12_button1)
Quetion12.add(q12_button2)
Quetion12.add(q12_button3)
Quetion12.add(q12_button4)

#問題13
Quetion13 = pygame.sprite.Group()
q13_button1 = button(WIDTH / 2, 250, 250, 50, quetion13_a ,20,WHITE, BLACK, 255)
q13_button2 = button(WIDTH / 2, 250 + b, 250, 50, quetion13_b ,20,WHITE, BLACK, 255)
q13_button3 = button(WIDTH / 2, 250 + c, 250, 50, quetion13_c ,20,WHITE, BLACK, 255)
q13_button4 = button(WIDTH / 2, 250 + d, 250, 50, quetion13_d ,20,WHITE, BLACK, 255)
Quetion13.add(q13_button1)
Quetion13.add(q13_button2)
Quetion13.add(q13_button3)
Quetion13.add(q13_button4)

#問題14
Quetion14 = pygame.sprite.Group()
q14_button1 = button(WIDTH / 2, 250, 250, 50, quetion14_a ,20,WHITE, BLACK, 255)
q14_button2 = button(WIDTH / 2, 250 + b, 250, 50, quetion14_b ,20,WHITE, BLACK, 255)
q14_button3 = button(WIDTH / 2, 250 + c, 250, 50, quetion14_c ,20,WHITE, BLACK, 255)
q14_button4 = button(WIDTH / 2, 250 + d, 250, 50, quetion14_d ,20,WHITE, BLACK, 255)
Quetion14.add(q14_button1)
Quetion14.add(q14_button2)
Quetion14.add(q14_button3)
Quetion14.add(q14_button4)

#問題15
Quetion15 = pygame.sprite.Group()
q15_button1 = button(WIDTH / 2, 250, 270, 50, quetion15_a ,20,WHITE, BLACK, 255)
q15_button2 = button(WIDTH / 2, 250 + b, 270, 50, quetion15_b ,20,WHITE, BLACK, 255)
q15_button3 = button(WIDTH / 2, 250 + c, 270, 50, quetion15_c ,20,WHITE, BLACK, 255)
q15_button4 = button(WIDTH / 2, 250 + d, 270, 50, quetion15_d ,20,WHITE, BLACK, 255)
Quetion15.add(q15_button1)
Quetion15.add(q15_button2)
Quetion15.add(q15_button3)
Quetion15.add(q15_button4)

#問題16
Quetion16 = pygame.sprite.Group()
q16_button1 = button(WIDTH / 2, 250, 300, 50, quetion16_a ,20,WHITE, BLACK, 255)
q16_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion16_b ,20,WHITE, BLACK, 255)
q16_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion16_c ,20,WHITE, BLACK, 255)
q16_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion16_d ,20,WHITE, BLACK, 255)
Quetion16.add(q16_button1)
Quetion16.add(q16_button2)
Quetion16.add(q16_button3)
Quetion16.add(q16_button4)

#問題17
Quetion17 = pygame.sprite.Group()
q17_button1 = button(WIDTH / 2, 250, 320, 50, quetion17_a ,20,WHITE, BLACK, 255)
q17_button2 = button(WIDTH / 2, 250 + b, 300, 50, quetion17_b ,20,WHITE, BLACK, 255)
q17_button3 = button(WIDTH / 2, 250 + c, 300, 50, quetion17_c ,20,WHITE, BLACK, 255)
q17_button4 = button(WIDTH / 2, 250 + d, 300, 50, quetion17_d ,20,WHITE, BLACK, 255)
Quetion17.add(q17_button1)
Quetion17.add(q17_button2)
Quetion17.add(q17_button3)
Quetion17.add(q17_button4)


#狀態
running = True
gamestate = 0
score = 0
number = 0
pygame.mixer.music.play(-1)

#遊戲迴圈
while running:
    clock.tick(FPS) #在一秒鐘之內最多只能被執行n次
    #取得輸入
    for event in pygame.event.get(): #回傳所有事件(鍵盤按下、滑鼠)列表
        if event.type == pygame.QUIT:
            running = False  
    #畫面顯示
    if (gamestate == 0):
        screen.fill(BLACK_BLUE)#RGB  
        screen.blit(pink_fish,(WIDTH / 2 - 200, -150))
        all_sprites.update()
        quetion.fill(WHITE)
        score = 0
        draw_text(screen, "Quiz Game", 35, WIDTH / 2, HEIGHT / 2, YELLOW)
        draw_text(screen, "NCTU Baby Makers", 20, WIDTH / 2, HEIGHT - 30, YELLOW)
        if (button1.pressed()):
            gamestate = 1
            number = 1
        elif (button2.pressed()):
            gamestate = 1
            number = 2
    if(number == 1):
        if (gamestate == 1):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            blit_text(quetion, quetion1, (30,20) ,font1 , BLACK )
            Quetion1.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q1_button1.pressed() or q1_button2.pressed() or q1_button4.pressed()):
                gamestate = -2
                temp_gamestate = 1
            if (q1_button3.pressed()):
                gamestate = -1
                temp_gamestate = 1
                score += 1

        elif (gamestate == 2):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion2, (30,20) ,font1 , BLACK )
            Quetion2.update()  
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)
            if (q2_button1.pressed() or q2_button2.pressed() or q2_button3.pressed()):
                gamestate = -2
                temp_gamestate = 2
            if (q2_button4.pressed()):
                gamestate = -1
                temp_gamestate = 2
                score += 1

        elif (gamestate == 3):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion3, (30,20) ,font1, BLACK )
            Quetion3.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q3_button1.pressed() or q3_button2.pressed() or q3_button3.pressed()):
                gamestate = -2
                temp_gamestate = 3
            if (q3_button4.pressed()):
                gamestate = -1
                temp_gamestate = 3  
                score += 1   

        elif (gamestate == 4):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion4, (30,20) , font1, BLACK )
            Quetion4.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q4_button1.pressed() or q4_button3.pressed() or q4_button4.pressed()):
                gamestate = -2
                temp_gamestate = 4
            if (q4_button2.pressed()):
                gamestate = -1
                temp_gamestate = 4 
                score += 1   

        elif (gamestate == 5):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion5, (30,19.5) , font1, BLACK )
            Quetion5.update()
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)  
            if (q5_button1.pressed() or q5_button2.pressed() or q5_button4.pressed()):
                gamestate = -2
                temp_gamestate = 5
            if (q5_button3.pressed()):
                gamestate = -1
                temp_gamestate = 5 
                score += 1 

        elif (gamestate == 6):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion6, (30,20) , font, BLACK )
            Quetion6.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q6_button1.pressed() or q6_button3.pressed() or q6_button4.pressed()):
                gamestate = -2
                temp_gamestate = 6
            if (q6_button2.pressed()):
                gamestate = -1
                temp_gamestate = 6 
                score += 1                                         

        elif (gamestate == 7):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion7, (30,20) , font, BLACK )
            Quetion7.update()  
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)
            if (q7_button2.pressed() or q7_button3.pressed() or q7_button4.pressed()):
                gamestate = -2
                temp_gamestate = 7
            if (q7_button1.pressed()):
                gamestate = -1
                temp_gamestate = 7 
                score += 1   

        elif (gamestate == 8):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion8, (22,30) , font1, BLACK )
            Quetion8.update()  
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)
            if (q8_button1.pressed() or q8_button2.pressed() or q8_button4.pressed()):
                gamestate = -2
                temp_gamestate = 8
            if (q8_button3.pressed()):
                gamestate = -1
                temp_gamestate = 8
                score += 1            

        elif (gamestate == 9):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion9, (30,30) , font, BLACK )
            Quetion9.update()  
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)
            if (q9_button1.pressed() or q9_button3.pressed() or q9_button4.pressed()):
                gamestate = -2
                temp_gamestate = 9
            if (q8_button2.pressed()):
                gamestate = -1
                temp_gamestate = 9 
                score += 1

        elif (gamestate == 10):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion10, (35,25) , font, BLACK )
            Quetion10.update() 
            draw_text(quetion, str(gamestate), 30, 17, 15, BLACK) 
            if (q10_button1.pressed() or q10_button3.pressed() or q10_button4.pressed()):
                gamestate = -2
                temp_gamestate = 10
            if (q10_button2.pressed()):
                gamestate = -1
                temp_gamestate = 10 
                score += 1
                

        elif (gamestate == -1):
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            draw_text(screen, "Great!", 64, WIDTH / 2, HEIGHT / 2 - 100, YELLOW)
            Answer.update()
            if(next.pressed()):
                if (temp_gamestate == 10):
                    gamestate = -3
                else:
                    gamestate = temp_gamestate + 1


        elif (gamestate == -2):
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))   
            draw_text(screen, "QQ", 64, WIDTH / 2, HEIGHT / 2 - 100, YELLOW) 
            Answer.update()
            if(next.pressed()):
                if (temp_gamestate == 10):
                    gamestate = -3
                else:
                    gamestate = temp_gamestate + 1

        elif (gamestate == -3):
            screen.fill(BLACK_BLUE)#RGB  
            screen.blit(pink_fish,(WIDTH / 2 - 200, -150))
            draw_text(screen, "Score", 30, WIDTH / 2, HEIGHT / 2 , YELLOW)
            draw_text(screen, str(score), 30, WIDTH / 2 - 30, HEIGHT / 2 + 50, YELLOW)
            draw_text(screen, " / 10", 30, WIDTH / 2 + 15, HEIGHT / 2 + 50, YELLOW)
            draw_text(screen, "NCTU Baby Makers", 20, WIDTH / 2, HEIGHT - 30, YELLOW)
            if (score == 10 or score == 9):
                draw_text(screen, "你是CPR高手!", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW)
            elif (score <= 8 and score >= 6):
                draw_text(screen, "只差一點QQ", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW)
            elif (score <= 5 and score >= 3):
                draw_text(screen, "記得上健康課", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW) 
            elif (score <= 2 and score >= 0):
                draw_text(screen, "找老師個別輔導", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW)
            end.update()
            if(button3.pressed()):
                gamestate = 0

    if(number == 2):
        if (gamestate == 1):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            blit_text(quetion, quetion11, (30,20) ,font1 , BLACK )
            Quetion11.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q11_button1.pressed() or q11_button2.pressed() or q11_button3.pressed()):
                gamestate = -2
                temp_gamestate = 1
            if (q11_button4.pressed()):
                gamestate = -1
                temp_gamestate = 1
                score += 1

        elif (gamestate == 2):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion12, (30,20) ,font , BLACK )
            Quetion12.update()  
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)
            if (q12_button1.pressed() or q12_button2.pressed() or q12_button3.pressed()):
                gamestate = -2
                temp_gamestate = 2
            if (q12_button4.pressed()):
                gamestate = -1
                temp_gamestate = 2
                score += 1

        elif (gamestate == 3):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion13, (30,20) ,font1, BLACK )
            Quetion13.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q13_button1.pressed() or q13_button2.pressed() or q13_button4.pressed()):
                gamestate = -2
                temp_gamestate = 3
            if (q13_button3.pressed()):
                gamestate = -1
                temp_gamestate = 3  
                score += 1   

        elif (gamestate == 4):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion14, (30,20) , font1, BLACK )
            Quetion14.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q14_button1.pressed() or q14_button2.pressed() or q14_button3.pressed()):
                gamestate = -2
                temp_gamestate = 4
            if (q14_button4.pressed()):
                gamestate = -1
                temp_gamestate = 4 
                score += 1   

        elif (gamestate == 5):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion15, (30,19.5) , font, BLACK )
            Quetion15.update()
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)  
            if (q15_button1.pressed() or q15_button3.pressed() or q15_button4.pressed()):
                gamestate = -2
                temp_gamestate = 5
            if (q15_button2.pressed()):
                gamestate = -1
                temp_gamestate = 5 
                score += 1 

        elif (gamestate == 6):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion16, (30,20) , font1, BLACK )
            Quetion16.update() 
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK) 
            if (q16_button1.pressed() or q16_button2.pressed() or q16_button3.pressed()):
                gamestate = -2
                temp_gamestate = 6
            if (q16_button4.pressed()):
                gamestate = -1
                temp_gamestate = 6 
                score += 1                                         

        elif (gamestate == 7):  
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            screen.blit(quetion, (50,50))
            quetion.fill(WHITE)
            quetion.set_alpha(200)
            blit_text(quetion, quetion17, (30,20) , font1, BLACK )
            Quetion17.update()  
            draw_text(quetion, str(gamestate), 30, 13, 15, BLACK)
            if (q17_button2.pressed() or q17_button3.pressed() or q17_button4.pressed()):
                gamestate = -2
                temp_gamestate = 7
            if (q17_button1.pressed()):
                gamestate = -1
                temp_gamestate = 7 
                score += 1   

        elif (gamestate == -1):
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))
            draw_text(screen, "Great!", 64, WIDTH / 2, HEIGHT / 2 - 100, YELLOW)
            Answer.update()
            if(next.pressed()):
                if (temp_gamestate == 7):
                    gamestate = -3
                else:
                    gamestate = temp_gamestate + 1


        elif (gamestate == -2):
            screen.fill(BLACK)#RGB  
            screen.blit(background, (0,0))   
            draw_text(screen, "QQ", 64, WIDTH / 2, HEIGHT / 2 - 100, YELLOW) 
            Answer.update()
            if(next.pressed()):
                if (temp_gamestate == 7):
                    gamestate = -3
                else:
                    gamestate = temp_gamestate + 1

        elif (gamestate == -3):
            screen.fill(BLACK_BLUE)#RGB  
            screen.blit(pink_fish,(WIDTH / 2 - 200, -150))
            
            draw_text(screen, "Score", 30, WIDTH / 2, HEIGHT / 2 , YELLOW)
            draw_text(screen, str(score), 30, WIDTH / 2 - 30, HEIGHT / 2 + 50, YELLOW)
            draw_text(screen, " / 7", 30, WIDTH / 2 + 15, HEIGHT / 2 + 50, YELLOW)
            draw_text(screen, "NCTU Baby Makers", 20, WIDTH / 2, HEIGHT - 30, YELLOW)
            if (score == 7 or score == 6):
                draw_text(screen, "你非常熱心助人!", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW)
            elif (score == 5):
                draw_text(screen, "只差一點QQ", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW)
            elif (score <= 4 and score >= 3):
                draw_text(screen, "可以再勇敢一點", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW) 
            elif (score <= 2 and score >= 0):
                draw_text(screen, "找老師個別輔導", 30, WIDTH / 2 , HEIGHT / 2 + 100, YELLOW)
            end.update()
            if(button3.pressed()):
                gamestate = 0


    pygame.display.update()#更新顏色

pygame.quit()         