class NotAcknowledged(Exception):
    """When the device does not acknowledge a command"""

    pass


class BadCRC(Exception):
    """When the device believes your CRC to be bad."""

    pass


class UnknownResponseCode(Exception):
    """When the device returns an unknown response code."""

    pass


class StopTrying(Exception):
    """Stop Trying"""

    pass


class SkyentificError(Exception):
    """Base class for Skyentific exceptions."""

    pass
