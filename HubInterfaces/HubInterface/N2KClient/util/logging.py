from enum import Enum
import logging
import os
import sys
from typing import Any


class ConsoleThemeStyle(str, Enum):
    Text = "text"
    SecondaryText = "secondaryText"
    TertiaryText = "tertiaryText"
    Invalid = "invalid"
    Null = "null"
    Name = "name"
    String = "string"
    Number = "number"
    Boolean = "boolean"
    Scalar = "scalar"
    LevelVerbose = "levelVerbose"
    LevelDebug = "levelDebug"
    LevelInformation = "levelInformation"
    LevelWarning = "levelWarning"
    LevelError = "levelError"
    LevelFatal = "levelFatal"


class ColorTheme:
    colors: dict[ConsoleThemeStyle, str]

    def __init__(self, colors: dict[ConsoleThemeStyle, str]):
        self.colors = colors


class CodeColorTheme(ColorTheme):
    def __init__(self):
        ColorTheme.__init__(
            self,
            {
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
            },
        )


class ColoredLogRecord(logging.LogRecord):

    _reset = "\x1b[0m"

    _theme: ColorTheme

    def __init__(self, theme: ColorTheme, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.levelname = self.levelname.upper()
        self._theme = theme

        self.levelname = self._colorize_level()

    def getMessage(self) -> str:
        msg = str(self.msg)
        if self.args:
            arg_list = list(self.args)
            for index, record in enumerate(arg_list):
                arg_list[index] = self._colorize_arg(record)
            arg_tuple = tuple(arg_list)
            msg = msg % arg_tuple
        return msg

    def _colorize_level(self) -> str:
        level_name = self.levelname.rjust(6)

        if self.levelno == logging.DEBUG:
            return self.__colorize(level_name, ConsoleThemeStyle.LevelDebug)
        elif self.levelno == logging.INFO:
            return self.__colorize(level_name, ConsoleThemeStyle.LevelInformation)
        elif self.levelno == logging.WARNING:
            return self.__colorize(level_name, ConsoleThemeStyle.LevelWarning)
        elif self.levelno == logging.ERROR:
            return self.__colorize(level_name, ConsoleThemeStyle.LevelError)
        elif self.levelno == logging.CRITICAL:
            return self.__colorize(level_name, ConsoleThemeStyle.LevelFatal)

        return level_name

    def _colorize_arg(self, val: Any) -> str:

        style = None

        if isinstance(val, str):
            style = ConsoleThemeStyle.String
        elif isinstance(val, int):
            style = ConsoleThemeStyle.Number
        elif isinstance(val, bool):
            style = ConsoleThemeStyle.Boolean

        if style is None:
            return str(val)

        return self.__colorize(val, style)

        color = self._theme.colors[style]
        return f"{color}{val}{self._reset}"

    def __colorize(self, string_val: str, style: ConsoleThemeStyle) -> str:
        color = self._theme.colors[style]
        return f"{color}{string_val}{self._reset}"


def has_colors():
    if os.environ.get("NO_COLOR", "") != "":
        return False
    if os.environ.get("CLICOLOR_FORCE", "") != "":
        return True
    if os.environ.get("CLICOLOR", "") != "":
        return sys.stdout.isatty()
    else:
        return False


class ColoredLoggingFormatter(logging.Formatter):
    pass


def configure_logging():
    colors = has_colors()
    custom_handler = logging.StreamHandler(sys.stdout)
    custom_handler.setFormatter(
        logging.Formatter(
            "{levelname} | {asctime} | {filename}:{lineno} | {message}",
            "%Y-%m-%dT%H:%M:%SZ",
            style="{",
        )
    )

    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[custom_handler],
    )

    if colors:

        color_theme = CodeColorTheme()

        def colorered_log_factory(*args, **kwargs):
            record = ColoredLogRecord(color_theme, *args, **kwargs)
            return record

        logging.setLogRecordFactory(colorered_log_factory)
