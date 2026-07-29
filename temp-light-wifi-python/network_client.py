import logging
import time

import network

logger = logging.getLogger(__name__)


class NetworkClient:
    def __init__(
        self, network_ssid: str, password: str, connection_retry_limit: int = 20
    ):
        self.network_ssid = network_ssid
        self.password = password
        self.connection_retry_limit = connection_retry_limit

        logger.info("Starting the network...")

        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        networks = self.wlan.scan()
        logger.info("Available networks:")

        networkAvailable = False
        for net in networks:
            logger.info(net)
            if net[0].decode("utf-8") == network_ssid:
                networkAvailable = True
                break
        if not networkAvailable:
            raise Exception(f"Network {network_ssid} not available.")  # noqa: TRY002

    def connect(self) -> str:
        if not self.wlan.isconnected():
            logger.info(f"Connecting to network {self.network_ssid}...")
            self.wlan.connect(self.network_ssid, self.password)
            attempts = 0
            while attempts < self.connection_retry_limit:
                status = self.wlan.status()
                if status == network.STAT_GOT_IP:
                    break
                if status < 0:
                    logger.error(f"Connection error, status: {status}")
                    break
                logger.info(
                    f"Waiting to connect (attempt {attempts + 1}/{self.connection_retry_limit}), status: {status}..."
                )
                time.sleep(1)
                attempts += 1
            ip = self.wlan.ifconfig()[0]
            if (
                self.wlan.status() == network.STAT_GOT_IP
                and ip != "0.0.0.0"
                and self.wlan.isconnected()
            ):
                logger.info(f"Connected! IP: {ip}")
                return ip
            else:
                raise Exception(  # noqa: TRY002
                    f"Error: Could not obtain a valid IP address. Status: {self.wlan.status()}"
                )
        else:
            ip = self.wlan.ifconfig()[0]
            logger.info(f"Already connected. IP: {ip}")
            return ip

    def disconnect(self):
        self.wlan.disconnect()
        self.wlan.active(False)
        logger.info("Network stopped.")
