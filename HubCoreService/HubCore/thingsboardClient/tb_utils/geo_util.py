import math

class GeoUtil:
    EARTH_RADIUS = 6371000  # in meters

    @staticmethod
    def calculate_distance(
        longitude1_degrees, latitude1_degrees, longitude2_degrees, latitude2_degrees
    ):
        """
        Calculate the distance between two Longitude/Latitude points and returns the distance in meters.
        """
        lat1_radians = math.radians(latitude1_degrees)
        lat2_radians = math.radians(latitude2_degrees)

        delta_lat_radians = math.radians(latitude2_degrees - latitude1_degrees)
        delta_long_radians = math.radians(longitude2_degrees - longitude1_degrees)

        a = (
            math.sin(delta_lat_radians / 2) ** 2
            + math.cos(lat1_radians)
            * math.cos(lat2_radians)
            * math.sin(delta_long_radians / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        distance = round(GeoUtil.EARTH_RADIUS * c, 2)

        return distance

    @staticmethod
    def validate_coordinates(longitude_degrees, latitude_degrees):
        """
        Validate if the values provided are valid degrees for longitude and latitude.
        """
        if longitude_degrees is None or latitude_degrees is None:
            return False

        return -90 <= latitude_degrees <= 90 and -180 <= longitude_degrees <= 180