#!/usr/bin/env python3
import doctest
import itertools

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    18407158
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
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
        for (x, y), weight in zip(BIODIVERSITY_ORDER, BIODIVERSITY_WEIGHTS)
        if scan[y][x]
    ), 0)


def repeat_evolve_scan(scan, count):
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
        current_scan = evolve_scan(current_scan)

    return current_scan


def evolve_scan(scan):
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
    neighbour_counts = get_all_neighbour_counts(scan)

    return [
        [
            (
                True
                if neighbour_count == 1 else
                False
            ) if spot else (
                True
                if neighbour_count in (1, 2) else
                False
            )
            for neighbour_count, spot in zip(neighbour_counts_line, line)
        ]
        for neighbour_counts_line, line in zip(neighbour_counts, scan)
    ]


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


def get_all_neighbour_counts(scan):
    """
    >>> list(map(list, get_all_neighbour_counts(parse_scan(
    ...     "..#.#\\n"
    ...     "#####\\n"
    ...     ".#...\\n"
    ...     "...#.\\n"
    ...     "##...\\n"
    ... ))))
    [[1, 2, 1, 3, 1], [1, 3, 3, 2, 2], [2, 1, 2, 2, 1], [1, 2, 1, 0, 1], [1, 1, 1, 1, 0]]
    """
    return (
        (
            get_neighbour_count(scan, x, y)
            for x, spot in enumerate(line)
        )
        for y, line in enumerate(scan)
    )


OFFSETS = list(sorted([
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
]))


def get_neighbour_count(scan, x, y):
    """
    >>> get_neighbour_count([[True]], 0, 0)
    0
    >>> get_neighbour_count(
    ...     [[True, False, True], [False, True, False], [True, False, True]],
    ...     1, 1)
    0
    >>> get_neighbour_count(
    ...     [[True, False, True], [False, True, False], [True, False, True]],
    ...     0, 0)
    0
    >>> get_neighbour_count(
    ...     [[True, False, True], [False, True, False], [True, False, True]],
    ...     1, 0)
    3
    >>> get_neighbour_count(
    ...     [[True, False, True], [False, True, False], [True, False, True]],
    ...     0, 1)
    3
    """
    return sum(
        1
        for neighbour_x, neighbour_y in get_neighbours(x, y)
        if 0 <= neighbour_y < len(scan)
        and 0 <= neighbour_x < len(scan[neighbour_y])
        and scan[neighbour_y][neighbour_x]
    )


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


SHOW_SCAN_MAP = {
    True: '#',
    False: '.',
}


def show_scan(scan):
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
            SHOW_SCAN_MAP[spot]
            for spot in line
        )
        for line in scan
    )


PARSE_SCAN_MAP = {
    '#': True,
    '.': False,
}


def parse_scan(scan_text):
    """
    >>> parse_scan(
    ...     "..#.#\\n"
    ...     "#####\\n"
    ...     ".#...\\n"
    ...     "...#.\\n"
    ...     "##...\\n"
    ... )
    [[False, False, True, False, True], [True, True, True, True, True], \
[False, True, False, False, False], [False, False, False, True, False], \
[True, True, False, False, False]]
    """
    lines = scan_text.splitlines()
    non_empty_lines = filter(None, lines)
    return [
        [
            PARSE_SCAN_MAP[spot_text]
            for spot_text in line
        ]
        for line in non_empty_lines
    ]


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
