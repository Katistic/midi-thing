import midistuff.midi_parser.events as events
import threading
import logging
import time


class InvalidMidiFile(Exception):
    pass


class MThd:
    chunk_id = "MThd"

    def __init__(self, data):
        if data[:4] != b'MThd':
            raise InvalidMidiFile("Invalid midi file!")

        self.chunk_size = int.from_bytes(data[4:8], "big")
        self.format_type = int.from_bytes(data[8:10], "big")
        self.track_count = int.from_bytes(data[10:12], "big")
        self.time_division = int.from_bytes(data[12:14], "big")

    def __repr__(self):
        return "MThd(chunk_size={}, format_type={}, track_count={}, time_division={})".format(
            self.chunk_size, self.format_type, self.track_count, self.time_division)


class MTrk:
    chunk_id = "MTrk"

    def __init__(self, header_data):
        if header_data[:4] != b'MTrk':
            raise InvalidMidiFile("Invalid midi file!")

        self.chunk_size = int.from_bytes(header_data[4:8], "big")
        self.events = []
        self.last_read_event = None
        self.last_index = -1

    def __repr__(self):
        return "MTrk(chunk_size={}, event_count={})".format(
            self.chunk_size, len(self.events))

    def _find_var_len_data(self, data, index):
        var_len_data = []

        for byte_index in range(0, len(data[index:])):
            bits = self._get_bits_from_byte(data[index+byte_index])
            cont_bit = bits.pop(0)
            var_len_data += bits

            if cont_bit == 0:
                break

        return self._correct_byte(var_len_data), byte_index+1

    def _get_bits_from_byte(self, byte):
        return [(byte >> i) & 1 for i in reversed(range(0, 8))]

    def _correct_byte(self, byte_list):
        byte = [0 for x in range(0, 8-(len(byte_list) % 8))] + byte_list
        return int("".join(map(lambda b: str(b), byte)), 2)

    def _load_data(self, data):
        loaded_data = 0
        delta_time_total = 0

        while loaded_data + 1 < self.chunk_size:
            # start_loaded_data = loaded_data
            # Meta event
            delta_time, data_loaded = self._find_var_len_data(data,
                                                              loaded_data)
            delta_time_total += delta_time
            loaded_data += data_loaded

            if data[loaded_data] == 255:
                event_type = 255
                meta_type = data[loaded_data+1]
                length, length_len = self._find_var_len_data(
                    data, loaded_data+2)
                event_data = data[
                    loaded_data+2+length_len:loaded_data+2+length_len+length]

                loaded_data += 2+length_len+length

                event = events.get_event(
                    delta_time, event_type, event_data, meta_type)

                if event is not None:
                    event.abs_delta_time = delta_time_total
                    self.events.append(event)
            else:
                bits = self._get_bits_from_byte(data[loaded_data])
                event_type = self._correct_byte(bits[:4])

                channel = self._correct_byte(bits[4:])
                param1 = data[loaded_data+1]
                param2 = data[loaded_data+2]

                loaded_data += 2
                event = events.get_event(
                    delta_time, event_type, [param1, param2], channel=channel)

                if event is None:
                    logging.debug("Assuming running status")

                    loaded_data -= 2

                    param1 = data[loaded_data]
                    param2 = data[loaded_data+1]

                    event = self.events[-1]
                    event = events.get_event(
                        event.delta_time, event.event, [param1, param2],
                        channel=event.channel)

                    loaded_data += 1

                self.events.append(event)
                event.abs_delta_time = delta_time_total

                if event.param_count == 2:
                    loaded_data += 1

            logging.debug("Loaded event: " + str(event))
            # print(data[start_loaded_data:loaded_data])

    def get_next_events(self):
        last_event_index = self.last_index
        if last_event_index + 1 >= len(self.events):
            return None

        events = [self.events[last_event_index + 1]]

        for event_index in range(last_event_index + 1, len(self.events)):
            if self.events[event_index].delta_time == 0:
                events.append(self.events[event_index])
            else:
                break

        self.last_read_event = events[-1]
        self.last_index = event_index - 1

        if len(events) == 1:
            self.last_index += 1

        return events


class MidiFile:
    def __init__(self, file):
        self.file = file
        self._file = None
        self.header = None

        self.tempo = 120
        self.time_sig = None
        self.key_sig = None
        self.copyright_notice = None

        self.chunks = []

        self._open()

    def _open(self):
        with open(self.file, "rb", buffering=0) as file:

            # Read header chunk
            self.header = MThd(file.read(14))

            for chunk_index in range(0, self.header.track_count):
                self.chunks.append(self._read_next_chunk(file))

        logging.info(f'LOADED {len(self.chunks)} CHUNKS AND {sum([len(chunk.events) for chunk in self.chunks])} EVENTS')

    def _read_next_chunk(self, file):
        chunk = MTrk(file.read(8))
        chunk._load_data(file.read(chunk.chunk_size))

        return chunk

    def get_next_events(self):
        if self.header.format_type == 1:
            events = []
            for chunk in self.chunks:
                events.append(chunk.get_next_events())

            return events
        elif self.header.format_type == 2:
            for chunk in self.chunks:
                if type(chunk.last_read_event) is not events.EndOfTrackEvent:
                    return chunk.get_next_events()

    def get_delta_time_in_seconds(self, delta_time):
        return (60 * delta_time) / (self.tempo * self.header.time_division)

    def _play_events(self, levents, controller):
        for event in levents:
            if type(event) in [events.NoteOnEvent, events.NoteOffEvent]:
                controller.send_message(
                    event.note, event.velocity, event.channel)
            elif type(event) is events.SetTempoEvent:
                self.tempo = event.tempo

    def _play(self, chunk, controller):
        last_events = []
        last_clock = 0

        while last_events is not None:
            if last_events == []:
                last_events = chunk.get_next_events()
                last_clock = time.time()
                continue

            try:
                self._busy_wait(
                    self.get_delta_time_in_seconds(last_events[0].delta_time) - (time.time() - last_clock))
            except Exception:
                pass

            last_clock = time.time()

            thread = threading.Thread(
                target=self._play_events, args=[last_events, controller])
            thread.daemon = True
            thread.start()

            last_events = chunk.get_next_events()
            if last_events[-1].__class__ == events.EndOfTrackEvent:
                return

    def play(self, controller):
        self.reset()

        if self.header.format_type == 1:
            threads = []

            for chunk in self.chunks:
                thread = threading.Thread(
                    target=self._play, args=[chunk, controller])
                thread.daemon = True
                threads.append(thread)

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

    def reset(self):
        for chunk in self.chunks:
            chunk.last_index = -1
            chunk.last_read_event = None

    def _busy_wait(self, t):

        if t < 0.01:
            target = time.time() + t
            while time.time() < target:
                pass
        else:
            time.sleep(t)


def load(file_name):
    return MidiFile(file_name)
