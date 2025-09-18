"""
test_logging.py
"""

import unittest
import logging
from N2KClient.n2kclient.util.logging import (
    ConsoleThemeStyle,
    CodeColorTheme,
    ColoredLogRecord,
    has_colors,
)


class CodeColorThemeTest(unittest.TestCase):
    """
    Class to test the init of CodeColorTheme
    and the default values used
    """

    def test_code_color_theme_init(self):
        """
        Test case for init function
        """
        color_theme = CodeColorTheme()

        self.assertIsNotNone(color_theme)

    def test_code_color_theme_defaults(self):
        """
        Test case for the default values produced from the
        init function
        """
        color_theme = CodeColorTheme()

        color_config = {
            ConsoleThemeStyle.Text: "\x1b[38;5;0253m",
            ConsoleThemeStyle.SecondaryText: "\x1b[38;5;0246m",
            ConsoleThemeStyle.TertiaryText: "\x1b[38;5;0242m",
            ConsoleThemeStyle.Invalid: "\x1b[33;1m",
            ConsoleThemeStyle.Null: "\x1b[38;5;0038m",
            ConsoleThemeStyle.Name: "\x1b[38;5;0081m",
            ConsoleThemeStyle.String: "\x1b[38;5;0216m",
            ConsoleThemeStyle.Number: "\x1b[38;5;151m",
            ConsoleThemeStyle.Boolean: "\x1b[38;5;0038m",
            ConsoleThemeStyle.Scalar: "\x1b[38;5;0079m",
            ConsoleThemeStyle.LevelVerbose: "\x1b[37m",
            ConsoleThemeStyle.LevelDebug: "\x1b[37m",
            ConsoleThemeStyle.LevelInformation: "\x1b[37;1m",
            ConsoleThemeStyle.LevelWarning: "\x1b[38;5;0229m",
            ConsoleThemeStyle.LevelError: "\x1b[38;5;0197m\x1b[48;5;0238m",
            ConsoleThemeStyle.LevelFatal: "\x1b[38;5;0197m\x1b[48;5;0238m",
        }
        self.assertEqual(color_theme.colors, color_config)


class ColorLogRecordTest(unittest.TestCase):
    """
    Class to test the functionality of the
    ColorLogRecord class in logging.py
    """

    def test_color_log_record_init(self):
        """
        Test case for init function with only the color theme
        """
        record = ColoredLogRecord(
            theme=CodeColorTheme(),
            name="loggingName",
            level=logging.INFO,
            pathname="./",
            lineno="123456",
            msg="testMessage",
            args=None,
            exc_info=None,
        )

        self.assertIsNotNone(record)

    def test_color_log_record_get_message(self):
        """
        Test case for getting the message from the log record
        """
        test_message = "test log"
        record = ColoredLogRecord(
            theme=CodeColorTheme(),
            name="loggingName",
            level=logging.INFO,
            pathname="./",
            lineno="123456",
            msg=test_message,
            args=None,
            exc_info=None,
        )

        self.assertEqual(record.getMessage(), test_message)

    def test_color_log_record_colorize_level(self):
        """
        Test case for getting the colorized level from the log record
        """
        test_message = "test log"
        record = ColoredLogRecord(
            theme=CodeColorTheme(),
            name="loggingName",
            level=logging.INFO,
            pathname="./",
            lineno="123456",
            msg=test_message,
            args=None,
            exc_info=None,
        )
        # pylint: disable=protected-access
        self.assertEqual(
            record._colorize_level(), "\x1b[37;1m\x1b[37;1m  INFO\x1b[0m\x1b[0m"
        )

    def test_color_log_record_colorize_arg(self):
        """
        Test case for getting the colorized level from the log record
        """
        test_message = "test log"
        record = ColoredLogRecord(
            theme=CodeColorTheme(),
            name="loggingName",
            level=logging.INFO,
            pathname="./",
            lineno="123456",
            msg=test_message,
            args=None,
            exc_info=None,
        )
        # pylint: disable=protected-access
        self.assertEqual(
            record._colorize_arg(test_message), "\x1b[38;5;0216mtest log\x1b[0m"
        )


class LoggingFunctionsTest(unittest.TestCase):
    """
    Class to test the misc functions in logging.py
    """

    def test_has_colors(self):
        """
        Test case for checking to see if the os has colors
        """
        self.assertFalse(has_colors())


if __name__ == "__main__":
    unittest.main()
