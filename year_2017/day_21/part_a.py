#!/usr/bin/env python3
import itertools
import re
from dataclasses import dataclass
from typing import Tuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        188
        """
        return Book.from_book_text(_input)\
            .step_grid_many(5, debug=debug)\
            .get_pixel_count()


class Book:
    re_line = re.compile(r"^([.#/]+) => ([.#/]+)$")

    @classmethod
    def from_book_text(cls, book_text, ignore_checks=False):
        """
        >>> book = Book.from_book_text(
        ...     "../.# => ##./#../...\\n"
        ...     ".#./..#/### => #..#/..../..../#..#\\n"
        ... , True)
        >>> print(book.result_by_hash[
        ...     Grid.from_grid_text('../.#').get_hash()].show())
        ##.
        #..
        ...
        >>> print(book.result_by_hash[
        ...     Grid.from_grid_text('#./..').get_hash()].show())
        ##.
        #..
        ...
        """
        lines = book_text.strip().splitlines()
        rules = map(cls.parse_rule, lines)
        hash_rules = [
            (_hash, result_grid)
            for match_grid, result_grid in rules
            for _hash in match_grid.get_equivalent_hashes()
        ]
        result_by_hash = dict(hash_rules)
        if not ignore_checks:
            if len(result_by_hash) != len(hash_rules):
                raise Exception(f"Some rules were clashing")
        sizes = {
            size
            for size, _ in result_by_hash
        }
        if not ignore_checks:
            expected_hashes = set(itertools.chain(*map(
                Grid.get_all_possible_hashes, sizes)))
            missing_hashes = expected_hashes - set(result_by_hash)
            if missing_hashes:
                missing_sizes = {
                    size
                    for size, _ in missing_hashes
                }
                raise Exception(
                    f"{len(missing_hashes)} hashes for sizes {missing_sizes} "
                    f"were not represented in the rules")

        return cls(result_by_hash)

    @classmethod
    def parse_rule(cls, line):
        """
        >>> print("\\n=>\\n".join(map(
        ...     Grid.show, Book.parse_rule('../.. => .##/##./.#.'))))
        ..
        ..
        =>
        .##
        ##.
        .#.
        """
        match_grid_str, result_grid_str = cls.re_line.match(line).groups()
        match_grid = Grid.from_grid_text(match_grid_str)
        result_grid = Grid.from_grid_text(result_grid_str)

        return match_grid, result_grid

    def __init__(self, result_by_hash):
        self.result_by_hash = result_by_hash

    INITIAL_GRID_PATTERN = ".#./..#/###"

    @classmethod
    def get_initial_grid(cls):
        return Grid.from_grid_text(cls.INITIAL_GRID_PATTERN)

    def step_grid_many(self, count, grid=None, debug=False):
        """
        >>> print(Book.from_book_text(
        ...     "../.# => ##./#../...\\n"
        ...     ".#./..#/### => #..#/..../..../#..#\\n"
        ... , True).step_grid_many(2).show())
        ##.##.
        #..#..
        ......
        ##.##.
        #..#..
        ......
        """
        if grid is None:
            grid = self.get_initial_grid()
        if debug:
            print(f"Start:\n{grid.show()}")
        for step in range(count):
            grid = self.step_grid(grid, debug=debug)
            if debug:
                print(f"Step {step}:\n{grid.show()}")

        return grid

    def step_grid(self, grid=None, debug=False):
        """
        >>> print(Book.from_book_text(
        ...     "../.# => ##./#../...\\n"
        ...     ".#./..#/### => #..#/..../..../#..#\\n"
        ... , True).step_grid().show())
        #..#
        ....
        ....
        #..#
        """
        if grid is None:
            grid = self.get_initial_grid()
        if grid.size % 2 == 0:
            count = 2
        else:
            count = 3
        arrangement = grid.split(count)
        if debug:
            print(f"Split:\n{arrangement.show()}")
        stepped_arrangement = Arrangement([
            [
                self.result_by_hash[grid.get_hash()]
                for grid in row
            ]
            for row in arrangement.splits
        ])
        if debug:
            print(f"Stepped:\n{stepped_arrangement.show()}")
        return stepped_arrangement.join()


class Arrangement:
    @classmethod
    def from_splitting_grid(cls, grid, count):
        return grid.split(count)

    def __init__(self, splits):
        self.splits = splits
        if self.splits:
            self.grid_size = self.splits[0][0].size
        else:
            self.grid_size = None
        self.size = len(self.splits)

    def join(self):
        """
        >>> print(Grid.from_grid_text(
        ...     '#..#/..../..../#..#').split(2).join().show())
        #..#
        ....
        ....
        #..#
        """
        return Grid(
            self.grid_size * self.size,
            sum(map(self.join_row, self.splits), ()))

    def join_row(self, row):
        """
        >>> Arrangement([]).join_row([
        ...     Grid.from_grid_text('../.#'),
        ...     Grid.from_grid_text('#./##'),
        ... ])
        ((False, False, True, False), (False, True, True, True))
        >>> print(Grid(4, Arrangement([]).join_row([
        ...     Grid.from_grid_text('../.#'),
        ...     Grid.from_grid_text('#./##'),
        ... ]) * 2).show())
        ..#.
        .###
        ..#.
        .###
        """
        lines_parts = zip(*(
            grid.pixels
            for grid in row
        ))
        return tuple(
            sum(parts, ())
            for parts in lines_parts
        )

    def show(self):
        if not self.splits:
            return ""
        horizontal_divider = "\n{}\n".format(
            "+".join(("-" * self.grid_size,) * self.size),
        )
        return horizontal_divider.join(map(self.show_row, self.splits))

    def show_row(self, row):
        shows = map(Grid.show, row)
        shows_lines = map(str.splitlines, shows)
        lines = map("|".join, zip(*shows_lines))
        return "\n".join(lines)


@dataclass(eq=True, order=True, frozen=True)
class Grid:
    size: int
    pixels: Tuple[Tuple[bool, ...], ...]

    PARSE_MAP = {
        '.': False,
        '#': True,
    }

    @classmethod
    def from_grid_text(cls, grid_text):
        """
        >>> Grid.from_grid_text('../..')
        Grid(size=2, pixels=((False, False), (False, False)))
        """
        lines = grid_text.strip().split('/')
        size = len(lines)
        if not size:
            raise Exception(f"Got empty grid: {grid_text}")
        line_sizes = set(map(len, lines))
        if line_sizes != {size}:
            raise Exception(
                f"Expected lines to all be {size}, but got "
                f"{sorted(line_sizes)}")
        extra_characters = set("".join(lines)) - set(cls.PARSE_MAP)
        if extra_characters:
            raise Exception(
                f"Got unknown characters: {sorted(extra_characters)}")
        return cls(size, tuple(
            tuple(
                cls.PARSE_MAP[content]
                for content in line
            )
            for line in lines
        ))

    def __post_init__(self):
        if len(self.pixels) != self.size:
            raise Exception(f"Got size {self.size} but {len(self.pixels)} rows")

    def __getitem__(self, item):
        if not isinstance(item, tuple):
            raise ValueError(f"Expected 2-tuple not {item}")
        if len(item) != 2:
            raise ValueError(f"Expected 2-tuple not {len(item)}-tuple {item}")
        x, y = item
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError(f"Expected 2-tuple of ints not {item}")
        if not (0 <= x < self.size) or not (0 <= y < self.size):
            raise ValueError(
                f"Expected coordinates to be in [0, {self.size}), not {item}")
        return self.pixels[y][x]

    def get_pixel_count(self):
        """
        >>> Grid.from_grid_text('../..').get_pixel_count()
        0
        >>> Grid.from_grid_text(
        ...     '##.##./#..#../....../##.##./#..#../......').get_pixel_count()
        12
        """
        return utils.helper.iterable_length(filter(
            None, itertools.chain(*self.pixels)))

    def join(self, splits):
        sizes = {
            grid.size
            for row in splits
            for grid in row
        }
        if not sizes:
            raise Exception(f"No splits were passed in")

    def split(self, count):
        """
        >>> print(Grid.from_grid_text('../..').split(1).show())
        .|.
        -+-
        .|.
        >>> print(Grid.from_grid_text('#..#/..../..../#..#').split(2).show())
        #.|.#
        ..|..
        --+--
        ..|..
        #.|.#
        >>> print(Grid.from_grid_text(
        ...     '##.#.#/#.##.#/..####/.#..##/#.###./##..#.').split(2).show())
        ##|.#|.#
        #.|##|.#
        --+--+--
        ..|##|##
        .#|..|##
        --+--+--
        #.|##|#.
        ##|..|#.
        """
        if self.size % count != 0:
            raise Exception(f"{count} does not evenly divide {self.size}")
        cls = type(self)
        # noinspection PyArgumentList
        return Arrangement([
            [
                cls(count, tuple(
                    tuple(
                        self[x_start + x, y_start + y]
                        for x in range(count)
                    )
                    for y in range(count)
                ))
                for x_start in range(0, self.size, count)
            ]
            for y_start in range(0, self.size, count)
        ])

    def get_equivalent_hashes(self):
        """
        >>> sorted(_hash for _, _hash in
        ...        Grid.from_grid_text('../..').get_equivalent_hashes())
        [0]
        >>> sorted(_hash for _, _hash in
        ...        Grid.from_grid_text('#./..').get_equivalent_hashes())
        [1, 2, 4, 8]
        >>> sorted(_hash for _, _hash in
        ...        Grid.from_grid_text('.#/..').get_equivalent_hashes())
        [1, 2, 4, 8]
        >>> sorted(_hash for _, _hash in
        ...        Grid.from_grid_text('../#.').get_equivalent_hashes())
        [1, 2, 4, 8]
        >>> sorted(_hash for _, _hash in
        ...        Grid.from_grid_text('../.#').get_equivalent_hashes())
        [1, 2, 4, 8]
        >>> sorted(_hash for _, _hash in
        ...        Grid.from_grid_text('#./.#').get_equivalent_hashes())
        [6, 9]
        """
        return {
            oriented.get_hash()
            for oriented in self.get_orientations()
        }

    def get_hash(self):
        """
        >>> Grid.from_grid_text('../..').get_hash()
        (2, 0)
        >>> Grid.from_grid_text('#./..').get_hash()
        (2, 1)
        >>> Grid.from_grid_text('.#/..').get_hash()
        (2, 2)
        >>> Grid.from_grid_text('../#.').get_hash()
        (2, 4)
        >>> Grid.from_grid_text('../.#').get_hash()
        (2, 8)
        >>> [
        ...     Grid.from_grid_text(f'{a}{b}/{c}{d}').get_hash()[1]
        ...     for d, c, b, a in itertools.product(('.', '#'), repeat=4)
        ... ]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        """
        return (self.size, sum(
            2 ** index
            for index, pixel in enumerate(
                pixel
                for line in self.pixels
                for pixel in line
            )
            if pixel
        ))

    @classmethod
    def get_all_possible_hashes(cls, size):
        """
        >>> list(Grid.get_all_possible_hashes(1))
        [(1, 0), (1, 1)]
        >>> [_hash for _, _hash in Grid.get_all_possible_hashes(2)]
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        """
        return (
            (size, _hash)
            for _hash in range(2 ** (size ** 2))
        )

    def get_orientations(self):
        """
        >>> print("\\n-\\n".join(sorted(map(
        ...     Grid.show, Grid.from_grid_text('../..').get_orientations()))))
        ..
        ..
        >>> print("\\n-\\n".join(sorted(map(
        ...     Grid.show, Grid.from_grid_text('.#/..').get_orientations()))))
        #.
        ..
        -
        .#
        ..
        -
        ..
        #.
        -
        ..
        .#
        """
        return self.get_rotations() | self.flip().get_rotations()

    def get_rotations(self):
        orientations = set()
        rotated = self
        orientations.add(rotated)
        rotated = rotated.rotate()
        orientations.add(rotated)
        rotated = rotated.rotate()
        orientations.add(rotated)
        rotated = rotated.rotate()
        orientations.add(rotated)

        return orientations

    def flip(self):
        """
        >>> print(Grid.from_grid_text('.#./..#/###').flip().show())
        .#.
        #..
        ###
        >>> print(Grid.from_grid_text('.#./..#/###').flip().flip().show())
        .#.
        ..#
        ###
        """
        cls = type(self)
        rotate_map = self.get_flip_map()
        # noinspection PyArgumentList
        return cls(self.size, tuple(
            tuple(
                self[rotate_map[(x, y)]]
                for x in range(self.size)
            )
            for y in range(self.size)
        ))

    FLIP_MAP = {}

    def get_flip_map(self):
        if self.size not in self.FLIP_MAP:
            self.FLIP_MAP[self.size] = {
                (self.size - 1 - x, y): (x, y)
                for x in range(self.size)
                for y in range(self.size)
            }

        return self.FLIP_MAP[self.size]

    def rotate(self):
        """
        >>> print(Grid.from_grid_text('.#./..#/###').rotate().show())
        .##
        #.#
        ..#
        >>> print(Grid.from_grid_text('.#./..#/###').rotate().rotate().show())
        ###
        #..
        .#.
        >>> print(Grid.from_grid_text('.#./..#/###')
        ...       .rotate().rotate().rotate().show())
        #..
        #.#
        ##.
        >>> print(Grid.from_grid_text('.#./..#/###')
        ...       .rotate().rotate().rotate().rotate().show())
        .#.
        ..#
        ###
        """
        cls = type(self)
        rotate_map = self.get_rotate_map()
        # noinspection PyArgumentList
        return cls(self.size, tuple(
            tuple(
                self[rotate_map[(x, y)]]
                for x in range(self.size)
            )
            for y in range(self.size)
        ))

    ROTATE_MAP = {}

    def get_rotate_map(self):
        if self.size not in self.ROTATE_MAP:
            self.ROTATE_MAP[self.size] = {
                (y, self.size - 1 - x): (x, y)
                for x in range(self.size)
                for y in range(self.size)
            }

        return self.ROTATE_MAP[self.size]

    SHOW_MAP = {
        pixel: content
        for content, pixel in PARSE_MAP.items()
    }

    def show(self):
        """
        >>> print(Grid.from_grid_text('../..').show())
        ..
        ..
        >>> print(Grid.from_grid_text('.#./..#/###').show())
        .#.
        ..#
        ###
        >>> print(Grid.from_grid_text('#..#/..../#..#/.##.').show())
        #..#
        ....
        #..#
        .##.
        """
        return "\n".join(
            "".join(
                self.SHOW_MAP[pixel]
                for pixel in line
            )
            for line in self.pixels
        )


Challenge.main()
challenge = Challenge()
