#! /usr/bin/python3

import can

from can import Listener
from gi.repository import GLib

class PeripheralDeviceListener(Listener):
    _callback = None

    def __init__(self, vs_callback):
        self._callback = vs_callback

    def on_message_received(self, msg):
        if msg is None or self._callback is None:
            return
    
        if self._check_msg(msg) is False:
            return

        self._callback(msg.data)

    def _check_msg(self, msg):
        if msg.is_error_frame:
            print('Error frame received on CAN ifc at ' + repr(msg.timestamp))
            return False

        return True

class VehicleCANModule:
    _msg_listener = None
    _bus = None
    _notifier = None
    _listening = False
    _callback = None

    def __init__(self):
        self._msg_listener = PeripheralDeviceListener(self.on_msg)
        self._bus = can.interface.Bus(bustype='socketcan',
                                        channel='can0', bitrate=500000)

        print('Initialized CAN interface, ready to receive messages')
    
    def on_msg(self, temperature):
        if not self._listening:
            return

        if not self._callback:
            return

        self._callback(temperature)

    def start_listening(self, callback):
        if self._notifier:
            self._notifier.stop()

        self._listening = True
        self._callback = callback

        """
        Starts listening and waits for 2 secs. If message is received
        within this time frame then listener would be notified with the
        message received
        """
        print('Creating CAN message listener')
        self._notifier = can.Notifier(self._bus, [ self._msg_listener ], 2.0, None)
    
    def stop_listening(self):
        if self._notifier:
            self._notifier.stop()
            self._callback = None

        self._listening = False
