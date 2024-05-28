from enum import Enum


class BarTrend(int, Enum):
    """
    Represents the trend of a barometer reading.

    Each trend is associated with a code and a description.
    """

    FALLING_RAPIDLY = -60
    FALLING_SLOWLY = -20
    STABLE = 0
    RISING_SLOWLY = 20
    RISING_RAPIDLY = 60
