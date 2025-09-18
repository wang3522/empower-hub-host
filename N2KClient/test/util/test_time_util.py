import unittest
from N2KClient.n2kclient.util.time_util import TimeUtil


class TestTimeUtil(unittest.TestCase):
    """
    Class to test the functions inside of
    the time_util.py file
    """

    def test_current_time(self):
        """
        Test case for the current_time function
        """
        self.assertIsInstance(TimeUtil.current_time(), int)
