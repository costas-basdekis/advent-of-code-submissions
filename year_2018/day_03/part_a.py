#!/usr/bin/env python3
import doctest
import re
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    104439
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return Claims.from_lines(_input).get_overlapping_square_count()


class Claims:
    @classmethod
    def from_lines(cls, claims_text):
        """
        >>> list(map(tuple, Claims.from_lines(
        ...     "#1 @ 1,3: 4x4\\n"
        ...     "#2 @ 3,1: 4x4\\n"
        ...     "#3 @ 5,5: 2x2\\n"
        ... ).claims))
        [('1', 1, 3, 4, 4), ('2', 3, 1, 4, 4), ('3', 5, 5, 2, 2)]
        """
        lines = claims_text.splitlines()
        non_empty_lines = filter(None, lines)
        return cls(list(map(Claim.from_line, non_empty_lines)))

    def __init__(self, claims):
        self.claims = claims

    def get_sum_of_areas(self):
        """
        >>> Claims.from_lines(
        ...     "#1 @ 1,3: 4x4\\n"
        ...     "#2 @ 3,1: 4x4\\n"
        ...     "#3 @ 5,5: 2x2\\n"
        ... ).get_sum_of_areas()
        36
        """
        return sum(claim.get_area() for claim in self.claims)

    def get_overlapping_square_count(self):
        """
        >>> Claims.from_lines(
        ...     "#1 @ 1,3: 4x4\\n"
        ...     "#2 @ 3,1: 4x4\\n"
        ...     "#3 @ 5,5: 2x2\\n"
        ... ).get_overlapping_square_count()
        4
        >>> Claims.from_lines(
        ...     "#0 @ 3,3: 2x2\\n"
        ...     "#1 @ 1,3: 4x4\\n"
        ...     "#2 @ 3,1: 4x4\\n"
        ...     "#3 @ 5,5: 2x2\\n"
        ... ).get_overlapping_square_count()
        4
        """
        count = 0
        seen = {}
        for claim in self.claims:
            for square in claim.squares():
                if square not in seen:
                    seen[square] = 1
                elif seen[square] == 1:
                    count += 1
                    seen[square] += 1

        return count


class Claim(namedtuple("Claim", ("id", "left", "top", "width", "height"))):
    re_claim = re.compile(r"^#(\d+) @ (\d+),(\d+): (\d+)x(\d+)$")

    @classmethod
    def from_line(cls, claim_text):
        """
        >>> Claim.from_line("#123 @ 3,2: 5x4")
        Claim(id='123', left=3, top=2, width=5, height=4)
        """
        _id, left_str, top_str, width_str, height_str = \
            cls.re_claim.match(claim_text).groups()
        return cls(
            id=_id, left=int(left_str), top=int(top_str),
            width=int(width_str), height=int(height_str))

    def get_area(self):
        """
        >>> Claim(id='123', left=3, top=2, width=5, height=4).get_area()
        20
        >>> Claim(id='123', left=3, top=2, width=1, height=4).get_area()
        4
        >>> Claim(id='123', left=3, top=2, width=5, height=1).get_area()
        5
        """
        return self.width * self.height

    def squares(self):
        """
        >>> tuple(Claim.from_line("#123 @ 3,2: 3x2").squares())
        ((3, 2), (3, 3), (4, 2), (4, 3), (5, 2), (5, 3))
        """
        return (
            (x, y)
            for x in range(self.left, self.left + self.width)
            for y in range(self.top, self.top + self.height)
        )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
