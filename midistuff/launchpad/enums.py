class MK2Layout:
    Session = 0
    User1 = 1
    User2 = 2
    Ableton = 3
    Volume = 4
    Pan = 5

    @staticmethod
    def layout_name(self, t):
        layouts = ["Session", "User 1", "User 2", "Ableton", "Volume", "Pan"]
        if t < len(layouts) and t >= 0:
            return layouts[t]

        raise Errors.InvalidLayout("Layout does not exist!")

class Errors:
    class WrongLayout(Exception):
        pass

    class InvalidLayout(Exception):
        pass
