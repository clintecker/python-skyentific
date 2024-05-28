# Standard Library
import datetime
import logging
import random
from typing import Dict, List, Optional, Literal

# Third Party Code
from bitstring import BitStream
from dateutil.tz import tzlocal

# Supercell Code
from .exceptions import BadCRC
from .utils import crc16, CRC16_TABLE, make_time
from .bar_trend import BarTrend

logger = logging.getLogger(__name__)

FORECAST_RULES = [
    "Mostly clear and cooler.",
    "Mostly clear with little temperature change.",
    "Mostly clear for 12 hours with little temperature change.",
    "Mostly clear for 12 to 24 hours and cooler.",
    "Mostly clear with little temperature change.",
    "Partly cloudy and cooler.",
    "Partly cloudy with little temperature change.",
    "Partly cloudy with little temperature change.",
    "Mostly clear and warmer.",
    "Partly cloudy with little temperature change.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 24 to 48 hours.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds with little temperature change. Precipitation possible within 24 hours.",
    "Mostly clear with little temperature change.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds with little temperature change. Precipitation possible within 12 hours.",
    "Mostly clear with little temperature change.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 24 hours.",
    "Mostly clear and warmer. Increasing winds.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.",
    "Mostly clear and warmer. Increasing winds.",
    "Increasing clouds and warmer.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.",
    "Mostly clear and warmer. Increasing winds.",
    "Increasing clouds and warmer.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 hours. Increasing winds.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly clear and warmer. Precipitation possible within 48 hours.",
    "Mostly clear and warmer.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds with little temperature change. Precipitation possible within 24 to 48 hours.",
    "Increasing clouds with little temperature change.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 6 to 12 hours.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 6 to 12 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 to 24 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation possible within 12 hours.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and warmer. Precipitation likley.",
    "Clearing and cooler. Precipitation ending within 6 hours.",
    "Partly cloudy with little temperature change.",
    "Clearing and cooler. Precipitation ending within 6 hours.",
    "Mostly clear with little temperature change.",
    "Clearing and cooler. Precipitation ending within 6 hours.",
    "Partly cloudy and cooler.",
    "Partly cloudy with little temperature change.",
    "Mostly clear and cooler.",
    "Clearing and cooler. Precipitation ending within 6 hours.",
    "Mostly clear with little temperature change.",
    "Clearing and cooler. Precipitation ending within 6 hours.",
    "Mostly clear and cooler.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds with little temperature change. Precipitation possible within 24 hours.",
    "Mostly cloudy and cooler. Precipitation continuing.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation likely.",
    "Mostly cloudy with little temperature change. Precipitation continuing.",
    "Mostly cloudy with little temperature change. Precipitation likely.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible and windy within 6 hours.",
    "Increasing clouds with little temperature change. Precipitation possible and windy within 6 hours.",
    "Mostly cloudy and cooler. Precipitation continuing. Increasing winds.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation likely. Increasing winds.",
    "Mostly cloudy with little temperature change. Precipitation continuing. Increasing winds.",
    "Mostly cloudy with little temperature change. Precipitation likely. Increasing winds.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 12 to 24 hours possible wind shift to the W NW or N.",
    "Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours possible wind "
    "shift to the W NW or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W NW or N.",
    "Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to "
    "the W NW or N.",
    "Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W NW or N.",
    "Mostly cloudy and cooler. Possible wind shift to the W NW or N.",
    "Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W "
    "NW or N.",
    "Mostly cloudy with little temperature change. Possible wind shift to the W NW or N.",
    "Mostly cloudy and cooler. Precipitation ending within 12 hours possible wind shift to the W NW or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation possible within 24 hours possible wind shift to the W NW or N.",
    "Mostly cloudy with little temperature change. Precipitation ending within 12 hours possible wind shift to the W "
    "NW or N.",
    "Mostly cloudy with little temperature change. Precipitation possible within 24 hours possible wind shift to the "
    "W NW or N.",
    "Clearing cooler and windy. Precipitation ending within 6 hours.",
    "Clearing cooler and windy.",
    "Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy with possible wind shift to the W NW or N.",
    "Mostly cloudy and cooler. Windy with possible wind shift to the W NW or N.",
    "Clearing cooler and windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy with little temperature change. Precipitation possible within 12 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 12 hours possibly heavy at times. Windy.",
    "Mostly cloudy and cooler. Precipitation ending within 6 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation possible within 12 hours. Windy.",
    "Mostly cloudy and cooler. Precipitation ending in 12 to 24 hours.",
    "Mostly cloudy and cooler.",
    "Mostly cloudy and cooler. Precipitation continuing possible heavy at times. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours. Windy.",
    "Mostly cloudy with little temperature change. Precipitation continuing possibly heavy at times. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds with little temperature change. Precipitation possible within 12 hours possibly heavy at "
    "times. Windy.",
    "Mostly cloudy and cooler. Windy.",
    "Mostly cloudy and cooler. Precipitation continuing possibly heavy at times. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation likely possibly heavy at times. Windy.",
    "Mostly cloudy with little temperature change. Precipitation continuing possibly heavy at times. Windy.",
    "Mostly cloudy with little temperature change. Precipitation likely possibly heavy at times. Windy.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 6 hours. Windy.",
    "Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy",
    "Increasing clouds and cooler. Precipitation continuing. Windy with possible wind shift to the W NW or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W NW or N.",
    "Mostly cloudy with little temperature change. Precipitation continuing. Windy with possible wind shift to the W "
    "NW or N.",
    "Mostly cloudy with little temperature change. Precipitation likely. Windy with possible wind shift to the W NW "
    "or N.",
    "Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W NW "
    "or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 6 hours possible wind shift to the W NW or N.",
    "Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible "
    "wind shift to the W NW or N.",
    "Increasing clouds with little temperature change. Precipitation possible within 6 hours possible wind shift to "
    "the W NW or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 6 hours. Windy with possible wind shift to the W NW "
    "or N.",
    "Increasing clouds with little temperature change. Precipitation possible within 6 hours. Windy with possible "
    "wind shift to the W NW or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Increasing clouds and cooler. Precipitation possible within 12 to 24 hours. Windy with possible wind shift to "
    "the W NW or N.",
    "Increasing clouds with little temperature change. Precipitation possible within 12 to 24 hours. Windy with "
    "possible wind shift to the W NW or N.",
    "Mostly cloudy and cooler. Precipitation possibly heavy at times and ending within 12 hours. Windy with possible "
    "wind shift to the W NW or N.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation possible within 6 to 12 hours possibly heavy at times. Windy with "
    "possible wind shift to the W NW or N.",
    "Mostly cloudy with little temperature change. Precipitation ending within 12 hours. Windy with possible wind "
    "shift to the W NW or N.",
    "Mostly cloudy with little temperature change. Precipitation possible within 6 to 12 hours possibly heavy at "
    "times. Windy with possible wind shift to the W NW or N.",
    "Mostly cloudy and cooler. Precipitation continuing.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation likely. Windy with possible wind shift to the W NW or N.",
    "Mostly cloudy with little temperature change. Precipitation continuing.",
    "Mostly cloudy with little temperature change. Precipitation likely.",
    "Partly cloudy with little temperature change.",
    "Mostly clear with little temperature change.",
    "Mostly cloudy and cooler. Precipitation possible within 12 hours possibly heavy at times. Windy.",
    "FORECAST REQUIRES 3 HOURS OF RECENT DATA",
    "Mostly clear and cooler.",
    "Mostly clear and cooler.",
    "Mostly clear and cooler.",
    "Unknown forecast rule.",
]

