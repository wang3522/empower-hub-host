import threading
import time
import gpiod
import logging

from enum import Enum
from gpiod.line import Direction, Value

logger = logging.getLogger(__name__)


class E_LED(Enum):
    POWER = 0
    WIFI = 1
    AP = 2
    LTE = 3


class GPIO:
    _instance = None
    led_line = None
    can_bus = None
    thread = None
    stop_event = None

    wifi_led_state = False
    ap_led_state = False
    power_led_state = False
    lte_led_state = False

    GPIO_WIFI_AP_LED_LINE = 22
    GPIO_POWER_LED_LINE = 21
    GPIO_LTE_LED_LINE = 20

    def __new__(cls):
        if cls._instance is None:
            try:
                cls._instance = super().__new__(cls)

                cls._instance.led_line = gpiod.request_lines(
                    "/dev/gpiochip0",
                    consumer="hub-core-led",
                    config={
                        tuple([cls.GPIO_WIFI_AP_LED_LINE, cls.GPIO_POWER_LED_LINE, cls.GPIO_LTE_LED_LINE]): gpiod.LineSettings(
                            direction=Direction.OUTPUT, active_low=True
                        )
                    },
                )

            except Exception as error:
                logger.error(f"Error initializing GPIO: {error}")
                cls._instance = None
                raise error
        return cls._instance

    def __del__(self):
        logger.debug("----------------GPIO deleted")
        self.stop()

    def start(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._gpio_thred)
        self.thread.start()

    def _gpio_thred(self):
        val = {self.GPIO_WIFI_AP_LED_LINE: Value.INACTIVE, self.GPIO_POWER_LED_LINE: Value.INACTIVE, self.GPIO_LTE_LED_LINE: Value.INACTIVE}
        while not self.stop_event.is_set():
            if self.wifi_led_state:
                val[self.GPIO_WIFI_AP_LED_LINE] = Value.ACTIVE
            elif self.ap_led_state:
                val[self.GPIO_WIFI_AP_LED_LINE] = Value.ACTIVE if val[self.GPIO_WIFI_AP_LED_LINE] == Value.INACTIVE else Value.INACTIVE
            else:
                val[self.GPIO_WIFI_AP_LED_LINE] = Value.INACTIVE
                
            if self.power_led_state:
                val[self.GPIO_POWER_LED_LINE] = Value.ACTIVE
            else:
                val[self.GPIO_POWER_LED_LINE] = Value.INACTIVE
                
            if self.lte_led_state:
                val[self.GPIO_LTE_LED_LINE] = Value.ACTIVE
            else:
                val[self.GPIO_LTE_LED_LINE] = Value.INACTIVE
                
            self.led_line.set_values(val)
            time.sleep(0.5)
        pass

    def stop(self):
        time.sleep(1)
        if self.stop_event:
            self.stop_event.set()
        if self.thread:
            self.thread.join()
        if self.led_line:
            self.led_line.release()
        if self.can_bus:
            self.can_bus.release()

    def update_led(self, led: E_LED, mode: bool):
        if led == E_LED.WIFI:
            self.wifi_led_state = mode
        elif led == E_LED.AP:
            self.ap_led_state = mode
        elif led == E_LED.POWER:
            self.power_led_state = mode
        elif led == E_LED.LTE:
            self.lte_led_state = mode
        else:
            logger.debug("Invalid led")
