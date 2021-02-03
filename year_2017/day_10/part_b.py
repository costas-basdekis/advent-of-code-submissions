#!/usr/bin/env python3
import functools

import utils
from year_2017.day_10 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'dc7e7dee710d4c7201ce42713e6b8359'
        """
        return KnotExtended.from_knot_ascii_text(_input)\
            .step_many()\
            .get_dense_hash()


class KnotExtended(part_a.Knot):
    @classmethod
    def from_knot_ascii_text(cls, knot_text, position=0, skip_size=0,
                             length=256):
        """
        >>> KnotExtended.from_knot_ascii_text('1,2,3').lengths
        [49, 44, 50, 44, 51, 17, 31, 73, 47, 23]
        """
        lengths = list(map(ord, knot_text.strip())) + [17, 31, 73, 47, 23]
        return cls(lengths, position, skip_size, list(range(length)))

    def get_dense_hash(self, block_size=16):
        """
        >>> KnotExtended.from_knot_ascii_text('').get_dense_hash()
        '00000000000000000000000000000000'
        >>> KnotExtended.from_knot_ascii_text('').step_many().get_dense_hash()
        'a2582a3a0e66e6e86e3812dcb672a272'
        >>> next((
        ...     count
        ...     for count in range(128)
        ...     if (
        ...         KnotExtended.from_knot_ascii_text('')
        ...         .step_many(count)
        ...         .get_dense_hash()
        ...     ) == 'a2582a3a0e66e6e86e3812dcb672a272'
        ... ), None)
        64
        >>> KnotExtended.from_knot_ascii_text(
        ...     'AoC 2017').step_many().get_dense_hash()
        '33efeb34ea91902bb2f59c9920caa6cd'
        >>> KnotExtended.from_knot_ascii_text(
        ...     '1,2,3').step_many().get_dense_hash()
        '3efbe78a8d82f29979031a4aa0b16a9d'
        >>> KnotExtended.from_knot_ascii_text(
        ...     '1,2,4').step_many().get_dense_hash()
        '63960835bcdc130f0b66d7ff4f6a5a8e'
        """
        return self.get_dense_hash_for_elements(self.elements, block_size)

    def get_dense_hash_for_elements(self, elements, block_size=16):
        """
        >>> KnotExtended.from_knot_ascii_text('')\\
        ...     .get_dense_hash_for_elements([64, 7, 255], 1)
        '4007ff'
        """
        blocks = self.get_blocks(elements, block_size=block_size)
        block_outputs = (
            self.get_block_output(block)
            for block in blocks
        )
        block_characters = (
            self.show_output(output)
            for output in block_outputs
        )
        return "".join(block_characters)

    def show_output(self, output):
        """
        >>> KnotExtended.from_knot_ascii_text('').show_output(64)
        '40'
        >>> KnotExtended.from_knot_ascii_text('').show_output(7)
        '07'
        >>> KnotExtended.from_knot_ascii_text('').show_output(255)
        'ff'
        """
        return "{:02x}".format(output)

    def get_block_output(self, block):
        """
        >>> KnotExtended.from_knot_ascii_text('').get_block_output(
        ...     [65, 27, 9, 1, 4, 3, 40, 50, 91, 7, 6, 0, 2, 5, 68, 22])
        64
        """
        return functools.reduce(int.__xor__, block)

    def get_blocks(self, elements, block_size=16):
        """
        >>> list(KnotExtended.from_knot_ascii_text('').get_blocks(
        ...     list(range(10))))
        [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
        >>> list(KnotExtended.from_knot_ascii_text('').get_blocks(
        ...     list(range(10)), 2))
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
        >>> list(KnotExtended.from_knot_ascii_text('').get_blocks(
        ...     list(range(256))))
        [[0, ..., 15], [16, ..., 31], ..., [240, ..., 255]]
        """
        return (
            elements[start:start + block_size]
            for start in range(0, len(elements), block_size)
        )

    def step_many(self, count=64):
        for _ in range(count):
            self.step()

        return self


Challenge.main()
challenge = Challenge()
