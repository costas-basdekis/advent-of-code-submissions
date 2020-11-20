#!/usr/bin/env python3
import doctest
import itertools
from string import ascii_uppercase

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    590
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    walkways = parse_map_walkways(_input)
    portals = parse_map_portals(_input, walkways)
    walkways_neighbours, free_portals = \
        combine_map_walkways_and_portals(walkways, portals)
    return find_path_length(
        walkways_neighbours, free_portals['AA'], free_portals['ZZ'])


def find_path_length(walkways_neighbours, start, end, include_visits=False):
    """
    >>> map_text_a = (
    ...     "         A           \\n"
    ...     "         A           \\n"
    ...     "  #######.#########  \\n"
    ...     "  #######.........#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #####  B    ###.#  \\n"
    ...     "BC...##  C    ###.#  \\n"
    ...     "  ##.##       ###.#  \\n"
    ...     "  ##...DE  F  ###.#  \\n"
    ...     "  #####    G  ###.#  \\n"
    ...     "  #########.#####.#  \\n"
    ...     "DE..#######...###.#  \\n"
    ...     "  #.#########.###.#  \\n"
    ...     "FG..#########.....#  \\n"
    ...     "  ###########.#####  \\n"
    ...     "             Z       \\n"
    ...     "             Z       \\n"
    ... )
    >>> walkways_a = parse_map_walkways(map_text_a)
    >>> portals_a = parse_map_portals(map_text_a, walkways_a)
    >>> walkways_neighbours_a, free_portals_a = \\
    ...     combine_map_walkways_and_portals(walkways_a, portals_a)
    >>> find_path_length(
    ...     walkways_neighbours_a, free_portals_a['AA'], free_portals_a['ZZ'])
    23
    >>> map_text_b = (
    ...    "                   A               \\n"
    ...    "                   A               \\n"
    ...    "  #################.#############  \\n"
    ...    "  #.#...#...................#.#.#  \\n"
    ...    "  #.#.#.###.###.###.#########.#.#  \\n"
    ...    "  #.#.#.......#...#.....#.#.#...#  \\n"
    ...    "  #.#########.###.#####.#.#.###.#  \\n"
    ...    "  #.............#.#.....#.......#  \\n"
    ...    "  ###.###########.###.#####.#.#.#  \\n"
    ...    "  #.....#        A   C    #.#.#.#  \\n"
    ...    "  #######        S   P    #####.#  \\n"
    ...    "  #.#...#                 #......VT\\n"
    ...    "  #.#.#.#                 #.#####  \\n"
    ...    "  #...#.#               YN....#.#  \\n"
    ...    "  #.###.#                 #####.#  \\n"
    ...    "DI....#.#                 #.....#  \\n"
    ...    "  #####.#                 #.###.#  \\n"
    ...    "ZZ......#               QG....#..AS\\n"
    ...    "  ###.###                 #######  \\n"
    ...    "JO..#.#.#                 #.....#  \\n"
    ...    "  #.#.#.#                 ###.#.#  \\n"
    ...    "  #...#..DI             BU....#..LF\\n"
    ...    "  #####.#                 #.#####  \\n"
    ...    "YN......#               VT..#....QG\\n"
    ...    "  #.###.#                 #.###.#  \\n"
    ...    "  #.#...#                 #.....#  \\n"
    ...    "  ###.###    J L     J    #.#.###  \\n"
    ...    "  #.....#    O F     P    #.#...#  \\n"
    ...    "  #.###.#####.#.#####.#####.###.#  \\n"
    ...    "  #...#.#.#...#.....#.....#.#...#  \\n"
    ...    "  #.#####.###.###.#.#.#########.#  \\n"
    ...    "  #...#.#.....#...#.#.#.#.....#.#  \\n"
    ...    "  #.###.#####.###.###.#.#.#######  \\n"
    ...    "  #.#.........#...#.............#  \\n"
    ...    "  #########.###.###.#############  \\n"
    ...    "           B   J   C               \\n"
    ...    "           U   P   P               \\n"
    ... )
    >>> walkways_b = parse_map_walkways(map_text_b)
    >>> portals_b = parse_map_portals(map_text_b, walkways_b)
    >>> walkways_neighbours_b, free_portals_b = \\
    ...     combine_map_walkways_and_portals(walkways_b, portals_b)
    >>> find_path_length(
    ...     walkways_neighbours_b, free_portals_b['AA'], free_portals_b['ZZ'])
    58
    """
    visited = {start}
    if include_visits:
        visits = []
    stack = [(start, 0)]
    while stack:
        position, distance = stack.pop(0)
        if include_visits:
            visits.append((position, distance))
        next_distance = distance + 1
        next_positions = set(walkways_neighbours[position]) - visited
        if end in next_positions:
            if include_visits:
                return next_distance, visits
            return next_distance
        visited |= next_positions
        for next_position in next_positions:
            stack.append((next_position, next_distance))

    if include_visits:
        return visits
    raise Exception("Could not find end")


