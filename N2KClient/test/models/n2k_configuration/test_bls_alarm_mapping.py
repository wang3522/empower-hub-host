import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.bls_alarm_mapping import (
    BLSAlarmMapping,
)


class TestBLSAlarmMapping(unittest.TestCase):
    def test_bls_alarm_mapping_values(self):
        bls_mock = MagicMock()
        mapping = BLSAlarmMapping(alarm_channel=5, bls=bls_mock)
        self.assertEqual(mapping.alarm_channel, 5)
        self.assertIs(mapping.bls, bls_mock)
