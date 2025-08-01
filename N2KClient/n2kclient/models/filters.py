from ..models.constants import Constants
from ..util.settings_util import SettingsUtil
from reactivex import operators as ops
import reactivex as rx


def create_filter(min_change):
    return ops.distinct_until_changed(
        lambda state: state,
        lambda current, previous: abs(current - previous) < min_change,
    )


def create_filter_for_engine_speed(min_change):
    return ops.distinct_until_changed(
        lambda state: state,
        lambda current, previous: (
            (abs(current - previous) < min_change) and (current >= min_change)
        ),
    )


def create_sampling_timer(min_time):
    return ops.sample(rx.interval(min_time))


class Engine:
    SPEED_MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.ENGINE,
        Constants.SPEED,
        Constants.MIN_CHANGE,
        default_value=200,
    )
    SPEED_SAMPLE_MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.ENGINE,
        Constants.SPEED,
        Constants.MIN_SAMPLE_FREQ_IN_SECONDS,
        default_value=5,
    )
    SPEED_FILTER = create_filter_for_engine_speed(SPEED_MIN_CHANGE)
    SPEED_SAMPLE_TIMER = create_sampling_timer(SPEED_SAMPLE_MIN_CHANGE)
    ENGINER_HOURS_MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.ENGINE,
        Constants.ENGINE_HOURS_IN_MINUTES,
        Constants.MIN_CHANGE,
        default_value=60,
    )
    ENGINE_HOURS_FILTER = create_filter(ENGINER_HOURS_MIN_CHANGE)


class HubFilter:
    SIGNAL_STRENGTH_MIN_CHANGE = SettingsUtil.get_setting(
        Constants.HUB, Constants.SIGNAL_STRENGTH, Constants.MIN_CHANGE, default_value=5
    )
    SIGNAL_STRENGTH_FILTER = create_filter(SIGNAL_STRENGTH_MIN_CHANGE)


class Voltage:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.VOLTAGE,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY, Constants.VOLTAGE, Constants.ROUND, default_value=1
    )
    FILTER = create_filter(MIN_CHANGE)


class Current:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.CURRENT,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY, Constants.CURRENT, Constants.ROUND, default_value=2
    )
    FILTER = create_filter(MIN_CHANGE)


class Temperature:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.TEMPERATURE,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.TEMPERATURE,
        Constants.ROUND,
        default_value=1,
    )
    FILTER = create_filter(MIN_CHANGE)


class Pressure:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.PRESSURE,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY, Constants.PRESSURE, Constants.ROUND, default_value=2
    )
    FILTER = create_filter(MIN_CHANGE)


class Frequency:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.FREQUENCY,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.FREQUENCY,
        Constants.ROUND,
        default_value=2,
    )
    FILTER = create_filter(MIN_CHANGE)


class Power:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.POWER,
        Constants.MIN_CHANGE,
        default_value=1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY, Constants.POWER, Constants.ROUND, default_value=0
    )
    FILTER = create_filter(MIN_CHANGE)


class Volume:
    MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.VOLUME,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY, Constants.VOLUME, Constants.ROUND, default_value=2
    )
    FILTER = create_filter(MIN_CHANGE)
    SAMPLE_TIMER = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.VOLUME,
        Constants.MIN_SAMPLE_FREQ_IN_SECONDS,
        default_value=60,
    )
    LEVEL_ABSOLUTE_MIN_CHANGE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.VOLUME,
        Constants.LEVEL_ABSOLUTE,
        Constants.MIN_CHANGE,
        default_value=0.1,
    )
    LEVEL_ABSOLUTE_FILTER = create_filter(LEVEL_ABSOLUTE_MIN_CHANGE)


class Location:
    # GNSS update sample in seconds
    LOCATION_GNSS_UPDATE_SAMPLE = SettingsUtil.get_setting(
        Constants.THINGSBOARD_SETTINGS_KEY,
        Constants.GNSS,
        Constants.LOCATION,
        Constants.GNSS_UPDATE_INTERVAL,
        default_value=10,
    )


class CapacityRemaining:
    ROUND_VALUE = SettingsUtil.get_setting(
        Constants.N2K_SETTINGS_KEY,
        Constants.CAPACITY_REMAINING,
        Constants.ROUND,
        default_value=0,
    )
