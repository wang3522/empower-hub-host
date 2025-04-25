#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import sys
import os
import logging
import logging.handlers
import traceback  # [x] debug

from threading import Event

from HubInterface.utility.gpio import GPIO, E_LED
from HubInterface.bleService.ble import BLE
from HubInterface.thingsBoardService.tb import TB
from HubInterface.network.lte import LTE
from HubInterface.utility.config import SystemConfig as HubConfig
from HubInterface.dbusService.server import DBusServer

logger = logging.getLogger()

def wifi_ap_setup():
    from HubInterface.network.wifi import configure_wifi_settings
    from HubInterface.network.ap import configure_wap_settings
    
    wifi = configure_wifi_settings()
    ap = configure_wap_settings()
    
    logger.debug(f"wifi: {wifi}, ap: {ap}")
    
    gpio = GPIO()
    gpio.update_led(E_LED.WIFI, wifi)
    gpio.update_led(E_LED.AP, ap)

def initialize_ble():
    try:
        ble = BLE()
        ble.configure()
        ble.start()
        logger.info("BLE started.")
        return ble
    except Exception as error:
        logger.error(f"Error starting BLE: {error}")
        raise Exception("BLE not started.")
    
def initialize_lte():
    try:
        lte = LTE()
        lte.configure_network()
        lte.configure_gnss()
        lte.start_gnss()
        
        gpio = GPIO()
        gpio.update_led(E_LED.LTE, True)
        
        logger.info("LTE GNSS started.")
        return lte
    except Exception as error:
        logger.error(f"Error starting LTE GNSS: {error}")
        raise Exception("LTE GNSS not started.")

def main_loop():
    try:
        logger.debug("main loop started")
        Event().wait()
    # except Exception as error:
    #     logger.debug(f"Error in main loop: {error}")
    finally:
        logger.info("main loop stopped.")

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    
    gpio = None
    ble = None
    lte = None
    tb = None
    _config = None
    dbus_server = None
    
    try:
        _config = HubConfig()
        gpio = GPIO()
        gpio.start()
        gpio.update_led(E_LED.POWER, True)

        wifi_ap_setup()
        ble = initialize_ble() # [x]
        lte = initialize_lte()
        
        tb = TB()
        tb.start()
        
        dbus_server = DBusServer()
        dbus_server.start()
        
        main_loop()
    finally:
        if ble:
            ble.stop()
        if lte:
            lte.stop_gnss()
        if tb:
            tb.stop()
        if dbus_server:
            dbus_server.stop()
        if gpio:
            gpio.update_led(E_LED.WIFI, False)
            gpio.update_led(E_LED.AP, False)
            gpio.update_led(E_LED.LTE, False)
            gpio.stop()

if __name__ == "__main__":
    try:
        log_path = os.getenv("HUB_LOGDIR", "/var/log/hub")
        LOG_FILENAME = os.path.join(log_path, "HubInterfaces.log")

        log_level = os.getenv("HUB_LOG_LEVEL", "DEBUG")

        FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"

        if os.path.isdir(log_path):
            handler = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME, maxBytes=10000000, backupCount=10)
            handler.setFormatter(logging.Formatter(FORMAT))
            logger.addHandler(handler)
        # else: # [x] debug
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(stream_handler)

        logger.setLevel(log_level)

        logger.info("HubInterfaces application started.")

        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("HubInterfaces application stopped by user.")
        sys.exit(0)
    except Exception as error:
        logger.error(error)
        traceback.print_exc()  # [x] debug
        sys.exit(1)
    finally:
        logger.info("HubInterfaces application stopped.")
        logger.info("")
