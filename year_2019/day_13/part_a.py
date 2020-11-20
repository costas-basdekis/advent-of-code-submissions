#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


TILE_BLOCK = 2


def solve(_input=None):
    """
    >>> solve()
    247
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, output_stream = get_program_result_and_output_extended(_input, [2])
    if len(output_stream) % 3 != 0:
        raise Exception(f"Expected triplets, but got {len(output_stream)}")

    game = {}
    for index in range(0, len(output_stream), 3):
        x, y, tile_id = output_stream[index:index + 3]
        game[(x, y)] = tile_id

    return sum(
        1
        for tile_id in game.values()
        if tile_id == TILE_BLOCK
    )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
