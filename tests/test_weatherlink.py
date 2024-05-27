import logging

from weatherlink import get_current
from weatherlink.utils import ACKNOWLEDGED_RESPONSE_CODE
from .mocks import MockSocket

logger = logging.getLogger(__name__)


def test_get_current():
    loop_packet = b"LOO\x14\x00\xb1\x02It\x1e\x03\x0f\x8a\x02\x02\x03\x8c\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x1b\xff\xff\xff\xff\xff\xff\xff\x00\x00V\xff\x7f\x00\x00\xff\xff\x00\x00\x02\x00\x02\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006\x03\x03\xc0\x1b\x02\xe3\x07\n\r\xee\x00"
    # Convert ACKNOWLEDGED_RESPONSE_CODE to bytes
    code_bytes = ACKNOWLEDGED_RESPONSE_CODE.to_bytes(1, "big")
    test_packet = code_bytes + loop_packet
    mock_socket = MockSocket(test_packet)
    mock_socket.open = True
    # Test the get_current function
    response = get_current(mock_socket)
    assert mock_socket.sentData == b"LOOP 1\n"
    assert response == loop_packet
