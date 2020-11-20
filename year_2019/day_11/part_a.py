#!/usr/bin/env python3
import doctest
from collections import defaultdict

from utils import get_current_directory
from year_2019.day_05.part_a import InsufficientInputError
from year_2019.day_05.part_b import get_program_result_and_output_extended


DIRECTION_UP = 'up'
DIRECTION_DOWN = 'down'
DIRECTION_RIGHT = 'right'
DIRECTION_LEFT = 'left'


OFFSET_MAP = {
    DIRECTION_UP: (0, -1),
    DIRECTION_DOWN: (0, 1),
    DIRECTION_LEFT: (-1, 0),
    DIRECTION_RIGHT: (1, 0),
}


ROTATION_CW = 'cw'
ROTATION_CCW = 'ccw'


ROTATION_MAP = {
    (DIRECTION_UP, ROTATION_CW): DIRECTION_RIGHT,
    (DIRECTION_UP, ROTATION_CCW): DIRECTION_LEFT,
    (DIRECTION_DOWN, ROTATION_CW): DIRECTION_LEFT,
    (DIRECTION_DOWN, ROTATION_CCW): DIRECTION_RIGHT,
    (DIRECTION_LEFT, ROTATION_CW): DIRECTION_UP,
    (DIRECTION_LEFT, ROTATION_CCW): DIRECTION_DOWN,
    (DIRECTION_RIGHT, ROTATION_CW): DIRECTION_DOWN,
    (DIRECTION_RIGHT, ROTATION_CCW): DIRECTION_UP,
}


COMMAND_TURN_LEFT = 0
COMMAND_TURN_RIGHT = 1


def solve(_input=None):
    """
    >>> solve()
    1785
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    program_text = _input
    paint_map = paint_panels(program_text)

    return len(paint_map)


def paint_panels(program_text, initial_paint=None):
    position = (0, 0)
    direction = DIRECTION_UP
    paint_map = defaultdict(lambda: 0)
    if initial_paint:
        paint_map.update(initial_paint)
    error = None
    input_stream = []
    while True:
        paint = paint_map[position]
        input_stream.append(paint)
        # print(
        #     f"In {position}, facing {direction}, paint is {paint}, input is "
        #     f"{input_stream}, counter is "
        #     f"{error.input_stream_counter if error else 0}")
        try:
            _, output = get_program_result_and_output_extended(
                program_text, input_stream, error=error)
            # print("Finished")
            break
        except InsufficientInputError as e:
            error = e
        new_output = error.output_stream
        # print(new_output)
        if len(new_output) != 2:
            raise Exception(
                f"Expected 2 new outputs, but got {new_output}")
        new_paint, command = new_output
        if new_paint not in [0, 1]:
            raise Exception(
                f"Expected paint to be 0 or 1, but was '{new_paint}'")
        paint_map[position] = new_paint
        if command == COMMAND_TURN_LEFT:
            rotation = ROTATION_CCW
        elif command == COMMAND_TURN_RIGHT:
            rotation = ROTATION_CW
        else:
            raise Exception(f"Unknown rotation command '{command}'")
        direction = rotate(direction, rotation)
        position = move(position, direction)
        # paint = paint_map[position]
        # print(f"In {position}, facing {direction}, paint is {paint}")

    return paint_map


def rotate(direction, rotation):
    """
    >>> rotate(DIRECTION_UP, ROTATION_CW)
    'right'
    >>> rotate(rotate(DIRECTION_UP, ROTATION_CW), ROTATION_CW)
    'down'
    >>> rotate(rotate(rotate(\
        DIRECTION_UP, ROTATION_CW), ROTATION_CW), ROTATION_CW)
    'left'
    >>> rotate(rotate(rotate(rotate(\
        DIRECTION_UP, ROTATION_CW), ROTATION_CW), ROTATION_CW), ROTATION_CW)
    'up'
    >>> rotate(rotate(rotate(rotate(\
        DIRECTION_UP, ROTATION_CW), ROTATION_CCW), ROTATION_CW), ROTATION_CCW)
    'up'
    """
    return ROTATION_MAP[(direction, rotation)]


def move(position, direction):
    """
    >>> move((0, 0), DIRECTION_UP)
    (0, -1)
    >>> move((0, -1), DIRECTION_DOWN)
    (0, 0)
    >>> move((0, -1), DIRECTION_LEFT)
    (-1, -1)
    """
    offset_x, offset_y = OFFSET_MAP[direction]
    x, y = position
    return x + offset_x, y + offset_y



if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
