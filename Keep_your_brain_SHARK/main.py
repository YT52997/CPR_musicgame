import random
import time

from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout

Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from transform import transform, transform_perspective, transform_2d
    from user_action import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down
    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    # set vertical lines
    V_NB_LINES = 2
    V_LINES_SPACING = .25  # the ratio of width
    vertical_lines = []

    # set horizontal lines
    H_NB_LINES = 10
    H_LINES_SPACING = .12  # the ratio of height
    horizontal_lines = []

    # 往前走速度
    current_offset_y = 0
    BPM = 110

    current_offset_x = 0

    current_y_loop = 0
    score = 0
    flag = 1

    # 地板白磚塊設定
    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    # 船設定
    SHIP_WIDTH = 0.13
    SHIP_HEIGHT = 0.06
    SHIP_BASE_Y = 0.07
    ship = None  # 建立船物件
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    # 記錄遊戲輸贏狀態
    state_game_over = False
    state_game_has_started = False

    # 介面設定
    menu_title = StringProperty("Keep your brain\n\n       SHARK")
    menu_button_title = StringProperty("START")
    score_txt = StringProperty("JUMP: 0")
    time_txt = StringProperty("TIME: 0 : 0")
    start_time = time.time()
    t = 0

    # 聲音物件
    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_gameover1_voice = None
    sound_music1 = None
    sound_music2 = None
    sound_music3 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("init W: "+str(self.width)+" H: "+str(self.height))
        self.init_audio()
        self.init_vertical_line()
        self.init_horizontal_line()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        self.sound_galaxy.play()

        # 如果這是電腦才能判斷空白鍵 (否則手機會跳出鍵盤影響遊戲畫面呈現)
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        # 每1/60 秒 執行一次update (FPS=60)
        Clock.schedule_interval(self.update, 1.0/60.0)

    # 設定音效
    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/click_sound.wav")
        self.sound_galaxy = SoundLoader.load("audio/lets-go-sound-effect.mp3")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_sound.wav")
        self.sound_gameover1_voice = SoundLoader.load("audio/win_sound.wav")
        self.sound_music1 = SoundLoader.load("audio/BabyShark.wav")
        self.sound_music1.loop = True  # 遊戲音樂會無限播放
        self.sound_music2 = SoundLoader.load("audio/monster_watch.mp3")
        self.sound_music2.loop = True
        self.sound_music3 = SoundLoader.load("audio/meou.mp3")
        self.sound_music3.loop = True
        self.sound_restart = SoundLoader.load("audio/click_sound.wav")

        self.sound_begin.volume = .4
        self.sound_galaxy.volume = .8
        self.sound_gameover_impact.volume = .4
        self.sound_gameover_voice.volume = .2
        self.sound_gameover1_voice.volume = .6
        self.sound_music1.volume = .5
        self.sound_music2.volume = .5
        self.sound_music3.volume = .5
        self.sound_restart.volume = .4

    def reset_game(self):
        self.current_offset_y = 0
        self.current_offset_x = 0
        self.current_y_loop = 0
        self.time_txt = "TIME: 0 : 0"
        self.t = 0
        self.score_txt = "JUMP: 0"
        self.score = 0
        self.flag = 1
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinate()
        Clock.schedule_interval(self.change_speed, 30)

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    # 定義垂直線
    def init_vertical_line(self):
        for i in range(0, self.V_NB_LINES):
            self.vertical_lines.append(Line())

    # 定義及畫水平線
    def init_horizontal_line(self):
        with self.canvas:
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    # 定義及畫船(三角形)
    def init_ship(self):
        with self.canvas:
            self.ship = Triangle()

    # 取得船的點和像素
    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height

        self.ship_coordinates[0] = (center_x-ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y+ship_height)
        self.ship_coordinates[2] = (center_x+ship_half_width, base_y)
        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])
        self.ship.points = (x1, y1, x2, y2, x3, y3)

    # 確認撞擊狀況 (是->撞到 / 否->安全)
    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            # 不用管兩格以上的磚塊(因為磚塊只會在底下兩格) current_y_loop是畫面中的最後一條水平線
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    # 輸入地板磚塊的座標(以左下角作為該磚塊座標)，即可判斷那格是否有包含三角形的"任何"一點
    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    # 遊戲剛開始還不會變化，預設是往前面鋪地板 * 10
    def pre_fill_tiles_coordinates(self):
        # 10 tiles in a straight line
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))
        self.generate_tiles_coordinate()

    def generate_tiles_coordinate(self):
        last_x = 0
        last_y = 0
        # clean the coordinates that are out of the screen
        # ti_y < self.current_y_loop
        for i in range(len(self.tiles_coordinates)-1, -1, -1):  # not include -1 till 0
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]  # ####### cannot get it...#########
            last_y = last_coordinates[1] + 1
            last_x = last_coordinates[0]

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(1, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

    def get_line_x_from_index(self, index):
        offset = index - 0.5
        spacing = self.V_LINES_SPACING * self.width
        central_line_x = self.perspective_point_x
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing = self.H_LINES_SPACING * self.height
        line_y = index * spacing - self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            ti_x, ti_y = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
            xmax, ymax = self.get_tile_coordinates(ti_x+1, ti_y+1)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_line(self):
        # -1 0 1 2
        start_index = -int(self.V_NB_LINES/2) + 1
        end_index = start_index + self.V_NB_LINES
        for i in range(start_index, end_index):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def update_horizontal_line(self):
        # -1 0 1 2
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index + self.V_NB_LINES -1
        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = (x1, y1, x2, y2)

    def change_speed(self, dt):
        r = random.randint(0, 2)
        if r == 0:
            self.BPM = 100
        elif r == 1:
            self.BPM = 110
        else:
            self.BPM = 120

    def update(self, dt):
        time_factor = dt * 60
        self.update_vertical_line()
        self.update_horizontal_line()
        self.update_tiles()
        self.update_ship()

        if not self.state_game_over and self.state_game_has_started:
            speed_y = self.BPM / 3600 * 2 * self.H_LINES_SPACING * self.height
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y > spacing_y:  # repeat enough times in case starting prob
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = "JUMP: " + str(self.score)
                self.t = int(time.time()-self.start_time)
                minute = int(self.t/60)
                sec = self.t % 60
                self.time_txt = "TIME: " + str(minute) + " : " + str(sec)
                self.generate_tiles_coordinate()

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            if self.t < 60:  # 0-0:59
                self.menu_title = "GAME OVER\n\n  try again!"
                Clock.schedule_once(self.play_game_over_voice_sound, 1)
            elif self.t < 120:  # 1-1:59
                self.menu_title = "       good job\n\nYou can be better"
                Clock.schedule_once(self.play_game_over1_voice_sound, 1)
            elif self.t < 180:  # 2-2:59
                self.menu_title = "      bravo\n\nalmost there"
                Clock.schedule_once(self.play_game_over1_voice_sound, 1)
            else:  # 3-
                self.menu_title = "        excellent\n\nyou are cpr master"
                Clock.schedule_once(self.play_game_over1_voice_sound, 1)
            self.menu_button_title = "RESTART"
            self.menu_widget.opacity = 1
            print("Game Over")
            self.sound_music1.stop()
            self.sound_music2.stop()
            self.sound_music3.stop()
            self.sound_gameover_impact.play()

    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()

    def play_game_over1_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover1_voice.play()

    def on_menu_button_pressed(self):
        print("Button")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.reset_game()
        self.start_time = time.time()
        self.state_game_has_started = True
        self.state_game_over = False
        self.menu_widget.opacity = 0

    def on_menu_button_L_pressed(self):
        print("Button_L")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music2.play()
        self.reset_game()
        self.start_time = time.time()
        self.state_game_has_started = True
        self.state_game_over = False
        self.menu_widget.opacity = 0

    def on_menu_button_R_pressed(self):
        print("Button_R")
        if self.state_game_over:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music3.play()
        self.reset_game()
        self.start_time = time.time()
        self.state_game_has_started = True
        self.state_game_over = False
        self.menu_widget.opacity = 0


class KeepYourBrainSHARKApp(App):
    pass


KeepYourBrainSHARKApp().run()