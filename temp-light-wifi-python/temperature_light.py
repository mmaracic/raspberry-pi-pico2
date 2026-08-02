import json

import machine
import urequests
from machine import Pin
from utime import sleep

import custom_logging
from network_client import NetworkClient
from utils import get_env_variable, get_url_with_params, load_json_file

custom_logging.basicConfig(level=custom_logging.INFO)
logger = custom_logging.getLogger(__name__)

env = load_json_file("local_settings.json")
NETWORK_SSID = get_env_variable("NETWORK_SSID", env)
PASSWORD = get_env_variable("PASSWORD", env)
CONNECTION_RETRY_LIMIT = 20

REQUEST_URL = get_env_variable("REQUEST_URL", env)
AZURE_CODE = get_env_variable("AZURE_CODE", env)
CONTAINER_NAME = get_env_variable("CONTAINER_NAME", env)
TOPIC_NAME = get_env_variable("TOPIC_NAME", env)
LIMIT = get_env_variable("LIMIT", env)
SAMPLE_INTERVAL_SEC = get_env_variable("SAMPLE_INTERVAL_SEC", env)

led = Pin("LED", Pin.OUT)
adc_int_temp = machine.ADC(4)  # Connect to the internal temperature sensor
adc_temp = machine.ADC(0)  # Connect to channel 0 (GP26)
adc_light = machine.ADC(1)  # Connect to channel 1 (GP27)
conversion_factor = 3.3 / (65535)

logger.info("Starting application...")
led.toggle()
sleep(1)  # sleep 1sec
led.toggle()

try:
    network_client = NetworkClient(NETWORK_SSID, PASSWORD, CONNECTION_RETRY_LIMIT)
    while True:
        ip = network_client.connect()
        led.toggle()
        adc_int_temp_value = adc_int_temp.read_u16() * conversion_factor
        int_temp_c = 27 - (adc_int_temp_value - 0.706) / 0.001721
        adc_temp_value = adc_temp.read_u16() * conversion_factor
        adc_light_value = adc_light.read_u16() * conversion_factor
        logger.info(
            f"Internal Temperature: {adc_int_temp_value:.2f} V ({int_temp_c:.2f} °C), Temperature: {adc_temp_value:.2f} V, Light: {adc_light_value:.2f} V"
        )

        post_data = json.dumps(
            {
                "source": "pico-w",
                "text": "Connected to wifi",
                "ip": ip,
                "internal_temperature": f"{int_temp_c:.2f} degC",
                "internal_temperature_voltage": f"{adc_int_temp_value:.2f} V",
                "temperature_voltage": f"{adc_temp_value:.2f} V",
                "light_voltage": f"{adc_light_value:.2f} V",
            }
        )
        request_url = get_url_with_params(
            REQUEST_URL,
            {
                "container_name": CONTAINER_NAME,
                "topic_name": TOPIC_NAME,
                "limit": LIMIT,
            },
        )
        res = urequests.post(
            request_url,
            headers={
                "content-type": "application/json",
                "x-functions-key": AZURE_CODE,
            },
            data=post_data,
        )
        logger.info(res.json())
        res.close()
        led.toggle()
        sleep(SAMPLE_INTERVAL_SEC)  # sleep SAMPLE_INTERVAL_SEC sec
except KeyboardInterrupt:
    logger.info("Stopped by user.")
finally:
    network_client.disconnect()
    logger.info("Application stopped.")