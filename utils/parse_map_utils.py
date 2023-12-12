__all__ = [
    'parse_map_points',
]

from typing import List, Union, Iterable, Tuple, Set

from utils.point import Point2D


def parse_map_points(text: str, char_sets: List[Union[str, Iterable[str]]]) -> Tuple[Set[Point2D], ...]:
    """
    >>> list(map(sorted, parse_map_points("#.\\n.#", ["#", "."])))
    [[Point2D(x=0, y=0), Point2D(x=1, y=1)], [Point2D(x=0, y=1), Point2D(x=1, y=0)]]
    """
    lines = list(map(str.strip, text.strip().splitlines()))
    point_sets = tuple(set() for _ in char_sets)
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            point = Point2D(x, y)
            for char_set, point_set in zip(char_sets, point_sets):
                if char in char_set:
                    point_set.add(point)
                    break
    return point_sets
