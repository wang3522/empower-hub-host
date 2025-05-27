"""
Main entry point for testing the Thingsboard Client.
Will Update with the program when project is ready.
"""
import time
#pylint: disable=import-error
import services.sync_service
from mqtt_client import ThingsBoardClient
from tb_utils.tb_client_logger import configure_logging

def main():
    """
    Main function to run the Thingsboard Client.
    """
    print("This is the main entry point for the Thingsboard Client.")
    syncing_service = services.sync_service.SyncService()
    print("SyncService instance created:", syncing_service)
    syncing_service.subscribe_to_attribute("location")
    outside_client = ThingsBoardClient()
    #pylint: disable=protected-access, invalid-name
    COUNTER = 0
    while COUNTER < 5:
        loop_client = ThingsBoardClient()
        loop_client.connect()
        while not outside_client._is_connected_internal.value:
            time.sleep(1)
        time.sleep(1)
        print("Sending telemetry and attributes")
        # Simulate sending telemetry
        loop_client.send_telemetry({"temperature": 25, "humidity": 60})
        # Simulate updating attributes
        if COUNTER == 1:
            loop_client.update_attributes({"location": "home", "status": "active"})
        else:
            loop_client.update_attributes({"location": "home"})
        COUNTER += 1
        time.sleep(10)
        loop_client.disconnect()
    outside_client.disconnect()

    print("SyncService instance deleted.")
    syncing_service.__del__()

if __name__ == "__main__":
    configure_logging()
    main()
