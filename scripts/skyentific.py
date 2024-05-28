import argparse
import datetime
import json
import logging
import socket

from skyentific import get_current_condition
from skyentific.models import StationObservation
from skyentific.utils import connect


def configure_logging(verbose: bool, quiet: bool):
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.ERROR
    else:
        level = logging.WARNING

    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logging.Formatter.formatTime = (
        lambda self, record, datefmt: datetime.datetime.fromtimestamp(
            record.created
        ).isoformat()
    )


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve current weather conditions from a Skyentific IP Logger."
    )
    parser.add_argument(
        "host", help="The hostname or IP address of the Skyentific IP Logger."
    )
    parser.add_argument("port", type=int, help="The port number to connect to.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    parser.add_argument(
        "--quiet", action="store_true", help="Enable quiet mode (only error messages)."
    )
    args = parser.parse_args()

    configure_logging(args.verbose, args.quiet)

    try:
        sock = connect(args.host, args.port, socket.socket)
        observation = get_current_condition(sock, StationObservation.init_with_bytes)
        print(json.dumps(observation.to_dict(), indent=2))
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
