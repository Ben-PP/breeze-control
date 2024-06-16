from machine import Pin
from time import sleep_ms


class Breezer:

    POWER_OFF = 0
    POWER_ON = 1

    MODE_AUTO = 0
    MODE_SLOW = 1
    MODE_MEDIUM = 2
    MODE_FAST = 3
    MODE_TURBO = 4
    MODE_SILENT = 5

    def __init__(
        self,
        power_pin: Pin,
        mode_pin: Pin,
    ):
        self.power_pin = power_pin
        self.mode_pin = mode_pin
        self.mode = 0
        self.power = self.POWER_OFF

    def get_mode(self):
        if self.power == self.POWER_OFF:
            return "Off"
        if self.mode == self.MODE_AUTO:
            return "Auto"
        if self.mode == self.MODE_SLOW:
            return "Slow"
        if self.mode == self.MODE_MEDIUM:
            return "Medium"
        if self.mode == self.MODE_FAST:
            return "Fast"
        if self.mode == self.MODE_TURBO:
            return "Turbo"
        if self.mode == self.MODE_SILENT:
            return "Silent"

    def set_mode(self, mode: int):
        while self.mode != mode:
            self.mode_btn()
            sleep_ms(200)

    def power_btn(self):
        self.power_pin.on()
        sleep_ms(200)
        self.power_pin.off()
        if self.power == self.POWER_OFF:
            self.power = self.POWER_ON
        else:
            self.power = self.POWER_OFF
        self.mode = self.MODE_AUTO
        sleep_ms(200)

    def mode_btn(self):
        self.mode_pin.on()
        sleep_ms(200)
        self.mode_pin.off()
        self.mode += 1
        if self.mode > self.MODE_SILENT:
            self.mode = self.MODE_AUTO
        sleep_ms(200)
