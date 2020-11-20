#!/usr/bin/env python3
from utils import BaseChallenge, Cls, Self
from utils.collections_utils import in_groups
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1826
        """
        return TriangleSetExtended.from_triangles_text_vertically(_input)\
            .get_valid_triangle_count()


class TriangleSetExtended(part_a.TriangleSet):
    @classmethod
    def from_triangles_text_vertically(
            cls: Cls[part_a.TriangleSet], triangles_text: str
    ) -> Self[part_a.TriangleSet]:
        """
        >>> TriangleSetExtended.from_triangles_text_vertically(
        ...     "101 301 501\\n"
        ...     "102 302 502\\n"
        ...     "103 303 503\\n"
        ...     "201 401 601\\n"
        ...     "202 402 602\\n"
        ...     "203 403 603\\n"
        ... )
        TriangleSetExtended(triangles=[Triangle(sides=(101, 102, 103)),
            Triangle(sides=(301, 302, 303)), Triangle(sides=(501, 502, 503)),
            Triangle(sides=(201, 202, 203)), Triangle(sides=(401, 402, 403)),
            Triangle(sides=(601, 602, 603))])
        >>> TriangleSetExtended.from_triangles_text_vertically(
        ...     "883  357  185\\n"
        ...     "572  189  424\\n"
        ...     "842  206  272\\n"
        ... )
        TriangleSetExtended(triangles=[Triangle(sides=(572, 842, 883)),
            Triangle(sides=(189, 206, 357)), Triangle(sides=(185, 272, 424))])
        """
        triangles = cls.from_triangles_text(triangles_text, sort=False)\
            .triangles
        if len(triangles) % 3 != 0:
            raise Exception(
                f"Expected triangle count to be a multiple of 3, but there "
                f"were {len(triangles)} triangles")
        triangles_vertically = [
            triangle
            for group in in_groups(triangles, 3)
            for triangle
            in map(part_a.Triangle,
                   zip(*(triangle.sides for triangle in group)))
        ]
        return cls(triangles_vertically)


Challenge.main()
challenge = Challenge()
