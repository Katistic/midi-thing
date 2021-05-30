import logging


class MidiEvent:
    def __init__(self, delta_time, event, channel):
        self.event = event
        self.delta_time = delta_time

        self.is_meta = False
        self.param_count = 1

        self.channel = channel

        if channel is not None:
            self.channel += 1


class NoteOffEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 8, channel)
        self.param_count = 2

        self.note = data[0]
        self.velocity = data[1]


class NoteOnEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 9, channel)
        self.param_count = 2

        self.note = data[0]
        self.velocity = data[1]


class ControllerEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 9, channel)
        self.param_count = 2

        self.controller_type = data[0]
        self.value = data[1]


class ProgramChangeEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 12, channel)

        self.program_number = data[0]


class PitchBendEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 14, channel)
        self.param_count = 2

        self.value_lsb = data[0]
        self.value_msb = data[1]


class MetaEvent(MidiEvent):
    def __init__(self, delta_time, meta_type):
        super().__init__(delta_time, 255, None)
        self.meta_type = meta_type
        self.is_meta = True


class CopyrightNoticeEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 2)

        self.notice = data.decode("latin-1")


class TrackNameEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 3)

        self.name = data.decode("ascii")


class InstrumentNameEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 4)

        self.name = data.decode("ascii")


class EndOfTrackEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 47)


class SetTempoEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 81)

        self.ms_per_quater_note = int.from_bytes(data, "big")


class TimeSignatureEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 88)

        self.numer = data[0]
        self.denom = data[1]
        self.metro = data[2]
        self.ttnds = data[3]


class KeySignatureEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 89)

        self.key = data[0]
        self.scale = data[1]


def get_event(delta_time, event_type, data, meta_type=None, channel=None):
    print(delta_time)

    meta_events = {
        2: CopyrightNoticeEvent,
        3: TrackNameEvent,
        4: InstrumentNameEvent,
        47: EndOfTrackEvent,
        81: SetTempoEvent,
        88: TimeSignatureEvent,
        89: KeySignatureEvent,
    }

    midi_events = {
        8: NoteOffEvent,
        9: NoteOnEvent,
        11: ControllerEvent,
        12: ProgramChangeEvent,
        14: PitchBendEvent
    }

    if event_type == 255:
        if meta_type in meta_events:
            return meta_events[meta_type](delta_time, data)

    if event_type in midi_events:
        return midi_events[event_type](delta_time, data, channel)

    logging.critical("NOT FOUND EVENT: " + str(event_type) + " (event type) " + str(meta_type) + " (meta type)")
