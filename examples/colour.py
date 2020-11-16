import time
from midistuff.launchpad import mk2, enums

mk2 = mk2.LaunchpadMK2()

@mk2.event
def on_key_up(key):
    print("KEY UP! " + str(key))

@mk2.event
def on_key_down(key):
    print("KEY DOWN! " + str(key))

mk2.open()

mk2.set_all_led_colour(3)
mk2.set_led_colour(104, 21)
mk2.set_row_colour(8, 5)
mk2.set_column_colour(2, 67)

mk2.set_led_colour_pulsing(56, 25)
mk2.set_led_colour_flashing(89, 127)


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
