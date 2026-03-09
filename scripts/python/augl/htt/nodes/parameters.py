"""
Provides an object that allows easy access to node parameters.
"""

from typing import Any

import hou


class Parameters:
    """
    Object that provides easy access to node parameters.
    """

    node: hou.Node
    values: dict[str, Any] = {}

    def __init__(self, node: hou.Node | None = None) -> None:
        self.node = node
        if node is None:
            self.node = hou.pwd()

        self.values = {}

    def __getattr__(self, name):
        return self.values.setdefault(name, self.node.parm(name).eval())

    def __getitem__(self, index: int | str):
        return self.__getattr__(index)
