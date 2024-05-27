# Standard Library
import datetime
import logging
import socket
from typing import List, Optional

# Third Party Code
from bitstring import BitStream

# Supercell Code
from exceptions import BadCRC, NotAcknowledged, UnknownResponseCode

socket.setdefaulttimeout(2.0)
logger = logging.getLogger(__name__)

SOCKET_BUFFER_SIZE = 16

RESPONSE_CODE_SIZE = 1

NACK_RESPONSE_CODE = 0x21
BAD_CRC_RESPONSE_CODE = 0x18
ACKNOWLEDGED_RESPONSE_CODE = 0x06

CRC16_TABLE = [
    0x0000,
    0x1021,
    0x2042,
    0x3063,
    0x4084,
    0x50A5,
    0x60C6,
    0x70E7,
    0x8108,
    0x9129,
    0xA14A,
    0xB16B,
    0xC18C,
    0xD1AD,
    0xE1CE,
    0xF1EF,
    0x1231,
    0x0210,
    0x3273,
    0x2252,
    0x52B5,
    0x4294,
    0x72F7,
    0x62D6,
    0x9339,
    0x8318,
    0xB37B,
    0xA35A,
    0xD3BD,
    0xC39C,
    0xF3FF,
    0xE3DE,
    0x2462,
    0x3443,
    0x0420,
    0x1401,
    0x64E6,
    0x74C7,
    0x44A4,
    0x5485,
    0xA56A,
    0xB54B,
    0x8528,
    0x9509,
    0xE5EE,
    0xF5CF,
    0xC5AC,
    0xD58D,
    0x3653,
    0x2672,
    0x1611,
    0x0630,
    0x76D7,
    0x66F6,
    0x5695,
    0x46B4,
    0xB75B,
    0xA77A,
    0x9719,
    0x8738,
    0xF7DF,
    0xE7FE,
    0xD79D,
    0xC7BC,
    0x48C4,
    0x58E5,
    0x6886,
    0x78A7,
    0x0840,
    0x1861,
    0x2802,
    0x3823,
    0xC9CC,
    0xD9ED,
    0xE98E,
    0xF9AF,
    0x8948,
    0x9969,
    0xA90A,
    0xB92B,
    0x5AF5,
    0x4AD4,
    0x7AB7,
    0x6A96,
    0x1A71,
    0x0A50,
    0x3A33,
    0x2A12,
    0xDBFD,
    0xCBDC,
    0xFBBF,
    0xEB9E,
    0x9B79,
    0x8B58,
    0xBB3B,
    0xAB1A,
    0x6CA6,
    0x7C87,
    0x4CE4,
    0x5CC5,
    0x2C22,
    0x3C03,
    0x0C60,
    0x1C41,
    0xEDAE,
    0xFD8F,
    0xCDEC,
    0xDDCD,
    0xAD2A,
    0xBD0B,
    0x8D68,
    0x9D49,
    0x7E97,
    0x6EB6,
    0x5ED5,
    0x4EF4,
    0x3E13,
    0x2E32,
    0x1E51,
    0x0E70,
    0xFF9F,
    0xEFBE,
    0xDFDD,
    0xCFFC,
    0xBF1B,
    0xAF3A,
    0x9F59,
    0x8F78,
    0x9188,
    0x81A9,
    0xB1CA,
    0xA1EB,
    0xD10C,
    0xC12D,
    0xF14E,
    0xE16F,
    0x1080,
    0x00A1,
    0x30C2,
    0x20E3,
    0x5004,
    0x4025,
    0x7046,
    0x6067,
    0x83B9,
    0x9398,
    0xA3FB,
    0xB3DA,
    0xC33D,
    0xD31C,
    0xE37F,
    0xF35E,
    0x02B1,
    0x1290,
    0x22F3,
    0x32D2,
    0x4235,
    0x5214,
    0x6277,
    0x7256,
    0xB5EA,
    0xA5CB,
    0x95A8,
    0x8589,
    0xF56E,
    0xE54F,
    0xD52C,
    0xC50D,
    0x34E2,
    0x24C3,
    0x14A0,
    0x0481,
    0x7466,
    0x6447,
    0x5424,
    0x4405,
    0xA7DB,
    0xB7FA,
    0x8799,
    0x97B8,
    0xE75F,
    0xF77E,
    0xC71D,
    0xD73C,
    0x26D3,
    0x36F2,
    0x0691,
    0x16B0,
    0x6657,
    0x7676,
    0x4615,
    0x5634,
    0xD94C,
    0xC96D,
    0xF90E,
    0xE92F,
    0x99C8,
    0x89E9,
    0xB98A,
    0xA9AB,
    0x5844,
    0x4865,
    0x7806,
    0x6827,
    0x18C0,
    0x08E1,
    0x3882,
    0x28A3,
    0xCB7D,
    0xDB5C,
    0xEB3F,
    0xFB1E,
    0x8BF9,
    0x9BD8,
    0xABBB,
    0xBB9A,
    0x4A75,
    0x5A54,
    0x6A37,
    0x7A16,
    0x0AF1,
    0x1AD0,
    0x2AB3,
    0x3A92,
    0xFD2E,
    0xED0F,
    0xDD6C,
    0xCD4D,
    0xBDAA,
    0xAD8B,
    0x9DE8,
    0x8DC9,
    0x7C26,
    0x6C07,
    0x5C64,
    0x4C45,
    0x3CA2,
    0x2C83,
    0x1CE0,
    0x0CC1,
    0xEF1F,
    0xFF3E,
    0xCF5D,
    0xDF7C,
    0xAF9B,
    0xBFBA,
    0x8FD9,
    0x9FF8,
    0x6E17,
    0x7E36,
    0x4E55,
    0x5E74,
    0x2E93,
    0x3EB2,
    0x0ED1,
    0x1EF0,
]


