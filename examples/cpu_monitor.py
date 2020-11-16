from midistuff.launchpad import mk2
import threading
import psutil
import math
import time

class LightArray:
    def __init__(self, controller):
        self.list = [ [0, 0] for x in range(0, 9) ]
        self.controller = controller

    def update(self, percent):
        print("{}%".format(percent))

        del self.list[0]
        colour = 21


        percent = math.ceil(percent / 100 * 9)
        if percent > 4:
            colour = 13

        if percent >= 8:
            colour = 5

        self.list.append([percent, colour])
        self.push()

    def push(self):
        # self.controller.reset_all_leds()
        empty_rows = [x for x in range(0, 9)]

        ccount = 0
        for column in self.list:
            ccount += 1

            for button in range(0, column[0] + 1):
                if button in empty_rows:
                    empty_rows.remove(button)

        ccount = 0
        for column in self.list:
            ccount += 1

            bcount = 0
            for button in range(1, column[0] + 1):
                if button == 9:
                    self.controller.set_led_colour(103 + ccount, column[1])
                    continue

                self.controller.set_led_colour(int("{}{}".format(button, ccount)), column[1])
                bcount += 1

            for button in range(bcount + 1, 11):
                if button not in empty_rows or ccount == 1:
                    if button == 10:
                        self.controller.set_led_colour(104 + ccount, 0)
                        continue

                    self.controller.set_led_colour(int("{}{}".format(button, ccount)), 0)

        for row in empty_rows:
            self.controller.set_row_colour(row, 0, True)

class Controller(mk2.LaunchpadMK2):
    def __init__(self):
        super().__init__()
        self.lightarray = LightArray(self)

        self.stop_thread = False
        self.listen_thread = threading.Thread(target=self.thread)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def on_key_down(self, key):
        print("KEY DOWN! " + str(key))

    def on_key_up(self, key):
        print("KEY UP! " + str(key))

    def thread(self):
        while True:
            self.lightarray.update(psutil.cpu_percent())
            time.sleep(1)

controller = Controller()
controller.open()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