LOOP_RECORD_SIZE_BYTES = 99
LOOP_RECORD_SIZE_BITS = LOOP_RECORD_SIZE_BYTES * 8

REVISION_A = "A"
REVISION_B = "B"

LOOP_HEADER = b"LOOP"

LOOP2_PACKET_TYPE = 1
LOOP_PACKET_TYPE = 0

LUNATION_LOOKUP = {
    0.05: "New Moon",
    0.15: "Crescent",
    0.25: "First Quarter",
    0.45: "Gibbous",
    0.55: "Full Moon",
    0.65: "Gibbous",
    0.85: "Last Quarter",
    0.95: "Crescent",
    1.00: "New Moon",
}


WIND_DIRECTION_LOOKUP = {
    10: "N",
    35: "NNE",
    55: "NE",
    80: "NEE",
    110: "E",
    125: "SEE",
    145: "SE",
    170: "SSE",
    190: "S",
    215: "SSW",
    235: "SW",
    260: "SWW",
    280: "W",
    305: "NWW",
    325: "NW",
    350: "NNW",
    360: "N",
}


def lunation_text(lunation: float) -> str:
    """Converts the lunation value to a string."""
    if lunation < 0 or lunation > 1.0:
        raise ValueError("Lunation must be between 0.0 - 1.0")

    if lunation < 0.5:
        direction = "Waxing"
    elif lunation == 0.5 or lunation == 1.0:
        direction = ""
    else:
        direction = "Waning"

    lunation_text = "Unknown Lunation"

    for lunation_value, lunation_text in LUNATION_LOOKUP.items():
        if lunation > lunation_value:
            continue
        break

    if direction == "":
        return "{text}".format(text=lunation_text)
    return "{text} ({direction})".format(text=lunation_text, direction=direction)


