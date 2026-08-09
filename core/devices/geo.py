from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from math import atan2, cos, radians, sin, sqrt
from typing import Optional
from config.settings import Settings

@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float
    country: str
    region: str
    timezone: str

@dataclass(frozen=True)
class TravelSignal:
    distance_km: float
    elapsed_hours: float
    estimated_speed_kmh: float
    max_speed_kmh: float
    impossible_travel: bool

class GeoManager:
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, settings: Settings):
        self.settings = settings

    @staticmethod
    def normalize_country(country: str) -> str:
        return country.strip().lower()

    @staticmethod
    def normalize_region(region: str) -> str:
        return region.strip().lower()

    @staticmethod
    def normalize_timezone(timezone_name: str) -> str:
        return timezone_name.strip().lower()

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float,) -> None:
        if not -90.0 <= latitude <= 90.0:
            raise ValueError("Latitude must be between -90 and 90.")

        if not -180.0 <= longitude <= 180.0:
            raise ValueError("Longitude must be between -180 and 180.")

    @staticmethod
    def validate_timestamp(timestamp: datetime) -> None:
        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")

    def calculate_distance(self, previous_lat: float, previous_lon: float, current_lat: float, current_lon: float,) -> float:
        self.validate_coordinates(previous_lat, previous_lon,)
        self.validate_coordinates(current_lat, current_lon,)
        lat1 = radians(previous_lat)
        lon1 = radians(previous_lon)
        lat2 = radians(current_lat)
        lon2 = radians(current_lon)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2)
        a = min(1.0, max(0.0, a))
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return self.EARTH_RADIUS_KM * c

    def analyze_travel(self, previous_location: Location, current_location: Location, previous_timestamp: datetime, current_timestamp: datetime,) -> TravelSignal:
        self.validate_timestamp(previous_timestamp)
        self.validate_timestamp(current_timestamp)

        if current_timestamp < previous_timestamp:
            raise ValueError("Current timestamp cannot be earlier than previous timestamp.")

        distance = self.calculate_distance(
            previous_location.latitude,
            previous_location.longitude,
            current_location.latitude,
            current_location.longitude,
        )

        elapsed_seconds = (current_timestamp - previous_timestamp).total_seconds()
        elapsed_hours = elapsed_seconds / 3600.0

        if elapsed_hours <= 0:
            estimated_speed = 0.0
        else:
            estimated_speed = distance / elapsed_hours

        max_speed = float(
            getattr(
                self.settings,
                "max_travel_speed_kmh",
                900.0,
            )
        )

        impossible = (elapsed_hours > 0 and estimated_speed > max_speed)

        return TravelSignal(
            distance_km=round(distance, 3),
            elapsed_hours=round(elapsed_hours, 6),
            estimated_speed_kmh=round(estimated_speed, 3),
            max_speed_kmh=max_speed,
            impossible_travel=impossible,
        )

    def is_impossible_travel(self, previous_location: Location, current_location: Location, previous_timestamp: datetime, current_timestamp: datetime) -> bool:
        signal = self.analyze_travel(
            previous_location=previous_location,
            current_location=current_location,
            previous_timestamp=previous_timestamp,
            current_timestamp=current_timestamp,
        )

        return signal.impossible_travel

    def build_location_signal(self, location: Optional[Location],) -> Optional[dict[str, str | float]]:
        if location is None:
            return None

        self.validate_coordinates(
            location.latitude,
            location.longitude,
        )

        return {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "country": self.normalize_country(location.country),
            "region": self.normalize_region(location.region),
            "timezone": self.normalize_timezone(location.timezone),
        }

__all__ = [
    "Location",
    "TravelSignal",
    "GeoManager",
]