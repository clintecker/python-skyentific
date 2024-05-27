import logging
import socket
import time

from unittest.mock import Mock
from unittest import TestCase

from weatherlink import get_current, get_current_condition, LOOP_RECORD_SIZE_BYTES
from weatherlink.utils import ACKNOWLEDGED_RESPONSE_CODE
from weatherlink.exceptions import StopTrying, NotAcknowledged, WeatherLinkError

from .mocks import MockSocket

logger = logging.getLogger(__name__)


class TestWeatherLink(TestCase):
    code_bytes = ACKNOWLEDGED_RESPONSE_CODE.to_bytes(1, "big")
    loop_packet = b"LOO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"
    mock_socket = None

    def setUp(self):
        logging.debug(f"Setting up test.")
        test_packet = self.code_bytes + self.loop_packet
        self.mock_socket = MockSocket(test_packet)
        self.mock_socket.open = True

    def test_get_current(self):
        # Test the get_current function
        response = get_current(self.mock_socket)
        assert self.mock_socket.sentData == b"LOOP 1\n"
        assert response == self.loop_packet
        assert len(response) == LOOP_RECORD_SIZE_BYTES

    def test_get_current_socket_error(self):
        # Test the get_current function with a socket error
        mock_socket = MockSocket(b"", recv_side_effect=socket.timeout("Timeout"))
        with self.assertRaises(NotAcknowledged):
            get_current(mock_socket)

    def test_get_current_condition(self):
        mock_initialization_function = Mock(return_value=b"\x00")
        delays = [0.1, 1.0]
        retry_count = 0

        def delay_function():
            nonlocal retry_count
            if retry_count + 1 > len(delays):
                raise StopTrying
            time.sleep(delays[retry_count])
            retry_count += 1

        get_current_condition(
            self.mock_socket, mock_initialization_function, delay_function
        )
        mock_initialization_function.assert_called_once_with(self.loop_packet)
        assert retry_count == 0

    def test_get_current_condition_initialization_errors(self):
        mock_initialization_function = Mock(side_effect=Exception("Bad Initialization"))
        delays = [0.1, 1.0]
        retry_count = 0

        def delay_function():
            nonlocal retry_count
            if retry_count + 1 > len(delays):
                raise StopTrying
            time.sleep(delays[retry_count])
            retry_count += 1

        with self.assertRaises(WeatherLinkError):
            get_current_condition(
                self.mock_socket, mock_initialization_function, delay_function
            )
        mock_initialization_function.assert_called_once_with(self.loop_packet)
        assert retry_count == 0

    def test_current_condition_retry(self):
        receive_error_mock_socket = MockSocket(b"", recv_side_effect=NotAcknowledged)
        receive_error_mock_socket.open = True
        mock_initialization_function = Mock(side_effect=Exception("Bad Initialization"))
        delays = [0.1, 0.1]
        retry_count = 0

        def delay_function():
            nonlocal retry_count
            if retry_count + 1 > len(delays):
                logger.debug(f"Out of delays. Raising StopTrying exception.")
                raise StopTrying
            logger.debug(f"Delaying for {delays[retry_count]} seconds.")
            time.sleep(delays[retry_count])
            retry_count += 1

        with self.assertRaises(WeatherLinkError):
            get_current_condition(
                receive_error_mock_socket, mock_initialization_function, delay_function
            )

        mock_initialization_function.assert_not_called()
        assert retry_count == 2
