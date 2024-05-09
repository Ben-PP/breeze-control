import network
from machine import Pin
from time import sleep_ms
from mqtt import MQTTClient
from config import *
from breezer import Breezer

SW_VERSION = "0.0.1"
HW_VERSION = "0.1"

# These will be same across multiple devices
DEVICE_NAME = "Breezer-9000 alpha"
MANUFACTURER = "Karel Parkkola"
MODEL = "Breezer-9000"
AVAILABILITY_TOPIC = (
    f"homeassistant/availability/{IDENTIFIERS}"  # IDENTIFIERS is defined in config.py
)

LED = Pin("LED", Pin.OUT)


def get_discovery_topic(uid: str):
    return f"homeassistant/sensor/{uid}/config"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    network.hostname(UID)
    wlan.active(True)
    wlan.connect(SSID, WIFI_PASSWORD)
    try:
        i = 0
        while not wlan.isconnected():
            print("Connecting to Wi-Fi...")
            LED.on()
            sleep_ms(500)
            LED.off()
            sleep_ms(500)
            if i > 30:
                raise Exception("Wi-Fi connection timeout")
            i += 1
        return True
    except Exception as e:
        print("Error connecting to Wi-Fi")
        print(e)
        return False


def discover(client):
    device_data = {
        "name": DEVICE_NAME,
        "identifiers": IDENTIFIERS,
    }
    device_data_first = {
        "name": DEVICE_NAME,
        "identifiers": IDENTIFIERS,
        "model": MODEL,
        "manufacturer": MANUFACTURER,
        "sw_version": SW_VERSION,
        "hw_version": HW_VERSION,
    }
    # TODO Discover sensors and commands


def mqtt_connect():
    print(UID)
    print(MQTT_BROKER)
    print(MQTT_PORT)
    print(MQTT_USER)
    print(MQTT_PASSWORD)
    client = MQTTClient(
        UID,
        MQTT_BROKER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
    )
    # TODO Set last will maybe?
    client.set_last_will(AVAILABILITY_TOPIC, "offline", retain=True)
    sleep_ms(500)
    client.connect(clean_session=True)
    sleep_ms(500)
    discover(client)
    client.publish(AVAILABILITY_TOPIC, "online", retain=True)
    return client


def main():
    connect_wifi()
    if not connect_wifi():
        print("Wi-Fi connection failed")
        return
    sleep_ms(500)
    client = mqtt_connect()
    # TODO Add listener for commands
    breezer = Breezer(power_pin=27, mode_pin=26)
    breezer.power_btn()


main()
