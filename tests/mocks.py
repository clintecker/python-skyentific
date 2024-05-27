import logging

logger = logging.getLogger(__name__)


class MockSocket:
    """
    A mock implementation of a socket for testing purposes.

    Attributes:
        data (bytes): The data to be received by the socket.
        host (str): The host address.
        port (int): The port number.
        open (bool): Indicates whether the socket is open or closed.
        sentData (bytes): The data sent by the socket.
        position (int): The current position in the received data.
    """

    def __init__(self, data, send_side_effect=None, recv_side_effect=None):
        self.data = data
        self.host = None
        self.port = None
        self.open = False
        self.sentData = b""
        self.position = 0
        logger.debug("MockSocket initialized with data of length %d", len(data))
        self.send_side_effect = send_side_effect
        self.recv_side_effect = recv_side_effect

    def sendall(self, data: bytes) -> None:
        """
        Sends all the given data through the socket.

        Args:
            data (bytes): The data to be sent.
        """
        if self.send_side_effect:
            raise self.send_side_effect
        logger.info(f"Sending data: {data}")
        self.sentData += data

    def recv(self, buffer_size: int) -> bytes:
        """
        Receives data from the socket.

        Args:
            buffer_size (int): The maximum number of bytes to receive.

        Returns:
            bytes: The received data.

        Raises:
            Exception: If there is no more data to read.
        """
        if self.recv_side_effect:
            raise self.recv_side_effect
        logger.debug(
            f"Receiving data of size {buffer_size} from position {self.position}. Data is {len(self.data)}"
        )
        if self.position >= len(self.data):
            raise Exception(
                f"No more data to read, position: {self.position} longer than data: {len(self.data)}"
            )
        end_position = self.position + buffer_size
        partialData = self.data[self.position : end_position]
        logger.debug(f"Data received: {partialData}")
        logger.debug(f"New socket position is {self.position + buffer_size}")
        self.position += buffer_size
        return partialData

    def close(self) -> None:
        """
        Closes the socket.

        Raises:
            Exception: If the socket is already closed.
        """
        logger.debug("Attmpting to close socket.")
        if self.open:
            self.open = False
        else:
            raise Exception("Socket already closed")
        logger.debug("Socket closed.")

    def connect(self, address: tuple[str, int]) -> None:
        """
        Connects the socket to the given address.

        Args:
            address (tuple): The host and port to connect to.

        Raises:
            Exception: If the socket is already open.
        """
        if self.open:
            raise Exception("Socket already open")
        self.host, self.port = address
        self.open = True
