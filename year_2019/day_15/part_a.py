#!/usr/bin/env python3
import doctest
import sys
import click

from utils import get_current_directory
from year_2019.day_05.part_a import InsufficientInputError
from year_2019.day_05.part_b import get_program_result_and_output_extended


def solve(_input=None):
    """
    >>> solve()
    236
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return get_minimum_distance_to_oxygen(play_game(_input))


def run_interactive_program(program_text, endless=False):
    error = None
    input_stream = []

    while True:
        try:
            _, output = get_program_result_and_output_extended(
                program_text, input_stream, error=error)
            if endless:
                raise Exception("Endless interactive program exited")
            yield True, output
            break
        except InsufficientInputError as e:
            error = e

        next_input_or_inputs = yield False, error.output_stream
        if isinstance(next_input_or_inputs, int):
            next_input = next_input_or_inputs
            next_inputs = [next_input]
        else:
            next_inputs = next_input_or_inputs
        input_stream.extend(next_inputs)


def run_interactive_game(program_text=None):
    if program_text is None:
        program_text = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    program = run_interactive_program(program_text, endless=True)
    game = fill_game(None, None, False, game=None)

    def run_handler():
        _, first_output = program.send(None)
        is_visiting, last_command = yield first_output
        while True:
            _, output = program.send(last_command)
            fill_game(last_command, output, is_visiting, game=game)
            is_visiting, last_command = yield output

    handler = run_handler()
    handler.send(None)
    return game, handler


def play_game(program_text=None, interactive=False):
    game, handler = run_interactive_game(program_text)

    def auto_discover():
        for auto_command in COMMANDS_MOVE:
            auto_position = apply_offset(game["position"], auto_command)
            if auto_position in game["map"]:
                continue

            handler.send((False, auto_command))
            if game["position"] != auto_position:
                continue

            handler.send((False, OPPOSITE_MOVE_MAP[auto_command]))

    def get_user_command():
        command = None
        while command is None:
            suggestion = get_suggestion()
            try:
                click.echo(
                    f"Move, show all, or delete"
                    f"{f' (or suggestion: {suggestion})' if suggestion else ''}: ", nl=False)
                user_input = click.getchar()
                click.echo()
            except EOFError:
                return True, None
            if user_input == '\r' and suggestion:
                command = suggestion
            else:
                command = INPUT_COMMAND_MAP.get(user_input)
            if handle_fake_command(command):
                if command == COMMAND_SHOW_ALL:
                    print(show_game(game, max_offset_show=None))
                command = None

        return False, command

    def handle_fake_command(command):
        if command == COMMAND_DELETE:
            fill_game(command, [RESPONSE_DELETE], True, game=game)
            return True
        elif command == COMMAND_MARK:
            fill_game(command, [RESPONSE_MARK], True, game=game)
            return True
        elif command == COMMAND_SHOW_ALL:
            return True

    def get_suggestion():
        neighbour_positions = get_neighbour_positions(game["position"])
        unvisited_neighbour_positions = [
            (position, move_command)
            for position, move_command in neighbour_positions
            if game["map"].get(position) == CONTENT_EMPTY
            and position not in game["visited"]
        ]
        if unvisited_neighbour_positions:
            _, suggestion = unvisited_neighbour_positions[0]
            return suggestion

        if game["map"][game["position"]] == CONTENT_EMPTY:
            return COMMAND_DELETE

        visited_neighbour_positions = [
            (position, move_command)
            for position, move_command in neighbour_positions
            if game["map"].get(position) == CONTENT_EMPTY
            and position in game["visited"]
        ]
        if len(visited_neighbour_positions) == 1:
            _, suggestion = visited_neighbour_positions[0]
            return suggestion

        return None

    while True:
        auto_discover()

        if interactive:
            print(show_game(game))
            should_exit, user_command = get_user_command()
            if should_exit:
                print("Exiting")
                break
            handler.send((True, user_command))
        else:
            auto_command = get_suggestion()
            if auto_command is None:
                break

            if not handle_fake_command(auto_command):
                handler.send((True, auto_command))

    return game


def get_neighbour_positions(position):
    neighbour_positions = [
        (apply_offset(position, move_command), move_command)
        for move_command in COMMANDS_MOVE
    ]
    return neighbour_positions


COMMAND_MARK = -3
COMMAND_SHOW_ALL = -2
COMMAND_DELETE = -1
COMMAND_NORTH = 1
COMMAND_SOUTH = 2
COMMAND_WEST = 3
COMMAND_EAST = 4


COMMANDS_MOVE = [COMMAND_NORTH, COMMAND_SOUTH, COMMAND_EAST, COMMAND_WEST]


OPPOSITE_MOVE_MAP = {
    COMMAND_NORTH: COMMAND_SOUTH,
    COMMAND_SOUTH: COMMAND_NORTH,
    COMMAND_WEST: COMMAND_EAST,
    COMMAND_EAST: COMMAND_WEST,
}


INPUT_COMMAND_MAP = {
    ' ': COMMAND_SHOW_ALL,
    'k': COMMAND_DELETE,
    'm': COMMAND_MARK,
    'w': COMMAND_NORTH,
    'a': COMMAND_WEST,
    's': COMMAND_SOUTH,
    'd': COMMAND_EAST,
    '\x1b[3~': COMMAND_DELETE,
    '\x05': COMMAND_MARK,
    '\x1b[A': COMMAND_NORTH,
    '\x1b[D': COMMAND_WEST,
    '\x1b[B': COMMAND_SOUTH,
    '\x1b[C': COMMAND_EAST,
}


OFFSET_MAP = {
    COMMAND_DELETE: (0, 0),
    COMMAND_MARK: (0, 0),
    COMMAND_NORTH: (0, -1),
    COMMAND_SOUTH: (0, 1),
    COMMAND_WEST: (-1, 0),
    COMMAND_EAST: (1, 0),
}


RESPONSE_WALL = 0
RESPONSE_MOVED = 1
RESPONSE_ARRIVED = 2
RESPONSE_DELETE = 3
RESPONSE_MARK = 4


CONTENT_EMPTY = 'empty'
CONTENT_WALL = 'wall'
CONTENT_OXYGEN = 'oxygen'
CONTENT_UNKNOWN = 'unknown'
CONTENT_DELETED = 'deleted'
CONTENT_MARKED = 'marked'


def fill_game(last_command, output_stream, is_visiting, game=None):
    if game is None:
        game = {
            "position": (0, 0),
            "map": {(0, 0): CONTENT_EMPTY},
            "visited": {(0, 0)},
            "oxygen_location": None,
        }
    if last_command is None:
        if output_stream:
            raise Exception(
                "Got output, even though there was no last command")
        return game

    if len(output_stream) != 1:
        raise Exception(f"Expected a single response {len(output_stream)}")
    response, = output_stream

    target_position = apply_offset(game["position"], last_command)
    if response in [RESPONSE_MOVED, RESPONSE_ARRIVED]:
        new_position = target_position
        if response == RESPONSE_ARRIVED:
            game["oxygen_location"] = new_position
            content = CONTENT_OXYGEN
        else:
            content = CONTENT_EMPTY
    else:
        new_position = game["position"]
        if response == RESPONSE_DELETE:
            if game["map"][target_position] != CONTENT_OXYGEN:
                content = CONTENT_DELETED
            else:
                content = CONTENT_OXYGEN
        elif response == RESPONSE_MARK:
            if game["map"][target_position] != CONTENT_OXYGEN:
                content = CONTENT_MARKED
            else:
                content = CONTENT_OXYGEN
        else:
            content = CONTENT_WALL
    if is_visiting:
        game["visited"].add(target_position)
    game["map"][target_position] = content
    game["position"] = new_position

    return game


def get_minimum_distance_to_oxygen(game):
    oxygen_location = game["oxygen_location"]
    if not oxygen_location:
        raise Exception("Have not found oxygen yet")
    minimum_distances = get_minimum_distances(game)
    if not is_game_fully_discovered(game, minimum_distances):
        raise Exception("Have not discovered everything yet")

    return minimum_distances[oxygen_location]


def is_game_fully_discovered(game, minimum_distances=None):
    if minimum_distances is None:
        minimum_distances = get_minimum_distances(game)

    return not any(
        minimum_distance == -1
        for minimum_distance in minimum_distances.values()
    )


def get_minimum_distances(game):
    minimum_distances = {
        (0, 0): 0,
    }
    search_stack = [(0, 0)]
    visited = set()
    while search_stack:
        position = search_stack.pop(0)
        if position in visited:
            continue
        visited.add(position)
        minimum_distance = minimum_distances[position]
        neighbour_positions = get_neighbour_positions(position)
        next_neighbour_positions = [
            next_position
            for next_position, _ in neighbour_positions
            if game["map"].get(next_position)
            in [CONTENT_EMPTY, CONTENT_OXYGEN, CONTENT_DELETED]
        ]
        search_stack.extend(next_neighbour_positions)
        for next_position in next_neighbour_positions:
            minimum_distances[next_position] = \
                min(minimum_distances.get(next_position, minimum_distance + 1),
                    minimum_distance + 1)
        unknown_neighbour_positions = [
            unknown_position
            for unknown_position, _ in neighbour_positions
            if game["map"].get(unknown_position) == CONTENT_UNKNOWN
        ]
        for unknown_position in unknown_neighbour_positions:
            minimum_distances[unknown_position] = -1

    return minimum_distances


def apply_offset(position, command):
    offset_x, offset_y = OFFSET_MAP[command]
    x, y = position
    return x + offset_x, y + offset_y


CONTENT_SHOW_MAP = {
    CONTENT_EMPTY: '.',
    CONTENT_WALL: click.style('#', bg='black', fg='black'),
    CONTENT_OXYGEN: click.style('O', bg='green'),
    CONTENT_UNKNOWN: click.style('?', bg='red', fg='red'),
    CONTENT_DELETED: click.style('*', bg='magenta', fg='magenta'),
    CONTENT_MARKED: ' ',
}


def show_game(game, max_offset_show=5):
    xs = [x for x, y in game["map"]] or [0]
    min_x, max_x = min(xs), max(xs)
    ys = [y for x, y in game["map"]] or [0]
    min_y, max_y = min(ys), max(ys)
    if max_offset_show is not None:
        x, y = game["position"]
        min_x, max_x = limit_range(min_x, max_x, x, max_offset_show)
        min_y, max_y = limit_range(min_y, max_y, y, max_offset_show)

    return "\n".join([
        "\n".join(
            "".join(
                click.style((
                    'X'
                    if game["position"] == game["oxygen_location"] else
                    'x'
                ), fg='blue')
                if (x, y) == game["position"] else
                CONTENT_SHOW_MAP[game["map"].get((x, y), CONTENT_UNKNOWN)]
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        ),
        f"Current location: {game['position']}",
        f"Oxygen location: {game['oxygen_location']}",
    ])


def limit_range(_min, _max, position, max_offset):
    if _min < position - max_offset and _max > position + max_offset:
        _min = position - max_offset
        _max = position + max_offset
    elif _min < position - max_offset:
        _min = max(_min, _max - 2 * max_offset)
    elif _max > position + max_offset:
        _max = min(_max, _min + 2 * max_offset)

    return _min, _max


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1:] != ['play']:
            raise Exception(f"Only valid argument is 'play'")
        _game = play_game(interactive=False)
        print(show_game(_game, max_offset_show=None))
        if is_game_fully_discovered(_game):
            print("Fully discovered")
            print(f"Minimum steps to oxygen: "
                  f"{get_minimum_distance_to_oxygen(_game)}")
        else:
            print("Couldn't discover everything")
    else:
        if doctest.testmod().failed:
            print("Tests failed")
        else:
            print("Tests passed")
        print("Solution:", solve())