def wind_direction_text(wind_direction: int) -> str:
    """Converts the wind direction value to text."""
    if wind_direction < 0 or wind_direction > 360:
        raise ValueError(
            "Wind direction (%s) must be between 0 - 360" % (wind_direction)
        )

    wind_direction_text = "Unknown Wind Direction"

    for wind_direction_value, wind_direction_text in WIND_DIRECTION_LOOKUP.items():
        if wind_direction >= wind_direction_value:
            continue
        break
    return wind_direction_text


FORECAST_ICONS_LOOKUP = {
    0: "Rain within 12 hrs",
    1: "Cloudy",
    2: "Mostly Cloudy",
    3: "Partly Cloudy",
    4: "Snow",
}


def forecast_icons_text(forecast_icons: int) -> List[str]:
    """
    | Value | Bit | Forecast Icon                   |
    |-------|-----|---------------------------------|
    |       | 0   | Rain within 12 hours            |
    |       | 1   | Cloud                           |
    |       | 2   | Partly Cloudy                   |
    |       | 3   | Sun                             |
    |       | 4   | Snow                            |

    For example this controls the icons:

    - `0b0000 0000` (0x00) - Unknown?
    - `0b0000 0001` (0x01) - Rain within 12 hours
    - `0b0000 0010` (0x02) - Cloud
    - `0b0000 0100` (0x04) - Partly Cloudy
    - `0b0000 1000` (0x08) - Sunny
    - `0b0001 0000` (0x10) - Snow

    These then combine to create complex forecasts:

    - `0b0000 1000` (0x08) - Sun = Mostly Clear
    - `0b0000 0110` (0x06) - Partial Sun + Cloud = Partly Cloudy
    - `0x0000 0010` (0x02) - Cloud = Mostly Cloudy
    - `0x0000 0011` (0x03) - Rain + Cloud = Mostly Cloudy, Rain within 12 hours
    - `0x0001 0010` (0x12) - Cloud + Snow = Mostly Cloudy, Snow within 12 hours
    - `0x0001 0011` (0x13) - Cloud + Rain + Snow = Mostly Cloud, Rain or Snow within 12 hours
    - `0x0000 0111` (0x07) - Partial Sun + Cloud + Rain = Partly Cloudy, Rain within 12 hours
    - `0x0001 0110` (0x16) - Partial Sun + Cloud + Snow = Partly Cloudy, Snow within 12 hours
    - `0x0001 0111` (0x17) - Partial Sun + Cloud + Rain + Snow = Partly Cloudy, Snow or Rain within 12 hours
    """
    if forecast_icons < 0 or forecast_icons > 31:
        raise ValueError("Forecast icons must be between 0 - 31.")

    logger.debug(f"Forecast Icons For: {forecast_icons}, binary: {bin(forecast_icons)}")

    forecast_icons_text = []
    if forecast_icons == 0:
        return "Unknown"
    else:
        for i in range(5):
            if forecast_icons & (1 << i):
                logger.debug(f"Forecast Icon: {i} -> {FORECAST_ICONS_LOOKUP[i]}")
                forecast_icons_text.append(FORECAST_ICONS_LOOKUP[i])
            else:
                logger.debug(f"Forecast Icon: {i} -> Not Set")

    return ", ".join(forecast_icons_text)


