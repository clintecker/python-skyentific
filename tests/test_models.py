import copy
import datetime

from unittest.mock import Mock
from unittest import TestCase

from bitstring import BitStream

from skyentific.bar_trend import BarTrend
from skyentific.exceptions import BadCRC
from skyentific.models import (
    lunation_text,
    wind_direction_text,
    forecast_icons_text,
    StationObservation,
)

loop_packet = b"LOO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"
loop2_packet = b"LOO\x14\x01\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"
loop_packet_badCRC = b"POO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"


class TestModel(TestCase):
    def test_lunation_text(self):
        with self.assertRaises(ValueError):
            lunation_text(-1)

        assert lunation_text(0) == "New Moon (Waxing)"
        assert lunation_text(0.25) == "First Quarter (Waxing)"
        assert lunation_text(0.5) == "Full Moon"
        assert lunation_text(0.75) == "Last Quarter (Waning)"
        assert lunation_text(1) == "New Moon"

    def test_wind_direction_text(self):
        self.assertRaises(ValueError, wind_direction_text, -1)
        self.assertRaises(ValueError, wind_direction_text, 361)
        assert wind_direction_text(0) == "N"
        assert wind_direction_text(45) == "NE"
        assert wind_direction_text(90) == "E"
        assert wind_direction_text(135) == "SE"
        assert wind_direction_text(180) == "S"
        assert wind_direction_text(225) == "SW"
        assert wind_direction_text(270) == "W"
        assert wind_direction_text(315) == "NW"
        assert wind_direction_text(360) == "N"

    def test_forecast_icons_text(self):
        self.assertRaises(ValueError, forecast_icons_text, -1)
        self.assertRaises(ValueError, forecast_icons_text, 38)

        assert forecast_icons_text(0) == "Unknown"
        assert forecast_icons_text(1) == "Rain within 12 hrs"
        assert forecast_icons_text(2) == "Cloudy"
        assert forecast_icons_text(3) == "Rain within 12 hrs, Cloudy"
        assert forecast_icons_text(4) == "Mostly Cloudy"
        assert forecast_icons_text(5) == "Rain within 12 hrs, Mostly Cloudy"
        assert forecast_icons_text(6) == "Cloudy, Mostly Cloudy"

    def test_StationObservation(self):
        validate_type_stream = BitStream(loop_packet)
        validate_type_stream.pos = 32
        StationObservation.validate_packet_type(validate_type_stream)

        with self.assertRaises(ValueError):
            StationObservation.validate_packet_type(1234)

        with self.assertRaises(ValueError):
            loop2_stream = BitStream(loop2_packet)
            loop2_stream.pos = 32
            StationObservation.validate_packet_type(loop2_stream)

        StationObservation.validate_record(BitStream(loop_packet))
        with self.assertRaises(ValueError):
            StationObservation.validate_record(1234)
        with self.assertRaises(BadCRC):
            StationObservation.validate_record(BitStream(loop_packet_badCRC))
        with self.assertRaises(ValueError):
            StationObservation.validate_record(
                BitStream(b"LOO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00")
            )
        observation = StationObservation(
            bar_trend=0,
            barometer=650.1,
            inside_temperature=20.1,
            inside_humidity=23.2,
            outside_temperature=27.3,
            outside_humidity=27.8,
            wind_speed=25,
            ten_min_avg_wind_speed=25,
            wind_direction=30,
            rain_rate=200,
            console_battery_voltage=4.1,
            forecast_icons=0x05,
            forecast_rule_number=10,
            sunrise=datetime.time(6, 30, 0),
            sunset=datetime.time(20, 1, 0),
            observation_made_at=datetime.datetime(2024, 5, 27, 17, 14, 13, 234193),
            identifier=101,
        )
        assert observation.bar_trend == 0
        assert observation.wind_direction_text() == "NNE"
        assert observation.forecast_icons_text() == "Rain within 12 hrs, Mostly Cloudy"
        assert observation.sunrise == datetime.time(6, 30, 0)
        assert observation.sunset == datetime.time(20, 1, 0)
        assert observation.identifier == 101
        assert observation.console_battery_voltage == 4.1
        assert (
            observation.forecast_text()
            == "Partly cloudy with little temperature change."
        )
        assert observation.to_dict() == {
            "bar_trend": 0,
            "barometer": 650.1,
            "inside_temperature": 20.1,
            "inside_humidity": 23.2,
            "outside_temperature": 27.3,
            "outside_humidity": 27.8,
            "wind_speed": 25,
            "ten_min_avg_wind_speed": 25,
            "wind_direction": 30,
            "wind_direction_text": "NNE",
            "rain_rate": 200,
            "console_battery_voltage": 4.1,
            "forecast_icons": 5,
            "forecast_icons_text": "Rain within 12 hrs, Mostly Cloudy",
            "forecast_rule_number": 10,
            "forecast_text": "Partly cloudy with little temperature change.",
            "sunrise": "06:30:00",
            "sunset": "20:01:00",
            "observation_made_at": "2024-05-27T17:14:13.234193",
            "identifier": 101,
        }
        observation_from_bytes = StationObservation.init_with_bytes(
            loop_packet,
            101,
            observation_made_at=datetime.datetime(2024, 5, 27, 17, 34, 9, 120265),
        ).to_dict()
        self.assertEqual(
            observation_from_bytes,
            {
                "bar_trend": BarTrend.RISING_SLOWLY,
                "barometer": 29.769,
                "inside_temperature": 79.8,
                "inside_humidity": 15.0,
                "outside_temperature": 65.0,
                "outside_humidity": 27.0,
                "wind_speed": 2,
                "ten_min_avg_wind_speed": 3,
                "wind_direction": 140,
                "wind_direction_text": "SE",
                "rain_rate": 0,
                "console_battery_voltage": 4.81640625,
                "forecast_icons": 3,
                "forecast_icons_text": "Rain within 12 hrs, Cloudy",
                "forecast_rule_number": 192,
                "forecast_text": "Mostly cloudy and cooler. Precipitation possible within 12 hours possibly heavy at times. Windy.",
                "sunrise": "05:39:00",
                "sunset": "20:19:00",
                "observation_made_at": "2024-05-27T17:34:09.120265",
                "identifier": 101,
            },
        )
