#!/usr/bin/env python3
from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return PrinterProtocol.from_text(_input).get_sum_of_middle_pages_of_valid_updates()


@dataclass
class PrinterProtocol:
    ruleset: "Ruleset"
    updates: List["Update"]

    @classmethod
    def from_text(cls, text: str) -> "PrinterProtocol":
        """
        >>> _protocol = PrinterProtocol.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ...
        ...     75,47,61,53,29
        ...     97,61,53,29,13
        ...     75,29,13
        ...     75,97,47,61,53
        ...     61,13,29
        ...     97,13,75,29,47
        ... ''')
        >>> len(_protocol.ruleset.previous_pages), len(_protocol.updates)
        (6, 6)
        """
        precedence_str, updates_str = text.strip().split("\n\n")
        return cls(
            ruleset=Ruleset.from_text(precedence_str),
            updates=list(map(Update.from_text, updates_str.strip().splitlines())),
        )

    def get_sum_of_middle_pages_of_valid_updates(self) -> int:
        """
        >>> PrinterProtocol.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ...
        ...     75,47,61,53,29
        ...     97,61,53,29,13
        ...     75,29,13
        ...     75,97,47,61,53
        ...     61,13,29
        ...     97,13,75,29,47
        ... ''').get_sum_of_middle_pages_of_valid_updates()
        143
        """
        return sum(self.get_middle_pages_of_valid_updates())

    def get_middle_pages_of_valid_updates(self) -> Iterable[int]:
        """
        >>> list(PrinterProtocol.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ...
        ...     75,47,61,53,29
        ...     97,61,53,29,13
        ...     75,29,13
        ...     75,97,47,61,53
        ...     61,13,29
        ...     97,13,75,29,47
        ... ''').get_middle_pages_of_valid_updates())
        [61, 53, 29]
        """
        return (
            update.get_middle_page()
            for update in self.get_valid_updates()
        )

    def get_valid_updates(self) -> Iterable["Update"]:
        """
        >>> _protocol = PrinterProtocol.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ...
        ...     75,47,61,53,29
        ...     97,61,53,29,13
        ...     75,29,13
        ...     75,97,47,61,53
        ...     61,13,29
        ...     97,13,75,29,47
        ... ''')
        >>> print("\\n".join(map(str, _protocol.get_valid_updates())))
        75,47,61,53,29
        97,61,53,29,13
        75,29,13
        """
        return (
            update
            for update in self.updates
            if update.is_valid(self.ruleset)
        )


@dataclass
class Ruleset:
    previous_pages: Dict[int, Set[int]]
    next_pages: Dict[int, Set[int]]

    @classmethod
    def from_text(cls, text: str) -> "Ruleset":
        previous_pages = {}
        next_pages = {}
        for line in text.strip().splitlines():
            first, second = map(int, line.split("|"))
            previous_pages.setdefault(second, set()).add(first)
            next_pages.setdefault(first, set()).add(second)
        return cls(previous_pages=previous_pages, next_pages=next_pages)

    def are_pages_in_order(self, first: int, second: int) -> bool:
        """
        >>> _ruleset = Ruleset.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ... ''')
        >>> [_ruleset.are_pages_in_order(first, second) for first, second in [(75, 29), (29, 13), (75, 13)]]
        [True, True, True]
        """
        return second not in self.previous_pages.get(first, set())


@dataclass
class Update:
    pages: List[int]

    @classmethod
    def from_text(cls, text: str) -> "Update":
        return cls(pages=list(map(int, text.strip().split(","))))

    def __str__(self) -> str:
        return ",".join(map(str, self.pages))

    def is_valid(self, ruleset: Ruleset) -> bool:
        """
        >>> _ruleset = Ruleset.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ... ''')
        >>> Update.from_text("75,29,13").is_valid(_ruleset)
        True
        """
        return all(
            ruleset.are_pages_in_order(first, second)
            for first, second in combinations(self.pages, 2)
        )

    def get_middle_page(self) -> int:
        return self.pages[len(self.pages) // 2]


Challenge.main()
challenge = Challenge()
