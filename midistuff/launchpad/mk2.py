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

    def set_row_colour(self, row, colour):
        self.send_sysex_message(13, 8 - row, colour)

    def set_all_led_colour(self, colour):
        self.send_sysex_message(14, colour)

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

    def set_row_rgb(self, row, red, green, blue):
        start = 104

        if row != 0:
            start = 11 + 10 * (8 - row)

        for key in range(start, start + 9):
            self.set_led_rgb(key, red, green, blue)

    def set_all_led_rgb(self, red, green, blue):
        for key in self.valid_keys:
            self.set_led_rgb(key, red, green, blue)

    # Resets

    def reset_all_leds(self):
        self.set_all_led_colour(0)

    # Callback

    def _callback(self, msg, data=None):
        msg = msg[0]
