import json
from sys import print_exception

import bluetooth
import struct
import binascii
import ubinascii
from bluetooth_advertize import advertising_payload

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_IRQ_ENCRYPTION_UPDATE = const(28)
_IRQ_PASSKEY_ACTION = const(31)

_IRQ_GET_SECRET = const(29)
_IRQ_SET_SECRET = const(30)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

_FLAG_READ_ENCRYPTED = const(0x0200)

_IO_CAPABILITY_DISPLAY_ONLY = const(0)
_IO_CAPABILITY_DISPLAY_YESNO = const(1)
_IO_CAPABILITY_KEYBOARD_ONLY = const(2)
_IO_CAPABILITY_NO_INPUT_OUTPUT = const(3)
_IO_CAPABILITY_KEYBOARD_DISPLAY = const(4)

_PASSKEY_ACTION_INPUT = const(2)
_PASSKEY_ACTION_DISP = const(3)
_PASSKEY_ACTION_NUMCMP = const(4)

# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)

# org.bluetooth.characteristic.temperature
_TEMP_CHAR = (
    bluetooth.UUID(0x2A6E),
    _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE, # | _FLAG_READ_ENCRYPTED, Unsupported for now on Pico
)
_ENV_SENSE_SERVICE = (
    _ENV_SENSE_UUID,
    (_TEMP_CHAR,),
)

# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)


class BLESensor:
    def __init__(self, ble: bluetooth.BLE, name=""):
        self._ble = ble
        self._ble.active(True)
        self._load_secrets()
# Below are unsupported for now on Pico
#        self._ble.config(bond=True)
#        self._ble.config(le_secure=True)
#        self._ble.config(mitm=True)
#        self._ble.config(io=_IO_CAPABILITY_NO_INPUT_OUTPUT)
        self._ble.irq(self._irq)
        ((self._handle,),) = self._ble.gatts_register_services((_ENV_SENSE_SERVICE,))
        self._connections = set()
        if len(name) == 0:
            name = 'Pico %s' % ubinascii.hexlify(self._ble.config('mac')[1],':').decode().upper()
        print('Sensor name %s' % name)
        self._payload = advertising_payload(
            name=name, services=[_ENV_SENSE_UUID]
        )
        self._advertise()

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            self._save_secrets()
            # Start advertising again to allow a new connection.
            self._advertise()
        elif event == _IRQ_ENCRYPTION_UPDATE:
            conn_handle, encrypted, authenticated, bonded, key_size = data
            print("encryption update", conn_handle, encrypted, authenticated, bonded, key_size)
        elif event == _IRQ_PASSKEY_ACTION:
            conn_handle, action, passkey = data
            print("passkey action", conn_handle, action, passkey)
            if action == _PASSKEY_ACTION_NUMCMP:
                accept = int(input("accept? "))
                self._ble.gap_passkey(conn_handle, action, accept)
            elif action == _PASSKEY_ACTION_DISP:
                print("displaying 123456")
                self._ble.gap_passkey(conn_handle, action, 123456)
            elif action == _PASSKEY_ACTION_INPUT:
                print("prompting for passkey")
                passkey = int(input("passkey? "))
                self._ble.gap_passkey(conn_handle, action, passkey)
            else:
                print("unknown action")
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data
        elif event == _IRQ_SET_SECRET:
            sec_type, key, value = data
            key = sec_type, bytes(key)
            value = bytes(value) if value else None
            print("set secret:", key, value)
            if value is None:
                if key in self._secrets:
                    del self._secrets[key]
                    return True
                else:
                    return False
            else:
                self._secrets[key] = value
            return True
        elif event == _IRQ_GET_SECRET:
            sec_type, index, key = data
            print("get secret:", sec_type, index, bytes(key) if key else None)
            if key is None:
                i = 0
                for (t, _key), value in self._secrets.items():
                    if t == sec_type:
                        if i == index:
                            return value
                        i += 1
                return None
            else:
                key = sec_type, bytes(key)
                return self._secrets.get(key, None)

    def _load_secrets(self):
        self._secrets = {}
        try:
            with open("secrets.json", "r") as f:
                entries = json.load(f)
                for sec_type, key, value in entries:
                    self._secrets[sec_type, binascii.a2b_base64(key)] = binascii.a2b_base64(value)
        except:
            print("no secrets available")

    def _save_secrets(self):
        try:
            with open("secrets.json", "w") as f:
                json_secrets = [
                    (sec_type, binascii.b2a_base64(key), binascii.b2a_base64(value))
                    for (sec_type, key), value in self._secrets.items()
                ]
                json.dump(json_secrets, f)
        except Exception as e:
            print("failed to save secrets")
            print_exception(e)
            pass

    def update_value(self, notify=False, indicate=False, value: str|None=None):
        # Write the local value, ready for a central to read.
        print("Advertising value: %s" % value);
        self._ble.gatts_write(self._handle, struct.pack("<s", value))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, self._handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, self._handle)
