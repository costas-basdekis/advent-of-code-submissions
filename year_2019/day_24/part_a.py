#!/usr/bin/env python3
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        18407158
        """
        _, repeated_scan, _ = find_scan_evolution_cycle(parse_scan(_input))

        return get_biodiversity_rating(repeated_scan)


def find_scan_evolution_cycle(scan):
    """
    >>> find_scan_evolution_cycle(parse_scan(
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     "#....\\n"
    ...     ".#...\\n"
    ... ))[0]
    12
    >>> find_scan_evolution_cycle(parse_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#..##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ))[2]
    12
    >>> print("!", show_scan(find_scan_evolution_cycle(parse_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#..##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ))[1]))
    ! .....
    .....
    .....
    #....
    .#...
    """
    current_scan = scan
    seen_scan_hashes = {
        get_biodiversity_rating(scan): 0
    }
    for count in itertools.count(1):
        current_scan = evolve_scan(current_scan)
        current_scan_hash = get_biodiversity_rating(current_scan)
        if current_scan_hash in seen_scan_hashes:
            return count, current_scan, \
                count - seen_scan_hashes[current_scan_hash]
        seen_scan_hashes[current_scan_hash] = count

    raise Exception("Exited endless loop")


BIODIVERSITY_ORDER = [
    (x, y)
    for y in range(5)
    for x in range(5)
]

BIODIVERSITY_WEIGHTS = [
    int(2 ** index)
    for index in range(len(BIODIVERSITY_ORDER))
]


def get_biodiversity_rating(scan):
    """
    >>> get_biodiversity_rating(parse_scan(
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ... ))
    0
    >>> get_biodiversity_rating(parse_scan(
    ...     "#....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ... ))
    1
    >>> get_biodiversity_rating(parse_scan(
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     "#....\\n"
    ...     ".#...\\n"
    ... ))
    2129920
    >>> get_biodiversity_rating(parse_scan(
    ...     "#....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     "#....\\n"
    ...     ".#...\\n"
    ... ))
    2129921
    """
    return sum((
        weight
        for position, weight in zip(BIODIVERSITY_ORDER, BIODIVERSITY_WEIGHTS)
        if scan[position]
    ), 0)


def get_spot_next_state(spot, neighbour_count):
    """
    >>> get_spot_next_state(True, 0)
    False
    >>> get_spot_next_state(True, 1)
    True
    >>> get_spot_next_state(True, 2)
    False
    >>> get_spot_next_state(True, 3)
    False
    >>> get_spot_next_state(False, 0)
    False
    >>> get_spot_next_state(False, 1)
    True
    >>> get_spot_next_state(False, 2)
    True
    >>> get_spot_next_state(False, 3)
    False
    """
    if spot:
        return neighbour_count == 1
    else:
        return neighbour_count in (1, 2)


OFFSETS = list(sorted([
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
]))


def create_neighbour_map():
    """
    >>> NEIGHBOUR_MAP[(0, 0)]
    ((0, 1), (1, 0))
    >>> NEIGHBOUR_MAP[(2, 2)]
    ((1, 2), (2, 1), (2, 3), (3, 2))
    >>> NEIGHBOUR_MAP[(4, 4)]
    ((3, 4), (4, 3))
    >>> {
    ...     position: non_reciprocal_neighbours
    ...     for position, non_reciprocal_neighbours in (
    ...         (position, sorted(tuple(
    ...             neighbour
    ...             for neighbour in neighbours
    ...             if position not in NEIGHBOUR_MAP[neighbour]
    ...         )))
    ...         for position, neighbours in NEIGHBOUR_MAP.items()
    ...     )
    ...     if non_reciprocal_neighbours
    ... }
    {}
    >>> {
    ...     position: external_neighbours
    ...     for position, external_neighbours in (
    ...         (position, sorted(tuple(
    ...             (neighbour_x, neighbour_y)
    ...             for neighbour_x, neighbour_y in neighbours
    ...             if (
    ...                 neighbour_x < 0
    ...                 or neighbour_x > 4
    ...                 or neighbour_y < 0
    ...                 or neighbour_y > 4
    ...             )
    ...         )))
    ...         for position, neighbours in NEIGHBOUR_MAP.items()
    ...     )
    ...     if external_neighbours
    ... }
    {}
    >>> {
    ...     position: non_adjacent_neighbours
    ...     for position, non_adjacent_neighbours in (
    ...         ((x, y), sorted(tuple(
    ...             (neighbour_x, neighbour_y)
    ...             for neighbour_x, neighbour_y in neighbours
    ...             if abs(neighbour_x - x) + abs(neighbour_y - y) != 1
    ...         )))
    ...         for (x, y), neighbours in NEIGHBOUR_MAP.items()
    ...     )
    ...     if non_adjacent_neighbours
    ... }
    {}
    """
    return {
        (x, y): tuple(sorted(
            (neighbour_x, neighbour_y)
            for neighbour_x, neighbour_y in get_neighbours(x, y)
            if 0 <= neighbour_y < 5
            and 0 <= neighbour_x < 5
        ))
        for x in range(5)
        for y in range(5)
    }


def get_neighbours(x, y):
    """
    >>> get_neighbours(0, 0)
    [(-1, 0), (0, -1), (0, 1), (1, 0)]
    >>> get_neighbours(4, 3)
    [(3, 3), (4, 2), (4, 4), (5, 3)]
    >>> get_neighbours(-4, -3)
    [(-5, -3), (-4, -4), (-4, -2), (-3, -3)]
    """
    return [
        (x + offset_x, y + offset_y)
        for offset_x, offset_y in OFFSETS
    ]


NEIGHBOUR_MAP = create_neighbour_map()


# noinspection PyDefaultArgument
def repeat_evolve_scan(scan, count, neighbour_map=NEIGHBOUR_MAP):
    """
    >>> print(show_scan(repeat_evolve_scan(parse_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#..##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ), 4)))
    ####.
    ....#
    ##..#
    .....
    ##...
    >>> scan_a = parse_scan(
    ...     ".....\\n"
    ...     ".....\\n"
    ...     ".....\\n"
    ...     "#....\\n"
    ...     ".#...\\n"
    ... )
    >>> repeat_evolve_scan(scan_a, 12) == scan_a
    True
    """
    current_scan = scan
    for _ in range(count):
        current_scan = evolve_scan(current_scan, neighbour_map=neighbour_map)

    return current_scan


# noinspection PyDefaultArgument
def evolve_scan(scan, neighbour_map=NEIGHBOUR_MAP):
    """
    >>> print(show_scan(evolve_scan(parse_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#..##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ))))
    #..#.
    ####.
    ###.#
    ##.##
    .##..
    >>> print(show_scan(evolve_scan(evolve_scan(evolve_scan(evolve_scan(parse_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#..##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... )))))))
    ####.
    ....#
    ##..#
    .....
    ##...
    """
    return {
        position: get_spot_next_state(
            spot, get_neighbour_count(
                scan, position, neighbour_map=neighbour_map))
        for position, spot in scan.items()
    }


# noinspection PyDefaultArgument
def get_neighbour_count(scan, position, neighbour_map=NEIGHBOUR_MAP):
    """
    >>> get_neighbour_count(parse_scan('#.#\\n.#.\\n#.#'), (1, 1))
    0
    >>> get_neighbour_count(parse_scan('#.#\\n.#.\\n#.#'), (0, 0))
    0
    >>> get_neighbour_count(parse_scan('#.#\\n.#.\\n#.#'), (1, 0))
    3
    >>> get_neighbour_count(parse_scan('#.#\\n.#.\\n#.#'), (0, 1))
    3
    """
    return sum(
        1
        for neighbour in neighbour_map[position]
        if scan[neighbour]
    )


SHOW_SCAN_MAP = {
    True: '#',
    False: '.',
}


# noinspection PyDefaultArgument
def show_scan(scan, show_scan_map=SHOW_SCAN_MAP):
    """
    >>> print(show_scan(parse_scan(
    ...     "..#.#\\n"
    ...     "#####\\n"
    ...     ".#...\\n"
    ...     "...#.\\n"
    ...     "##...\\n"
    ... )))
    ..#.#
    #####
    .#...
    ...#.
    ##...
    """
    return "\n".join(
        "".join(
            show_scan_map[scan[(x, y)]]
            for x in range(5)
        )
        for y in range(5)
    )


PARSE_SCAN_MAP = {
    '#': True,
    '.': False,
}


# noinspection PyDefaultArgument
def parse_scan(scan_text, parse_scan_map=PARSE_SCAN_MAP):
    lines = scan_text.splitlines()
    non_empty_lines = filter(None, lines)
    return {
        (x, y): parse_scan_map[spot_text]
        for y, line in enumerate(non_empty_lines)
        for x, spot_text in enumerate(line)
    }


challenge = Challenge()
challenge.main()
