"""
Provides methods for working with volume geometries.
"""

from typing import List, Optional

import hou


class Volume:
    """
    Provides methods for working with volume geometries.
    """

    @staticmethod
    def heightfields_from_geometry(geo: hou.Geometry) -> List[hou.Volume]:
        """
        Returns a list of heightfield volumes from the given geometry.
        """

        heightfields: List[hou.Volume] = []
        for prim in geo.prims():
            if prim.isHeightField():
                heightfields.append(prim)

        return heightfields

    @staticmethod
    def layer_from_geometry_by_name(
        geo: hou.Geometry, name: str
    ) -> Optional[hou.Volume]:
        """
        Returns a list of volumes from the given geometry
        that match the given layer name.
        """

        for prim in geo.prims():
            try:
                if prim.stringAttribValue("name") == name:
                    return prim
            except hou.OperationFailed as err:
                print(err)
                continue

        return None
