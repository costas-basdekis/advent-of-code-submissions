#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_11.part_a import paint_panels
import year_2019.day_09.part_a


def solve(_input=None):
    """
    >>> print("\\n".join(filter(None, (line.strip() for line in solve().splitlines()))))
    #  #   ##  ##  #      ## #### #### #  #
    #  #    # #  # #       #    # #    #  #
    ####    # #  # #       #   #  ###  ####
    #  #    # #### #       #  #   #    #  #
    #  # #  # #  # #    #  # #    #    #  #
    #  #  ##  #  # ####  ##  #### #    #  #
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    program_text = _input
    paint_map = paint_panels(program_text, {(0, 0): 1})

    return f"\n{show_paint_map(paint_map)}"


def show_paint_map(paint_map):
    xs = [point[0] for point in paint_map]
    min_x = min(xs)
    max_x = max(xs)
    ys = [point[1] for point in paint_map]
    min_y = min(ys)
    max_y = max(ys)

    return "\n".join(
        "".join(
            '#' if paint_map.get((x, y), 0) == 1 else ' '
            for x in range(min_x, max_x + 1)
        )
        for y in range(min_y, max_y + 1)
    )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
