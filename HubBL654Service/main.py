#!/usr/bin/env python3
import dbus
import dbus.mainloop.glib
import sys
import os
import logging
import logging.handlers
import traceback  # [x] debug

from threading import Event

from .bleService.bleuart import BLE_UART
from .dbusService.server import initialize_dbus_server

logger = logging.getLogger()

def initialize_ble():
    try:
        ble_uart = BLE_UART()
        ble_uart.configure()
        ble_uart.start()
        logger.info("BLE uart started.")
        return ble_uart
    except Exception as error:
        logger.error(f"Error starting BLE UART: {error}")
        raise Exception("BLE uart not started.")


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

    ble = None
    lte = None
    tb = None
    dbus_server = None

    try:
        dbus_server = initialize_dbus_server()
        dbus_server.start()

        main_loop()
    finally:
        if ble:
            ble.stop()
        if dbus_server:
            dbus_server.stop()


if __name__ == "__main__":
    try:
        log_path = os.getenv("HUB_LOGDIR", "/data/hub/log")
        LOG_FILENAME = os.path.join(log_path, "HubBL654Service.log")

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

        logger.info("HubBL654Service started.")

        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("HubBL654Service stopped by user.")
        sys.exit(0)
    except Exception as error:
        logger.error(error)
        traceback.print_exc()  # [x] debug
        sys.exit(1)
    finally:
        logger.info("HubBL654Service stopped.")
        logger.info("")
