#! /usr/bin/python3

import can

from can import Listener
from gi.repository import GLib

class PeripheralDeviceListener(Listener):
    _vs_callback = None

    def __init__(self, vs_callback):
        _vs_callback = vs_callback

    def on_message_received(self, msg):
        return None

    def _get_temperature(self, msg):
        if msg.is_error_frame:
            print('Error frame received on CAN ifc at ' + msg.timestamp)

        return msg.data[0]

class VehicleCANModule:
    _msg_listener = None
    _bus = None
    _notifier = None

    def __init__(self, callback):
        self._msg_listener = self.PeripheralDeviceListener(callback)
        self._bus = can.interface.Bus(bustype='socketcan',
                                        channel='can0', bitrate=500000)
    
    def start_listening(self):
        if self._notifier:
            self._notifier.stop()

        self._notifier = can.Notifier(self._bus, [ self._msg_listener ], 2.0, GLib.MainLoop())
        
    def stop_listening(self):
        if self._notifier:
            self._notifier.stop()
