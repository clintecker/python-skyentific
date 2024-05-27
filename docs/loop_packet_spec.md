# WeatherLink IP LOOP Packet Documentation

A LOOP Packet is 99 bytes long. Little Endian.

## Packet Structure

### Header

| Field       | Offset | Size | Explanation                                                                                             |
|-------------|--------|------|---------------------------------------------------------------------------------------------------------|
| 'L'  | 0      | 1    | Indicates the start of a LOOP packet, always 'L' (0x4C).                                                |
| 'O'        | 1    | 1   | 0x4F |
| 'O'        | 2    | 1   | 0x4F
| 'P' / Bar Trend   | 3      | 1    | Signed byte indicating the current 3-hour barometer trend: <br>-60 = 0xC4 (Falling Rapidly) <br>-20 = 0xEC (Falling Slowly) <br>0 = 0x00 (Steady) <br>20 = 0x14 (Rising Slowly) <br>60 = 0x3C (Rising Rapidly) <br>'P' (0x50) for Rev A Firmware (no trend info). |

### Data Records

| Field                       | Offset | Size | Explanation                                                                   |
|-----------------------------|--------|------|-------------------------------------------------------------------------------|
| Packet Type                 | 4      | 1    | Indicates LOOP (0) or LOOP2 (1) packet type.                                   |
| Next Record                 | 5      | 2    | Location in the archive memory where the next data packet will be written. This can be monitored to detect when a new record is created. |
| Barometer                   | 7      | 2    | Current barometer value in 1/1000 inHg. The barometric value should be between 20 inches and 32.5 inches in Vantage Pro and between 20 inches and 32.5 inches in both Vantage Pro Vantage Pro2. Values outside these ranges will not be logged.                                    |
| Inside Temperature          | 9      | 2    | Inside temperature in 1/10°F.                                                  |
| Inside Humidity             | 11     | 1    | Inside relative humidity in %.                                                 |
| Outside Temperature         | 12     | 2    | Outside temperature in 1/10°F.                                                 |
| Wind Speed                  | 14     | 1    | Wind speed in mph.                                                             |
| 10-Minute Average Wind Speed| 15     | 1    | Average wind speed in mph over 10 minutes.                                     |
| Wind Direction              | 16     | 2    | Wind direction in degrees.                                                     |
| Extra Temperatures          | 18     | 7    | Extra temperature values (7 sensors) in whole degrees °F.                      |
| Soil Temperatures           | 25     | 4    | Soil temperature values (4 sensors) in whole degrees °F.                       |
| Leaf Temperatures           | 29     | 4    | Leaf temperature values (4 sensors) in whole degrees °F.                       |
| Outside Humidity            | 33     | 1    | Outside relative humidity in %.                                                |
| Extra Humidity              | 34     | 7    | Extra humidity values (7 sensors) in %.                                        |
| Rain Rate                   | 41     | 2    | Rain rate in clicks (0.2mm or 0.01in).                                         |
| UV Index                    | 43     | 1    | UV index value.                                                                |
| Solar Radiation             | 44     | 2    | Solar radiation in W/m².                                                       |
| Storm Rain                  | 46     | 2    | Storm rain in clicks (0.2mm or 0.01in).                                        |
| Start Date of Storm         | 48     | 2    | Start date of the storm.                                                       |
| Day Rain                    | 50     | 2    | Daily rain in clicks (0.2mm or 0.01in).                                        |
| Month Rain                  | 52     | 2    | Monthly rain in clicks (0.2mm or 0.01in).                                      |
| Year Rain                   | 54     | 2    | Yearly rain in clicks (0.2mm or 0.01in).                                       |
| Day ET                      | 56     | 2    | Daily ET in clicks (0.01in).                                                   |
| Month ET                    | 58     | 2    | Monthly ET in clicks (0.01in).                                                 |
| Year ET                     | 60     | 2    | Yearly ET in clicks (0.01in).                                                  |
| Soil Moistures              | 62     | 4    | Soil moisture values (4 sensors).                                              |
| Leaf Wetness                | 66     | 4    | Leaf wetness values (4 sensors).                                               |

### Miscellaneous

| Field                       | Offset | Size | Explanation                                                                   |
|-----------------------------|--------|------|-------------------------------------------------------------------------------|
| Transmitter Battery Status  | 86     | 1    | Transmitter battery status.                                                   |
| Console Battery Voltage     | 87     | 2    | Voltage = ((Data *300)/512)/100.0                                            |
| Forecast Icons              | 89     | 1    | Forecast icons (bit map). See below                                           |
| Forecast Rule Number        | 90     | 1    | See Forecast Rules
| Time of Sunrise             | 91     | 2    | Time of sunrise (hour* 100 + minute).                                        |
| Time of Sunset              | 93     | 2    | Time of sunset (hour * 100 + minute).                                         |
| "\n" <LF> = 0x0A            | 95     | 1    |                                                                               |
| "\r" <CR> = 0x0D            | 96     | 1    |                                                                               |
| CRC                         | 97     | 2    | Cyclic Redundancy Check.                                                      |
| Total Length                | 99     |      |                                                                               |

### Forecast Icons

Forcast Icons are in byte 89:

| Value | Bit | Forecast Icon                   |
|-------|-----|---------------------------------|
|       | 0   | Rain within 12 hours            |
|       | 1   | Cloudy                          |
|       | 2   | Mostly cloudy                   |
|       | 3   | Partly cloudy                   |
|       | 4   | Clear                           |

For example this controls the icons:

- `0b0000 0000` (0x00) - Clear
- `0b0000 0001` (0x01) - Rain within 12 hours
- `0b0000 0010` (0x02) - Cloud
- `0b0000 0100` (0x04) - Partly Cloudy
- `0b0000 1000` (0x08) - Sun
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
