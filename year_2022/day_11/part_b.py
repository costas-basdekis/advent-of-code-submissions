#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge, lcm
from year_2022.day_11 import part_a
from year_2022.day_11.part_a import Monkey, Item, MonkeySet, MONKEYS_TEST_TEXT


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        23612457316
        """
        return MonkeySetExtended\
            .from_monkeys_text(_input)\
            .apply_rounds(10000, debugger=debugger)\
            .get_monkey_business()


@dataclass
class MonkeySetExtended(MonkeySet["MonkeyExtended"]):
    """
    >>> monkeys = MonkeySetExtended.from_monkeys_text(MONKEYS_TEST_TEXT)
    >>> print(monkeys.apply_rounds(1).display_inspection_counts())
    Monkey 0 inspected items 2 times.
    Monkey 1 inspected items 4 times.
    Monkey 2 inspected items 3 times.
    Monkey 3 inspected items 6 times.
    >>> print(monkeys.apply_rounds(999).display_inspection_counts())
    Monkey 0 inspected items 5204 times.
    Monkey 1 inspected items 4792 times.
    Monkey 2 inspected items 199 times.
    Monkey 3 inspected items 5192 times.
    >>> print(monkeys.apply_rounds(9000).display_inspection_counts())
    Monkey 0 inspected items 52166 times.
    Monkey 1 inspected items 47830 times.
    Monkey 2 inspected items 1938 times.
    Monkey 3 inspected items 52013 times.
    """

    def __post_init__(self):
        test_lcm = lcm(*(
            monkey.test_divisor
            for monkey in self.monkeys_by_id.values()
        ))
        for monkey in self.monkeys_by_id.values():
            monkey: MonkeyExtended
            monkey.worry_level_modulo = test_lcm


class MonkeyExtended(Monkey):
    worry_level_modulo: int = 0

    def relief_worry(self, item: Item) -> None:
        item.worry_level = item.worry_level % self.worry_level_modulo


Challenge.main()
challenge = Challenge()
