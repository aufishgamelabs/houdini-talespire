"""
Provides functionality for project nodes.
"""

from typing import List

import hou

from ..geo import Volume
from .node import Node


class ProjectNode(Node):
    """
    Represents a project node within the geometry system.
    """

    iterations: int = 5

    faces: List[hou.Face]
    height_field: hou.Prim
    output: hou.Face

    def __init__(self, node: hou.Node | None = None) -> None:
        super().__init__(node)

        self.faces = self.geo.prims()

        heightfields = Volume.heightfields_from_geometry(
            self.inputs[1].geometry()
        )
        if len(heightfields) != 1:
            raise ValueError(
                f"Height field input must contain exactly one heightfield found {len(heightfields)}."
            )
        self.height_field = heightfields[0]

    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

        for face in self.faces:
            for point in face.points():
                pos = point.position()
                pos[1] = 0

                height = self.height_field.sample(pos)
                point.setPosition((pos[0], height, pos[2]))
                point.setPosition((pos[0], height, pos[2]))
