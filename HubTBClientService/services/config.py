"""
Filtering patterns for telemetry and location data in the HubCore service.
"""

telemetry_filter_patterns = [
    "marineEngine.\\d+.speed",
]

bilge_pump_power_filter_pattern = r"bilgePump\.(\d+)\.p"

location_filter_pattern = r"gnss\.(.+?)\.loc"

location_priority_sources = [
    "gpsd",
    "n2k",  # n2k internal will be prioritized over n2k external
    "cell",
]
