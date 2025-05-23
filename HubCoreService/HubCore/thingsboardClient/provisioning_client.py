"""
Thingsboard Client for the N2k Client
This client is used to connect to Thingsboard and send telemetry and attributes
to the Thingsboard server.
"""
import ssl
import logging
from tb_device_mqtt import ProvisionClient

logger = logging.getLogger("EmpowerProvisionClient")

class EmpowerProvisionClient(ProvisionClient):
    """
    This class is used to provision a device to ThingsBoard using MQTT.
    """
    # TLS has to be enabled but ProvisionClient doesn't provide that option
    def __init__(self, host, port, provision_request):
        super().__init__(host, port, provision_request)

    def provision(self, ca_certs=None, cert_file=None, key_file=None):
        logger.info("[EmpowerProvisionClient] Connecting to ThingsBoard")
        self.__credentials = None
        try:
            self.tls_set(
                ca_certs=ca_certs,
                certfile=cert_file,
                keyfile=key_file,
                cert_reqs=ssl.CERT_REQUIRED,
                tls_version=ssl.PROTOCOL_TLSv1_2,
                ciphers=None,
            )
            self.tls_insecure_set(False)
        except ValueError:
            pass
        self.connect(self._host, self._port, 120)
        self.loop_forever()
