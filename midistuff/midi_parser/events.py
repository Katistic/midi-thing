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


class NoteAftertouchEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 10, channel)
        self.param_count = 2

        self.note = data[0]
        self.velocity = data[1]


class ControllerEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 11, channel)
        self.param_count = 2

        self.controller_type = data[0]
        self.value = data[1]


class ProgramChangeEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 12, channel)

        self.program_number = data[0]


class ChannelAftertouchEvent(MidiEvent):
    def __init__(self, delta_time, data, channel):
        super().__init__(delta_time, 13, channel)

        self.velocity = data[0]


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


class SequenceNumberEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 0)

        self.number_msb = data[0]
        self.number_lsb = data[1]


class TextEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 1)

        self.text = data.decode("ascii")


class CopyrightNoticeEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 2)

        self.notice = data.decode("latin-1")

    def __repr__(self):
        return "Copyright: " + self.notice


class TrackNameEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 3)

        self.name = data.decode("ascii")

    def __repr__(self):
        return f"TrackNameEvent(name={self.name})"


class InstrumentNameEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 4)

        self.name = data.decode("ascii")

    def __repr__(self):
        return f"InstrumentNameEvent(name={self.name})"


class LyricEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 5)

        self.lyric = data.decode("ascii")


class MarkerEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 6)

        self.marker = data.decode("ascii")


class CuePointEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 7)

        self.cue = data.decode("ascii")


class MidiChannelPrefixEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 32)

        self.channel = 1 + data[0]


class EndOfTrackEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 47)

    def __repr__(self):
        return "EndOfTrack()"


class SetTempoEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 81)

        self.tempo = 60000000 / int.from_bytes(data, "big")

    def __repr__(self):
        return f"SetTempoEvent(temp={self.tempo})"


class SMPTEOffsetEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 84)

        self.hour = data[0]
        self.minute = data[1]
        self.secord = data[2]
        self.frame = data[3]
        self.sub_frame = data[4]

        # TODO: Correctly define these


class TimeSignatureEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 88)

        self.numerator = data[0]
        self.denominator = 2**data[1]
        self.metro = data[2]
        self.ttnds = data[3]

    def __repr__(self):
        return f"TimeSignatureEvent(signature={self.numerator}/{self.denominator})"


class KeySignatureEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 89)

        self.key = data[0]
        self.scale = data[1]

    def __repr__(self):
        return f"KeySignatureEvent(key={self.key}, scale={self.scale})"


class SequencerSpecificEvent(MetaEvent):
    def __init__(self, delta_time, data):
        super().__init__(delta_time, 127)

        if data[0] == 0:
            self.manufacture_id = int.from_bytes(data[:len(data)-3])
            self.data = data[3:]
        else:
            self.manufacture_id = data[0]
            self.data = data[1:]


def get_event(delta_time, event_type, data, meta_type=None, channel=None):
    meta_events = {
        0: SequenceNumberEvent,
        1: TextEvent,
        2: CopyrightNoticeEvent,
        3: TrackNameEvent,
        4: InstrumentNameEvent,
        5: LyricEvent,
        6: MarkerEvent,
        7: CuePointEvent,
        32: MidiChannelPrefixEvent,
        47: EndOfTrackEvent,
        81: SetTempoEvent,
        84: SMPTEOffsetEvent,
        88: TimeSignatureEvent,
        89: KeySignatureEvent,
        127: SequencerSpecificEvent
    }

    midi_events = {
        8: NoteOffEvent,
        9: NoteOnEvent,
        10: NoteAftertouchEvent,
        11: ControllerEvent,
        12: ProgramChangeEvent,
        13: ChannelAftertouchEvent,
        14: PitchBendEvent
    }

    if event_type == 255:
        if meta_type in meta_events:
            return meta_events[meta_type](delta_time, data)

    if event_type in midi_events:
        return midi_events[event_type](delta_time, data, channel)

    logging.critical("NOT FOUND EVENT: " + str(event_type) + " (event type) " + str(meta_type) + " (meta type)")
