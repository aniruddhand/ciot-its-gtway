import dbus
import dbus.service

import array
import sys

from gi.repository import GLib

from lib.gatt_svc import Service
from lib.gatt_chr import Characteristic
from lib.gatt_dsc import Descriptor
from lib.gatt_const  import * 

class VehicleStatusService(Service):
    VS_UUID = '0f7d0ee7-ab1f-47cf-93ed-9ef8038f8bec'
    
    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.VS_UUID, True)
        self.add_characteristic(VehicleStatusCharacteristic(bus, 0, self))


class VehicleStatusCharacteristic(Characteristic):
    VSC_UUID = '0f7d0ee8-ab1f-47cf-93ed-9ef8038f8bec'

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.VSC_UUID,
                ['notify'],
                service)
        self.add_descriptor(VehicleStatusCharacteristicUDDescriptor(bus, 0, self))
        self.notifying = False

    """
        Vehicle Status callback
    """
    def veh_status_update_cb(self):
        value = []
        veh_status = bytearray("38.23,100,191982.22332,98329832.2732789,N","utf-8")

        for byte in veh_status:
            value.append(dbus.Byte(byte))

        print('Updating value...')

        self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': value }, [])

        return self.notifying

    def _update_veh_status(self):
        print('Update Vehicle Status')

        if not self.notifying:
            return

        GLib.timeout_add(1000, self.veh_status_update_cb)

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True
        self._update_veh_status()

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False
        self._update_veh_status()


class VehicleStatusCharacteristicUDDescriptor(Descriptor):
    """
    Human readable descriptor for vehicle status characteristic
    """
    CUD_UUID = '2901'

    def __init__(self, bus, index, characteristic):
        self.value = array.array('B', b'Vehicle Status')
        self.value = self.value.tolist()
        Descriptor.__init__(
                self, bus, index,
                self.CUD_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return self.value


