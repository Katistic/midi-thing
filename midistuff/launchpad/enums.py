class MK2Layout:
    Session = 0
    User1 = 1
    User2 = 2
    Ableton = 3
    Volume = 4
    Pan = 5

class Errors:
    class WrongLayout(Exception):
        pass

    class InvalidLayout(Exception):
        pass
