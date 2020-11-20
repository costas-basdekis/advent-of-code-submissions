#!/usr/bin/env python3
import doctest
import itertools
import math

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    288
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, best_visibility = get_position_with_best_visibility(parse_map(_input))

    return best_visibility


def get_position_with_best_visibility(_map):
    """
    >>> get_position_with_best_visibility(parse_map(\
        ".#..#\\n.....\\n#####\\n....#\\n...##\\n"))
    ((3, 4), 8)
    >>> get_position_with_best_visibility(parse_map(\
        "......#.#.\\n#..#.#....\\n..#######.\\n.#.#.###..\\n.#..#....."\
        "\\n..#....#.#\\n#..#....#.\\n.##.#..###\\n##...#..#.\\n.#....####"))
    ((5, 8), 33)
    >>> get_position_with_best_visibility(parse_map(\
        "#.#...#.#.\\n.###....#.\\n.#....#...\\n##.#.#.#.#\\n....#.#.#."\
        "\\n.##..###.#\\n..#...##..\\n..##....##\\n......#...\\n.####.###."))
    ((1, 2), 35)
    >>> get_position_with_best_visibility(parse_map(\
        ".#..#..###\\n####.###.#\\n....###.#.\\n..###.##.#\\n##.##.#.#."\
        "\\n....###..#\\n..#.#..#.#\\n#..#.#.###\\n.##...##.#\\n.....#.#.."))
    ((6, 3), 41)
    >>> get_position_with_best_visibility(parse_map(\
        ".#..##.###...#######\\n##.############..##.\\n.#.######.########.#"\
        "\\n.###.#######.####.#.\\n#####.##.#.##.###.##\\n..#####..#.#########"\
        "\\n####################\\n#.####....###.#.#.##\\n##.#################"\
        "\\n#####.##.###..####..\\n..######..##.#######\\n####.##.####...##..#"\
        "\\n.#####..#.######.###\\n##...#.##########...\\n#.##########.#######"\
        "\\n.####.#.###.###.#.##\\n....##.##.###..#####\\n.#.#.###########.###"\
        "\\n#.#.#.#####.####.###\\n###.##.####.##.#..##"))
    ((11, 13), 210)
    """
    visibility_mapping = get_visibility_mapping(_map)
    best_position = max(
        visibility_mapping, key=lambda point: visibility_mapping[point])
    return best_position, visibility_mapping[best_position]


def get_visibility_mapping(_map):
    """
    >>> get_visibility_mapping(parse_map(\
        ".#..#\\n.....\\n#####\\n....#\\n...##\\n"))
    {(1, 0): 7, (4, 0): 7, (0, 2): 6, (1, 2): 7, (2, 2): 7, (3, 2): 7, \
(4, 2): 5, (4, 3): 7, (3, 4): 8, (4, 4): 7}
    """
    return {
        point: get_visible_asteroid_count(_map, point)
        for point in _map
    }


def get_visible_asteroid_count(_map, center):
    """
    >>> get_visible_asteroid_count(parse_map(\
        ".#..#\\n.....\\n#####\\n....#\\n...##\\n"), (3, 4))
    8
    """
    return len(group_map_by_gcd(_map, center)) - 1


def group_map_by_gcd(_map, center):
    """
    >>> group_map_by_gcd([(0, 0), (1, 1), (2, 2), (4, 2), (2, 1)], None)
    {(0, 0): [(0, 0)], (1, 1): [(1, 1), (2, 2)], (2, 1): [(2, 1), (4, 2)]}
    >>> group_map_by_gcd(parse_map(\
        ".#..#\\n.....\\n#####\\n....#\\n...##\\n"), (1, 2))
    {(-1, 0): [(-1, 0)], (0, -1): [(0, -2)], (0, 0): [(0, 0)], \
(1, 0): [(1, 0), (2, 0), (3, 0)], (1, 1): [(2, 2)], (3, -2): [(3, -2)], \
(3, 1): [(3, 1)], (3, 2): [(3, 2)]}
    """
    re_centered = re_center_map(_map, center)
    return {
        reduced: sorted(points, key=get_distance)
        for reduced, points
        in itertools.groupby(sorted(
            re_centered, key=reduce_point), key=reduce_point)
    }


def reduce_point(point):
    """
    >>> reduce_point((0, 0))
    (0, 0)
    >>> reduce_point((0, 1))
    (0, 1)
    >>> reduce_point((0, -1))
    (0, -1)
    >>> reduce_point((1, 0))
    (1, 0)
    >>> reduce_point((-1, 0))
    (-1, 0)
    >>> reduce_point((1, 1))
    (1, 1)
    >>> reduce_point((1, 2))
    (1, 2)
    >>> reduce_point((2, 1))
    (2, 1)
    >>> reduce_point((2, 2))
    (1, 1)
    >>> reduce_point((6, 2))
    (3, 1)
    >>> reduce_point((12, 18))
    (2, 3)
    >>> reduce_point((-12, 18))
    (-2, 3)
    >>> reduce_point((12, -18))
    (2, -3)
    >>> reduce_point((-12, -18))
    (-2, -3)
    """
    if point == (0, 0):
        return 0, 0
    x, y = point
    if x == 0:
        return 0, int(y / abs(y))
    if y == 0:
        return int(x / abs(x)), 0
    gcd = math.gcd(x, y)
    return int(x / gcd), int(y / gcd)


def get_distance(point):
    """
    >>> get_distance((0, 0))
    0.0
    >>> get_distance((3, 4))
    5.0
    >>> get_distance((-3, 4))
    5.0
    >>> get_distance((3, -4))
    5.0
    >>> get_distance((-3, -4))
    5.0
    """
    x, y = point
    return math.sqrt(x * x + y * y)


def re_center_map(_map, center):
    """
    >>> re_center_map([(1, 0), (4, 4)], None)
    [(1, 0), (4, 4)]
    >>> re_center_map([(1, 0), (4, 4)], (0, 0))
    [(1, 0), (4, 4)]
    >>> re_center_map([\
        (1, 0), (4, 0), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (4, 3),\
        (3, 4), (4, 4)], (2, 2))
    [(-1, -2), (2, -2), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (2, 1), \
(1, 2), (2, 2)]
    """
    if not center or center == (0, 0):
        return _map
    center_x, center_y = center
    return [
        (x - center_x, y - center_y)
        for x, y in _map
    ]


def parse_map(map_text):
    """
    >>> parse_map(".#..#\\n.....\\n#####\\n....#\\n...##\\n")
    [(1, 0), (4, 0), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (4, 3), (3, 4), \
(4, 4)]
    """
    lines = map_text.splitlines()
    non_empty_lines = filter(None, (
        line.strip()
        for line in lines
    ))
    return [
        (x, y)
        for y, line in enumerate(non_empty_lines)
        for x, section in enumerate(line)
        if section == '#'
    ]


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
