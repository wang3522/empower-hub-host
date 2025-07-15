"""
Thingsboard Client
Holds the constants used in the Thingsboard client.
"""

class Constants:
    """
    Constants for Thingsboard Client.
    """
    state = "s"
    ts = "ts"
    CONFIG_KEY = "configuration"
    CONFIG_CHECKSUM_KEY = "configuration.checksum"
    LOCATION_CONSENT_ENABLED_KEY = "locationConsentEnabled"
    GEOFENCE_ENABLED_KEY = "geofenceEnabled"
    GEOFENCE_KEY = "geofence"
    TB_ACCESS_TOKEN_PATH = "/data/tb_access_token"
    SN_PATH = "/data/factory/serial_number"
    TB_CONSENTS_PATH = "/data/tb_consents/"
    CURRENT_LOCATION_FILE = "/data/current_location.json"
    center = "center"
    radius = "radius"
    longitude = "longitude"
    latitude = "latitude"
