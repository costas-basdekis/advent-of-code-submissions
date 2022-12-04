#!/usr/bin/env python3
import string
from dataclasses import dataclass
from typing import ClassVar, Dict, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        8123
        """
        return RucksackSet\
            .from_rucksacks_text(_input)\
            .get_common_items_priority_sum()


@dataclass
class RucksackSet:
    rucksacks: ["Rucksack"]

    @classmethod
    def from_rucksacks_text(
        cls: Cls["RucksackSet"], rucksacks_text: str,
    ) -> Self["RucksackSet"]:
        """
        >>> RucksackSet.from_rucksacks_text(
        ...     "vJrwpWtwJgWrhcsFMMfFFhFp"
        ...     "\\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL"
        ...     "\\nPmmdzqPrVvPwwTWBwg"
        ...     "\\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn"
        ...     "\\nttgJtRGJQctTZtZT\\nCrZsJsPPZsGzwwsLwLmpwMDw"
        ... )
        RucksackSet(rucksacks=[Rucksack(contents=['v', 'J', 'r', 'w', 'p', 'W',
        't', 'w', 'J', 'g', 'W', 'r', 'h', 'c', 's', 'F', 'M', 'M', 'f', 'F',
        'F', 'h', 'F', 'p']), ...])
        """
        return cls(
            rucksacks=[
                Rucksack.from_rucksack_text(line)
                for line in rucksacks_text.strip().splitlines()
            ],
        )

    def get_common_items_priority_sum(self) -> int:
        """
        >>> RucksackSet.from_rucksacks_text(
        ...     "vJrwpWtwJgWrhcsFMMfFFhFp"
        ...     "\\njqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL"
        ...     "\\nPmmdzqPrVvPwwTWBwg"
        ...     "\\nwMqvLMZHhHMvwLHjbvcjnnSBnvTQFn"
        ...     "\\nttgJtRGJQctTZtZT\\nCrZsJsPPZsGzwwsLwLmpwMDw"
        ... ).get_common_items_priority_sum()
        157
        """
        return sum(
            rucksack.get_common_item_priority()
            for rucksack in self.rucksacks
        )


@dataclass
class Rucksack:
    contents: [str]

    @classmethod
    def from_rucksack_text(cls, rucksack_text: str) -> "Rucksack":
        """
        >>> Rucksack.from_rucksack_text("vJrwpWtwJgWrhcsFMMfFFhFp")
        Rucksack(contents=['v', 'J', 'r', 'w', 'p', 'W', 't', 'w', 'J', 'g',
        'W', 'r', 'h', 'c', 's', 'F', 'M', 'M', 'f', 'F', 'F', 'h', 'F', 'p'])
        """
        return cls(contents=list(rucksack_text.strip()))

    @property
    def front(self) -> [str]:
        """
        >>> Rucksack.from_rucksack_text("vJrwpWtwJgWrhcsFMMfFFhFp").front
        ['v', 'J', 'r', 'w', 'p', 'W', 't', 'w', 'J', 'g', 'W', 'r']
        """
        if len(self.contents) % 2 != 0:
            raise Exception(
                f"Rucksack contents were not of odd length: "
                f"{len(self.contents)}"
            )
        return self.contents[:(len(self.contents) // 2)]

    @property
    def back(self) -> [str]:
        """
        >>> Rucksack.from_rucksack_text("vJrwpWtwJgWrhcsFMMfFFhFp").back
        ['h', 'c', 's', 'F', 'M', 'M', 'f', 'F', 'F', 'h', 'F', 'p']
        """
        if len(self.contents) % 2 != 0:
            raise Exception(
                f"Rucksack contents were not of odd length: "
                f"{len(self.contents)}"
            )
        return self.contents[(len(self.contents) // 2):]

    def get_common_item(self) -> str:
        """
        >>> Rucksack.from_rucksack_text("vJrwpWtwJgWrhcsFMMfFFhFp")\\
        ...     .get_common_item()
        'p'
        >>> Rucksack.from_rucksack_text("jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL")\\
        ...     .get_common_item()
        'L'
        >>> Rucksack.from_rucksack_text("PmmdzqPrVvPwwTWBwg")\\
        ...     .get_common_item()
        'P'
        >>> Rucksack.from_rucksack_text("wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn")\\
        ...     .get_common_item()
        'v'
        >>> Rucksack.from_rucksack_text("ttgJtRGJQctTZtZT")\\
        ...     .get_common_item()
        't'
        >>> Rucksack.from_rucksack_text("CrZsJsPPZsGzwwsLwLmpwMDw")\\
        ...     .get_common_item()
        's'
        """
        front_items = set(self.front)
        back_items = set(self.back)
        common_items = front_items & back_items
        if len(common_items) != 1:
            raise Exception(
                f"There wasn't exactly one common item: {common_items}"
            )
        common_item, = common_items
        return common_item

    priority_map: ClassVar[Dict[str, int]] = {
        **{
            item: index
            for index, item in enumerate(string.ascii_lowercase, 1)
        },
        **{
            item: index + 26
            for index, item in enumerate(string.ascii_uppercase, 1)
        },
    }

    def get_common_item_priority(self) -> int:
        """
        >>> Rucksack.from_rucksack_text("vJrwpWtwJgWrhcsFMMfFFhFp")\\
        ...     .get_common_item_priority()
        16
        >>> Rucksack.from_rucksack_text("jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL")\\
        ...     .get_common_item_priority()
        38
        >>> Rucksack.from_rucksack_text("PmmdzqPrVvPwwTWBwg")\\
        ...     .get_common_item_priority()
        42
        >>> Rucksack.from_rucksack_text("wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn")\\
        ...     .get_common_item_priority()
        22
        >>> Rucksack.from_rucksack_text("ttgJtRGJQctTZtZT")\\
        ...     .get_common_item_priority()
        20
        >>> Rucksack.from_rucksack_text("CrZsJsPPZsGzwwsLwLmpwMDw")\\
        ...     .get_common_item_priority()
        19
        """
        return self.priority_map[self.get_common_item()]


Challenge.main()
challenge = Challenge()
