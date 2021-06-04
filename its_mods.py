import dbus
import dbus.service

import array
import sys

from gi.repository import GLib

from lib.gatt_svc import Service
from lib.gatt_chr import Characteristic
from lib.gatt_dsc import Descriptor
from lib.gatt_const  import * 

from its_can_mod import VehicleCANModule 

VEH_ID = 'fa438cb3-b805-4050-844a-413fa01335c9'

class VehicleStatusService(Service):
    VS_UUID = '0f7d0ee7-ab1f-47cf-93ed-9ef8038f8bec'
    
    _veh_status_chr = None

    def __init__(self, bus, index):
        Service.__init__(self, bus, index, self.VS_UUID, True)
      
        self._veh_status_chr = VehicleStatusCharacteristic(bus, 0, self)
        self.add_characteristic(self._veh_status_chr)

    def listen_to_updates(self):
        self._veh_status_chr.hook_to_can()

    def stop_listening_to_updates(self):
        self._veh_status_chr.unhook_from_can()


class VehicleStatusCharacteristic(Characteristic):
    VSC_UUID = '0f7d0ee8-ab1f-47cf-93ed-9ef8038f8bec'

    _veh_can_mod = None

    def __init__(self, bus, index, service):
        Characteristic.__init__(
                self, bus, index,
                self.VSC_UUID,
                ['notify'],
                service)
        self.add_descriptor(VehicleStatusCharacteristicUDDescriptor(bus, 0, self))
        self.notifying = False
        self._veh_can_mod = VehicleCANModule()

    def hook_to_can(self):
        self._veh_can_mod.start_listening(self.update_cb)

    def unhook_from_can(self):
        self._ven_can_mod.stop_listening()

    """
    Vehicle Status callback called from itc_can_mod.py
    """
    def update_cb(self, data):
        jsonData = '{ "vehicleID": "$id", "temperature": $temperature }'
        rawValue = []

        for i in range(len(data)):
            # We only have temperature data
            if i > 0:
                break
            
            if i == 0:
                jsonData = jsonData.replace("$temperature", str(data[i]))

        jsonData = jsonData.replace("$id", VEH_ID)

        print('BLE notification: ' + jsonData)

        for byte in bytearray(str(jsonData), 'utf-8'):
            rawValue.append(dbus.Byte(byte))

        self.PropertiesChanged(GATT_CHRC_IFACE, { 'Value': rawValue }, [])
        return self.notifying

    def StartNotify(self):
        if self.notifying:
            print('Already notifying, nothing to do')
            return

        self.notifying = True

    def StopNotify(self):
        if not self.notifying:
            print('Not notifying, nothing to do')
            return

        self.notifying = False


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


