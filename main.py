from machine import Pin
from time import sleep, sleep_ms

power_btn = Pin(27, Pin.OUT)
mode_btn = Pin(26, Pin.OUT)
led = Pin("LED", Pin.OUT)


def main():
    power_btn.value(0)
    mode_btn.value(0)


main()
