#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Tuple, Generic, TypeVar, List, Type, Iterable

from utils import BaseChallenge, Cls, Self, get_type_argument_class, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        982
        """
        return TriangleSet.from_triangles_text(_input)\
            .get_valid_triangle_count()


# noinspection PyTypeChecker
TriangleT = TypeVar('TriangleT', bound='Triangle')


@dataclass
class TriangleSet(Generic[TriangleT]):
    triangles: List[TriangleT]

    @classmethod
    def get_triangle_class(cls) -> Type[TriangleT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, TriangleT)

    @classmethod
    def from_triangles_text(cls: Cls['TriangleSet'], triangles_text: str
                            ) -> Self['TriangleSet']:
        """
        >>> TriangleSet.from_triangles_text(
        ...     "  883  357  185\\n  572  189  424\\n  842  206  272\\n")
        TriangleSet(triangles=[Triangle(sides=(185, 357, 883)),
            Triangle(sides=(189, 424, 572)), Triangle(sides=(206, 272, 842))])
        """
        return cls(list(map(
            cls.get_triangle_class().from_triangle_text,
            triangles_text.splitlines())))

    def get_valid_triangle_count(self) -> int:
        """
        >>> TriangleSet.from_triangles_text(
        ...     '5 10 25\\n5 10 15\\n5 10 14').get_valid_triangle_count()
        1
        """
        return helper.iterable_length(self.get_valid_triangles())

    def get_valid_triangles(self) -> Iterable[TriangleT]:
        """
        >>> list(TriangleSet.from_triangles_text(
        ...     '5 10 25\\n5 10 15\\n5 10 14').get_valid_triangles())
        [Triangle(sides=(5, 10, 14))]
        """
        return (
            triangle
            for triangle in self.triangles
            if triangle.is_valid()
        )


@dataclass
class Triangle:
    sides: Tuple[int, int, int]

    @classmethod
    def from_triangle_text(cls: Cls['Triangle'], triangle_text: str
                           ) -> Self['Triangle']:
        """
        >>> Triangle.from_triangle_text('  883  357  185\\n')
        Triangle(sides=(185, 357, 883))
        """
        side_strs = filter(None, triangle_text.strip().split(' '))
        small_side_a, small_side_b, big_side = sorted(map(int, side_strs))
        return cls((small_side_a, small_side_b, big_side))

    def is_valid(self) -> bool:
        """
        >>> Triangle.from_triangle_text('5 10 25').is_valid()
        False
        >>> Triangle.from_triangle_text('5 10 15').is_valid()
        False
        >>> Triangle.from_triangle_text('5 10 14').is_valid()
        True
        """
        small_side_a, small_side_b, big_side = self.sides
        return big_side < (small_side_a + small_side_b)


Challenge.main()
challenge = Challenge()
