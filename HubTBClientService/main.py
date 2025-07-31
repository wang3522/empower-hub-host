"""
Main entry point for testing the Thingsboard Client.
Will Update with the program when project is ready.
"""
#pylint: disable=import-error
from tb_utils.tb_client_logger import configure_logging
from services.empower_service import EmpowerService

def main():
    """
    Main function to run the Thingsboard Client.
    """
    print("This is the main entry point for the Thingsboard Client.")
    empower_client = EmpowerService()
    empower_client.run()

if __name__ == "__main__":
    configure_logging()
    main()
