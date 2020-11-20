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
    intersections = get_intersections(image)
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


OFFSET_MAP = {
    DIRECTION_UP: (0, -1),
    DIRECTION_DOWN: (0, 1),
    DIRECTION_RIGHT: (1, 0),
    DIRECTION_LEFT: (-1, 0),
}


def get_intersections(image):
    """
    >>> get_intersections(\
        "..#..........\\n"\
        "..#..........\\n"\
        "#######...###\\n"\
        "#.#...#...#.#\\n"\
        "#############\\n"\
        "..#...#...#..\\n"\
        "..#####...^..")
    [(2, 2), (2, 4), (6, 4), (10, 4)]
    """
    scaffolds = {
        (x, y)
        for y, line in enumerate(image.splitlines())
        for x, pixel in enumerate(line)
        if pixel in list('#^v<>')
    }

    return sorted(
        (x, y)
        for (x, y) in scaffolds
        if all(
            (x + offset_x, y + offset_y) in scaffolds
            for offset_x, offset_y in OFFSET_MAP.values()
        )
    )


def parse_image(image):
    return "".join(map(chr, image))


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
