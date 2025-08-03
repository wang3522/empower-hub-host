from datetime import datetime, time, timezone
import serial
import time
from .constants import Constants

class GPSParser:
    """
    A parser for GPS data from the GPSACP protocol.
    """

    def __init__(self, serial_port: str):
        self.serial_port = serial_port
        self.gnss_connection = None

    def connect_serial_and_start_gnss(self):
        self.gnss_connection = serial.Serial(self.serial_port, 115200, timeout=1)
        self.gnss_connection.flush()
        self.gnss_connection.write("AT$GPSP=1\r\n".encode())
        _ = self.gnss_connection.read_until(b'OK\r\n')

    def gpsacp_to_epoch(self, time_str, date_str):
        hours = int(time_str[0:2])
        minutes = int(time_str[2:4])
        seconds = float(time_str[4:])
        day = int(date_str[0:2])
        month = int(date_str[2:4])
        year = int(date_str[4:6]) + 2000  # assumes 21st century
        dt = datetime(
            year,
            month,
            day,
            hours,
            minutes,
            int(seconds),
            int((seconds % 1) * 1_000_000),
            tzinfo=timezone.utc
        )
        epoch_milliseconds = int(dt.timestamp() * 1000)
        return epoch_milliseconds

    def get_latitude(self, lat_raw):
        lat_deg = int(lat_raw[0:2])
        lat_min = float(lat_raw[2:-1])
        lat_dir = lat_raw[-1]
        latitude = lat_deg + lat_min / 60.0
        if lat_dir == "S":
            latitude = -latitude
        return latitude

    def get_longitude(self, lon_raw):
        lon_deg = int(lon_raw[0:3])
        lon_min = float(lon_raw[3:-1])
        lon_dir = lon_raw[-1]
        longitude = lon_deg + lon_min / 60.0
        if lon_dir == "W":
            longitude = -longitude
        return longitude

    def get_hdop(self, hdop_str):
        return float(hdop_str)

    def get_hdop_error_meters(self, hdop_str):
        hdop = float(hdop_str)
        return hdop * 5

    def get_fix_type(self, fix_type_str):
        return int(fix_type_str)

    def get_speed_ms(self, speed_kmh_str):
        speed_kmh = float(speed_kmh_str)
        return speed_kmh / 3.6

    def get_num_valid_sats(self, num_sats_str):
        return int(num_sats_str)

    def parse_gpsacp(self, response):
        response = response.strip().decode()
        print(f"Parsing GPSACP response: |{response}|")
        if not response.startswith("$GPSACP:"):
            raise ValueError("Invalid GPSACP response")
        elif response == "$GPSACP: ,,,,,1,,,,,,":
            raise ValueError("No valid GPS data in response")

        fields = response.split(":")[1].strip().split(",")
        if len(fields) < 12:
            raise ValueError("Incomplete GPSACP response")

        return {
            Constants.ts: self.gpsacp_to_epoch(fields[0], fields[9]),
            Constants.LAT: self.get_latitude(fields[1]),
            Constants.LONG: self.get_longitude(fields[2]),
            "error": {
                "x": self.get_hdop_error_meters(fields[3]),
                "y": self.get_hdop_error_meters(fields[3]),
            },
            "mode": self.get_fix_type(fields[5]),
            Constants.sp: self.get_speed_ms(fields[7]),
            "sats_valid": self.get_num_valid_sats(fields[10]) + self.get_num_valid_sats(fields[11]),
        }

    def get_location(self):
        """
        Connects to the GPS device and retrieves the current location.
        :return: A dictionary with latitude, longitude, speed, and timestamp.
        """
        try:
            self.gnss_connection.write("AT$GPSACP\r\n".encode())
            response_raw = self.gnss_connection.read(self.gnss_connection.in_waiting)
            response_raw = response_raw.replace(b'OK', b'').replace(b'AT$GPSACP', b''
                ).replace(b'\r\n', b'')
            return self.parse_gpsacp(response_raw)
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Temporary Constants for testing
    class Constants:
        TS = "ts"
        LAT = "lat"
        LONG = "long"
        sp = "sp"

    SERIAL_PORT = "/dev/ttyUSB1"
    gps_parser = GPSParser(SERIAL_PORT)

    try:
        print("Starting while loop to read GPS data...")
        gps_parser.connect_serial_and_start_gnss()
        print(f"Connected to GPS on {SERIAL_PORT}. Reading data...")
    except Exception as e:
        print(f"Error connecting to GPS: {e}")

    while True:
        try:
            print("Reading GPS data...")
            gps_data = gps_parser.get_location()
            print(gps_data)
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting GPS data reading loop.")
            break
        except Exception as e:
            print(f"Error reading GPS data: {e}")

    # test_response = "$GPSACP: 191913.000,4527.0142N,12236.5625W,1.0,56.5,3,264.5,0.0,0.0,230725,06,05"
    # print(gps_parser.parse_gpsacp(test_response))