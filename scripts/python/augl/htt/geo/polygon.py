"""
Provides the Poly class, which is responsible for rendering polygonal geometry in Houdini. It includes methods for creating polygons from input primitives and managing the geometry's points and vertices. The class also handles the deletion of original primitives after rendering to ensure a clean output.
"""

import math

import hou


class Polygon(hou.Polygon):
    @staticmethod
    def smooth(
        poly: hou.Polygon, max_angle: float = 45, max_refinements=10
    ) -> None:
        """
        Smooths the polygon by averaging the positions of its vertices.
        """

        points = poly.points()
        point_count = len(poly.vertices())
        if point_count < 3:
            return

        updated = True
        while updated and max_refinements > 0:
            max_refinements -= 1
            updated = False
            for i, vertex in enumerate(points):
                if i == 0 or i == point_count - 1:
                    continue

                a = points[i - 1].position()
                b = vertex.position()
                c = points[i + 1].position()

                ab = (b - a).normalized()
                bc = (c - b).normalized()

                if ab.length() == 0 or bc.length() == 0:
                    continue

                deg = math.degrees(ab.dot(bc))
                if (deg > max_angle and deg < 180 - max_angle) or (
                    deg < -max_angle and deg > -180 + max_angle
                ):

                    vertex.setPosition((a + c) / 2)
                    updated = True
