"""
Tools for retrieving the current conditions from a Davis Weatherlink IP Logger
"""

# Standard Library
import logging
import socket
import time

# Weatherlink Code
from .exceptions import BadCRC, NotAcknowledged, UnknownResponseCode
from .models import StationObservation
from .utils import receive_data, request

LOOP_COMMAND = b"LOOP %d\n"
LOOP_RECORD_SIZE_BYTES = 99
LOOP_RECORD_SIZE_BITS = LOOP_RECORD_SIZE_BYTES * 8

logger = logging.getLogger(__name__)


def get_current(sock: socket.socket) -> bytes:
    """
    Gets the current readings on the device.

    Parameters:
    - host (str): The IP address or hostname of the device.
    - port (int): The port number to connect to.

    Returns:
    - bytes: The current readings data.

    Raises:
    - BadCRC: If the loop command fails due to a bad CRC.
    - NotAcknowledged: If the loop command fails to be acknowledged.
    - UnknownResponseCode: If the loop command receives an unknown response code.
    - socket.timeout: If a socket timeout occurs while issuing the loop command.
    """
    loop_data = b""
    logger.debug("Attempting to get current conditions.")
    try:
        try:
            request(sock, LOOP_COMMAND % 1)
            logger.debug("Loop command issued successfully.")
        except (BadCRC, NotAcknowledged, UnknownResponseCode) as e:
            logger.exception("Could not issue loop command: %s", str(e))
            raise
        while len(loop_data) != LOOP_RECORD_SIZE_BYTES:
            data = receive_data(sock)
            loop_data += data
            logger.debug(
                f"Data received: {len(data)} bytes, loop data is {len(loop_data)} of {LOOP_RECORD_SIZE_BYTES} bytes."
            )
        logger.info("Loop data received successfully.")
    except socket.error as socket_error:
        logger.exception(
            f"Could not issue loop command due to socket error: ", str(socket_error)
        )
        raise NotAcknowledged()
    finally:
        sock.close()
    return loop_data


def get_current_condition(sock: socket.socket) -> StationObservation:
    """Obtains the current conditions."""
    try:
        current_bytes = get_current(sock)
    except (BadCRC, NotAcknowledged, UnknownResponseCode):
        # Wait a little and try again.
        time.sleep(0.1)
        try:
            current_bytes = get_current(sock)
        except (BadCRC, NotAcknowledged, UnknownResponseCode):
            # Wait twice as long and try again.
            time.sleep(1.0)
            try:
                current_bytes = get_current(sock)
            except (BadCRC, NotAcknowledged, UnknownResponseCode):
                # Ok just give up.
                raise
    return StationObservation.init_with_bytes(current_bytes)
