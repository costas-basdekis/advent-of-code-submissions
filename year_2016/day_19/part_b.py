#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Sized, List

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1424135
        """
        return OppositeGame.from_length_text(_input).solve(debugger=debugger)


@dataclass
class OppositeGame(part_a.BaseGame):
    remaining: List[int]
    position: int = 1
    index: int = 0

    @classmethod
    def from_length(cls, length: int):
        """
        >>> OppositeGame.from_length(5)
        OppositeGame(remaining=[1, 2, 3, 4, 5], position=1, index=0)
        """
        return cls(list(range(1, length + 1)))

    def step(self):
        """
        >>> game = OppositeGame.from_length(5)
        >>> game.step()
        OppositeGame(remaining=[1, 2, 4, 5], position=2, index=1)
        >>> game.step()
        OppositeGame(remaining=[1, 2, 4], position=4, index=2)
        >>> game.step()
        OppositeGame(remaining=[2, 4], position=2, index=0)
        >>> game.step()
        OppositeGame(remaining=[2], position=2, index=0)
        >>> game.step()
        OppositeGame(remaining=[2], position=2, index=0)
        >>> OppositeGame.from_length(5).solve()
        2
        """
        if self.has_finished():
            return self
        offset = len(self.remaining) // 2
        removed_index = (self.index + offset) % len(self.remaining)
        if removed_index > self.index:
            next_index = (self.index + 1) % (len(self.remaining) - 1)
        else:
            next_index = self.index % (len(self.remaining) - 1)
        self.remaining[removed_index:removed_index + 1] = []
        self.index = next_index
        self.position = self.remaining[self.index]

        return self

    def get_remaining_positions(self) -> Sized:
        return self.remaining


Challenge.main()
challenge = Challenge()
