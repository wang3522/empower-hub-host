#!/usr/bin/env python3
import argparse
import logging
import base64
import dbus

logger = logging.getLogger()

def configure_network(mode, action, ssid=None, password=None, apn=None, device_id=None):
    bus = dbus.SystemBus()
    
    if mode == 'wifi':
        dbus_object = "/org/navico/HubInterface/wifi"
        dbus_interface = "org.navico.HubInterface.wifi"
        obj = bus.get_object(dbus_interface, dbus_object)
        if action == 'enable' and ssid and password:
            logger.debug(f"Enabling WiFi with SSID: {ssid} and Password: {password}")
            method = obj.get_dbus_method('configure', dbus_interface)
            result = method(ssid, password)
            logger.debug(f"WiFi configured successfully: {result}")
        elif action == 'disable':
            logger.debug("Disabling WiFi")
            method = obj.get_dbus_method('disable')
            result = method()
            logger.debug(f"{dbus_interface}: {result}")
            
    elif mode == 'hotspot':
        if action == 'enable':
            logger.debug(f"Enabling Hotspot.")
        elif action == 'disable':
            logger.debug("Disabling Hotspot")
    elif mode == 'lte':
        if action == 'enable':
            logger.debug("Enabling LTE")
        elif action == 'disable':
            logger.debug("Disabling LTE")
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