def combine_map_walkways_and_portals(walkways, portals):
    """
    >>> map_text_a = (
    ...     "         A           \\n"
    ...     "         A           \\n"
    ...     "  #######.#########  \\n"
    ...     "  #######.........#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #####  B    ###.#  \\n"
    ...     "BC...##  C    ###.#  \\n"
    ...     "  ##.##       ###.#  \\n"
    ...     "  ##...DE  F  ###.#  \\n"
    ...     "  #####    G  ###.#  \\n"
    ...     "  #########.#####.#  \\n"
    ...     "DE..#######...###.#  \\n"
    ...     "  #.#########.###.#  \\n"
    ...     "FG..#########.....#  \\n"
    ...     "  ###########.#####  \\n"
    ...     "             Z       \\n"
    ...     "             Z       \\n"
    ... )
    >>> walkways_a = parse_map_walkways(map_text_a)
    >>> portals_a = parse_map_portals(map_text_a, walkways_a)
    >>> walkways_neighbours_a, free_portals_a = \\
    ...     combine_map_walkways_and_portals(walkways_a, portals_a)
    >>> free_portals_a
    {'AA': (9, 2), 'ZZ': (13, 16)}
    >>> walkways_neighbours_a[(2, 8)]
    ((3, 8), (9, 6))
    >>> walkways_neighbours_a[(3, 8)]
    ((2, 8), (4, 8))
    >>> walkways_neighbours_a[(9, 6)]
    ((2, 8), (9, 5))
    >>> map_text_b = (
    ...    "                   A               \\n"
    ...    "                   A               \\n"
    ...    "  #################.#############  \\n"
    ...    "  #.#...#...................#.#.#  \\n"
    ...    "  #.#.#.###.###.###.#########.#.#  \\n"
    ...    "  #.#.#.......#...#.....#.#.#...#  \\n"
    ...    "  #.#########.###.#####.#.#.###.#  \\n"
    ...    "  #.............#.#.....#.......#  \\n"
    ...    "  ###.###########.###.#####.#.#.#  \\n"
    ...    "  #.....#        A   C    #.#.#.#  \\n"
    ...    "  #######        S   P    #####.#  \\n"
    ...    "  #.#...#                 #......VT\\n"
    ...    "  #.#.#.#                 #.#####  \\n"
    ...    "  #...#.#               YN....#.#  \\n"
    ...    "  #.###.#                 #####.#  \\n"
    ...    "DI....#.#                 #.....#  \\n"
    ...    "  #####.#                 #.###.#  \\n"
    ...    "ZZ......#               QG....#..AS\\n"
    ...    "  ###.###                 #######  \\n"
    ...    "JO..#.#.#                 #.....#  \\n"
    ...    "  #.#.#.#                 ###.#.#  \\n"
    ...    "  #...#..DI             BU....#..LF\\n"
    ...    "  #####.#                 #.#####  \\n"
    ...    "YN......#               VT..#....QG\\n"
    ...    "  #.###.#                 #.###.#  \\n"
    ...    "  #.#...#                 #.....#  \\n"
    ...    "  ###.###    J L     J    #.#.###  \\n"
    ...    "  #.....#    O F     P    #.#...#  \\n"
    ...    "  #.###.#####.#.#####.#####.###.#  \\n"
    ...    "  #...#.#.#...#.....#.....#.#...#  \\n"
    ...    "  #.#####.###.###.#.#.#########.#  \\n"
    ...    "  #...#.#.....#...#.#.#.#.....#.#  \\n"
    ...    "  #.###.#####.###.###.#.#.#######  \\n"
    ...    "  #.#.........#...#.............#  \\n"
    ...    "  #########.###.###.#############  \\n"
    ...    "           B   J   C               \\n"
    ...    "           U   P   P               \\n"
    ... )
    >>> walkways_b = parse_map_walkways(map_text_b)
    >>> portals_b = parse_map_portals(map_text_b, walkways_b)
    >>> walkways_neighbours_b, free_portals_b = \\
    ...     combine_map_walkways_and_portals(walkways_b, portals_b)
    >>> free_portals_b
    {'AA': (19, 2), 'ZZ': (2, 17)}
    >>> walkways_neighbours_b[(2, 15)]
    ((3, 15), (8, 21))
    >>> walkways_neighbours_b[(8, 21)]
    ((2, 15), (7, 21))
    """
    walkways_by_portals = {
        label: list(portal_walkway for _, portal_walkway in portal_walkways)
        for label, portal_walkways in itertools.groupby(sorted(
            (label, walkway)
            for walkway, label in portals.items()
        ), key=lambda item: item[0])
    }
    free_portals = {
        portal: portal_walkways[0]
        for portal, portal_walkways in walkways_by_portals.items()
        if len(portal_walkways) == 1
    }
    overcrowded_portals = {
        portal: portal_walkways[0]
        for portal, portal_walkways in walkways_by_portals.items()
        if len(portal_walkways) > 2
    }
    if overcrowded_portals:
        raise Exception(
            f"Got {len(overcrowded_portals)} overcrowded portals: "
            f"{overcrowded_portals}")
    walkways_portals = {
        walkway_a: walkway_b
        for portal, portal_walkways in walkways_by_portals.items()
        if len(portal_walkways) == 2
        for walkway_a, walkway_b
        in [portal_walkways, reversed(portal_walkways)]
    }

    walkways_set = set(walkways)
    walkways_neighbours = {
        walkway: tuple(sorted((set(get_neighbours(walkway)) & walkways_set) | (
            {walkways_portals[walkway]}
            if walkway in walkways_portals else
            set()
        )))
        for walkway in walkways
    }

    return walkways_neighbours, free_portals