def crc16(data: BitStream) -> int:
    """
    Calculate CRC16 using the given table.

    - `data`: The data to calculate the CRC of

    Return calculated value of CRC. Should be 0.
    """
    crc = 0
    for data_byte in iter(data):
        high_byte = crc >> 8
        low_byte = (crc & 0x00FF) << 8
        table_index = high_byte ^ data_byte
        table_value = CRC16_TABLE[table_index]
        crc = low_byte ^ table_value
    return crc


def connect(host: str, port: int) -> socket.socket:
    """Connects to a TCP/IP host."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.info("Connecting to %s:%s", host, port)
    sock.connect((host, port))
    return sock


def request(sock: socket.socket, body: bytes) -> None:
    """Send a request to a socket."""
    sock.sendall(body)
    response_code = BitStream(receive_data(sock, RESPONSE_CODE_SIZE)).int
    if response_code == NACK_RESPONSE_CODE:
        logger.error("Request was not acknowledged.")
        raise NotAcknowledged()
    elif response_code == BAD_CRC_RESPONSE_CODE:
        logger.error("Request contained a bad CRC, retransmit.")
        raise BadCRC()
    elif response_code == ACKNOWLEDGED_RESPONSE_CODE:
        logger.info("Request was acknowledged.")
    else:
        logger.error("Unknown response code %s", response_code)
        raise UnknownResponseCode()


def receive_data(sock: socket.socket, buffer_size: Optional[int] = None) -> bytes:
    """Receives data from a socket."""
    return sock.recv(buffer_size or SOCKET_BUFFER_SIZE)


def make_time(time_stamp: int) -> datetime.time:
    """Converts an integer time to a time object."""
    hour = int(time_stamp / 100)
    minute = time_stamp - (hour * 100)
    return datetime.time(hour=hour, minute=minute)


def make_datetime(
    date_stamp: BitStream, time_stamp: int
) -> Optional[datetime.datetime]:
    """Converts a date stamp and time stamp into a datetime object."""
    year = date_stamp.read(7).uint
    month = date_stamp.read(4).uint
    day = date_stamp.read(5).uint
    timestamp = make_time(time_stamp)
    return datetime.datetime(
        year=2000 + year,
        month=month,
        day=day,
        hour=timestamp.hour,
        minute=timestamp.minute,
    )


def test_crc16():
    # Known input data for which we know the expected CRC result
    # This data should be a list of bytes. Example: b"hello world"
    input_data = b"LOO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"

    # Convert input data to a list of integers representing bytes, as expected by the crc16 function
    input_data_as_bytes = BitStream(input_data)

    # Expected CRC result after processing the input data
    # This value should be changed to what is actually expected for the given input
    # For demonstration, let's assume we expect 0x1D0F, but you should calculate this based on your CRC16 variant
    expected_crc_result = 0x0

    # Call the crc16 function with the test data
    calculated_crc = crc16(input_data_as_bytes)

    # Assert that the calculated CRC matches the expected result
    assert (
        calculated_crc == expected_crc_result
    ), f"Expected CRC: {expected_crc_result}, but got: {calculated_crc}"


def test_connect(host, port):
    sock = connect(host, port)

    LOOP_COMMAND = b"LOOP %d\n"
    LOOP_RECORD_SIZE_BYTES = 99
    # LOOP_RECORD_SIZE_BITS = LOOP_RECORD_SIZE_BYTES * 8

    loop_data = b""
    try:
        try:
            request(sock, LOOP_COMMAND % 1)
        except (BadCRC, NotAcknowledged, UnknownResponseCode):
            logger.exception("Could not issue loop command.")
            raise

        while len(loop_data) != LOOP_RECORD_SIZE_BYTES:
            data = receive_data(sock)
            loop_data += data
    except socket.timeout:
        logger.exception("Could not issue loop command")
        raise NotAcknowledged()
    finally:
        sock.close()
    return loop_data


if __name__ == "__main__":
    test_crc16()
    print("CRC16 test passed.")
    test_connect("127.0.0.1", 22222)
    print()
    logger.info("All tests passed.")
