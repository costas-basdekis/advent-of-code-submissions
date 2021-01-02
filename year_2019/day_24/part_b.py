#!/usr/bin/env python3
import itertools

import utils

from year_2019.day_24.part_a import get_neighbours, parse_scan, show_scan,\
    evolve_scan, get_neighbour_count, SHOW_SCAN_MAP, PARSE_SCAN_MAP


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1998
        """

        return repeat_evolve_scan_extended(NestedScan.from_scan(_input), 200)\
            .bug_count()


def repeat_evolve_scan_extended(scan, count):
    """
    >>> print(repeat_evolve_scan_extended(NestedScan.from_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#.?##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ), 10).show())
    Depth -5:
    ..#..
    .#.#.
    ..?.#
    .#.#.
    ..#..
    <BLANKLINE>
    Depth -4:
    ...#.
    ...##
    ..?..
    ...##
    ...#.
    <BLANKLINE>
    Depth -3:
    #.#..
    .#...
    ..?..
    .#...
    #.#..
    <BLANKLINE>
    Depth -2:
    .#.##
    ....#
    ..?.#
    ...##
    .###.
    <BLANKLINE>
    Depth -1:
    #..##
    ...##
    ..?..
    ...#.
    .####
    <BLANKLINE>
    Depth 0:
    .#...
    .#.##
    .#?..
    .....
    .....
    <BLANKLINE>
    Depth 1:
    .##..
    #..##
    ..?.#
    ##.##
    #####
    <BLANKLINE>
    Depth 2:
    ###..
    ##.#.
    #.?..
    .#.##
    #.#..
    <BLANKLINE>
    Depth 3:
    ..###
    .....
    #.?..
    #....
    #...#
    <BLANKLINE>
    Depth 4:
    .###.
    #..#.
    #.?..
    ##.#.
    .....
    <BLANKLINE>
    Depth 5:
    ####.
    #..#.
    #.?#.
    ####.
    .....
    >>> repeat_evolve_scan_extended(NestedScan.from_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#.?##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ), 10).bug_count()
    99
    """
    current_scan = scan
    for _ in range(count):
        current_scan = evolve_scan_extended(current_scan)

    return current_scan


def evolve_scan_extended(scan):
    """
    >>> get_neighbour_count(NestedScan.from_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#.?##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ), (0, (0, 0)), NESTED_NEIGHBOUR_MAP)
    1
    >>> print(show_scan_extended(evolve_scan({(2, 2): False, **NestedScan.from_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#.?##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... ).by_level[0]})))
    #..#.
    ####.
    ###.#
    ##.##
    .##..
    >>> print(evolve_scan_extended(NestedScan.from_scan(
    ...     "....#\\n"
    ...     "#..#.\\n"
    ...     "#.?##\\n"
    ...     "..#..\\n"
    ...     "#....\\n"
    ... )).show())
    Depth -1:
    .....
    ..#..
    ..?#.
    ..#..
    .....
    <BLANKLINE>
    Depth 0:
    #..#.
    ####.
    ##?.#
    ##.##
    .##..
    <BLANKLINE>
    Depth 1:
    ....#
    ....#
    ..?.#
    ....#
    #####
    """
    return NestedScan.from_dict(evolve_scan(
        scan, neighbour_map=NESTED_NEIGHBOUR_MAP))


def create_nested_neighbour_map():
    """
    >>> (2, 2) in BASE_NESTED_NEIGHBOUR_MAP
    False
    >>> [
    ...     position
    ...     for position, neighbours
    ...     in BASE_NESTED_NEIGHBOUR_MAP.items()
    ...     if (2, 2) in (neighbour for __, neighbour in neighbours)
    ... ]
    []
    >>> {
    ...     position: non_reciprocal_neighbours
    ...     for position, non_reciprocal_neighbours in (
    ...         (position, tuple(sorted(
    ...             (level, neighbour)
    ...             for (level, neighbour) in neighbours
    ...             if (-level, position) not in BASE_NESTED_NEIGHBOUR_MAP[neighbour]
    ...         )))
    ...         for position, neighbours in BASE_NESTED_NEIGHBOUR_MAP.items()
    ...     )
    ...     if non_reciprocal_neighbours
    ... }
    {}
    >>> BASE_NESTED_NEIGHBOUR_MAP[(0, 0)]
    ((-1, (1, 2)), (-1, (2, 1)), (0, (0, 1)), (0, (1, 0)))
    >>> BASE_NESTED_NEIGHBOUR_MAP[(2, 1)]
    ((0, (1, 1)), (0, (2, 0)), (0, (3, 1)), (1, (0, 0)), (1, (1, 0)), (1, (2, 0)), (1, (3, 0)), (1, (4, 0)))
    >>> BASE_NESTED_NEIGHBOUR_MAP[(2, 3)]
    ((0, (1, 3)), (0, (2, 4)), (0, (3, 3)), (1, (0, 4)), (1, (1, 4)), (1, (2, 4)), (1, (3, 4)), (1, (4, 4)))
    """
    lower_level_map = {
        **{
            (x, -1): (-1, (2, 1))
            for x in range(5)
        },
        **{
            (x, 5): (-1, (2, 3))
            for x in range(5)
        },
        **{
            (-1, y): (-1, (1, 2))
            for y in range(5)
        },
        **{
            (5, y): (-1, (3, 2))
            for y in range(5)
        },
    }

    higher_level_map = {
        (2, 1): tuple(
            (1, (x, 0))
            for x in range(5)
        ),
        (2, 3): tuple(
            (1, (x, 4))
            for x in range(5)
        ),
        (1, 2): tuple(
            (1, (0, y))
            for y in range(5)
        ),
        (3, 2): tuple(
            (1, (4, y))
            for y in range(5)
        ),
    }

    return {
        (x, y): tuple(sorted(sum((
            (lower_level_map.get(neighbour),)
            if neighbour in lower_level_map else (
                higher_level_map[(x, y)]
            ) if neighbour == (2, 2) else (
                ((0, neighbour),)
            )
            for neighbour in get_neighbours(x, y)
        ), ())))
        for x in range(5)
        for y in range(5)
        if (x, y) != (2, 2)
    }


BASE_NESTED_NEIGHBOUR_MAP = create_nested_neighbour_map()


class NestedNeighbourMap:
    def __getitem__(self, item):
        level, position = item

        neighbours = BASE_NESTED_NEIGHBOUR_MAP[position]

        return tuple(
            (level + level_offset, spot)
            for level_offset, spot in neighbours
        )


NESTED_NEIGHBOUR_MAP = NestedNeighbourMap()


class NestedScan:
    @classmethod
    def from_dict(cls, _dict):
        return cls.from_items(_dict.items())

    @classmethod
    def from_items(cls, items):
        def item_level(item):
            nested_position, _ = item
            level, _ = nested_position
            return level

        by_level = {
            level: {
                position: spot
                for (level, position), spot in level_items
                if position != (2, 2)
            }
            for level, level_items
            in itertools.groupby(sorted(items, key=item_level), key=item_level)
        }
        if not by_level:
            raise Exception("No items passed")
        if 0 not in by_level:
            raise Exception("No base level passed")

        for level, level_map in by_level.items():
            if set(level_map) != set(BASE_NESTED_NEIGHBOUR_MAP):
                raise Exception(
                    f"Level {level} did not match keys: {set(level_map)}")

        nested_scan = cls(by_level[0])
        for level, level_map in by_level.items():
            if level == 0:
                continue
            nested_scan.by_level[level] = level_map

        nested_scan.cleanup()

        return nested_scan

    @classmethod
    def from_scan(cls, scan_text, frozen=True):
        return cls(parse_scan_extended(scan_text), frozen=frozen)

    def __init__(self, base_scan, frozen=True):
        self.base_scan = base_scan
        self.by_level = {}
        self.ensure_level(0)
        self.frozen = frozen

    def __getitem__(self, item):
        level, position = item
        self.ensure_level(level)

        return self.by_level[level][position]

    def __setitem__(self, item, value):
        if self.frozen:
            raise Exception("Can't update frozen scan")
        level, position = item
        self.ensure_level(level)

        if position not in self.by_level[level]:
            raise KeyError(item)

        self.by_level[level][position] = value

    def cleanup(self):
        for level, level_map in list(self.by_level.items()):
            if level == 0:
                continue
            if not any(level_map.values()):
                del self.by_level[level]

    def ensure_level(self, level):
        if level in self.by_level:
            return

        self.by_level[level] = self.create_level(level)

    def create_level(self, level):
        """
        >>> set(NestedScan.from_scan(
        ...     ".....\\n"
        ...     ".....\\n"
        ...     "..?..\\n"
        ...     ".....\\n"
        ...     ".....\\n"
        ... ).create_level(0).values())
        {False}
        >>> NestedScan.from_scan(
        ...     "....#\\n"
        ...     "#..#.\\n"
        ...     "#.?##\\n"
        ...     "..#..\\n"
        ...     "#....\\n"
        ... ).create_level(0)[(4, 0)]
        True
        >>> ns_a = NestedScan.from_scan(
        ...     "....#\\n"
        ...     "#..#.\\n"
        ...     "#.?##\\n"
        ...     "..#..\\n"
        ...     "#....\\n"
        ... , frozen=False)
        >>> ns_a.create_level(0) == ns_a.by_level[0]
        True
        >>> ns_a[(0, (4, 0))]
        True
        >>> ns_a[(0, (2, 2))]
        Traceback (most recent call last):
        ...
        KeyError: (2, 2)
        >>> ns_a[(1, (4, 0))]
        False
        >>> ns_a[(1, (2, 2))]
        Traceback (most recent call last):
        ...
        KeyError: (2, 2)
        >>> list(sorted(ns_a.by_level))
        [0, 1]
        >>> ns_a.cleanup()
        >>> list(sorted(ns_a.by_level))
        [0]
        >>> ns_a[(1, (4, 0))]
        False
        >>> ns_a[(1, (4, 0))] = True
        >>> ns_a.cleanup()
        >>> list(sorted(ns_a.by_level))
        [0, 1]
        >>> ns_a[(1, (4, 0))] = False
        >>> ns_a.cleanup()
        >>> list(sorted(ns_a.by_level))
        [0]
        >>> ns_a[(1, (4, 0))] = True
        >>> list(sorted(ns_a.by_level[0]))
        [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 1), (1, 2), \
(1, 3), (1, 4), (2, 0), (2, 1), (2, 3), (2, 4), (3, 0), (3, 1), (3, 2), \
(3, 3), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        >>> len(ns_a.by_level)
        2
        >>> len(ns_a.keys())
        96
        """
        return {
            position: self.base_scan[position] if level == 0 else False
            for position in BASE_NESTED_NEIGHBOUR_MAP
        }

    def keys(self):
        return [
            nested_position
            for nested_position, _ in self.items()
        ]

    def items(self):
        min_level = min(self.by_level) - 1
        max_level = max(self.by_level) + 1

        return [
            ((level, position), self[(level, position)])
            for level in range(min_level, max_level + 1)
            for position in BASE_NESTED_NEIGHBOUR_MAP
        ]

    def bug_count(self):
        """
        >>> NestedScan.from_scan(
        ...     ".....\\n"
        ...     ".....\\n"
        ...     "..?..\\n"
        ...     ".....\\n"
        ...     ".....\\n"
        ... ).bug_count()
        0
        >>> NestedScan.from_scan(
        ...     "....#\\n"
        ...     ".....\\n"
        ...     "..?..\\n"
        ...     ".....\\n"
        ...     ".....\\n"
        ... ).bug_count()
        1
        >>> NestedScan.from_scan(
        ...     "....#\\n"
        ...     "#..#.\\n"
        ...     "#.?##\\n"
        ...     "..#..\\n"
        ...     "#....\\n"
        ... ).bug_count()
        8
        """
        return sum(
            1
            for level_map in self.by_level.values()
            for spot in level_map.values()
            if spot
        )

    def show(self):
        """
        >>> print("!", show_scan_extended({(2, 2): '?', **NestedScan.from_scan(
        ...     ".....\\n"
        ...     ".....\\n"
        ...     "..?..\\n"
        ...     ".....\\n"
        ...     ".....\\n"
        ... ).by_level[0]}))
        ! .....
        .....
        ..?..
        .....
        .....
        >>> print(NestedScan.from_scan(
        ...     ".....\\n"
        ...     ".....\\n"
        ...     "..?..\\n"
        ...     ".....\\n"
        ...     ".....\\n"
        ... ).show())
        Depth 0:
        .....
        .....
        ..?..
        .....
        .....
        >>> print(NestedScan.from_scan(
        ...     "..#.#\\n"
        ...     "#####\\n"
        ...     ".#?..\\n"
        ...     "...#.\\n"
        ...     "##...\\n"
        ... ).show())
        Depth 0:
        ..#.#
        #####
        .#?..
        ...#.
        ##...
        >>> ns_a = NestedScan.from_scan(
        ...     "..#.#\\n"
        ...     "#####\\n"
        ...     ".#?..\\n"
        ...     "...#.\\n"
        ...     "##...\\n"
        ... , frozen=False)
        >>> ns_a[(1, (0, 0))] = True
        >>> print(ns_a.show())
        Depth 0:
        ..#.#
        #####
        .#?..
        ...#.
        ##...
        <BLANKLINE>
        Depth 1:
        #....
        .....
        ..?..
        .....
        .....
        >>> ns_a[(0, (0, 0))] = True
        >>> print(ns_a.show())
        Depth 0:
        #.#.#
        #####
        .#?..
        ...#.
        ##...
        <BLANKLINE>
        Depth 1:
        #....
        .....
        ..?..
        .....
        .....
        >>> ns_a[(1, (0, 0))] = False
        >>> ns_a.cleanup()
        >>> print(ns_a.show())
        Depth 0:
        #.#.#
        #####
        .#?..
        ...#.
        ##...
        """
        return "\n\n".join(
            "\n".join([
                f"Depth {level}:",
                show_scan_extended({(2, 2): '?', **level_map}),
            ])
            for level, level_map in sorted(self.by_level.items())
        )


SHOW_SCAN_EXTENDED_MAP = {
    **SHOW_SCAN_MAP,
    '?': '?',
}


def show_scan_extended(scan):
    return show_scan({(2, 2): '?', **scan}, SHOW_SCAN_EXTENDED_MAP)


PARSE_SCAN_EXTENDED_MAP = {
    **PARSE_SCAN_MAP,
    '?': '?'
}


def parse_scan_extended(scan_text):
    scan = parse_scan(scan_text, PARSE_SCAN_EXTENDED_MAP)
    del scan[(2, 2)]

    return scan


challenge = Challenge()
challenge.main()
