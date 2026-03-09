"""
Provides a base Node class for Houdini nodes.
"""

from abc import abstractmethod

import hou

from .inputs import Inputs
from .parameters import Parameters


class Node:
    """
    Base class for Houdini nodes.
    """

    geo: hou.Geometry
    node: hou.Node
    inputs: Inputs
    parameters: Parameters

    def __init__(self, node: hou.Node | None = None) -> None:
        self.node = node
        if node is None:
            self.node = hou.pwd()

        if hasattr(self.node, "geometry"):
            self.geo = self.node.geometry()

        self.inputs = Inputs(self.node)
        self.parameters = Parameters(self.node)

    @abstractmethod
    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

    @classmethod
    def cook(cls) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

        node = cls()
        node.render()
