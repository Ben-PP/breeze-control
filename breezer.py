from machine import Pin
from time import sleep_ms

POWER_OFF = False
POWER_ON = True

MODE_OFF = 0
MODE_AUTO = 1
MODE_SLOW = 2
MODE_MEDIUM = 3
MODE_FAST = 4
MODE_TURBO = 5
MODE_SILENT = 6


class Breezer:

    def __init__(self, power_pin, mode_pin):
        self.power_pin = Pin(power_pin, Pin.OUT)
        self.mode_pin = Pin(mode_pin, Pin.OUT)
        self.power_state = False
        self.mode = 0

    def power_btn(self):
        self.power_pin.on()
        sleep_ms(200)
        self.power_pin.off()