def parse_map_portals(map_text, walkways):
    """
    >>> map_text_a = (
    ...     "         A           \\n"
    ...     "         A           \\n"
    ...     "  #######.#########  \\n"
    ...     "  #######.........#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #####  B    ###.#  \\n"
    ...     "BC...##  C    ###.#  \\n"
    ...     "  ##.##       ###.#  \\n"
    ...     "  ##...DE  F  ###.#  \\n"
    ...     "  #####    G  ###.#  \\n"
    ...     "  #########.#####.#  \\n"
    ...     "DE..#######...###.#  \\n"
    ...     "  #.#########.###.#  \\n"
    ...     "FG..#########.....#  \\n"
    ...     "  ###########.#####  \\n"
    ...     "             Z       \\n"
    ...     "             Z       \\n"
    ... )
    >>> walkways_a = parse_map_walkways(map_text_a)
    >>> list(sorted(parse_map_portals(map_text_a, walkways_a).items()))
    [((2, 8), 'BC'), ((2, 13), 'DE'), ((2, 15), 'FG'), ((6, 10), 'DE'), ((9, 2), 'AA'), ((9, 6), 'BC'), ((11, 12), 'FG'), ((13, 16), 'ZZ')]
    """
    lines = map_text.splitlines()
    non_empty_lines = filter(None, lines)
    label_points = {
        (x, y): content
        for y, line in enumerate(non_empty_lines)
        for x, content in enumerate(line)
        if content in ascii_uppercase
    }
    label_points_set = set(label_points)
    unpaired_points = set(label_points)
    point_pairs = set()
    for position in label_points:
        neighbours = set(get_neighbours(position)) & label_points_set
        pairs = {
            tuple(sorted([position, neighbour]))
            for neighbour in neighbours
        }
        over_paired_points = neighbours - unpaired_points
        if over_paired_points:
            raise Exception(
                f"Got over-paired points {over_paired_points} for {position}")
        point_pairs |= pairs
        unpaired_points -= set(sum(map(list, pairs), [])) - {position}
    if unpaired_points:
        raise Exception(
            f"There were {len(unpaired_points)} unpaired points left")

    portals = {}
    walkways_set = set(walkways)
    for point_a, point_b in point_pairs:
        label = label_points[point_a] + label_points[point_b]
        neighbour_walkways = {
            neighbour
            for position in [point_a, point_b]
            for neighbour in get_neighbours(position)
        } & walkways_set
        if len(neighbour_walkways) != 1:
            raise Exception(
                f"Expected 1 walkway for pair {point_a}/{point_b}, but got "
                f"{len(neighbour_walkways)}: {neighbour_walkways}")
        walkway, = neighbour_walkways
        portals[walkway] = label

    return portals


OFFSETS = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
]


def get_neighbours(position):
    x, y = position
    return [
        (x + offset_x, y + offset_y)
        for offset_x, offset_y in OFFSETS
    ]


def parse_map_walkways(map_text):
    """
    >>> sorted(parse_map_walkways(
    ...     "         A           \\n"
    ...     "         A           \\n"
    ...     "  #######.#########  \\n"
    ...     "  #######.........#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #####  B    ###.#  \\n"
    ...     "BC...##  C    ###.#  \\n"
    ...     "  ##.##       ###.#  \\n"
    ...     "  ##...DE  F  ###.#  \\n"
    ...     "  #####    G  ###.#  \\n"
    ...     "  #########.#####.#  \\n"
    ...     "DE..#######...###.#  \\n"
    ...     "  #.#########.###.#  \\n"
    ...     "FG..#########.....#  \\n"
    ...     "  ###########.#####  \\n"
    ...     "             Z       \\n"
    ...     "             Z      \\n"
    ... ))[:12]
    [(2, 8), (2, 13), (2, 15), (3, 8), (3, 13), (3, 14), (3, 15), (4, 8), (4, 9), (4, 10), (5, 10), (6, 10)]
    """
    lines = map_text.splitlines()
    non_empty_lines = filter(None, lines)
    return [
        (x, y)
        for y, line in enumerate(non_empty_lines)
        for x, content in enumerate(line)
        if content == '.'
    ]


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
