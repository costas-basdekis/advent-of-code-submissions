#!/usr/bin/env python3
import math

import utils

from year_2019.day_10.part_a import parse_map, group_map_by_gcd,\
    get_position_with_best_visibility

PI = math.asin(1) * 2


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        616
        """
        best_position, _ = get_position_with_best_visibility(parse_map(_input))
        vapourisation_order = get_vapourisation_order(
            parse_map(_input), best_position)
        vapourised_200 = vapourisation_order[199]
        x, y = vapourised_200
        return x * 100 + y


def get_vapourisation_order(_map, center):
    """
    >>> map_a = parse_map(\
        ".#....#####...#..\\n##...##.#####..##\\n##...#...#.#####."\
        "\\n..#.....X...###..\\n..#.#.....#....##")
    >>> set(map_a) == set(get_vapourisation_order(map_a, (8, 3)))
    True
    >>> set(map_a) == set(get_vapourisation_order(map_a, (10, 2)))
    True
    >>> map_b = parse_map(\
        ".#..##.###...#######\\n##.############..##.\\n.#.######.########.#"\
        "\\n.###.#######.####.#.\\n#####.##.#.##.###.##\\n..#####..#.#########"\
        "\\n####################\\n#.####....###.#.#.##\\n##.#################"\
        "\\n#####.##.###..####..\\n..######..##.#######\\n####.##.####...##..#"\
        "\\n.#####..#.######.###\\n##...#.##########...\\n#.##########.#######"\
        "\\n.####.#.###.###.#.##\\n....##.##.###..#####\\n.#.#.###########.###"\
        "\\n#.#.#.#####.####.###\\n###.##.####.##.#..##")
    >>> vo_b = get_vapourisation_order(map_b, (11, 13))
    >>> vo_b[:3] + [vo_b[9], vo_b[19], vo_b[49], vo_b[99]] + vo_b[198:201] + [vo_b[298]]
    [(11, 12), (12, 1), (12, 2), (12, 8), (16, 0), (16, 9), (10, 16), (9, 6), \
(8, 2), (10, 9), (11, 1)]
    """
    points_left = set(_map) - {center}
    vapourisation_order = []
    while points_left:
        visible_points = get_visible_asteroids(points_left, center)
        sorted_points = sort_points_around_center(visible_points, center)
        if not sorted_points:
            raise Exception("Could not see any points, even though some exist")
        vapourisation_order += sorted_points
        points_left -= set(sorted_points)

    return vapourisation_order


def vapourise_asteroids(_map, points):
    """
    >>> vapourise_asteroids(\
        [(0, -2), (2, -2), (2, 0), (2, 2), (0, 2)], [(2, -2), (0, 2)])
    [(0, -2), (2, 0), (2, 2)]
    """
    return [
        point
        for point in _map
        if point not in points
    ]


def sort_points_around_center(points, center):
    """
    >>> sort_points_around_center([\
        (0, -2), (2, -2), (2, 0), (2, 2), (0, 2), (-2, 2), (-2, 0), (-2, -2)],\
        (0, 0))
    [(0, -2), (2, -2), (2, 0), (2, 2), (0, 2), (-2, 2), (-2, 0), (-2, -2)]
    >>> sort_points_around_center(reversed([\
        (0, -2), (2, -2), (2, 0), (2, 2), (0, 2), (-2, 2), (-2, 0), (-2, -2)]),\
        (0, 0))
    [(0, -2), (2, -2), (2, 0), (2, 2), (0, 2), (-2, 2), (-2, 0), (-2, -2)]
    """
    return sorted(
        points, key=lambda point: get_point_angle(point, center))


def get_point_angle(point, center):
    """
    >>> get_point_angle((0, -2), None) / (PI / 2)
    0.0
    >>> get_point_angle((2, -2), None) / (PI / 2)
    0.5
    >>> get_point_angle((2, 0), None) / (PI / 2)
    1.0
    >>> get_point_angle((2, 2), None) / (PI / 2)
    1.5
    >>> get_point_angle((0, 2), None) / (PI / 2)
    2.0
    >>> get_point_angle((-2, 2), None) / (PI / 2)
    2.5
    >>> get_point_angle((-2, 0), None) / (PI / 2)
    3.0
    >>> get_point_angle((-2, -2), None) / (PI / 2)
    3.5
    """
    point = re_center_point(point, center)

    x, y = point
    angle = math.atan2(y, x) + PI / 2
    if angle < 0:
        angle += PI * 2

    return angle


def get_visible_asteroids(_map, center):
    """
    >>> sorted(get_visible_asteroids(parse_map(\
        ".#..#\\n.....\\n#####\\n....#\\n...##\\n"), (3, 4)))
    [(0, 2), (1, 2), (2, 2), (3, 2), (4, 0), (4, 2), (4, 3), (4, 4)]
    """
    return [
        un_center_point(group[0], center)
        for gdc, group in group_map_by_gcd(_map, center).items()
        if gdc != (0, 0)
    ]


def re_center_point(point, center):
    """
    >>> re_center_point((0, 0), (0, 0))
    (0, 0)
    >>> re_center_point((0, 0), (2, 3))
    (-2, -3)
    >>> re_center_point((2, 3), (0, 0))
    (2, 3)
    >>> re_center_point((2, 3), (1, 1))
    (1, 2)
    >>> re_center_point((2, 3), (-3, 4))
    (5, -1)
    """
    if not center or center == (0, 0):
        return point
    x, y = point
    center_x, center_y = center
    return x - center_x, y - center_y


def un_center_point(point, center):
    """
    >>> un_center_point((0, 0), (0, 0))
    (0, 0)
    >>> un_center_point((0, 0), (2, 3))
    (2, 3)
    >>> un_center_point((2, 3), (0, 0))
    (2, 3)
    >>> un_center_point((2, 3), (1, 1))
    (3, 4)
    >>> un_center_point((2, 3), (-3, 4))
    (-1, 7)
    """
    if not center or center == (0, 0):
        return point
    center_x, center_y = center
    return re_center_point(point, (-center_x, -center_y))


challenge = Challenge()
challenge.main()
