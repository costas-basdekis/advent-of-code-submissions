#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1935
        """
        knot = Knot.from_knot_text(_input)
        if debug:
            print(knot)
            print(knot.show())
        return knot.step().get_hash()


@dataclass
class Knot:
    lengths: List[int]
    position: int
    skip_size: int
    elements: List[int]

    @classmethod
    def from_knot_text(cls, knot_text, position=0, skip_size=0, length=256):
        lengths = list(map(int, knot_text.strip().split(',')))
        return cls(lengths, position, skip_size, list(range(length)))

    def get_hash(self):
        """
        >>> Knot.from_knot_text('3,4,1,5', length=5).step().get_hash()
        12
        """
        return self.elements[0] * self.elements[1]

    def step(self):
        """
        >>> Knot.from_knot_text('3,4,1,5', length=5).step().show()
        '3 4 2 1 [0]'
        """
        for length in self.lengths:
            self.step_length(length)

        return self

    def step_length(self, length):
        """
        >>> knot = Knot.from_knot_text('3,4,1,5', length=5)
        >>> knot.step_length(3).show()
        '2 1 0 [3] 4'
        >>> knot.step_length(4).show()
        '4 3 0 [1] 2'
        >>> knot.step_length(1).show()
        '4 [3] 0 1 2'
        >>> knot.step_length(5).show()
        '3 4 2 1 [0]'
        """
        start = self.position
        end = (self.position + length) % len(self.elements)
        if length == 0:
            pass
        elif end > start:
            self.elements[start:end] = reversed(self.elements[start:end])
        else:
            elements = self.elements[start:] + self.elements[:end]
            reversed_elements = list(reversed(elements))
            self.elements[start:] = reversed_elements[:-end]
            self.elements[:end] = reversed_elements[-end:]

        self.position = (end + self.skip_size) % len(self.elements)
        self.skip_size += 1

        return self

    def show(self):
        """
        >>> Knot.from_knot_text('3,4,1,5', length=5).show()
        '[0] 1 2 3 4'
        """
        return " ".join(
            f"[{element}]"
            if index == self.position else
            str(element)
            for index, element in enumerate(self.elements)
        )


challenge = Challenge()
challenge.main()
