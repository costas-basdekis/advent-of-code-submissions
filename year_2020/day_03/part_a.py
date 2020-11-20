#!/usr/bin/env python3
import doctest

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    187
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return TreeMap.from_text(_input)\
        .get_tree_count_on_slope((3, 1))


class TreeMap:
    PARSE_MAP = {
        '.': False,
        '#': True,
    }

    @classmethod
    def from_text(cls, tree_map_text):
        """
        >>> TreeMap.from_text(
        ...     "..#\\n"
        ...     "#..\\n"
        ...     ".#.\\n"
        ... ).lines
        [[False, False, True], [True, False, False], [False, True, False]]
        """
        lines = tree_map_text.splitlines()
        non_empty_lines = filter(None, lines)
        return cls([
            list(map(cls.PARSE_MAP.__getitem__, line))
            for line in non_empty_lines
        ])

    def __init__(self, lines):
        self.lines = lines
        if self.lines:
            self.line_length = len(self.lines[0])
        else:
            self.line_length = None

    def get_tree_count_on_slope(self, slope):
        """
        >>> TreeMap([[False] * 3] * 3).get_tree_count_on_slope((1, 1))
        0
        >>> TreeMap([[True] * 3] * 3).get_tree_count_on_slope((1, 1))
        3
        >>> tree_map_a = TreeMap.from_text(
        ...     "..#\\n"
        ...     "#..\\n"
        ...     ".#.\\n"
        ... )
        >>> tree_map_a.get_tree_count_on_slope((1, 1))
        0
        >>> tree_map_a.get_tree_count_on_slope((2, 1))
        1
        >>> tree_map_a.get_tree_count_on_slope((1, 2))
        1
        >>> tree_map_b = TreeMap.from_text(
        ...     "..##.......\\n"
        ...     "#...#...#..\\n"
        ...     ".#....#..#.\\n"
        ...     "..#.#...#.#\\n"
        ...     ".#...##..#.\\n"
        ...     "..#.##.....\\n"
        ...     ".#.#.#....#\\n"
        ...     ".#........#\\n"
        ...     "#.##...#...\\n"
        ...     "#...##....#\\n"
        ...     ".#..#...#.#\\n"
        ... )
        >>> tree_map_b.get_tree_count_on_slope((3, 1))
        7
        """
        return self.get_tree_count_on_points(self.get_points_on_slope(slope))

    def get_tree_count_on_points(self, points):
        return sum(
            1
            for x, y in points
            if self.lines[y][x]
        )

    def get_points_on_slope(self, slope):
        """
        >>> tree_map_a = TreeMap.from_text(
        ...     "..#\\n"
        ...     "#..\\n"
        ...     ".#.\\n"
        ... )
        >>> tree_map_a.get_points_on_slope((1, 1))
        [(0, 0), (1, 1), (2, 2)]
        >>> tree_map_a.get_points_on_slope((2, 1))
        [(0, 0), (2, 1), (1, 2)]
        >>> tree_map_a.get_points_on_slope((1, 2))
        [(0, 0), (1, 2)]
        >>> tree_map_b = TreeMap.from_text(
        ...     "..##.......\\n"
        ...     "#...#...#..\\n"
        ...     ".#....#..#.\\n"
        ...     "..#.#...#.#\\n"
        ...     ".#...##..#.\\n"
        ...     "..#.##.....\\n"
        ...     ".#.#.#....#\\n"
        ...     ".#........#\\n"
        ...     "#.##...#...\\n"
        ...     "#...##....#\\n"
        ...     ".#..#...#.#\\n"
        ... )
        >>> tree_map_b.get_points_on_slope((3, 1))
        [(0, 0), (3, 1), (6, 2), (9, 3), (1, 4), (4, 5), (7, 6), (10, 7), (2, 8), (5, 9), (8, 10)]
        """
        delta_x, delta_y = slope
        return [
            ((y // delta_y * delta_x) % self.line_length, y)
            for y in range(0, len(self.lines), delta_y)
        ]


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
