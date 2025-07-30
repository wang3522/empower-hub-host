import logging
from n2kclient.client import N2KClient
from n2kclient.util.logging import configure_logging


class Main:
    logger = logging.getLogger("DBUS N2k Client: Main")

    def __init__(self):
        configure_logging()

    def run(self):
        self.logger.info("Starting N2K Client")
        n2k_client = N2KClient()
        n2k_client.start()
        self.logger.info("N2K Client is running")
        self.logger.info("Press Ctrl+C to stop")


def main():
    main = Main()
    main.run()


if __name__ == "__main__":
    main()
