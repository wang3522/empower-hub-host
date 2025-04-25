#!/usr/bin/env python3
import argparse
import logging
import base64
import dbus

from HubInterface.utility.config import SystemConfig as HubConfig

logger = logging.getLogger()

def perform_service_restart():
    bus = dbus.SystemBus()
    dbus_object = "/org/navico/HubInterface"
    dbus_interface = "org.navico.HubInterface"
    obj = bus.get_object(dbus_interface, dbus_object)
    method = obj.get_dbus_method("wifi.restart")
    result = method()
    logger.debug(f"{dbus_interface}: {result}")
    pass

def configure_network(mode, action, ssid=None, password=None, apn=None, device_id=None):
    config = HubConfig()
    if mode == 'wifi':
        if action == 'enable' and ssid and password:
            logger.debug(f"Enabling WiFi with SSID: {ssid} and Password: {password}")
            config.wifi['enable'] = True
            config.wifi['ssid'] = ssid
            config.wifi['password'] = base64.b64encode(password.encode("utf-8")).decode("utf-8")
        elif action == 'disable':
            logger.debug("Disabling WiFi")
            config.wifi['enable'] = False
        config.save_config()
        perform_service_restart()
    elif mode == 'hotspot':
        if action == 'enable':
            logger.debug(f"Enabling Hotspot.")
            config.wap['enable'] = True
        elif action == 'disable':
            logger.debug("Disabling Hotspot")
            config.wap['enable'] = False
        config.save_config()
        # perform_service_restart()
    elif mode == 'lte':
        if action == 'enable':
            logger.debug("Enabling LTE")
            config.lte['enable'] = True
            config.lte['apn'] = apn if apn else config.lte['apn']
            config.lte['device_id'] = device_id if device_id else config.lte['device_id']
        elif action == 'disable':
            logger.debug("Disabling LTE")
            config.lte['enable'] = False
        config.save_config()
        # perform_service_restart()
    else:
        logger.debug("Invalid mode. Please choose from 'wifi', 'hotspot', or 'lte'.")

def main():
    parser = argparse.ArgumentParser(description="Network Configuration Utility")
    parser.add_argument('mode', choices=['wifi', 'hotspot', 'lte'], help="Mode of operation")
    parser.add_argument('action', choices=['enable', 'disable'], help="Action to perform")
    parser.add_argument('--ssid', help="SSID for WiFi")
    parser.add_argument('--password', help="Password for WiFi")
    parser.add_argument('--apn', help="APN for LTE")
    parser.add_argument('--device_id', help="Device ID for LTE")

    args = parser.parse_args()

    configure_network(args.mode, args.action, args.ssid, args.password, args.apn, args.device_id)

if __name__ == "__main__":
    try:
        FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(FORMAT))
        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG)
        logger.debug("hub-network-utility started.")
        main()
    except Exception as error:
        logger.error(f"Error in hub-network-utility: {error}")
    finally:
        logger.debug("hub-network-utility stopped.")