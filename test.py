import time
from midistuff.launchpad_controller import *

mk2 = LaunchpadMK2()
mk2.open()

mk2.set_layout(MK2Layout.User1)
mk2.set_bpm(100)

## Grouped RGB commands are much slower than grouped colour commands

mk2.set_all_led_rgb(63, 63, 63)
mk2.set_led_rgb(104, 0, 63, 0)
mk2.set_led_colour_pulsing(56, 25)
mk2.set_row_rgb(8, 63, 32, 16)
mk2.set_column_rgb(2, 36, 62, 21)

mk2.get_version()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
