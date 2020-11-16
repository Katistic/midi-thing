import time
from midistuff.launchpad import mk2, enums

mk2 = mk2.LaunchpadMK2()
mk2.open()

mk2.set_layout(enums.MK2Layout.User2)

## Grouped RGB commands are much slower than grouped colour commands

mk2.set_all_led_rgb(63, 63, 63)
mk2.set_led_rgb(104, 0, 63, 0)
mk2.set_led_colour_pulsing(56, 25)
mk2.set_row_rgb(8, 63, 32, 16)
mk2.set_column_rgb(2, 36, 62, 21)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
