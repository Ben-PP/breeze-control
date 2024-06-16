import network
from machine import Pin
from time import sleep_ms
from json import dumps
from mqtt import MQTTClient
from config import *
from breezer import Breezer

SW_VERSION = "1.2.0"
HW_VERSION = "1.0"

# These will be same across multiple devices
DEVICE_NAME = "Breezer-9000"
MANUFACTURER = "Karel Parkkola"
MODEL = "Breezer-9000"
AVAILABILITY_TOPIC = (
    f"homeassistant/availability/{IDENTIFIERS}"  # IDENTIFIERS is defined in config.py
)

MODE_ID = f"{UID}_mode_select"
MODE_STATE = f"state/{MODE_ID}"
MODE_COMMAND = f"command/{MODE_ID}"

POWER_PIN = Pin(27, Pin.OUT)
MODE_PIN = Pin(26, Pin.OUT)
LED = Pin("LED", Pin.OUT)
PING_INTERVAL = 60  # 1 minute


def log(msg, level: str = "info"):
    if DEBUG:
        with open("sys.log", "a+") as file:
            if level == "info":
                print(f"[INFO]: {msg}")
                file.write(f"[INFO]: {msg}\n")
            elif level == "warning":
                print(f"[WARNING]: {msg}")
                file.write(f"[WARNING]: {msg}\n")
            elif level == "error":
                print(f"[ERROR]: {msg}")
                file.write(f"[ERROR]: {msg}\n")
            else:
                print(f"[UNKNOWN]: {msg}")
                file.write(f"[UNKNOWN]: {msg}\n")


def debug_print(msg):
    if DEBUG:
        print(msg)


def get_discovery_topic_select(uid: str):
    return f"homeassistant/select/{uid}/config"


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.config(pm=network.WLAN.PM_NONE)
    network.hostname(UID)
    wlan.active(True)
    i = 0
    tries = 0
    while not wlan.isconnected() and tries < 5:
        wlan.connect(SSID, WIFI_PASSWORD)
        while i < 10 and not wlan.isconnected():
            debug_print(f"Connecting to Wi-Fi... {i + 1}")
            LED.on()
            sleep_ms(500)
            LED.off()
            sleep_ms(500)
            i += 1
        if not wlan.isconnected():
            log(f"Wi-Fi connection failed {tries + 1}. attempt", "warning")
            sleep_ms(200)
            wlan.disconnect()
            sleep_ms(200)
        if i >= 10 and tries >= 5 and not wlan.isconnected():
            raise Exception("Wi-Fi connection timeout")
        i = 0
        tries += 1
    debug_print(f"Connected to Wi-Fi with ip: {wlan.ifconfig()[0]}")
    return True


def discover_mode_select(client: MQTTClient, device_data):
    discovery_data = {
        "name": "Mode select",
        "unique_id": MODE_ID,
        "state_topic": MODE_STATE,
        "optimistic": False,
        "availability": {
            "topic": AVAILABILITY_TOPIC,
            "payload_available": "online",
            "payload_not_available": "offline",
        },
        "device": device_data,
        "qos": 0,
        "retain": True,
        "command_topic": MODE_COMMAND,
        "options": [
            "Turn off",
            "Auto",
            "Slow",
            "Medium",
            "Fast",
            "Turbo",
            "Silent",
        ],
    }
    client.publish(
        get_discovery_topic_select(MODE_ID), dumps(discovery_data), retain=True
    )
    sleep_ms(200)


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
    discover_mode_select(client, device_data_first)
    sleep_ms(200)


def mqtt_connect():
    debug_print("Connecting to MQTT broker...")
    client = MQTTClient(
        UID,
        MQTT_BROKER,
        keepalive=PING_INTERVAL * 2,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
    )
    client.set_last_will(AVAILABILITY_TOPIC, "offline", retain=True)
    sleep_ms(200)
    client.connect(clean_session=False)
    debug_print("Connected!")
    sleep_ms(200)
    discover(client)
    client.publish(AVAILABILITY_TOPIC, "online", retain=True)
    return client


def main():
    connect_wifi()

    if not connect_wifi():
        raise Exception("Wi-Fi connection failed")
    breezer = Breezer(
        power_pin=POWER_PIN,
        mode_pin=MODE_PIN,
    )
    client = mqtt_connect()

    # I am up and running
    breezer.power_btn()
    sleep_ms(200)
    breezer.power_btn()
    sleep_ms(200)

    def listen_mqtt_commands(topic, msg):
        debug_print(topic)
        debug_print(msg)

        if topic == MODE_COMMAND.encode("ascii"):

            def check_power():
                if breezer.get_mode() == "Off":
                    breezer.power_btn()

            if msg == b"Turn off":
                if breezer.get_mode() == "Off":
                    return
                breezer.power_btn()
                client.publish(MODE_STATE, "Off", retain=True)
                return

            if msg == b"Auto":
                check_power()
                breezer.set_mode(breezer.MODE_AUTO)
            elif msg == b"Slow":
                check_power()
                breezer.set_mode(breezer.MODE_SLOW)
            elif msg == b"Medium":
                check_power()
                breezer.set_mode(breezer.MODE_MEDIUM)
            elif msg == b"Fast":
                check_power()
                breezer.set_mode(breezer.MODE_FAST)
            elif msg == b"Turbo":
                check_power()
                breezer.set_mode(breezer.MODE_TURBO)
            elif msg == b"Silent":
                check_power()
                breezer.set_mode(breezer.MODE_SILENT)
            client.publish(MODE_STATE, breezer.get_mode(), retain=True)

    client.set_callback(listen_mqtt_commands)
    sleep_ms(200)
    client.subscribe(MODE_COMMAND)
    sleep_ms(200)
    count = 0
    while True:
        count += 1
        if count > PING_INTERVAL * 2:
            client.ping()
            sleep_ms(200)
            count = 0
        client.check_msg()

        sleep_ms(500)


try:
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            log(e, "error")
finally:
    LED.off()
    POWER_PIN.off()
    MODE_PIN.off()
