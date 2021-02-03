#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List

import utils
from year_2017.day_10.part_b import KnotExtended


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        8304
        """
        return Disk.from_hash_input(_input.strip()).get_cell_count()


@dataclass
class Disk:
    cells: List[List[bool]]

    @classmethod
    def from_hash_input(cls, hash_input):
        row_hashes = (
            KnotExtendedTwice.get_dense_hash_for_text(f"{hash_input}-{index}")
            for index in range(128)
        )
        row_binaries = (
            cls.get_hash_binary(_hash)
            for _hash in row_hashes
        )
        rows = [
            cls.get_row_from_binary(binary)
            for binary in row_binaries
        ]

        return cls(rows)

    @classmethod
    def get_row_from_binary(cls, binary):
        """
        >>> Disk.get_row_from_binary('101011100')
        [True, False, True, False, True, True, True, False, False]
        """
        return [
            digit == '1'
            for digit in binary
        ]

    @classmethod
    def get_hash_binary(cls, _hash):
        """
        >>> Disk.get_hash_binary('a0c20170')
        '10100000110000100000000101110000'
        """
        return "".join(
            '{:04b}'.format(int(digit, 16))
            for digit in _hash
        )

    def get_cell_count(self):
        """
        >>> Disk.from_hash_input('flqrgnkx').get_cell_count()
        8108
        """
        return utils.helper.iterable_length(self.get_cells())

    def get_cells(self):
        """
        >>> sorted(set(Disk.from_hash_input('flqrgnkx').get_cells()) & {
        ...     utils.Point2D(x, y)
        ...     for x in range(3)
        ...    for y in range(3)
        ... })
        [Point2D(x=0, y=0), Point2D(x=1, y=0), Point2D(x=1, y=1)]
        """
        return (
            utils.Point2D(x, y)
            for y, row in enumerate(self.cells)
            for x, cell in enumerate(row)
            if cell
        )

    SHOW_MAP = {
        True: "#",
        False: ".",
    }

    def show(self, max_rows=128, max_columns=128):
        """
        >>> print(Disk.from_hash_input('flqrgnkx').show(8, 8))
        ##.#.#..
        .#.#.#.#
        ....#.#.
        #.#.##.#
        .##.#...
        ##..#..#
        .#...#..
        ##.#.##.
        """
        return "\n".join(
            "".join(
                self.SHOW_MAP[cell]
                for cell in row[:max_columns]
            )
            for row in self.cells[:max_rows]
        )


class KnotExtendedTwice(KnotExtended):
    @classmethod
    def get_dense_hash_for_text(cls, text, count=64, block_size=16):
        """
        >>> KnotExtendedTwice.get_dense_hash_for_text('')
        'a2582a3a0e66e6e86e3812dcb672a272'
        """
        return cls.from_knot_ascii_text(text)\
            .step_many(count)\
            .get_dense_hash(block_size)


Challenge.main()
challenge = Challenge()
