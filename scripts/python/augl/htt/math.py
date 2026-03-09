"""
Provides mathematical operators and classes for use in various parts of the
application.
"""

import math
from typing import Generator, Union

import hou

Number = Union[int, float]


def angle_between_vectors(v1: hou.Vector3, v2: hou.Vector3) -> float:
    """
    Calculate the angle between two 3D vectors in radians.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Angle between vectors in radians
    """
    dot_product = v1.dot(v2)
    magnitude_product = v1.length() * v2.length()

    if magnitude_product == 0:
        return 0.0

    cos_angle = dot_product / magnitude_product
    cos_angle = max(-1.0, min(1.0, cos_angle))

    return math.acos(cos_angle)


def direction(start: hou.Point, end: hou.Point) -> float:
    """
    Returns the direction in radians from start to end points.
    """

    delta = end.position() - start.position()
    angle = math.atan2(delta[2], delta[0])
    return angle


def perpendicular_direction(angle: float) -> float:
    """
    Returns the perpendicular direction in radians from a given direction.
    """

    return angle + math.pi / 2


def sequence(count: int, increment: Number = 1) -> Generator[float, None, None]:
    """
    Clamps a value between a minimum and maximum value.
    """

    for i in range(count):
        yield i * increment


class Average:
    """
    Acts as a comparator that returns the average of all values passed to it.
    """

    value: float = 0.0
    count: int = 0

    def __call__(self, value: float) -> float:
        self.value += value
        self.count += 1

        return self.value / self.count

    def compare(self, _: float, value: float) -> float:
        """
        Compare method that returns the average of all values passed to it.
        """
        return self(value)
