"""
Tools for retrieving the current conditions from a Davis Skyentific IP Logger
"""

# Standard Library
import logging
import socket
import time

# Skyentific Code
from .exceptions import (
    BadCRC,
    NotAcknowledged,
    UnknownResponseCode,
    StopTrying,
    SkyentificError,
)
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
            f"Could not issue loop command due to socket error: {str(socket_error)}"
        )
        raise NotAcknowledged()
    logger.debug("Returning loop data.")
    return loop_data


def get_current_condition(
    sock: socket.socket, initialization_function: callable, delay_function=callable
) -> StationObservation:
    """Obtains the current conditions."""
    keep_trying = True
    while keep_trying:
        try:
            current_bytes = get_current(sock)
            keep_trying = False
            sock.close()
        except (BadCRC, NotAcknowledged, UnknownResponseCode):
            # Wait a little and try again.
            logger.warning("Bad CRC, Not Acknowledged, or Unknown Response Code")
            if delay_function is not None:
                logger.info("Trying again with: %s", delay_function)
                try:
                    delay_function()
                except StopTrying:
                    logger.warning(f"StopTrying exception caught. Exiting loop.")
                    sock.close()
                    raise SkyentificError("Could not get current conditions.")
            else:
                logger.debug("No delay function provided.")
                raise SkyentificError("Could not get current conditions.")
    try:
        condition = initialization_function(current_bytes)
    except Exception as e:
        logger.exception("Initialization function failed.")
        raise SkyentificError("Could not initialize current conditions.")
    return condition
