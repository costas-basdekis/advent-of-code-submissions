#!/usr/bin/env python3
import doctest
import sys

from utils import get_current_directory
from year_2019.day_05.part_a import InsufficientInputError
from year_2019.day_05.part_b import get_program_result_and_output_extended
from year_2019.day_12.part_a import sign
from year_2019.day_13.part_a import fill_game, TILE_EMPTY, TILE_WALL,\
    TILE_BLOCK, TILE_PADDLE, TILE_BALL


def solve(_input=None):
    """
    >>> solve()
    12954
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    game = play_game(_input)
    return game.get((-1, 0))


def play_game(program_text=None, interactive=False):
    if program_text is None:
        program_text = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    error = None
    input_stream = []
    game = {}
    while True:
        try:
            _, output = get_program_result_and_output_extended(
                program_text, input_stream, substitutions={0: 2}, error=error)
            fill_game(output, game)
            # print("Finished")
            break
        except InsufficientInputError as e:
            error = e
        new_output = error.output_stream
        fill_game(new_output, game)
        tiles_positions = get_game_tile_positions(game)
        paddle_position, _ = tiles_positions[TILE_PADDLE]
        ball_position, _ = tiles_positions[TILE_BALL]
        suggestion = sign(ball_position - paddle_position)
        if interactive:
            print(show_game(game))
            user_input = None
            while user_input is None \
                    or user_input.strip() not in ['-1', '0', '1', '']:
                try:
                    options_with_suggestion = '/'.join(
                        f'[{option}]'
                        if option == suggestion else
                        f'{option}'
                        for option in [-1, 0, 1]
                    )
                    user_input = input(
                        f"Enter (paddle={paddle_position}, "
                        f"ball={ball_position}) {options_with_suggestion}:")
                except EOFError:
                    print("Exiting")
                    return None
            if user_input == '':
                paddle_input = suggestion
            else:
                paddle_input = int(user_input)
        else:
            paddle_input = suggestion
        input_stream.append(paddle_input)

    return game


def get_game_tile_positions(game, interesting_tiles=(TILE_PADDLE, TILE_BALL)):
    return {
        tile_id: position
        for position, tile_id in game.items()
        if tile_id in interesting_tiles
    }


TILE_SHOW_MAP = {
    TILE_EMPTY: ' ',
    TILE_WALL: 'X',
    TILE_BLOCK: 'O',
    TILE_PADDLE: '-',
    TILE_BALL: '*',
}


def show_game(game):
    xs = [x for x, y in game if (x, y) != (-1, 0)]
    min_x, max_x = min(xs), max(xs)
    ys = [y for x, y in game if (x, y) != (-1, 0)]
    min_y, max_y = min(ys), max(ys)

    return "\n".join([
        f"Score: {game.get((-1, 0))}",
        "\n".join(
            "".join(
                TILE_SHOW_MAP[game[(x, y)]]
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        ),
    ])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1:] != ['play']:
            raise Exception(f"Only valid argument is 'play'")
        play_game(interactive=True)
    else:
        if doctest.testmod().failed:
            print("Tests failed")
        else:
            print("Tests passed")
        print("Solution:", solve())