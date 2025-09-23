import unittest
from N2KClient.n2kclient.models.n2k_configuration.n2k_configuation import (
    N2kConfiguration,
)


class TestN2kConfiguration(unittest.TestCase):
    def test_n2k_configuration_init(self):
        config = N2kConfiguration()
        self.assertIsInstance(config.gnss, dict)
        self.assertIsInstance(config.circuit, dict)
        self.assertIsInstance(config.hidden_circuit, dict)
        self.assertIsInstance(config.dc, dict)
        self.assertIsInstance(config.ac, dict)
        self.assertIsInstance(config.tank, dict)
        self.assertIsInstance(config.inverter_charger, dict)
        self.assertIsInstance(config.device, dict)
        self.assertIsInstance(config.hvac, dict)
        self.assertIsInstance(config.audio_stereo, dict)
        self.assertIsInstance(config.binary_logic_state, dict)
        self.assertIsInstance(config.ui_relationships, list)
        self.assertIsInstance(config.pressure, dict)
