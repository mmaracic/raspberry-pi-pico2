# README

MicroPython project to send caemera data over Bluetooth Low Energy (BLE) using a Raspberry Pi Pico. The project includes a BLE sensor that can be used to advertise camera data to connected devices.

## Source files
- `bluetooth_camera.py`: Main application file that initializes the BLE sensor and updates its value
- `bluetooth_sensor.py`: Contains the `BLESensor` class that handles BLE advertising and connections
- `bluetooth_advertising.py`: Contains the `advertising_payload` function to create BLE advertising payloads

## Micropython libraries
Common and hardware specific:
https://docs.micropython.org/en/latest/library/index.html#

## Bluetooth
Micropython BLE implementation suggests using aioble package as high level micropython API for bluetooth.  
https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble

Micropython code exaamples, including BLE can be found here:
https://github.com/raspberrypi/pico-micropython-examples

There are more examples on micropython git - bonding example shows security pairing:
https://github.com/micropython/micropython/tree/master/examples/bluetooth

Example of pairing/bnonding:
https://github.com/micropython/micropython/issues/8837

Sample for push notifications (not Pico though):
https://hubble.com/community/guides/how-to-use-esp32-bluetooth-le-with-micropython-for-rapid-prototyping/

General info about bluetooth security:
https://www.allaboutcircuits.com/technical-articles/understanding-bluetooth-le-pairingstep-by-step/
https://www.allaboutcircuits.com/technical-articles/understanding-security-keys-in-bluetooth-low-energy/