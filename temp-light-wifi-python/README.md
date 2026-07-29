# README

MicroPython project to load environemnt variables from a JSON file and connect to a Wi-Fi network using those variables, measure temperature and light levels using ADC, and send the data to a server using HTTP requests with Json payload. The project is designed to run on a Raspberry Pi Pico W microcontroller.


## Setup

For the project to work, you need to create a `local_settings.json` file in the root directory of the project with the following structure:

```json
{
    "NETWORK_SSID": "your_network_ssid",
    "PASSWORD": "your_network_password",
    "REQUEST_URL": "https://your-server-url.com/endpoint",
    "AZURE_CODE": "your_azure_function_key",
    "CONTAINER_NAME": "your_container_name",
    "TOPIC_NAME": "your_topic_name",
    "LIMIT": 1,
    "SAMPLE_INTERVAL_SEC": 60
}
```
All three files `network.py`, `utils.py`, and `local_settings.json` are required for the project to work and need to be uploaded to the Pico.

The `network.py` file contains the code to connect to the Wi-Fi network, the `utils.py` file contains utility functions to load the JSON file and get environment variables, and the `local_settings.json` file contains the network credentials. Make sure to replace `your_network_ssid` and `your_network_password` with your actual Wi-Fi network credentials.

When importing other source files it is not possible to use relative imports, so the import statements in `network.py` and `utils.py` should be modified to use absolute imports instead of relative imports. For example, instead of using `from .utils import load_json_file, get_env_variable`, you should use `from utils import load_json_file, get_env_variable`.

## Notes
Pico wireless and bluetooth documentation:  
https://pip-assets.raspberrypi.com/categories/686-raspberry-pi-pico-w/documents/RP-008257-DS-2-connecting-to-the-internet-with-pico-w.pdf

Urequests library is used to send HTTP requests to the server. You can find more information about the urequests library and its usage in the official documentation:  
https://makeblock-micropython-api.readthedocs.io/en/latest/public_library/Third-party-libraries/urequests.html

Added ADC data. ADC conversion is 12-bit but converted to 16-bit number. The adc.read_u16() method is used to read the ADC value from three ADC channels: the internal temperature sensor and the external temperature and light sensors. The method returns a 16-bit integer value that represents the voltage level of the sensor. You can find more information about the ADC class and its methods in the official documentation:
https://pip-assets.raspberrypi.com/categories/610-raspberry-pi-pico/documents/RP-008355-DS-1-raspberry-pi-pico-python-sdk.pdf
https://docs.micropython.org/en/latest/library/machine.ADC.html