#!/usr/bin/env python3
import itertools

import utils

from year_2020.day_11 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2227
        """
        return SeatingExtended.from_seating_text(_input)\
            .tick_many(None, True)\
            .get_occupied_seat_count()


class SeatingExtended(part_a.Seating):
    """
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(1).show())
    #.##.##.##
    #######.##
    #.#.#..#..
    ####.##.##
    #.##.##.##
    #.#####.##
    ..#.#.....
    ##########
    #.######.#
    #.#####.##
    >>> print(SeatingExtended.from_seating_text(
    ...     "#.##.##.##\\n"
    ...     "#######.##\\n"
    ...     "#.#.#..#..\\n"
    ...     "####.##.##\\n"
    ...     "#.##.##.##\\n"
    ...     "#.#####.##\\n"
    ...     "..#.#.....\\n"
    ...     "##########\\n"
    ...     "#.######.#\\n"
    ...     "#.#####.##\\n"
    ... ).tick_many(1).show())
    #.LL.LL.L#
    #LLLLLL.LL
    L.L.L..L..
    LLLL.LL.LL
    L.LL.LL.LL
    L.LLLLL.LL
    ..L.L.....
    LLLLLLLLL#
    #.LLLLLL.L
    #.LLLLL.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(2).show())
    #.LL.LL.L#
    #LLLLLL.LL
    L.L.L..L..
    LLLL.LL.LL
    L.LL.LL.LL
    L.LLLLL.LL
    ..L.L.....
    LLLLLLLLL#
    #.LLLLLL.L
    #.LLLLL.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "#.LL.LL.L#\\n"
    ...     "#LLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLL#\\n"
    ...     "#.LLLLLL.L\\n"
    ...     "#.LLLLL.L#\\n"
    ... ).tick_many(1).show())
    #.L#.##.L#
    #L#####.LL
    L.#.#..#..
    ##L#.##.##
    #.##.#L.##
    #.#####.#L
    ..#.#.....
    LLL####LL#
    #.L#####.L
    #.L####.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(3).show())
    #.L#.##.L#
    #L#####.LL
    L.#.#..#..
    ##L#.##.##
    #.##.#L.##
    #.#####.#L
    ..#.#.....
    LLL####LL#
    #.L#####.L
    #.L####.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(4).show())
    #.L#.L#.L#
    #LLLLLL.LL
    L.L.L..#..
    ##LL.LL.L#
    L.LL.LL.L#
    #.LLLLL.LL
    ..L.L.....
    LLLLLLLLL#
    #.LLLLL#.L
    #.L#LL#.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(5).show())
    #.L#.L#.L#
    #LLLLLL.LL
    L.L.L..#..
    ##L#.#L.L#
    L.L#.#L.L#
    #.L####.LL
    ..#.#.....
    LLL###LLL#
    #.LLLLL#.L
    #.L#LL#.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(6).show())
    #.L#.L#.L#
    #LLLLLL.LL
    L.L.L..#..
    ##L#.#L.L#
    L.L#.LL.L#
    #.LLLL#.LL
    ..#.L.....
    LLL###LLL#
    #.LLLLL#.L
    #.L#LL#.L#
    >>> print(SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(None, True).show())
    #.L#.L#.L#
    #LLLLLL.LL
    L.L.L..#..
    ##L#.#L.L#
    L.L#.LL.L#
    #.LLLL#.LL
    ..#.L.....
    LLL###LLL#
    #.LLLLL#.L
    #.L#LL#.L#
    >>> SeatingExtended.from_seating_text(
    ...     "L.LL.LL.LL\\n"
    ...     "LLLLLLL.LL\\n"
    ...     "L.L.L..L..\\n"
    ...     "LLLL.LL.LL\\n"
    ...     "L.LL.LL.LL\\n"
    ...     "L.LLLLL.LL\\n"
    ...     "..L.L.....\\n"
    ...     "LLLLLLLLLL\\n"
    ...     "L.LLLLLL.L\\n"
    ...     "L.LLLLL.LL\\n"
    ... ).tick_many(None, True).get_occupied_seat_count()
    26
    """
    MAX_OCCUPIED_NEIGHBOURS_FOR_OCCUPIED = 5

    def get_neighbours(self, x, y):
        """
        >>> sorted(SeatingExtended.from_seating_text(
        ...     ".......#.\\n"
        ...     "...#.....\\n"
        ...     ".#.......\\n"
        ...     ".........\\n"
        ...     "..#L....#\\n"
        ...     "....#....\\n"
        ...     ".........\\n"
        ...     "#........\\n"
        ...     "...#.....\\n"
        ... ).get_neighbours(3, 4))
        [(0, 7), (1, 2), (2, 4), (3, 1), (3, 8), (4, 5), (7, 0), (8, 4)]
        >>> sorted(SeatingExtended.from_seating_text(
        ...     "#.##.##.##\\n"
        ...     "#######.##\\n"
        ...     "#.#.#..#..\\n"
        ...     "####.##.##\\n"
        ...     "#.##.##.##\\n"
        ...     "#.#####.##\\n"
        ...     "..#.#.....\\n"
        ...     "##########\\n"
        ...     "#.######.#\\n"
        ...     "#.#####.##\\n"
        ... ).get_neighbours(0, 0))
        [(0, 1), (1, 1), (2, 0)]
        """
        return filter(None, (
            self.get_visible_neighbour(x, y, d_x, d_y)
            for d_x, d_y in self.NEIGHBOUR_OFFSETS
        ))

    def get_visible_neighbour(self, x, y, d_x, d_y):
        """
        >>> SeatingExtended.from_seating_text(
        ...     ".......#.\\n"
        ...     "...#.....\\n"
        ...     ".#.......\\n"
        ...     ".........\\n"
        ...     "..#L....#\\n"
        ...     "....#....\\n"
        ...     ".........\\n"
        ...     "#........\\n"
        ...     "...#.....\\n"
        ... ).get_visible_neighbour(3, 4, -1, 0)
        (2, 4)
        >>> SeatingExtended.from_seating_text(
        ...     "#.##.##.##\\n"
        ...     "#######.##\\n"
        ...     "#.#.#..#..\\n"
        ...     "####.##.##\\n"
        ...     "#.##.##.##\\n"
        ...     "#.#####.##\\n"
        ...     "..#.#.....\\n"
        ...     "##########\\n"
        ...     "#.######.#\\n"
        ...     "#.#####.##\\n"
        ... ).get_visible_neighbour(0, 0, 0, 1)
        (0, 1)
        """
        for neighbour_x, neighbour_y \
                in self.get_neighbours_in_direction(x, y, d_x, d_y):
            if self.seats[neighbour_y][neighbour_x]:
                return neighbour_x, neighbour_y

        return None

    def get_neighbours_in_direction(self, x, y, d_x, d_y):
        """
        >>> list(SeatingExtended.from_seating_text(
        ...     ".......#.\\n"
        ...     "...#.....\\n"
        ...     ".#.......\\n"
        ...     ".........\\n"
        ...     "..#L....#\\n"
        ...     "....#....\\n"
        ...     ".........\\n"
        ...     "#........\\n"
        ...     "...#.....\\n"
        ... ).get_neighbours_in_direction(3, 4, -1, 0))
        [(2, 4), (1, 4), (0, 4)]
        """
        for distance in itertools.count(1):
            neighbour_x, neighbour_y = x + d_x * distance, y + d_y * distance
            if not self.is_within_grid(neighbour_x, neighbour_y):
                break
            yield neighbour_x, neighbour_y


challenge = Challenge()
challenge.main()
