#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_03.part_a import RucksackSet, Rucksack


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2620
        """
        return RucksackSetExtended\
            .from_rucksacks_text(_input)\
            .get_groups_badge_priority_sum()


class RucksackSetExtended(RucksackSet):
    def get_groups_badge_priority_sum(self) -> int:
        """
        >>> RucksackSetExtended.from_rucksacks_text(
        ...     "vJrwpWtwJgWrhcsFMMfFFhFp"
        ...     "\\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL"
        ...     "\\nPmmdzqPrVvPwwTWBwg"
        ...     "\\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn"
        ...     "\\nttgJtRGJQctTZtZT\\nCrZsJsPPZsGzwwsLwLmpwMDw"
        ... ).get_groups_badge_priority_sum()
        70
        """
        return sum(
            self.get_group_badge_priority(group)
            for group in self.get_groups()
        )

    def get_groups(self) -> [[Rucksack]]:
        """
        >>> RucksackSetExtended.from_rucksacks_text(
        ...     "vJrwpWtwJgWrhcsFMMfFFhFp"
        ...     "\\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL"
        ...     "\\nPmmdzqPrVvPwwTWBwg"
        ...     "\\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn"
        ...     "\\nttgJtRGJQctTZtZT\\nCrZsJsPPZsGzwwsLwLmpwMDw"
        ... ).get_groups()
        [[Rucksack(...), Rucksack(...), Rucksack(...)],
            [Rucksack(...), Rucksack(...), Rucksack(...)]]
        """
        if len(self.rucksacks) % 3 != 0:
            raise Exception(
                f"Expected rucksacks to be a multiple of 3: "
                f"{len(self.rucksacks)}"
            )

        return [
            self.rucksacks[start_index:start_index + 3]
            for start_index in range(0, len(self.rucksacks), 3)
        ]

    def get_group_badge_priority(self, rucksacks: [Rucksack]) -> int:
        """
        >>> rucksack_set = RucksackSetExtended.from_rucksacks_text(
        ...     "vJrwpWtwJgWrhcsFMMfFFhFp"
        ...     "\\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL"
        ...     "\\nPmmdzqPrVvPwwTWBwg"
        ...     "\\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn"
        ...     "\\nttgJtRGJQctTZtZT\\nCrZsJsPPZsGzwwsLwLmpwMDw"
        ... )
        >>> rucksack_set.get_group_badge_priority(rucksack_set.rucksacks[:3])
        18
        >>> rucksack_set.get_group_badge_priority(rucksack_set.rucksacks[3:6])
        52
        """
        return Rucksack.priority_map[self.get_group_badge(rucksacks)]

    def get_group_badge(self, rucksacks: [Rucksack]) -> str:
        """
        >>> rucksack_set = RucksackSetExtended.from_rucksacks_text(
        ...     "vJrwpWtwJgWrhcsFMMfFFhFp"
        ...     "\\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL"
        ...     "\\nPmmdzqPrVvPwwTWBwg"
        ...     "\\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn"
        ...     "\\nttgJtRGJQctTZtZT\\nCrZsJsPPZsGzwwsLwLmpwMDw"
        ... )
        >>> rucksack_set.get_group_badge(rucksack_set.rucksacks[:3])
        'r'
        >>> rucksack_set.get_group_badge(rucksack_set.rucksacks[3:6])
        'Z'
        """
        if not rucksacks:
            raise Exception("Empty group given")
        common_rucksack_items = set(rucksacks[0].contents)
        for rucksack in rucksacks[1:]:
            rucksack_items = set(rucksack.contents)
            common_rucksack_items &= rucksack_items
            if not common_rucksack_items:
                raise Exception("There are no common items in group")

        if len(common_rucksack_items) != 1:
            raise Exception(
                f"There isn't exactly 1 common item in the group: "
                f"{common_rucksack_items}"
            )

        badge, = common_rucksack_items
        return badge


Challenge.main()
challenge = Challenge()
