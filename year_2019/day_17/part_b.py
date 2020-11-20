#!/usr/bin/env python3
import doctest
import itertools

from utils import get_current_directory
from year_2019.day_05.part_b import get_program_result_and_output_extended
from year_2019.day_17.part_a import DIRECTION_UP, DIRECTION_DOWN,\
    DIRECTION_RIGHT, DIRECTION_LEFT, get_intersections,\
    get_neighbour_positions, get_scaffolds_start_position_and_direction, OFFSET_MAP, parse_image


def solve(_input=None):
    """
    >>> solve()
    42
    """
    """
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6,R,12,L,10,L,4,L,6,L,10,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6'
    'L,6,R,12'
    'L,10,L,4'
    'L,6'
    'L,10'
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6,R,12,L,10,L,4,L,6,L,10,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6'
    'L,10,L,10,L,4'
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,A,L,6,R,12,L,10,L,4,L,6,A,L,6,L,6,R,12,L,6,A,L,6'
    'A,A,B,C,A,A,B,C,A,C,D,B,A,B,C,D,B,C,A,C,D,B,C'
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6,R,12,L,10,L,4,L,6,L,10,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6'
    'L,6,R,12'
    'L,10,L,4'
    'L,10,L,4,L,6'
    'L,6,L,10'
    'A,A,C,A,A,C,A,D,B,A,B,D,C,A,D,C'
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6,R,12,L,10,L,4,L,6,L,10,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6'
    'L,6'
    'R,12'
    'L,10'
    'L,4'
    'A,B,A,B,C,D,A,A,B,A,B,C,D,A,A,B,A,C,C,D,A,B,C,D,A,C,C,D,A,A,B,A,C,C,D,A'
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6,R,12,L,10,L,4,L,6,L,10,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,10,L,4,L,6'
    'L,6,R,12'
    'A,A,L,10,L,4,L,6,A,A,L,10,L,4,L,6,A,L,6,L,10,L,10,L,4,A,L,10,L,4,L,6,L,10,L,10,L,4,L,6,A,L,6,L,10,L,10,L,4,L,6'
    'L,6,L,10,L,10,L,4'
    'A,A,L,10,L,4,L,6,A,A,L,10,L,4,L,6,A,B,A,L,10,L,4,B,L,6,A,B,L,6'
    """
    """
..........................#####..................
..........................#...#..................
..........................#...#..................
..........................#...#..................
..........................#...#..................
..........................#...#..................
..........................#######................
..............................#.#................
............................###########..........
............................#.#.#.....#..........
..................#############.#.....#..........
..................#.........#...#.....#..........
..................#.........#######...#..........
..................#.............#.#...#..........
..................#.............#.#...#..........
..................#.............#.#...#..........
......#############.............#.#...#..........
......#.........................#.#...#..........
###########.....................#######..........
#.....#...#.......................#..............
#.....#...#.......................#...#######....
#.....#...#.......................#...#.....#....
#######...#.......................#...#.....#....
..........#.......................#...#.....#....
..........#.......................###########....
..........#...........................#..........
..........#...........................#...#######
..........#...........................#...#.....#
..........#.........................#####.#.....#
..........#.........................#.#.#.#.....#
..........#######...................#.###########
................#...................#...#.#......
................#.............#############......
................#.............#.....#...#........
................#.............#.....#...#........
................#.............#.........#........
................#.............#.........#........
................#.............#.........#........
................#.............###########........
................#................................
................#................................
................#................................
................######^..........................
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    image = get_image_from_program_text(_input)
    movement_commands_text = get_movement_commands_text_from_image(image)
    routines = find_routine_and_functions_for_movement_commands(
        movement_commands_text.replace('12', '6,6').replace('10', '4,6').replace('4', '1,1,1,1').replace('6', '1,1,1,1,1,1'))
    if not routines:
        raise Exception("Could not find routines")

    routine_text, function_texts = list(sorted(routines, key=lambda rtft: len(rtft[0])))[0]
    function_texts = {
        name: function_text.replace('1,1,1,1,1,1', '6').replace('1,1,1,1', '4').replace('6,6', '12').replace('1,1', '2')
        for name, function_text in function_texts.items()
    }

    return routine_text, function_texts


def find_routine_and_functions_for_movement_commands(movement_commands):
    """
    >>> solution_a = ('A,B,C,B,A,C', {'A': 'R,8,R,8', 'B': 'R,4,R,4,R,8', \
        'C': 'L,6,L,2'})
    >>> movement_commands_a = get_movement_commands_text_from_image(\
        "#######...#####\\n"\
        "#.....#...#...#\\n"\
        "#.....#...#...#\\n"\
        "......#...#...#\\n"\
        "......#...###.#\\n"\
        "......#.....#.#\\n"\
        "^########...#.#\\n"\
        "......#.#...#.#\\n"\
        "......#########\\n"\
        "........#...#..\\n"\
        "....#########..\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#####......")
    >>> routines_a = find_routine_and_functions_for_movement_commands(\
        movement_commands_a)
    >>> set(routines_a[0][0]) == set('ABC,') if routines_a else None
    True
    >>> solution_a in routines_a
    True
    >>> all(\
        expand_main_routine(routine_text, function_texts) \
        == movement_commands_a \
        for routine_text, function_texts in routines_a\
    )
    True
    """
    max_length = 80
    without_commas = movement_commands.replace(',', '')
    possible_functions_without_commas = [
        (a, b, c)
        for a, b, c, remaining_after_a_b_c in [
            (a, b, c, remaining_after_a_b_c)
            for a, b, remaining_after_a_b in [
                (a, b, remaining_after_a_b)
                for a, remaining_after_a in [
                    (a, remaining_after_a)
                    for a in (
                        without_commas[:length_a]
                        for length_a
                        in range(1, min(max_length + 1, len(without_commas)))
                    )
                    for remaining_after_a
                    in list(filter(None, without_commas.split(a))) or ['']
                ]
                for b in (
                    remaining_after_a[:length_b]
                    for length_b
                    in range(1, min(max_length + 1, len(remaining_after_a)))
                )
                for remaining_after_a_b
                in list(filter(None, remaining_after_a.split(b))) or ['']
            ]
            for c in (
                remaining_after_a_b[:length_c]
                for length_c
                in range(1, min(max_length + 1, len(remaining_after_a_b)))
            )
            for remaining_after_a_b_c
            in list(filter(None, remaining_after_a_b.split(c))) or ['']
        ]
    ]
    all_possible_functions_without_commas = {
        (a, b, c)
        for triplet in possible_functions_without_commas
        if len(set(triplet)) == 3
        for a, b, c in itertools.permutations(triplet)
    }
    functions_without_commas = [
        (a, b, c)
        for a, b, c in all_possible_functions_without_commas
        if not (
            without_commas
            .replace(a, '|')
            .replace(b, '|')
            .replace(c, '|')
            .replace('|', '')
        )
        and len(
            without_commas
            .replace(a, 'A')
            .replace(b, 'B')
            .replace(c, 'C')
        ) <= max_length
    ]
    if not functions_without_commas:
        return []

    bracketed_routines_without_commas = {
        "|".join(sorted([a, b, c])): (
            without_commas
            .replace(a, 'A')
            .replace(b, 'B')
            .replace(c, 'C')
            .replace('A', f"({a})")
            .replace('B', f"({b})")
            .replace('C', f"({c})")
        )
        for a, b, c in functions_without_commas
    }

    all_permutations_of_functions_without_commas = {
        (a, b, c)
        for triplet in functions_without_commas
        for a, b, c in itertools.permutations(triplet)
    }

    def get_routine(a, b, c):
        _hash = "|".join(sorted([a, b, c]))
        bracketed_routine = bracketed_routines_without_commas[_hash]
        return ",".join(
            bracketed_routine
            .replace(f"({a})", 'A')
            .replace(f"({b})", 'B')
            .replace(f"({c})", 'C')
        )

    return [
        (get_routine(a, b, c), {
            'A': ",".join(a),
            'B': ",".join(b),
            'C': ",".join(c),
        })
        for a, b, c in all_permutations_of_functions_without_commas
    ]


def get_image_from_program_text(program_text=None):
    if program_text is None:
        program_text = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    _, output = get_program_result_and_output_extended(program_text, [])
    image = parse_image(output)

    return image


def get_movement_commands_text_from_image(image):
    """
    >>> get_movement_commands_text_from_image(\
        "#######...#####\\n"\
        "#.....#...#...#\\n"\
        "#.....#...#...#\\n"\
        "......#...#...#\\n"\
        "......#...###.#\\n"\
        "......#.....#.#\\n"\
        "^########...#.#\\n"\
        "......#.#...#.#\\n"\
        "......#########\\n"\
        "........#...#..\\n"\
        "....#########..\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#####......")
    'R,8,R,8,R,4,R,4,R,8,L,6,L,2,R,4,R,4,R,8,R,8,R,8,L,6,L,2'
    >>> get_movement_commands_text_from_image(get_image_from_program_text())
    'L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,6,R,12,L,10,L,4,L,6,L,6,R,12,L,\
6,L,10,L,10,L,4,L,6,R,12,L,10,L,4,L,6,L,10,L,10,L,4,L,6,L,6,R,12,L,6,L,10,L,\
10,L,4,L,6'
    """
    scaffolds, start_position, start_direction = \
        get_scaffolds_start_position_and_direction(image)
    movement_commands = get_movement_commands(
        get_scaffolds_order(scaffolds, start_position), start_direction)
    return ",".join(map(str, movement_commands))


def expand_main_routine(routine_text, function_texts):
    """
    >>> expand_main_routine('A,B,C,B,A,C', \
        {'A': 'R,8,R,8', 'B': 'R,4,R,4,R,8', 'C': 'L,6,L,2'})
    'R,8,R,8,R,4,R,4,R,8,L,6,L,2,R,4,R,4,R,8,R,8,R,8,L,6,L,2'
    """
    routine = routine_text.split(',')
    functions = {
        name: function_text.split(',')
        for name, function_text in function_texts.items()
    }
    replaced_routine = sum((
        functions[name]
        for name in routine
    ), [])

    return ','.join(replaced_routine)


def get_movement_commands(scaffolds_order, start_direction):
    """
    >>> _scaffolds, _start_position, _start_direction = \
        get_scaffolds_start_position_and_direction(\
        "#######...#####\\n"\
        "#.....#...#...#\\n"\
        "#.....#...#...#\\n"\
        "......#...#...#\\n"\
        "......#...###.#\\n"\
        "......#.....#.#\\n"\
        "^########...#.#\\n"\
        "......#.#...#.#\\n"\
        "......#########\\n"\
        "........#...#..\\n"\
        "....#########..\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#####......")
    >>> get_movement_commands(get_scaffolds_order(\
        _scaffolds, _start_position), _start_direction)
    ['R', 8, 'R', 8, 'R', 4, 'R', 4, 'R', 8, 'L', 6, 'L', 2, 'R', 4, 'R', 4, \
'R', 8, 'R', 8, 'R', 8, 'L', 6, 'L', 2]
    >>> get_movement_commands(get_scaffolds_order(\
        _scaffolds, _start_position), DIRECTION_RIGHT)
    [8, 'R', 8, 'R', 4, 'R', 4, 'R', 8, 'L', 6, 'L', 2, 'R', 4, 'R', 4, \
'R', 8, 'R', 8, 'R', 8, 'L', 6, 'L', 2]
    """
    directions = [
        DIRECTION_FROM_OFFSET_MAP[(get_offset(previous, current))]
        for previous, current in zip(scaffolds_order, scaffolds_order[1:])
    ]
    grouped_directions = [(start_direction, 1)] + [
        (direction, len(list(count)))
        for direction, count in itertools.groupby(directions)
    ]
    commands = sum((
        [get_direction_change_command(previous_direction, current_direction),
         current_count]
        for (previous_direction, _), (current_direction, current_count)
        in zip(grouped_directions, grouped_directions[1:])
    ), [])
    if not commands:
        return []

    first_command = commands[0]
    if not first_command:
        commands = commands[1:]

    return commands


COMMAND_RIGHT = "R"
COMMAND_LEFT = "L"


DIRECTION_FROM_OFFSET_MAP = {
    (0, -1): DIRECTION_UP,
    (0, 1): DIRECTION_DOWN,
    (1, 0): DIRECTION_RIGHT,
    (-1, 0): DIRECTION_LEFT,
}


DIRECTION_CHANGE_TO_COMMAND_MAP = {
    DIRECTION_UP: {
        DIRECTION_UP: None,
        DIRECTION_RIGHT: COMMAND_RIGHT,
        DIRECTION_LEFT: COMMAND_LEFT,
    },
    DIRECTION_DOWN: {
        DIRECTION_DOWN: None,
        DIRECTION_RIGHT: COMMAND_LEFT,
        DIRECTION_LEFT: COMMAND_RIGHT,
    },
    DIRECTION_RIGHT: {
        DIRECTION_UP: COMMAND_LEFT,
        DIRECTION_DOWN: COMMAND_RIGHT,
        DIRECTION_RIGHT: None,
    },
    DIRECTION_LEFT: {
        DIRECTION_UP: COMMAND_RIGHT,
        DIRECTION_DOWN: COMMAND_LEFT,
        DIRECTION_LEFT: None,
    },
}


def get_direction_change_command(previous, current):
    """
    >>> get_direction_change_command(DIRECTION_UP, DIRECTION_RIGHT)
    'R'
    >>> get_direction_change_command(DIRECTION_RIGHT, DIRECTION_UP)
    'L'
    >>> get_direction_change_command(DIRECTION_RIGHT, DIRECTION_RIGHT)
    >>> get_direction_change_command(DIRECTION_RIGHT, DIRECTION_LEFT)
    Traceback (most recent call last):
    ...
    Exception: Cannot change directions from right to left
    >>> right_rotations = [DIRECTION_UP, DIRECTION_RIGHT, DIRECTION_DOWN, \
        DIRECTION_LEFT, DIRECTION_UP]
    >>> {\
        get_direction_change_command(_previous, _current) \
        for _previous, _current in zip(right_rotations, right_rotations[1:])\
    }
    {'R'}
    >>> left_rotations = list(reversed(right_rotations))
    >>> {\
        get_direction_change_command(_previous, _current) \
        for _previous, _current in zip(left_rotations, left_rotations[1:])\
    }
    {'L'}
    >>> {\
        get_direction_change_command(item, item) \
        for item in left_rotations \
    }
    {None}
    """
    if current not in DIRECTION_CHANGE_TO_COMMAND_MAP[previous]:
        raise Exception(
            f"Cannot change directions from {previous} to {current}")

    return DIRECTION_CHANGE_TO_COMMAND_MAP[previous][current]


def get_scaffolds_order(scaffolds, start_position):
    """
    >>> _scaffolds, _start_position, _ = \
        get_scaffolds_start_position_and_direction(\
        "#######...#####\\n"\
        "#.....#...#...#\\n"\
        "#.....#...#...#\\n"\
        "......#...#...#\\n"\
        "......#...###.#\\n"\
        "......#.....#.#\\n"\
        "^########...#.#\\n"\
        "......#.#...#.#\\n"\
        "......#########\\n"\
        "........#...#..\\n"\
        "....#########..\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#...#......\\n"\
        "....#####......")
    >>> _scaffolds_order = get_scaffolds_order(_scaffolds, _start_position)
    >>> _scaffolds_order
    [(0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), \
(8, 7), (8, 8), (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14), (7, 14), \
(6, 14), (5, 14), (4, 14), (4, 13), (4, 12), (4, 11), (4, 10), (5, 10), \
(6, 10), (7, 10), (8, 10), (9, 10), (10, 10), (11, 10), (12, 10), (12, 9), \
(12, 8), (12, 7), (12, 6), (12, 5), (12, 4), (11, 4), (10, 4), (10, 3), \
(10, 2), (10, 1), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (14, 1), \
(14, 2), (14, 3), (14, 4), (14, 5), (14, 6), (14, 7), (14, 8), (13, 8), \
(12, 8), (11, 8), (10, 8), (9, 8), (8, 8), (7, 8), (6, 8), (6, 7), (6, 6), \
(6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (5, 0), (4, 0), (3, 0), \
(2, 0), (1, 0), (0, 0), (0, 1), (0, 2)]
    >>> _scaffolds_order[0] == _start_position
    True
    >>> set(_scaffolds_order) == set(_scaffolds)
    True
    >>> all(\
        get_offset(_previous, _current) in OFFSET_MAP.values() \
        for _previous, _current \
        in zip(_scaffolds_order, _scaffolds_order[1:]) \
    )
    True
    """
    intersections = get_intersections(scaffolds)
    intersections_left = set(intersections)
    position = start_position
    scaffolds_order = [position]
    scaffolds_left = set(scaffolds)
    scaffolds_left.remove(position)
    last_intersection_diff = None
    while scaffolds_left:
        neighbour_scaffolds = \
            set(get_neighbour_positions(position)) & scaffolds_left
        if not neighbour_scaffolds:
            raise Exception(
                f"There {len(scaffolds_left)} remaining scaffolds, but none "
                f"of them are near the current position {position} (order was "
                f"{scaffolds_order})")
        if len(neighbour_scaffolds) > 1:
            if not last_intersection_diff:
                raise Exception(
                    f"There are many neighbours around {position} "
                    f"({neighbour_scaffolds}), but we have no intersection "
                    f"information (order was {scaffolds_order})")
            last_intersection_diff_x, last_intersection_diff_y = \
                last_intersection_diff
            previous_x, previous_y = position
            expected_next_position = \
                previous_x + last_intersection_diff_x, \
                previous_y + last_intersection_diff_y
            if expected_next_position not in neighbour_scaffolds:
                raise Exception(f"Intersection suddenly stopped")
            next_position = expected_next_position
        else:
            next_position, = neighbour_scaffolds
        if next_position in intersections_left:
            intersections_left.remove(next_position)
            previous_x, previous_y = position
            current_x, current_y = next_position
            last_intersection_diff = \
                current_x - previous_x, current_y - previous_y
        else:
            scaffolds_left.remove(next_position)
            if position not in intersections:
                last_intersection_diff = None
        scaffolds_order.append(next_position)
        position = next_position

    return scaffolds_order


def get_offset(start, end):
    """
    >>> get_offset((0, 0), (0, 0))
    (0, 0)
    >>> get_offset((0, 0), (0, 1))
    (0, 1)
    >>> get_offset((-3, 4), (-4, 4))
    (-1, 0)
    """
    start_x, start_y = start
    end_x, end_y = end

    return end_x - start_x, end_y - start_y


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
