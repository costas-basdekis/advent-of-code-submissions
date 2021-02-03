#!/usr/bin/env python3
import utils

from year_2019.day_03.part_a import get_points_for_lines, get_cross_points


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3454
        >>> Challenge().solve(\
            "R75,D30,R83,U83,L12,D49,R71,U7,L72"\
            "\\nU62,R66,U55,R34,D71,R55,D58,R83")
        610
        """
        return get_smallest_cross_point_total_steps(_input)


def get_smallest_cross_point_total_steps(_input):
    """
    >>> get_smallest_cross_point_total_steps(\
        "R8,U5,L5,D3"\
        "\\nU7,R6,D4,L4")
    30
    >>> get_smallest_cross_point_total_steps(\
        "R75,D30,R83,U83,L12,D49,R71,U7,L72"\
        "\\nU62,R66,U55,R34,D71,R55,D58,R83")
    610
    >>> get_smallest_cross_point_total_steps(\
        "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51"\
        "\\nU98,R91,D20,R16,D67,R40,U7,R15,U6,R7")
    410
    """
    points_per_line = get_points_for_lines(_input)
    cross_points = get_cross_points(_input)
    return min(
        sum(
            get_steps_for_point_in_line(points, cross_point)
            for points in points_per_line
        )
        for cross_point in cross_points
    )


def get_steps_for_point_in_line(points, point):
    """
    >>> get_steps_for_point_in_line(['a', 'b', 'c'], 'a')
    1
    >>> get_steps_for_point_in_line(['a', 'b', 'c'], 'b')
    2
    >>> get_steps_for_point_in_line(['a', 'b', 'c'], 'c')
    3
    >>> get_steps_for_point_in_line(['a', 'b', 'c'], 'd')
    Traceback (most recent call last):
    ...
    Exception: Could not find point
    """
    if point not in points:
        raise Exception("Could not find point")
    return points.index(point) + 1


Challenge.main()
challenge = Challenge()
