#!/usr/bin/env python3
import utils

from year_2019.day_05.part_b import get_program_result_and_output_extended
import year_2019.day_09.part_a


TILE_EMPTY = 0
TILE_WALL = 1
TILE_BLOCK = 2
TILE_PADDLE = 3
TILE_BALL = 4


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        247
        """
        _, output_stream = get_program_result_and_output_extended(_input, [])
        game = fill_game(output_stream)

        return sum(
            1
            for tile_id in game.values()
            if tile_id == TILE_BLOCK
        )


def fill_game(output_stream, game=None):
    if len(output_stream) % 3 != 0:
        raise Exception(f"Expected triplets, but got {len(output_stream)}")

    if game is None:
        game = {}
    for index in range(0, len(output_stream), 3):
        x, y, tile_id = output_stream[index:index + 3]
        game[(x, y)] = tile_id

    return game


challenge = Challenge()
challenge.main()
