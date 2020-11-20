#!/usr/bin/env python3
import itertools
from dataclasses import dataclass
from typing import List

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        373160
        """
        return Message.from_text(_input).step_many().steps


@dataclass
class Message:
    instructions: List[int]
    position: int = 0
    steps: int = 0

    @classmethod
    def from_text(cls, text, position=0, steps=0):
        """
        >>> Message.from_text("0\\n3\\n0\\n1\\n-3")
        Message(instructions=[0, 3, 0, 1, -3], position=0, steps=0)
        """
        return cls(
            list(map(int, text.strip().splitlines())), position=position,
            steps=steps)

    def step_many(self, count=None):
        """
        >>> Message.from_text("0\\n3\\n0\\n1\\n-3").step_many(4)
        Message(instructions=[2, 4, 0, 1, -2], position=1, steps=4)
        >>> Message.from_text("0\\n3\\n0\\n1\\n-3").step_many(5)
        Message(instructions=[2, 5, 0, 1, -2], position=5, steps=5)
        >>> Message.from_text("0\\n3\\n0\\n1\\n-3").step_many(6)
        Message(instructions=[2, 5, 0, 1, -2], position=5, steps=5)
        >>> Message.from_text("0\\n3\\n0\\n1\\n-3").step_many()
        Message(instructions=[2, 5, 0, 1, -2], position=5, steps=5)
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        for _ in steps:
            self.step()
            if self.has_finished():
                break

        return self

    def step(self):
        """
        >>> Message.from_text("0\\n3\\n0\\n1\\n-3").step()
        Message(instructions=[1, 3, 0, 1, -3], position=0, steps=1)
        """
        if self.has_finished():
            return self

        next_position = self.position + self.instructions[self.position]
        self.instructions[self.position] += 1
        self.position = next_position
        self.steps += 1

        return self

    def has_finished(self):
        """
        >>> Message(instructions=[1, 3, 0, 1, -3], position=0).has_finished()
        False
        >>> Message(instructions=[1, 3, 0, 1, -3], position=4).has_finished()
        False
        >>> Message(instructions=[1, 3, 0, 1, -3], position=5).has_finished()
        True
        >>> Message(instructions=[1, 3, 0, 1, -3], position=-1).has_finished()
        True
        >>> Message(instructions=[1, 3, 0, 1, -3], position=10).has_finished()
        True
        """
        return not (0 <= self.position < len(self.instructions))


challenge = Challenge()
challenge.main()
