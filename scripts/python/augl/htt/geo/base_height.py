"""
Provides
"""

from enum import Enum

import hou

from ..math import Average


class BaseHeight(Enum):
    """
    Enum for determining the base height of a geometry within a heightfield.
    """

    MIN = 0
    MAX = 1
    AVG = 2

    def of_geometry(self, geo: hou.Geometry, heightfield) -> float:
        """
        The base height is the height of the water surface. This is the height
        of the water in the lake.
        """
        if self == BaseHeight.MIN:
            return self._of_geometry(geo, heightfield, min)
        elif self == BaseHeight.MAX:
            return self._of_geometry(geo, heightfield, max)
        elif self == BaseHeight.AVG:
            avg = Average()
            return self._of_geometry(geo, heightfield, avg.compare)
        else:
            raise ValueError(
                f"Invalid base height mode: {self} {BaseHeight.MIN}"
            )

    def _of_geometry(self, geo: hou.Geometry, heightfield, comparator) -> float:
        """
        Uses the given comparator to determine the base height.
        """

        height: float | None = 0.0
        for p in geo.points():
            pos = p.position()
            pos[1] = 0

            h = heightfield.sample(pos)
            height = h if height is None else comparator(height, h)

        return 0.0 if height is None else height
