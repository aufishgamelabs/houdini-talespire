"""
Provides easy access to node inputs with caching.
"""

from typing import Any

import hou


class Inputs:
    """
    Provides easy access to node inputs with caching.
    """

    node: hou.Node
    values: dict[int, Any] = {}

    def __init__(self, node: hou.Node | None = None) -> None:
        self.node = node
        if node is None:
            self.node = hou.pwd()
        self.values = {}

    def __getitem__(self, index: int):
        return self.values.setdefault(index, self.node.inputs()[index])
