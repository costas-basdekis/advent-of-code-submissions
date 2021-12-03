#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, count_by


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        353079
        """
        return School.from_school_text(_input).advance_many(80).fish_count


@dataclass
class School:
    counts: Dict[int, int]

    @classmethod
    def from_school_text(cls, school_text: str) -> "School":
        """
        >>> School.from_school_text("3,4,3,1,2")
        School(counts={1: 1, 2: 1, 3: 2, 4: 1})
        """
        timers = map(int, school_text.split(","))
        return cls.from_timers(timers)

    @classmethod
    def from_timers(cls, timers: Iterable[int]) -> "School":
        return cls(counts=count_by(timers))

    def advance(self) -> "School":
        """
        >>> School.from_school_text("3,4,3,1,2").advance()
        School(counts={0: 1, 1: 1, 2: 2, 3: 1})
        >>> School.from_school_text("3,4,3,1,2").advance().advance()
        School(counts={0: 1, 1: 2, 2: 1, 6: 1, 8: 1})
        >>> School.from_school_text("3,4,3,1,2,8,10").advance().advance()
        School(counts={0: 1, 1: 2, 2: 1, 6: 2, 8: 2})
        >>> School({}).advance()
        School(counts={})
        """
        if not self.counts:
            return self

        new_counts = {
            timer - 1: count
            for timer, count in self.counts.items()
            if timer > 0
        }
        zero_count = self.counts.get(0)
        if zero_count:
            new_counts.setdefault(6, 0)
            new_counts[6] += zero_count
            new_counts.setdefault(8, 0)
            new_counts[8] += zero_count

        self.counts = new_counts
        return self

    def advance_many(self, count: int) -> "School":
        """
        >>> School.from_school_text("3,4,3,1,2,8,10").advance_many(2)
        School(counts={0: 1, 1: 2, 2: 1, 6: 2, 8: 2})
        """
        for _ in range(count):
            self.advance()

        return self

    @property
    def fish_count(self) -> int:
        """
        >>> School.from_school_text("3,4,3,1,2").fish_count
        5
        >>> School.from_school_text("3,4,3,1,2").advance_many(18).fish_count
        26
        >>> School.from_school_text("3,4,3,1,2").advance_many(80).fish_count
        5934
        """
        return sum(self.counts.values())


Challenge.main()
challenge = Challenge()
