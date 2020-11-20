#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


def solve(_input=None):
    """
    >>> solve()
    8928
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, output = get_program_result_and_output_extended(_input, [])
    image = parse_image(output)
    scaffolds, _, _ = get_scaffolds_start_position_and_direction(image)
    intersections = get_intersections(scaffolds)
    return get_intersections_calibration(intersections)


def get_intersections_calibration(intersections):
    """
    >>> get_intersections_calibration([(2, 2), (2, 4), (6, 4), (10, 4)])
    76
    """
    return sum(map(get_intersection_alignment_parameter, intersections))


def get_intersection_alignment_parameter(intersection):
    """
    >>> get_intersection_alignment_parameter((2, 2))
    4
    >>> get_intersection_alignment_parameter((2, 4))
    8
    >>> get_intersection_alignment_parameter((6, 4))
    24
    >>> get_intersection_alignment_parameter((10, 4))
    40
    """
    x, y = intersection
    return x * y


DIRECTION_UP = 'up'
DIRECTION_DOWN = 'down'
DIRECTION_RIGHT = 'right'
DIRECTION_LEFT = 'left'


DIRECTIONS = [
    DIRECTION_UP,
    DIRECTION_DOWN,
    DIRECTION_RIGHT,
    DIRECTION_LEFT,
]


OFFSET_MAP = {
    DIRECTION_UP: (0, -1),
    DIRECTION_DOWN: (0, 1),
    DIRECTION_RIGHT: (1, 0),
    DIRECTION_LEFT: (-1, 0),
}


def get_intersections(scaffolds):
    """
    >>> get_intersections(get_scaffolds_start_position_and_direction(\
        "..#..........\\n"\
        "..#..........\\n"\
        "#######...###\\n"\
        "#.#...#...#.#\\n"\
        "#############\\n"\
        "..#...#...#..\\n"\
        "..#####...^..")[0])
    [(2, 2), (2, 4), (6, 4), (10, 4)]
    """
    return sorted(
        scaffold
        for scaffold in scaffolds
        if all(
            neighbour in scaffolds
            for neighbour in get_neighbour_positions(scaffold)
        )
    )


def get_neighbour_positions(position):
    """
    >>> get_neighbour_positions((0, 0))
    [(0, -1), (0, 1), (1, 0), (-1, 0)]
    >>> get_neighbour_positions((-3, 4))
    [(-3, 3), (-3, 5), (-2, 4), (-4, 4)]
    """
    x, y = position
    return [
        (x + offset_x, y + offset_y)
        for offset_x, offset_y in OFFSET_MAP.values()
    ]


POSITION_PARSING_MAP = {
    '^': DIRECTION_UP,
    'v': DIRECTION_DOWN,
    '>': DIRECTION_RIGHT,
    '<': DIRECTION_LEFT,
}


def get_scaffolds_start_position_and_direction(image):
    """
    >>> sorted(get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##^\\n")[0])
    [(0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    >>> get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##^\\n")[1]
    (2, 2)
    >>> get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##^\\n")[2]
    'up'
    >>> get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##^\\n")[1:]
    ((2, 2), 'up')
    >>> get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##>\\n")[1:]
    ((2, 2), 'right')
    >>> get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##v\\n")[1:]
    ((2, 2), 'down')
    >>> get_scaffolds_start_position_and_direction(\
        "..#\\n"\
        "..#\\n"\
        "##<\\n")[1:]
    ((2, 2), 'left')
    >>> get_scaffolds_start_position_and_direction(\
        "..#..........\\n"\
        "..#..........\\n"\
        "#######...###\\n"\
        "#.#...#...#.#\\n"\
        "#############\\n"\
        "..#...#...#..\\n"\
        "..#####...^..")[1:]
    ((10, 6), 'up')
    """
    positions = [
        ((x, y), pixel)
        for y, line in enumerate(image.splitlines())
        for x, pixel in enumerate(line)
        if pixel in list('^v<>')
    ]
    if len(positions) != 1:
        raise Exception(
            f"Expected a single start position, but got {len(positions)}")

    (start_position, direction_str), = positions
    direction = POSITION_PARSING_MAP[direction_str]

    scaffolds = {
        (x, y)
        for y, line in enumerate(image.splitlines())
        for x, pixel in enumerate(line)
        if pixel in list('#^v<>')
    }

    return scaffolds, start_position, direction


def parse_image(image):
    return "".join(map(chr, image))


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
