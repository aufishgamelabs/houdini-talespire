"""
Provides the RoadNode class for creating and managing road geometries.
"""

import math
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List

import augl.htt.math as auglmath
import hou

from ..geo import Polygon, Volume
from .node import Node

Row = List[hou.Vector3]
Mesh = List[Row]


class RoadHeightMethod(Enum):
    """
    Enumeration for road height calculation methods.
    """

    CENTERLINE = 0
    MIN = 1
    MAX = 2
    AVERAGE = 3


class RoadHeightSmoothMethod(Enum):
    """
    Enumeration for road height calculation methods.
    """

    ON_HEIGHTFIELD = 0
    AVERAGE = 1
    MAX_CHANGE = 2


@dataclass
class RoadHeightOptions:
    method: RoadHeightMethod
    base_height: float = 0
    curb_height: float = 0


@dataclass
class RoadHeightSmoothOptions:
    method: RoadHeightSmoothMethod
    lookback: int = 0
    delta: float = 0


@dataclass
class RoadHeightSnapOptions:
    to_roads: bool = False
    to_roads_threshold: float = 0
    to_towns: bool = False
    to_towns_threshold: float = 0


class RoadNode(Node):
    """
    Represents a road geometry node within the geometry system.
    """

    rows: int
    cols: int
    midline: int = 2

    prims: List[hou.Prim]
    mesh: Mesh

    def __init__(self, node=None):
        super().__init__(node)

        self.prims = self.geo.prims()
        if len(self.prims) == 0:
            raise ValueError("Road node must have at least one primitive.")

        self.rows = len(self.prims[0].points())
        self.cols = len(self.prims)
        self.midline = self.cols // 2

        self.mesh = [None] * self.rows

    @abstractmethod
    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """


class RoadHeightNode(RoadNode):
    """
    Represents a road bed node within the geometry system.
    """

    options: RoadHeightOptions
    smooth_options: RoadHeightSmoothOptions
    snap_options: RoadHeightSnapOptions

    height_field: hou.Volume
    mesh: Mesh

    def __init__(self, node=None):
        super().__init__(node)

        self.options = RoadHeightOptions(
            method=RoadHeightMethod(self.parameters.method),
            base_height=self.parameters.height,
            curb_height=-1 * self.parameters.curb_height,
        )

        self.smooth_options = RoadHeightSmoothOptions(
            method=RoadHeightSmoothMethod(self.parameters.smooth_method),
            lookback=self.parameters.smooth_lookback,
            delta=self.parameters.smooth_max_delta,
        )

        self.snap_options = RoadHeightSnapOptions(
            to_roads=self.parameters.snap_to_roads,
            to_towns=self.parameters.snap_to_towns,
        )

        heightfields = Volume.heightfields_from_geometry(self.inputs[1].geometry())
        if len(heightfields) != 1:
            raise ValueError(
                f"Height field input must contain exactly one heightfield found {len(heightfields)}."
            )
        self.height_field = heightfields[0]

        self.mesh = [
            [prim.points()[i].position() for prim in self.prims]
            for i in range(self.rows)
        ]

    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

        dcols = [
            0,
            self.options.curb_height,
            self.options.curb_height,
            self.options.curb_height,
            0,
        ]
        if self.cols == 3:
            dcols = dcols[1:4]

        for i, row in enumerate(self.mesh):
            heights = [self.height_field.sample(p) for p in row]

            y = heights[self.midline]
            if self.options.method == RoadHeightMethod.MIN:
                y = min(heights)
            elif self.options.method == RoadHeightMethod.MAX:
                y = max(heights)
            elif self.options.method == RoadHeightMethod.AVERAGE:
                y = sum(heights) / len(heights)

            for pos in row:
                pos[1] = y

            self._smooth()

            for col, pos in enumerate(row):
                pos[1] += dcols[col]

            self._snap()

            for col, pos in enumerate(row):
                pos[1] += self.options.base_height
                self.prims[col].points()[i].setPosition(pos)

    def _smooth(self):
        if self.smooth_options.method == RoadHeightSmoothMethod.ON_HEIGHTFIELD:
            return
        elif self.smooth_options.method == RoadHeightSmoothMethod.AVERAGE:
            self._smooth_average()
        elif self.smooth_options.method == RoadHeightSmoothMethod.MAX_CHANGE:
            self._smooth_max_change()

    def _smooth_average(self):
        for col in range(len(self.mesh[0])):
            prev_pos = self.mesh[0][col]
            prev_dy = (
                [prev_pos[1] / prev_pos.length()] if prev_pos.length() > 0 else [0]
            )

            for row in self.mesh[1:]:
                mag = (prev_pos - row[col]).length()

                # normalize
                dy = ((row[col][1] - prev_pos[1]) / mag) if mag > 0.0 else 0.0
                dy = self._capped_delta(dy, self.smooth_options.delta)

                prev_dy.append(dy)
                if len(prev_dy) > self.smooth_options.lookback:
                    prev_dy = prev_dy[-self.smooth_options.lookback :]

                row[col][1] = prev_pos[1] + sum(prev_dy) / len(prev_dy) * mag
                prev_pos = row[col]

    def _smooth_max_change(self):
        prev = self.mesh[0][0]
        for row in enumerate(self.mesh[1:], start=1):
            mag = (prev - row[0]).length()

            # normalize
            dy = ((row[0][1] - prev[1]) / mag) if mag > 0 else 0
            dy = self._capped_delta(dy, self.smooth_options.delta)

            for pos in row:
                pos[1] = prev[1] + dy * mag

            prev = row[0]

    def _capped_delta(self, delta: float, cap: float) -> float:
        if abs(delta) > cap:
            return math.copysign(cap, delta)
        return delta

    def _snap(self):
        if self.snap_options.to_roads:
            self._snap_to_("roads", self.snap_options.to_roads_threshold)
        if self.snap_options.to_towns:
            self._snap_to_("towns", self.snap_options.to_towns_threshold)

    def _snap_to_(self, layer_name: str, threshold: float):
        roads = Volume.layer_from_geometry_by_name(
            self.inputs[2].geometry(), layer_name
        )

        if not roads:
            print("No roads layer found for snapping.")
            return

        heightfield = Volume.heightfields_from_geometry(self.inputs[2].geometry())[0]
        for row in self.mesh:
            for pos in row:
                if roads.sample(pos) > threshold:
                    pos[1] = heightfield.sample(pos)


class RoadWidthNode(RoadNode):
    """
    Represents a road bed node within the geometry system.
    """

    bed_width: float
    curb_width: float

    def __init__(self, node=None):
        super().__init__(node)

        self.bed_width = self.parameters.bed_width
        self.curb_width = self.parameters.curb_width

        if len(self.prims) != 1:
            raise ValueError(
                f"Road width node must have exactly one primitive found {len(self.prims)}."
            )

        self.cols = 5 if self.curb_width > 0 else 3

    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

        for i, prim in enumerate(self.prims):
            self.render_col(i, prim)

        polys = [self.geo.createPolygon(is_closed=False) for _ in range(self.cols)]
        for col in self.mesh:
            for row, p in enumerate(self.geo.createPoints(col)):
                polys[row % self.cols].addVertex(p)

        self.geo.deletePrims(self.prims, keep_points=False)

    def render_col(self, _primid: int, prim: hou.Prim):
        """
        Renders a single primitive as a road segment.
        """
        if len(prim.points()) < 2:
            raise ValueError("Road prims must have at least 2 points.")

        Polygon.smooth(
            prim,
            max_angle=self.parameters.max_angle,
            max_refinements=self.parameters.iterations,
        )

        self.mesh[0] = self._center_point_to_row(
            prim.points()[1], prim.points()[0], reverse=True
        )
        for row, pnt in enumerate(prim.points()[1:], start=1):
            self.mesh[row] = self._center_point_to_row(prim.points()[row - 1], pnt)

    def _center_point_to_row(
        self,
        start: hou.Point,
        end: hou.Point,
        reverse: bool = False,
    ):
        angle = auglmath.perpendicular_direction(auglmath.direction(start, end))

        (x, y, z) = end.position()

        dx = self.bed_width * math.cos(angle) / 2
        dz = self.bed_width * math.sin(angle) / 2

        if reverse:
            dx = -dx
            dz = -dz

        dcx = dx + self.curb_width * math.cos(angle)
        dcz = dz + self.curb_width * math.sin(angle)

        row = [
            hou.Vector3(x + dcx, y, z + dcz),
            hou.Vector3(x + dx, y, z + dz),
            hou.Vector3(x, y, z),
            hou.Vector3(x - dx, y, z - dz),
            hou.Vector3(x - dcx, y, z - dcz),
        ]

        if self.cols == 3:
            row = row[1:4]
        return row