class StationObservation(object):
    """A station observation"""

    bar_trend: int
    barometer: float
    inside_temperature: float
    inside_humidity: float
    outside_temperature: float
    outside_humidity: float
    wind_speed: int
    ten_min_avg_wind_speed: int
    wind_direction: int
    rain_rate: int
    console_battery_voltage: float
    forecast_icons: int
    forecast_rule_number: int
    sunrise: datetime.time
    sunset: datetime.time
    observation_made_at: datetime.datetime
    identitier: int

    def __init__(
        self,
        bar_trend: BarTrend,
        barometer: float,
        inside_temperature: float,
        inside_humidity: float,
        outside_temperature: float,
        outside_humidity: float,
        wind_speed: int,
        ten_min_avg_wind_speed: int,
        wind_direction: int,
        rain_rate: int,
        console_battery_voltage: float,
        forecast_icons: int,
        forecast_rule_number: int,
        sunrise: datetime.time,
        sunset: datetime.time,
        observation_made_at: Optional[datetime.datetime] = None,
        identifier: Optional[int] = None,
    ) -> None:
        self.bar_trend = bar_trend
        self.barometer = float(barometer)
        self.inside_temperature = float(inside_temperature)
        self.inside_humidity = float(inside_humidity)
        self.outside_temperature = float(outside_temperature)
        self.outside_humidity = float(outside_humidity)
        self.wind_speed = int(wind_speed)
        self.ten_min_avg_wind_speed = int(ten_min_avg_wind_speed)
        self.wind_direction = int(wind_direction)
        self.rain_rate = int(rain_rate)
        self.console_battery_voltage = float(console_battery_voltage)
        self.forecast_icons = int(forecast_icons)
        self.forecast_rule_number = int(forecast_rule_number)
        self.sunrise = sunrise
        self.sunset = sunset
        self.observation_made_at = (
            observation_made_at or datetime.datetime.now(tzlocal())
        ).isoformat()
        self.identifier = identifier or random.getrandbits(32)

    def wind_direction_text(self) -> str:
        """Produces a string description of the wind direction."""
        return wind_direction_text(self.wind_direction)

    def forecast_icons_text(self) -> List[str]:
        return forecast_icons_text(self.forecast_icons)

    def forecast_text(self) -> str:
        """Returns the string version of the forecast rule."""
        return FORECAST_RULES[self.forecast_rule_number]

    def to_dict(self) -> Dict:
        """A dictionary representation of the observation."""
        return {
            "bar_trend": self.bar_trend,
            "barometer": self.barometer,
            "inside_temperature": self.inside_temperature,
            "inside_humidity": self.inside_humidity,
            "outside_temperature": self.outside_temperature,
            "outside_humidity": self.outside_humidity,
            "wind_speed": self.wind_speed,
            "ten_min_avg_wind_speed": self.ten_min_avg_wind_speed,
            "wind_direction": self.wind_direction,
            "wind_direction_text": self.wind_direction_text(),
            "rain_rate": self.rain_rate,
            "console_battery_voltage": self.console_battery_voltage,
            "forecast_icons": self.forecast_icons,
            "forecast_icons_text": self.forecast_icons_text(),
            "forecast_rule_number": self.forecast_rule_number,
            "forecast_text": self.forecast_text(),
            "sunrise": self.sunrise.isoformat(),
            "sunset": self.sunset.isoformat(),
            "observation_made_at": self.observation_made_at,
            "identifier": self.identifier,
        }

    @classmethod
    def validate_record(
        cls, record_bitstream: BitStream, validate_crc: bool = True
    ) -> None:
        """Validates a record."""
        if type(record_bitstream) is not BitStream:
            raise ValueError("Record must be a BitStream.")
        if len(record_bitstream) != LOOP_RECORD_SIZE_BITS:
            raise ValueError(
                "Records should be %d bits in length. It is %d"
                % (LOOP_RECORD_SIZE_BITS, len(record_bitstream))
            )
        if validate_crc and crc16(record_bitstream) != 0:
            raise BadCRC()

    @classmethod
    def validate_packet_type(cls, record_bitstream: BitStream) -> None:
        """Validates the packet type."""
        if type(record_bitstream) is not BitStream:
            raise ValueError("Record must be a BitStream.")
        packet_type_value = record_bitstream.read(8).int
        logger.debug(f"Packet Type Value: {packet_type_value}")
        if packet_type_value == LOOP2_PACKET_TYPE:
            raise ValueError("LOOP2 Packet Not Supported")

    @classmethod
    def init_with_bytes(
        cls,
        record_bytes: bytes,
        identifier: Optional[int] = None,
        observation_made_at: Optional[datetime.datetime] = None,
    ):
        """Creates a new Station Observation from record of bytes."""
        record_bitstream = BitStream(record_bytes)
        cls.validate_record(record_bitstream, False)
        # Set to position four
        record_bitstream.pos = 24
        # Awkwardly positioned bar trend
        bar_trend = BarTrend(record_bitstream.read(8).intle)
        cls.validate_packet_type(record_bitstream)
        # Skip 2 bytes
        record_bitstream.read(16)

        barometer = record_bitstream.read(16).uintle / 1000.0
        inside_temperature = record_bitstream.read(16).intle / 10.0
        inside_humidity = record_bitstream.read(8).uintle
        outside_temperature = record_bitstream.read(16).intle / 10.0
        wind_speed = record_bitstream.read(8).uintle
        ten_min_avg_wind_speed = record_bitstream.read(8).uintle
        wind_direction = record_bitstream.read(
            16
        ).uintle  # 0º = None, 90º = E, 180 = S, 270 = W, 360 = N

        # Skip "extra temperatures"
        record_bitstream.read(
            56
        )  # Each byte is a one extra temperature value in whole degrees F
        # with # an offset  of 90 degrees. 0 = -90, 100 = 10, 169 = 79
        # Skip soil temperatures
        record_bitstream.read(32)
        # Skip leaf temperatures
        record_bitstream.read(32)

        outside_humidity = record_bitstream.read(8).uintle

        # Skip extra humidities
        record_bitstream.read(56)

        rain_rate = record_bitstream.read(16).uintle

        # ultraviolet_index
        record_bitstream.read(8)

        # solar_radiation
        record_bitstream.read(16)

        # storm_rain
        record_bitstream.read(16)

        # start_date_of_storm
        record_bitstream.read(16)

        # day_rain
        record_bitstream.read(16)

        # month_rain
        record_bitstream.read(16)

        # year_rain
        record_bitstream.read(16)

        # day_et
        record_bitstream.read(16)

        # month_et
        record_bitstream.read(16)

        # year_et
        record_bitstream.read(16)

        # Skip extra soil moistures
        record_bitstream.read(32)
        # Skip extra leaf wetnesses
        record_bitstream.read(32)

        # inside_alarms
        record_bitstream.read(8)

        # rain_alarms
        record_bitstream.read(8)

        # outside_alarms
        record_bitstream.read(16)

        # Skip extra temp/humidity alarms
        record_bitstream.read(64)
        # Skip extra soil leaf alarms
        record_bitstream.read(32)

        # Skip tx battery status
        record_bitstream.read(8)

        console_battery_voltage = (
            (record_bitstream.read(16).uintle * 300.0) / 512.0
        ) / 100.0
        forecast_icons = record_bitstream.read(8).uintle
        forecast_rule_number = record_bitstream.read(8).uintle
        sunrise = make_time(record_bitstream.read(16).uintle)
        sunset = make_time(record_bitstream.read(16).uintle)

        return cls(
            bar_trend=bar_trend,
            barometer=barometer,
            inside_temperature=inside_temperature,
            inside_humidity=inside_humidity,
            outside_temperature=outside_temperature,
            outside_humidity=outside_humidity,
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            ten_min_avg_wind_speed=ten_min_avg_wind_speed,
            rain_rate=rain_rate,
            console_battery_voltage=console_battery_voltage,
            forecast_icons=forecast_icons,
            forecast_rule_number=forecast_rule_number,
            sunrise=sunrise,
            sunset=sunset,
            identifier=identifier,
            observation_made_at=observation_made_at,
        )
