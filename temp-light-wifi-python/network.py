import time

from machine import Pin
from utime import sleep

import network
from utils import get_env_variable, load_json_file

env = load_json_file("local_settings.json")
NETWORK_SSID = get_env_variable("NETWORK_SSID", env)
PASSWORD = get_env_variable("PASSWORD", env)

print("Starting application...")
led = Pin("LED", Pin.OUT)
led.toggle()
sleep(1)  # sleep 1sec
led.toggle()

print("Starting the network...")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
networks = wlan.scan()
print("Available networks:")

networkAvailable = False
for net in networks:
    print(net)
    if net[0].decode("utf-8") == NETWORK_SSID:
        networkAvailable = True
        break


if networkAvailable:
    wlan.connect(NETWORK_SSID, PASSWORD)
    attempts = 0
    while attempts < 15:
        status = wlan.status()
        if status == network.STAT_GOT_IP:
            break
        if status < 0:
            print(f"Connection error, status: {status}")
            break
        print(f"Waiting to connect (attempt {attempts + 1}/15), status: {status}...")
        time.sleep(1)
        attempts += 1
    ip = wlan.ifconfig()[0]
    if wlan.status() == network.STAT_GOT_IP and ip != "0.0.0.0" and wlan.isconnected():
        print(f"Connected! IP: {ip}")
    else:
        print(f"Error: Could not obtain a valid IP address. Status: {wlan.status()}")
else:
    print("Network not available.")
wlan.active(False)
print("Network stopped.")
