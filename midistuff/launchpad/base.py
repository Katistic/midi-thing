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
        self.midiin.ignore_types(sysex=False)
        self.reset_all_leds()

class LaunchpadKey:
    def __init__(self, msg):
        self.channel = msg[0][0]
        self.key = msg[0][1]
        self.state = msg[0][2]

        self.time = msg[1]

    def __repr__(self):
        return "LaunchpadKey(channel={}, key={}, state={}, time={})".format(
            self.channel,
            self.key,
            self.state,
            self.time
        )

    def __str__(self):
        return repr(self)
