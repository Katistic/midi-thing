from midistuff.controller import MidiController

class LaunchpadBase(MidiController):
    def __init__(self):
        super().__init__()

        self.session = 1
        self.user1 = 2
        self.user2 = 3

        self.name = "Launchpad"

    def open(self):
        super().open(self.name)
        self.reset_all_leds()
