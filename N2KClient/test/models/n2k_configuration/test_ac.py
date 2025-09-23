import unittest
from unittest.mock import MagicMock
from N2KClient.n2kclient.models.n2k_configuration.ac import AC, ACLine, ACType
from N2KClient.n2kclient.models.constants import AttrNames


class TestAC(unittest.TestCase):
    def test_ac_to_dict_exception(self):
        # Use MagicMock to raise when .value is accessed
        bad_enum = MagicMock()
        type(bad_enum).value = property(
            lambda self: (_ for _ in ()).throw(Exception("fail"))
        )
        ac = AC(
            line=bad_enum,
            output=True,
            nominal_frequency=60,
            ac_type=bad_enum,
        )
        d = ac.to_dict()
        self.assertEqual(d, {})

    def test_ac_to_json_string_exception(self):
        bad_enum = MagicMock()
        type(bad_enum).value = property(
            lambda self: (_ for _ in ()).throw(Exception("fail"))
        )
        ac = AC(line=bad_enum, ac_type=bad_enum)
        json_str = ac.to_json_string()
        self.assertEqual(json_str, "{}")

    def test_ac_to_dict(self):
        ac = AC(
            line=ACLine.Line2,
            output=True,
            nominal_frequency=60,
            ac_type=ACType.Generator,
        )
        d = ac.to_dict()
        self.assertIn(AttrNames.LINE, d)
        self.assertEqual(d[AttrNames.LINE], ACLine.Line2.value)
        self.assertIn(AttrNames.OUTPUT, d)
        self.assertTrue(d[AttrNames.OUTPUT])
        self.assertIn(AttrNames.NOMINAL_FREQUENCY, d)
        self.assertEqual(d[AttrNames.NOMINAL_FREQUENCY], 60)
        self.assertIn(AttrNames.AC_TYPE, d)
        self.assertEqual(d[AttrNames.AC_TYPE], ACType.Generator.value)

    def test_to_json_string(self):
        ac = AC(
            line=ACLine.Line3,
            output=False,
            nominal_frequency=50,
            ac_type=ACType.ShorePower,
        )
        json_str = ac.to_json_string()
        self.assertIsInstance(json_str, str)
        self.assertIn('"line": 2', json_str)
        self.assertIn('"output": false', json_str)
        self.assertIn('"nominal_frequency": 50', json_str)
        self.assertIn('"ac_type": 2', json_str)
