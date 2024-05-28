# Skyentific

Skyentific is a Python library for retrieving current weather conditions from a Davis Skyentific IP Logger.

## Features

- Retrieve current weather observations including temperature, humidity, wind speed, and more
- Automatically retry failed requests with configurable delays
- Extensive logging for diagnosing issues
- Fully type-hinted for ease of use and maintainability

## Installation

Install Skyentific using pip:

```shell
pip install skyentific
```

## Usage

Here's a basic example of how to use Skyentific to retrieve the current weather conditions:

```python
from skyentific import get_current_condition

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

## Command Line Usage

After installing the `skyentific` package, you can use the `skyentific` command line script to retrieve current weather conditions from a Skyentific IP Logger.

```shell
skyentific <host> <port>
```

- `host`: The hostname or IP address of the Skyentific IP Logger.
- `port`: The port number to connect to.

The script will output the current weather conditions in JSON format.

Example:

```shell
skyentific 192.168.1.100 22222
```

## Documentation

Full documentation is available at <https://skyentific.readthedocs.io/>.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for details on how to contribute to the project.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

Thanks to the Davis Instruments team for providing the Skyentific IP Logger and documentation.

## Support

If you have any questions, issues, or feature requests, please open an issue on GitHub.
