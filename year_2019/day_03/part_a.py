#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        217
        >>> Challenge().solve(\
            "R75,D30,R83,U83,L12,D49,R71,U7,L72"\
            "\\nU62,R66,U55,R34,D71,R55,D58,R83")
        159
        """
        return get_smallest_cross_point_distance(_input)


def get_smallest_cross_point_distance(_input):
    """
    >>> get_smallest_cross_point_distance(\
        "R8,U5,L5,D3"\
        "\\nU7,R6,D4,L4")
    6
    >>> get_smallest_cross_point_distance(\
        "R75,D30,R83,U83,L12,D49,R71,U7,L72"\
        "\\nU62,R66,U55,R34,D71,R55,D58,R83")
    159
    >>> get_smallest_cross_point_distance(\
        "R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51"\
        "\\nU98,R91,D20,R16,D67,R40,U7,R15,U6,R7")
    135
    """
    points = get_cross_points(_input)
    return min(map(get_manhattan_distance, points))


def get_manhattan_distance(point):
    """
    >>> get_manhattan_distance((0, 0))
    0
    >>> get_manhattan_distance((3, 0))
    3
    >>> get_manhattan_distance((0, 3))
    3
    >>> get_manhattan_distance((3, 3))
    6
    >>> get_manhattan_distance((-3, 3))
    6
    >>> get_manhattan_distance((3, -3))
    6
    >>> get_manhattan_distance((-3, -3))
    6
    """
    x, y = point
    return abs(x) + abs(y)


def get_cross_points(_input):
    """
    >>> sorted(get_cross_points(\
        "R8,U5,L5,D3"\
        "\\nU7,R6,D4,L4"))
    [(3, -3), (6, -5)]
    """
    points_per_line = get_points_for_lines(_input)
    common_points = set(points_per_line[0])
    for points in points_per_line[1:]:
        common_points &= set(points)

    return common_points


def get_points_for_lines(_input):
    """
    >>> get_points_for_lines("R2,D2,R2\\nR2,D2,U2")
    [[(1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)], \
[(1, 0), (2, 0), (2, 1), (2, 2), (2, 1), (2, 0)]]
    """
    lines = _input.splitlines()
    non_empty_lines = list(filter(None, lines))
    if not non_empty_lines:
        raise Exception("No lines were passed in")
    points_per_line = list(map(get_points_for_line, non_empty_lines))

    return points_per_line


def get_points_for_line(line):
    """
    >>> get_points_for_line("R2,D2,R2")
    [(1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2)]
    >>> get_points_for_line("R2,D2,U2")
    [(1, 0), (2, 0), (2, 1), (2, 2), (2, 1), (2, 0)]
    """
    move_texts = line.split(",")
    position = (0, 0)
    points = []
    for move_text in move_texts:
        position, points = move_and_add_points(position, move_text, points)

    return points


MOVE_MULTIPLIERS = {
    'R': (1, 0),
    'L': (-1, 0),
    'U': (0, -1),
    'D': (0, 1),
}


def move_and_add_points(position, move_text, points):
    """
    >>> move_and_add_points((0, 0), "R1", [])
    ((1, 0), [(1, 0)])
    >>> move_and_add_points((0, 0), "R4", [])
    ((4, 0), [(1, 0), (2, 0), (3, 0), (4, 0)])
    >>> move_and_add_points((0, 0), "L4", [])
    ((-4, 0), [(-1, 0), (-2, 0), (-3, 0), (-4, 0)])
    >>> move_and_add_points((0, 0), "U4", [])
    ((0, -4), [(0, -1), (0, -2), (0, -3), (0, -4)])
    >>> move_and_add_points((0, 0), "D4", [])
    ((0, 4), [(0, 1), (0, 2), (0, 3), (0, 4)])
    """
    move_direction_text, distance_text = move_text[0], move_text[1:]
    if move_direction_text not in MOVE_MULTIPLIERS:
        raise Exception(f"Unknown direction '{move_direction_text}'")
    move_multiplier_x, move_multiplier_y = MOVE_MULTIPLIERS[move_direction_text]
    distance = int(distance_text)
    for _ in range(distance):
        x, y = position
        position = (
            x + move_multiplier_x,
            y + move_multiplier_y,
        )
        points.append(position)
    return position, points


challenge = Challenge()
challenge.main()
