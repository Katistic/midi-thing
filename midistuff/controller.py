import rtmidi
import time

from midistuff.error import *

class MidiMessage:
    def __init__(self, port, channel, event, key, state, data):
        self.port = port
        self.channel = channel
        self.dtime = time.time()

        self.event = event
        self.key = key
        self.state = state
        self.data = data

    def __repr__(self):
        return "MidiMessage(port={}, channel={}, event={}, key={}, state={})".format(
            self.port,
            self.channel,
            self.event,
            self.key,
            bool(self.state)
        )

class MidiController:
    def __init__(self):
        self.midiin = rtmidi.MidiIn()
        self.midiout = rtmidi.MidiOut()

    def find_in_port(self, name):
        ports = self.midiin.get_ports()
        port_index = 0
        found_device = False

        for (port_index, port) in enumerate(ports):
            if name in port:
                found_device = True
                break

        if found_device:
            return port_index

        raise InPortNotFound("Could not find Midi IN port '{}'".format(name))

    def find_out_port(self, name):
        ports = self.midiout.get_ports()
        port_index = 0
        found_device = False

        for (port_index, port) in enumerate(ports):
            if name in port:
                found_device = True
                break

        if found_device:
            return port_index

        raise OutPortNotFound("Could not find Midi OUT port '{}'".format(name))

    def open_in_port(self, name):
        self.midiin.open_port(self.find_in_port(name))

    def open_out_port(self, name):
        self.midiout.open_port(self.find_out_port(name))

    def open(self, name=None, port=None):
        if name is not None:
            self.open_in_port(name)
            self.open_out_port(name)
        elif port is not None:
            name = self.midiin.get_port_name(port)
            self.open(name)

        self.midiin.set_callback(self._callback)
        self.midiin.set_error_callback(self._error_callback)

    def close(self):
        self.midiin.close_port()
        self.midiout.close_port()

    def send_raw_message(self, data):
        self.midiout.send_message(data)

    def _callback(self, msg, data=None):
        msg = msg[0]

        print(msg)
        print(data)

    def _error_callback(self, error, message, data=None):
        print(error)
        print(message)
        print(data)

class VirtualMidiController(MidiController):
    def open_in_port(self, name):
        self.midiin.open_virtual_port(self.find_in_port(name))

    def open_out_port(self, name):
        self.midiout.open_virtual_port(self.find_out_port(name))
