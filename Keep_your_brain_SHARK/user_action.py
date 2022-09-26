from kivy.uix.relativelayout import RelativeLayout


def keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard.unbind(on_key_up=self._on_keyboard_up)
    self._keyboard = None


def on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if not self.state_game_over and self.state_game_has_started:
        self.score += 1
        if keycode[0] == 32:
            if self.flag == 0:
                self.current_offset_x -= self.V_LINES_SPACING * self.width
            elif self.flag == 1:
                self.current_offset_x += self.V_LINES_SPACING * self.width
    return True


def on_keyboard_up(self, keyboard, keycode):
    # self.current_speed_x = 0
    if self.flag == 0:
        self.flag = 1
    elif self.flag == 1:
        self.flag = 0
    return True


def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_has_started:
        self.score += 1
        if self.flag == 0:
            self.current_offset_x -= self.V_LINES_SPACING * self.width
        elif self.flag == 1:
            self.current_offset_x += self.V_LINES_SPACING * self.width
    return super(RelativeLayout, self).on_touch_down(touch)


def on_touch_up(self, touch):
    if not self.state_game_over and self.state_game_has_started:
        # print("UP")
        if self.flag == 0:
            self.flag = 1
        elif self.flag == 1:
            self.flag = 0
