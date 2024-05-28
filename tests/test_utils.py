import datetime
import socket

from unittest.mock import Mock
from unittest import TestCase

from skyentific.exceptions import NotAcknowledged, BadCRC, UnknownResponseCode
from skyentific.utils import (
    crc16,
    connect,
    request,
    receive_data,
    make_time,
    NACK_RESPONSE_CODE,
    BAD_CRC_RESPONSE_CODE,
    ACKNOWLEDGED_RESPONSE_CODE,
)
from .mocks import MockSocket


class TestUtils(TestCase):
    loop_packet = b"LOO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"

    def setUp(self):
        pass

    def test_crc16(self):
        # Known input data for which we know the expected CRC result
        # This data should be a list of bytes. Example: b"hello world"
        expected_crc_result = 0x0
        calculated_crc = crc16(self.loop_packet)
        assert (
            calculated_crc == expected_crc_result
        ), f"Expected CRC: {expected_crc_result}, but got: {calculated_crc}"

    def test_connect(self):
        # Positive test cases
        socket_generator = Mock()
        socket_generator.return_value = Mock()
        socket_generator.return_value.connect = Mock()
        sock = connect("4.4.4.4", 8888, socket_generator)
        sock.connect.assert_called_once_with(("4.4.4.4", 8888))
        socket_generator.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

    def test_request_nack(self):
        mock_socket = MockSocket(NACK_RESPONSE_CODE.to_bytes(1, "big"))
        with self.assertRaises(NotAcknowledged):
            request(mock_socket, b"Hello World")

    def test_request_bad_crc(self):
        mock_socket = MockSocket(BAD_CRC_RESPONSE_CODE.to_bytes(1, "big"))
        with self.assertRaises(BadCRC):
            request(mock_socket, b"Hello World")

    def test_request_ack(self):
        mock_socket = MockSocket(ACKNOWLEDGED_RESPONSE_CODE.to_bytes(1, "big"))
        request(mock_socket, b"Hello World")

    def test_request_unknown_response_code(self):
        mock_socket = MockSocket(b"\xFF")
        with self.assertRaises(UnknownResponseCode):
            request(mock_socket, b"Hello World")

    def test_receive_data_big_buffer(self):
        mock_socket = MockSocket(b"Hello World")
        mock_socket.open = True
        assert receive_data(mock_socket, 100) == b"Hello World"

    def test_recieve_partial_data(self):
        mock_socket = MockSocket(b"Hello World")
        mock_socket.open = True
        assert receive_data(mock_socket, 5) == b"Hello"
        assert receive_data(mock_socket, 6) == b" World"
        with self.assertRaises(Exception):
            receive_data(mock_socket, 1) == b""

    def test_make_time(self):
        # Positive test cases
        self.assertEqual(
            make_time(1609459200), datetime.time(0, 0, 0)
        )  # 2021-01-01 00:00:00
        self.assertEqual(
            make_time(1609545599), datetime.time(23, 59, 59)
        )  # 2021-01-01 23:59:59
        self.assertEqual(
            make_time(1614556800), datetime.time(0, 0, 0)
        )  # 2021-03-01 00:00:00

        # Edge cases
        self.assertEqual(
            make_time(1609462799), datetime.time(0, 59, 59)
        )  # edge of an hour
        self.assertEqual(
            make_time(1609542000), datetime.time(23, 0, 0)
        )  # edge of a day

        # Additional corner cases
        self.assertEqual(
            make_time(2147483647), datetime.time(3, 14, 7)
        )  # maximum 32-bit integer
        self.assertEqual(
            make_time(9223372036854775807), datetime.time(15, 30, 7)
        )  # maximum 64-bit integer

        # Negative test cases
        with self.assertRaises(ValueError):
            make_time(-1)  # negative timestamp
        with self.assertRaises(TypeError):
            make_time(3661.0)  # float
        with self.assertRaises(TypeError):
            make_time("3661")  # string
        with self.assertRaises(TypeError):
            make_time(None)  # None`
