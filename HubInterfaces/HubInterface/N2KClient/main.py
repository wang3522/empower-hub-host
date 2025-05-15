import logging
from N2KClient.client import N2KClient


class Main:
    logger = logging.getLogger("DBUS N2k Client: Main")

    def __init__(self):
        self.logger.setLevel(logging.INFO)
        log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)

    def run(self):
        self.logger.info("Starting N2K Client")
        n2k_client = N2KClient()
        n2k_client.start()
        self.logger.info("N2K Client is running")


def main():
    main = Main()
    main.run()


if __name__ == "__main__":
    main()
