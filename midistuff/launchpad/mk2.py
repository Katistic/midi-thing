from midistuff.launchpad import enums, base

import time
import math

class LaunchpadMK2(base.LaunchpadBase):
    def __init__(self):
        super().__init__()

        self.user1 = 8
        self.user2 = 14

        self.name = "Launchpad MK2"
        self.layout = enums.MK2Layout.Session

        self.valid_keys = [key for key in range(11, 99)] + [key for key in range(104, 112)]

    def open(self):
        super().open()
        self.set_layout(enums.MK2Layout.Session)

    def send_message(self, key, colour, channel=None):
        if channel is None:
            channel = self.session

            if self.layout == enums.MK2Layout.User1:
                channel = self.user1
            elif self.layout == enums.MK2Layout.User2:
                channel = self.user2

        self.send_raw_message([143 + channel, key, colour])

    def send_sysex_message(self, mode, *data):
        super().send_raw_message([240, 0, 32, 41, 2, 24] + [mode] + list(data) + [247])

    # Helpers

    def number_to_xy(self, number):
        return (0, 0)

    def xy_to_number(self, x, y, force_session=False):
        return 104

    # Commands

    def set_layout(self, layout):
        enums.MK2Layout.layout_name(layout)
        self.send_sysex_message(34, layout)

    def get_device(self, id):
        self.send_raw_message([240, 126, id, 6, 1, 247])

    def get_version(self):
        self.send_raw_message([240, 0, 32, 41, 0, 112, 247])

    def boot_bootloader(self):
        self.send_raw_message([240, 0, 32, 41, 0, 113, 0, 105, 247])

    ## Colour

    def set_led_colour(self, key, colour):
        if type(key) == tuple or type(key) == list:
            key = self.xy_to_number(key[0], key[1], True)

        self.send_sysex_message(10, key, colour)

    def set_led_colour_flashing(self, key, colour):
        if type(key) == tuple or type(key) == list:
            key = self.xy_to_number(key[0], key[1], True)

        self.send_sysex_message(35, 0, key, colour)

    def set_led_colour_pulsing(self, key, colour):
        if type(key) == tuple or type(key) == list:
            key = self.xy_to_number(key[0], key[1], True)

        self.send_sysex_message(40, 0, key, colour)

    def set_column_colour(self, column, colour):
        self.send_sysex_message(12, column, colour)

    def set_row_colour(self, row, colour, raw_row_order=False):
        self.send_sysex_message(13, row if raw_row_order else 8 - row, colour)

    def set_all_led_colour(self, colour):
        self.send_sysex_message(14, colour)

    def initialise_fader(self, number, colour, value):
        if self.layout is not enums.MK2Layout.Volume and \
            self.layout is not enums.MK2Layout.Pan:

            raise enums.Errors.WrongLayout(
                "Layout must be either 'Volume' or 'Pan' to use faders! Current layout: {}".format(
                    enums.MK2Layout.layout_name(self.layout)
                )
            )

        self.send_sysex_message(43, number, 4 - self.layout, colour, value)

    ## RGB

    def set_led_rgb(self, key, red, green, blue):
        if type(key) == tuple or type(key) == list:
            key = self.xy_to_number(key[0], key[1], True)

        self.send_sysex_message(11, key, red, green, blue)

    def set_column_rgb(self, column, red, green, blue):
        start = 11 + column
        top = 104 + column

        for key in range(start, start + 10 * 9, 10):
            self.set_led_rgb(key, red, green, blue)

        if column != 8:
            self.set_led_rgb(top, red, green, blue)

    def set_row_rgb(self, row, red, green, blue, raw_row_order=False):
        start = 104

        if row != 0:
            start = 11 + 10 * (row if raw_row_order else 8 - row)

        for key in range(start, start + 9):
            self.set_led_rgb(key, red, green, blue)

    def set_all_led_rgb(self, red, green, blue):
        for key in self.valid_keys:
            self.set_led_rgb(key, red, green, blue)

    # Resets

    def reset_all_leds(self):
        self.set_all_led_colour(0)

    # Callback

    def event(self, func):
        if func.__name__ == "on_key_down":
            self.on_key_down = func
            return func
        elif func.__name__ == "on_key_up":
            self.on_key_up = func
            return func

        raise TypeError("Event function must be either 'on_key_down' or 'on_key_up'!")

    def _callback(self, msg, data=None):
        key = MK2Key(msg, self.layout)

        if key.state == 127:
            self.on_key_down(key)
        elif key.state == 0:
            self.on_key_up(key)

    def on_key_down(self, key):
        pass

    def on_key_up(self, key):
        pass

class MK2Key(base.LaunchpadKey):
    def __init__(self, msg, layout):
        super().__init__(msg)

        self.name = self.get_name(layout)

    def __repr__(self):
        return "MK2Key(channel={}, key={}, state={}, time={}, name={})".format(
            self.channel,
            self.key,
            self.state,
            self.time,
            self.name
        )

    def get_name(self, layout):
        top = ["Up", "Down", "Left", "Right", "Session", "User 1", "User 2", "Mixer"]
        right = ["Record Arm", "Solo", "Mute", "Stop", "Send B", "Send A", "Pan", "Volume"]

        # TODO: Key notes instead of 'Generic Key'
        # TODO: More descriptive name than 'Not a Key!'

        if layout == enums.MK2Layout.Session:
            if self.channel == 176:
                return top[self.key - 104]
            elif self.channel == 144:
                if str(self.key).endswith("9"):
                    return right[int(str(self.key)[0]) - 1]
                return "Generic Key"
            return "Not a Key!"
        if layout == enums.MK2Layout.User1:
            if self.channel == 181:
                return top[self.key - 104]
            elif self.channel == 149:
                if self.key >= 100:
                    return right[self.key - 100]
                return "Generic Key"
            return "Not a Key!"
        elif layout == enums.MK2Layout.User2:
            if self.channel == 189:
                return top[self.key - 104]
            elif self.channel == 157:
                if str(self.key).endswith("9"):
                    return right[int(str(self.key)[0]) - 1]
                return "Generic Key"
            return "Not a Key!"
