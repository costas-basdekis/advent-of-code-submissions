#!/usr/bin/env python3
import itertools
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2481
        """
        return Seating.from_seating_text(_input)\
            .tick_many(None, True)\
            .get_occupied_seat_count()


class Seating(namedtuple("Seating", ("seats", "sitting"))):
    MAX_OCCUPIED_NEIGHBOURS_FOR_OCCUPIED = 4

    @classmethod
    def from_seating_text(cls, seating_text):
        """
        >>> Seating.from_seating_text(
        ...     "L.L\\n"
        ...     ".##\\n"
        ...     "#L.\\n"
        ... )
        Seating(seats=((True, False, True), (False, True, True), (True, True, False)), \
sitting=((False, False, False), (False, True, True), (True, False, False)))
        """
        seats = tuple(
            tuple(
                position != '.'
                for position in line
            )
            for line in filter(None, seating_text.splitlines())
        )
        sitting = tuple(
            tuple(
                position == '#'
                for position in line
            )
            for line in filter(None, seating_text.splitlines())
        )

        return cls(seats, sitting)

    def get_occupied_seat_count(self):
        """
        >>> Seating.from_seating_text(
        ...     "#.#L.L#.##\\n"
        ...     "#LLL#LL.L#\\n"
        ...     "L.#.L..#..\\n"
        ...     "#L##.##.L#\\n"
        ...     "#.#L.LL.LL\\n"
        ...     "#.#L#L#.##\\n"
        ...     "..L.L.....\\n"
        ...     "#L#L##L#L#\\n"
        ...     "#.LLLLLL.L\\n"
        ...     "#.#L#L#.##\\n"
        ... ).get_occupied_seat_count()
        37
        """
        return sum(
            1
            for line in self.sitting
            for sitting in line
            if sitting
        )

    def tick_many(self, count, until_not_changing=False):
        """
        >>> print(Seating.from_seating_text(
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
        >>> print(Seating.from_seating_text(
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
        #.#L.L#.##
        #LLL#LL.L#
        L.#.L..#..
        #L##.##.L#
        #.#L.LL.LL
        #.#L#L#.##
        ..L.L.....
        #L#L##L#L#
        #.LLLLLL.L
        #.#L#L#.##
        >>> print(Seating.from_seating_text(
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
        #.#L.L#.##
        #LLL#LL.L#
        L.#.L..#..
        #L##.##.L#
        #.#L.LL.LL
        #.#L#L#.##
        ..L.L.....
        #L#L##L#L#
        #.LLLLLL.L
        #.#L#L#.##
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        previous, result = None, self
        for _ in steps:
            previous = result
            result = result.tick()
            if previous == result:
                break

        return result

    def tick(self):
        """
        >>> print(Seating.from_seating_text(
        ...     "L.L\\n"
        ...     ".##\\n"
        ...     "#L.\\n"
        ... ).tick().show())
        L.L
        .##
        #L.
        >>> print(Seating.from_seating_text(
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
        ... ).tick().show())
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
        """
        return self._replace(sitting=tuple(
            tuple(
                self.get_next_seat_state_at(x, y)
                for x in range(len(self.seats[0]))
            )
            for y in range(len(self.seats))
        ))

    def get_next_seat_state_at(self, x, y):
        """
        >>> seating_a = Seating.from_seating_text(
        ...     "L.L\\n"
        ...     ".##\\n"
        ...     "#L.\\n"
        ... )
        >>> seating_a.get_next_seat_state_at(1, 1)
        True
        >>> seating_a.get_next_seat_state_at(1, 0)
        False
        >>> seating_a.get_next_seat_state_at(0, 0)
        False
        """
        return self.get_next_seat_state(
            self.seats[y][x], self.sitting[y][x],
            self.get_neighbour_count(x, y))

    def get_next_seat_state(self, seat, sitting, neighbour_count):
        """
        >>> Seating((), ()).get_next_seat_state(False, True, 2)
        False
        >>> Seating((), ()).get_next_seat_state(True, True, 2)
        True
        >>> Seating((), ()).get_next_seat_state(True, True, 4)
        False
        >>> Seating((), ()).get_next_seat_state(True, True, 5)
        False
        >>> Seating((), ()).get_next_seat_state(True, False, 5)
        False
        >>> Seating((), ()).get_next_seat_state(True, False, 1)
        False
        >>> Seating((), ()).get_next_seat_state(True, False, 0)
        True
        """
        if not seat:
            return False

        if sitting:
            return neighbour_count < self.MAX_OCCUPIED_NEIGHBOURS_FOR_OCCUPIED
        else:
            return neighbour_count == 0

    NEIGHBOUR_OFFSETS = [
        (d_x, d_y)
        for d_x in range(-1, 2)
        for d_y in range(-1, 2)
        if (d_x, d_y) != (0, 0)
    ]

    def get_neighbour_count(self, x, y):
        """
        >>> seating_a = Seating.from_seating_text(
        ...     "L.L\\n"
        ...     ".##\\n"
        ...     "#L.\\n"
        ... )
        >>> seating_a.get_neighbour_count(1, 1)
        2
        >>> seating_a.get_neighbour_count(1, 2)
        3
        """
        return sum(
            self.sitting[y][x]
            for x, y in self.get_neighbours(x, y)
        )

    def get_neighbours(self, x, y):
        """
        >>> sorted(Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .get_neighbours(3, 4))
        [(2, 3), (2, 4), (2, 5), (3, 3), (3, 5), (4, 3), (4, 4), (4, 5)]
        >>> sorted(Seating(((True,) * 5,) * 5, ((False,) * 5,) * 5)\\
        ...     .get_neighbours(3, 4))
        [(2, 3), (2, 4), (3, 3), (4, 3), (4, 4)]
        """
        return (
            (neighbour_x, neighbour_y)
            for neighbour_x, neighbour_y in (
                (x + d_x, y + d_y)
                for d_x, d_y in self.NEIGHBOUR_OFFSETS
            )
            if self.is_within_grid(neighbour_x, neighbour_y)
        )

    def is_within_grid(self, x, y):
        """
        >>> Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .is_within_grid(0, 0)
        True
        >>> Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .is_within_grid(-1, 0)
        False
        >>> Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .is_within_grid(3, -5)
        False
        >>> Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .is_within_grid(3, 6)
        False
        >>> Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .is_within_grid(6, 0)
        False
        >>> Seating(((True,) * 6,) * 6, ((False,) * 6,) * 6)\\
        ...     .is_within_grid(4, 3)
        True
        """
        return (
            0 <= x < len(self.seats[0])
            and 0 <= y < len(self.seats)
        )

    def show(self):
        """
        >>> print(Seating.from_seating_text(
        ...     "L.L\\n"
        ...     ".##\\n"
        ...     "#L.\\n"
        ... ).show())
        L.L
        .##
        #L.
        >>> print(Seating.from_seating_text(
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
        ... ).show())
        L.LL.LL.LL
        LLLLLLL.LL
        L.L.L..L..
        LLLL.LL.LL
        L.LL.LL.LL
        L.LLLLL.LL
        ..L.L.....
        LLLLLLLLLL
        L.LLLLLL.L
        L.LLLLL.LL
        """
        return "\n".join(
            "".join(
                "#"
                if sitting else
                "L"
                if seat else
                "."
                for seat, sitting in zip(seat_line, sitting_line)
            )
            for seat_line, sitting_line in zip(self.seats, self.sitting)
        )


Challenge.main()
challenge = Challenge()
