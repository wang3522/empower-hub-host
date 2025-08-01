import json
import os
import logging

from ..config import (
    DEFAULT_APP_SETTINGS_FILE,
    OVERRIDE_APP_SETTINGS_FILE,
)


class SettingsUtil:
    _logger = logging.getLogger(__name__)
    _config = {}

    @staticmethod
    def recursive_update(d, u):
        """
        Recursively update dictionary d with values from dictionary u.

        Args:
            d (dict): The dictionary to be updated.
            u (dict): The dictionary with values to update d.
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d:
                d[k] = SettingsUtil.recursive_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    @staticmethod
    def load_settings(default_file, override_file=None):
        """
        Load settings from the default file and optionally override with another file.

        Args:
            default_file (str): Path to the default settings file.
            override_file (str, optional): Path to the override settings file.

        Returns:
            dict: The loaded configuration settings.
        """
        try:
            default_config = {}
            combined_config = {}
            SettingsUtil._logger.warning("Debug: Searching for appsettings file...")
            if default_file and os.path.exists(default_file):
                SettingsUtil._logger.warning(
                    "Debug: Found default appsettings file, loading now..."
                )
                with open(default_file, "r") as file:
                    default_config = json.load(file)
            else:
                SettingsUtil._logger.warning(
                    f"Warning: The file {default_file} does not exist."
                )

            if override_file and os.path.exists(override_file):
                SettingsUtil._logger.warning(
                    "Debug: Found override appsettings file, loading now..."
                )
                with open(override_file, "r") as file:
                    override_config = json.load(file)
                combined_config = SettingsUtil.recursive_update(
                    default_config, override_config
                )
            else:
                combined_config = default_config

            return combined_config
        except json.JSONDecodeError as e:
            SettingsUtil._logger.error(f"Error decoding JSON: {e}")
            return {}
        except Exception as e:
            SettingsUtil._logger.error(f"An unexpected error occurred: {e}")
            return {}

    @staticmethod
    def get_setting(*keys, default_value):
        """
        Retrieve a setting value from the configuration using a sequence of keys.

        Args:
            *keys: A sequence of keys to traverse the configuration dictionary.
            default_value: The value to return if the keys do not exist.

        Returns:
            The value from the configuration or the default value.
        """
        value = SettingsUtil._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default_value


# Initialize the _config attribute
SettingsUtil._config = SettingsUtil.load_settings(
    DEFAULT_APP_SETTINGS_FILE, OVERRIDE_APP_SETTINGS_FILE
)
