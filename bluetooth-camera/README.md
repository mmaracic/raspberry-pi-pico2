# README

MicroPython project to send caemera data over Bluetooth Low Energy (BLE) using a Raspberry Pi Pico. The project includes a BLE sensor that can be used to advertise camera data to connected devices.

## Source files
- `bluetooth_camera.py`: Main application file that initializes the BLE sensor and updates its value
- `bluetooth_sensor.py`: Contains the `BLESensor` class that handles BLE advertising and connections
- `bluetooth_advertising.py`: Contains the `advertising_payload` function to create BLE advertising payloads

## Notes
Micropython BLE implementation suggests using aioble package as high level micropython API for bluetooth.
https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble
