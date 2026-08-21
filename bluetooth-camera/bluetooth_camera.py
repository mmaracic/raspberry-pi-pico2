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
camera = BLESensor(ble, name="Pico Camera")
while True:
    try:
        pin.toggle()
        camera.update_row(
            start_row=0,
            start_col=0,
            bytes_per_pixel=3,
            total_row_bytes=640 * 3,
            data=b"\x00" * 20,
            notify=True,
        )
        pin.toggle()
        sleep(5)
    except KeyboardInterrupt:
        print("Application interrupted by user.")
        break
pin.off()
print("Application finished.")
