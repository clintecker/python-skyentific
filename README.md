# WeatherLink

WeatherLink is a Python library for retrieving current weather conditions from a Davis Weatherlink IP Logger.

## Features

- Retrieve current weather observations including temperature, humidity, wind speed, and more
- Automatically retry failed requests with configurable delays
- Extensive logging for diagnosing issues
- Fully type-hinted for ease of use and maintainability

## Installation

Install WeatherLink using pip:

```shell
pip install weatherlink
```

## Usage

Here's a basic example of how to use WeatherLink to retrieve the current weather conditions:

```python
from weatherlink import get_current_condition

host = '192.168.1.100'
port = 22222

try:
    observation = get_current_condition(host, port)
    print(f"Temperature: {observation.outside_temperature}°C")
    print(f"Humidity: {observation.outside_humidity}%")
    print(f"Wind Speed: {observation.wind_speed} km/h")
except Exception as e:
    print(f"Error: {e}")
```

For more detailed usage instructions and examples, please see the documentation.

## Documentation

Full documentation is available at <https://weatherlink.readthedocs.io/>.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for details on how to contribute to the project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Thanks to the Davis Instruments team for providing the Weatherlink IP Logger and documentation.

## Support

If you have any questions, issues, or feature requests, please open an issue on GitHub.
