#pylint: disable=import-error
import services.sync_service
from tb_utils.tb_client_logger import configure_logging

def main():
    print("This is the main entry point for the Thingsboard Client.")
    syncing_service = services.sync_service.SyncService()
    print("SyncService instance created:", syncing_service)

    print("SyncService instance deleted.")
    syncing_service.__del__()

if __name__ == "__main__":
    configure_logging()
    main()
