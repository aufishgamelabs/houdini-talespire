"""
Module for topology nodes in the Augl HTT framework.
"""

from dataclasses import dataclass
from typing import List

import hou

from .node import Node


@dataclass
class TopologyLayer:
    """
    Class representing a topology layer.
    """

    order: int
    prims: List[hou.Prim]

    def __gt__(self, other: "TopologyLayer") -> bool:
        return self.order > other.order

    def __ge__(self, other: "TopologyLayer") -> bool:
        return self.order >= other.order

    def __lt__(self, other: "TopologyLayer") -> bool:
        return self.order < other.order

    def __le__(self, other: "TopologyLayer") -> bool:
        return self.order <= other.order

    def __repr__(self):
        return f"TopologyLayer(order={self.order}, prims={len(self.prims)})"


class TopologyNode(Node):
    """
    Represents a topology node within the geometry system.
    """

    layers: List[TopologyLayer]

    def __init__(self, node: hou.Node | None = None) -> None:
        super().__init__(node)

        _, _, kind, _ = self.inputs[0].type().nameComponents()
        self.layers = self._node_to_layers(
            self.inputs[0],
            (
                self._curve_to_layer
                if kind == "merge"
                else self._curve_to_layers
            ),
        )

    def render(self) -> None:
        """
        This method is called when the node is rendered.
        It should be overridden by subclasses to implement the desired functionality.
        """

        for i, layer in enumerate(self.layers):
            for prim in layer.prims:
                for point in prim.points():
                    pos = point.position()
                    pos[1] = (i + 1) * self.parameters.height_increment
                    point.setPosition(pos)

    def _node_to_layers(
        self,
        node: hou.Node,
        curve_to_layers,
        layer_offset: int = 0,
        prim_offset: int = 0,
    ) -> List[TopologyLayer]:
        """
        Converts input geometry to topology layers.
        """

        _, _, kind, _ = node.type().nameComponents()
        if kind == "merge":
            return self._merge_to_layers(
                node,
                curve_to_layers,
                layer_offset=layer_offset,
                prim_offset=prim_offset,
            )
        if kind == "curve":
            return curve_to_layers(
                node, layer_offset=layer_offset, prim_offset=prim_offset
            )

        raise ValueError(f"Unsupported input node type: {kind}")

    def _merge_to_layers(
        self,
        node: hou.Node,
        curve_to_layers,
        layer_offset: int = 0,
        prim_offset: int = 0,
    ) -> List[TopologyLayer]:
        """
        Merges topology layers into the output geometry.
        """

        layers: List[TopologyLayer] = []
        for input_ in node.inputs():
            new_layers = self._node_to_layers(
                input_,
                curve_to_layers,
                layer_offset=layer_offset,
                prim_offset=prim_offset,
            )
            layers.extend(new_layers)

            layer_offset += len(new_layers)
            prim_offset += sum([len(layer.prims) for layer in new_layers])

        return layers

    def _curve_to_layer(
        self, node: hou.Node, layer_offset: int = 0, prim_offset: int = 0
    ) -> List[TopologyLayer]:
        """
        Converts a single curve to a topology layer.
        """

        return [
            TopologyLayer(
                layer_offset,
                self.geo.prims()[
                    prim_offset : prim_offset + len(node.geometry().prims())
                ],
            )
        ]

    def _curve_to_layers(
        self, node: hou.Node, layer_offset: int = 0, prim_offset: int = 0
    ) -> List[TopologyLayer]:
        """
        Converts curves to topology layers.
        """

        return [
            TopologyLayer(layer_offset + i, [prim])
            for i, prim in enumerate(
                self.geo.prims()[
                    prim_offset : prim_offset + len(node.geometry().prims())
                ]
            )
        ]
