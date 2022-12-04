#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        538
        """
        return AssignmentPairSet\
            .from_assignment_pairs_text(_input)\
            .get_containing_pair_count()


@dataclass
class AssignmentPairSet:
    pairs: ["AssignmentPair"]

    @classmethod
    def from_assignment_pairs_text(
        cls, assignment_pairs_text: str,
    ) -> "AssignmentPairSet":
        """
        >>> AssignmentPairSet.from_assignment_pairs_text(
        ...     "2-4,6-8\\n2-3,4-5\\n5-7,7-9\\n2-8,3-7\\n6-6,4-6\\n2-6,4-8")
        AssignmentPairSet(pairs=[AssignmentPair(first=Assignment(start=2, end=4),
            second=Assignment(start=6, end=8)), ...])
        """
        return cls(
            pairs=[
                AssignmentPair.from_assignment_pair_text(line)
                for line in assignment_pairs_text.strip().splitlines()
            ],
        )

    def get_containing_pair_count(self) -> int:
        """
        >>> AssignmentPairSet.from_assignment_pairs_text(
        ...     "2-4,6-8\\n2-3,4-5\\n5-7,7-9\\n2-8,3-7\\n6-6,4-6\\n2-6,4-8")\\
        ...     .get_containing_pair_count()
        2
        """
        return len(self.get_containing_pairs())

    def get_containing_pairs(self) -> ["AssignmentPair"]:
        """
        >>> AssignmentPairSet.from_assignment_pairs_text(
        ...     "2-4,6-8\\n2-3,4-5\\n5-7,7-9\\n2-8,3-7\\n6-6,4-6\\n2-6,4-8")\\
        ...     .get_containing_pairs()
        [AssignmentPair(first=Assignment(start=2, end=8),
            second=Assignment(start=3, end=7)),
            AssignmentPair(first=Assignment(start=6, end=6),
                second=Assignment(start=4, end=6))]
        """
        return [
            pair
            for pair in self.pairs
            if pair.is_an_assignment_contained()
        ]


@dataclass
class AssignmentPair:
    first: "Assignment"
    second: "Assignment"

    @classmethod
    def from_assignment_pair_text(
        cls, assignment_pair_text: str,
    ) -> "AssignmentPair":
        """
        >>> AssignmentPair.from_assignment_pair_text("2-4,6-8")
        AssignmentPair(first=Assignment(start=2, end=4),
            second=Assignment(start=6, end=8))
        """
        first_text, second_text = assignment_pair_text.strip().split(",")
        return cls(
            first=Assignment.from_assignment_text(first_text),
            second=Assignment.from_assignment_text(second_text),
        )

    def is_an_assignment_contained(self) -> bool:
        """
        >>> AssignmentPair.from_assignment_pair_text("2-4,6-8")\\
        ...     .is_an_assignment_contained()
        False
        >>> AssignmentPair.from_assignment_pair_text("2-8,3-7")\\
        ...     .is_an_assignment_contained()
        True
        >>> AssignmentPair.from_assignment_pair_text("6-6,4-6")\\
        ...     .is_an_assignment_contained()
        True
        """
        return (
            self.first.contains(self.second)
            or self.second.contains(self.first)
        )


@dataclass
class Assignment:
    start: int
    end: int

    re_assignment = re.compile(r"^(\d+)-(\d+)$")

    @classmethod
    def from_assignment_text(cls, assignment_text: str) -> "Assignment":
        """
        >>> Assignment.from_assignment_text("2-4")
        Assignment(start=2, end=4)
        """
        start_str, end_str = \
            cls.re_assignment.match(assignment_text.strip()).groups()
        return cls(start=int(start_str), end=int(end_str))

    def contains(self, other: "Assignment") -> bool:
        """
        >>> Assignment(2, 8).contains(Assignment(3, 7))
        True
        >>> Assignment(2, 8).contains(Assignment(3, 8))
        True
        >>> Assignment(2, 8).contains(Assignment(2, 7))
        True
        >>> Assignment(2, 8).contains(Assignment(2, 8))
        True
        >>> Assignment(2, 8).contains(Assignment(2, 9))
        False
        >>> Assignment(2, 8).contains(Assignment(1, 8))
        False
        >>> Assignment(2, 8).contains(Assignment(20, 30))
        False
        """
        return self.start <= other.start and self.end >= other.end


Challenge.main()
challenge = Challenge()
