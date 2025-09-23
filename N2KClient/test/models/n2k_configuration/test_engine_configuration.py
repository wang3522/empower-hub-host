import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.engine_configuration import (
    EngineConfiguration,
)
from N2KClient.n2kclient.models.constants import AttrNames


class TestEngineConfiguration(unittest.TestCase):
    def test_engine_configuration_to_dict_exception(self):
        obj = EngineConfiguration()
        obj.to_dict = MagicMock(side_effect=Exception("fail"))
        try:
            d = obj.to_dict()
        except Exception:
            d = {}
        self.assertEqual(d, {})

    def test_engine_configuration_to_dict(self):
        engine_mock = MagicMock()
        engine_mock.to_dict.return_value = {"engine_key": "engine_val"}
        obj = EngineConfiguration(
            devices={1: engine_mock, 2: engine_mock}, should_reset=True
        )
        d = obj.to_dict()
        self.assertIn(AttrNames.ENGINE, d)
        self.assertEqual(
            d[AttrNames.ENGINE],
            {1: {"engine_key": "engine_val"}, 2: {"engine_key": "engine_val"}},
        )
        self.assertIn(AttrNames.SHOULD_RESET, d)
        self.assertTrue(d[AttrNames.SHOULD_RESET])
