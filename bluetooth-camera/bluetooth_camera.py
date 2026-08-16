from machine import Pin
from utime import sleep
import bluetooth
from bluetooth_sensor import BLESensor
from machine import Pin

pin = Pin("LED", Pin.OUT)

print("Application starting...")
pin.toggle()
sleep(1) # sleep 1sec
pin.toggle()

ble = bluetooth.BLE()
sensor = BLESensor(ble, name="Pico Camera Sensor")
while True:
    try:
        pin.toggle()
        sensor.update_value(value="Hello from Pico Camera!")
        pin.toggle()
        sleep(5)
    except KeyboardInterrupt:
        print("Application interrupted by user.")
        break
pin.off()
print("Application finished.")
