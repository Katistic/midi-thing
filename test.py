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

## Grouped RGB commands are much slower than grouped colour commands

mk2.set_all_led_rgb(63, 63, 63)
mk2.set_led_rgb(104, 0, 63, 0)
mk2.set_led_colour_pulsing(56, 25)
mk2.set_row_rgb(8, 63, 0, 0)
mk2.set_column_rgb(2, 0, 0, 63)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
