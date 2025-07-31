class GeoPoint:
    """
    Represents a geographical point with latitude and longitude.
    Attributes:
        latitude (float): The latitude of the geographical point.
        longitude (float): The longitude of the geographical point.
    """
    latitude: float
    longitude: float

    def __init__(self, latitude: float, longitude: float):
        """
        Initializes a GeoPoint with the given latitude and longitude.
        Args:
            latitude (float): The latitude of the geographical point.
            longitude (float): The longitude of the geographical point.
        """
        self.latitude = latitude
        self.longitude = longitude


class Geofence:
    """
    Represents a geofence with a center point and a radius.
    Attributes:
        center (GeoPoint): The center point of the geofence.
        radius (float): The radius of the geofence in meters.
    """
    center: GeoPoint
    radius: float

    def __init__(self, center: GeoPoint, radius: float):
        """
        Initializes a Geofence with the given center point and radius.
        Args:
            center (GeoPoint): The center point of the geofence.
            radius (float): The radius of the geofence in meters.
        """
        self.center = center
        self.radius = radius
