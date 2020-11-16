from midistuff.controller import MidiController

class LaunchpadBase(MidiController):
    def __init__(self):
        super().__init__()

        self.session = 1
        self.user1 = 2
        self.user2 = 3

        self.out_channel = 1
        self.name = "Launchpad"

        self.valid_keys = [key for key in range(11, 99)] + [key for key in range(104, 112)]

    def open(self):
        super().open(self.name)
        self.reset_all_leds()
