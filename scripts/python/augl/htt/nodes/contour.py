"""
Provides functionality for contour nodes.
"""

import hou
from hou import primType

from .node import Node


class ContourNode(Node):
    """
    Represents a contour node within the geometry system.
    """

    iterations: int = 5

    curve: hou.Face
    height_field: hou.Prim
    output: hou.Face

    def __init__(self, node: hou.Node | None = None) -> None:
        super().__init__(node)

        self.curve = self.inputs[0].geometry().prim(0)
        self.height_field = self.inputs[1].geometry().prim(0)

        # ensure the output geometry is empty
        self.geo.clear()

        if self.curve.type() == primType.Polygon:
            self.output = self.geo.createPolygon(
                is_closed=self.curve.isClosed(),
            )
            for _ in range(self.curve.numVertices()):
                self.output.addVertex(
                    self.geo.createPoint(),
                )

        elif self.curve.type() == primType.BezierCurve:
            self.output = self.geo.createBezierCurve(
                num_points=self.curve.numVertices(),
                is_closed=self.curve.isClosed(),
            )

        elif self.curve.type() == primType.NURBSCurve:
            self.output = self.geo.createNURBSCurve(
                num_points=self.curve.numVertices(),
                is_closed=self.curve.isClosed(),
            )

        else:
            raise TypeError(f"Unsupported curve type: {self.curve.type().name}")

    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

        # Initialize the output curve by copying the input curve and setting Y
        # to the sampled height from the height field.
        for i, point in enumerate(self.output.points()):
            curve_point = self.curve.points()[i]
            curve_pos = curve_point.position()
            curve_pos[1] = 0

            height = self.height_field.sample(curve_pos)
            point.setPosition((curve_pos[0], height, curve_pos[2]))

        # Smooth the curve
        smooth = self.node.createNode("smooth::2.0")
        smooth.setInput(0, self.node)


def cook_contour_node() -> None:
    """
    Cooks the ContourNode.
    """

    ContourNode.cook()
