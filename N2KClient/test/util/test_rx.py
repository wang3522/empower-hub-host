"""
test_rx.py
"""

import unittest
import N2KClient.n2kclient.util.rx as react


class RxTest(unittest.TestCase):
    """
    Class to test the functions inside of
    the rx.py flie
    """

    def test_round_return(self):
        """
        Test that round_float operator rounds values in an Observable stream
        """
        import reactivex

        values = []
        obs = reactivex.of(1.2345)
        obs.pipe(react.round_float(2)).subscribe(values.append)
        self.assertEqual(values, [1.23])


if __name__ == "__main__":
    unittest.main()
