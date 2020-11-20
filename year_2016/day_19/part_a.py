#!/usr/bin/env python3
from dataclasses import dataclass
from itertools import count
from typing import Dict, Optional

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1842613
        """
        return Circle.from_length_text(_input).solve(debugger=debugger)


@dataclass
class Circle:
    next_map: Dict[int, int]
    position: int = 1

    @classmethod
    def from_length_text(cls, length_text: str):
        return cls.from_length(int(length_text))

    @classmethod
    def from_length(cls, length: int):
        """
        >>> Circle.from_length(5)
        Circle(next_map={1: 2, 2: 3, 3: 4, 4: 5, 5: 1}, position=1)
        """
        return cls({
            position: cls.get_next_position(position, length)
            for position in range(1, length + 1)
        })

    @classmethod
    def get_next_position(cls, position: int, length: int) -> int:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> [Circle.get_next_position(p, 5) for p in range(1, 5 + 1)]
        [2, 3, 4, 5, 1]
        >>> # noinspection PyUnresolvedReferences
        >>> [Circle.get_next_position(p, 1) for p in range(1, 1 + 1)]
        [1]
        """
        return (position % length) + 1

    def solve(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> Circle.from_length(5).solve()
        3
        >>> Circle({1: 1}).solve()
        1
        """
        return self.step_many(debugger=debugger).get_solution()

    def get_solution(self) -> int:
        """
        >>> Circle({1: 1}).get_solution()
        1
        """
        if not self.has_finished():
            raise Exception(f"Can't get solution before finishing")

        winner, = self.next_map

        return winner

    def step_many(self, step_count: Optional[int] = None,
                  debugger: Debugger = Debugger(enabled=False)):
        if step_count is None:
            steps = count()
        else:
            steps = range(step_count)
        debugger.reset()
        for _ in debugger.stepping(steps):
            self.step()
            if self.has_finished():
                break
            if debugger.should_report():
                debugger.default_report(
                    f"remaining: {len(self.next_map)}, position: "
                    f"{self.position}")

        return self

    def step(self):
        """
        >>> Circle.from_length(5).step()
        Circle(next_map={1: 3, 3: 4, 4: 5, 5: 1}, position=3)
        >>> Circle.from_length(1).step()
        Circle(next_map={1: 1}, position=1)
        >>> Circle({1: 1, 2: 1}).step()
        Traceback (most recent call last):
        ...
        Exception: Haven't finished, but current position pointed to itself: 1
        """
        if self.has_finished():
            return self

        next_position = self.next_map[self.position]
        if next_position == self.position:
            raise Exception(
                f"Haven't finished, but current position pointed to itself: "
                f"{self.position}")
        next_next_position = self.next_map[next_position]
        self.next_map[self.position] = next_next_position
        del self.next_map[next_position]
        self.position = next_next_position

        return self

    def has_finished(self) -> bool:
        return len(self.next_map) <= 1


Challenge.main()
challenge = Challenge()
