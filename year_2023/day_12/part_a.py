#!/usr/bin/env python3
import itertools
import math
from dataclasses import dataclass
from typing import Iterable, List, Union, Generic, Type

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        7017
        """
        return RecordSet.from_text("\n".join(_input.splitlines())).get_arrangement_total(debugger=debugger)


RecordT = TV["Record"]


@dataclass
class RecordSet(Generic[RecordT]):
    records: List["Record"]

    @classmethod
    def get_record_class(cls) -> Type[RecordT]:
        return get_type_argument_class(cls, RecordT)

    @classmethod
    def from_text(cls, text: str) -> "RecordSet":
        """
        >>> print(RecordSet.from_text('''
        ...     ???.### 1,1,3
        ...     .??..??...?##. 1,1,3
        ...     ?#?#?#?#?#?#?#? 1,3,1,6
        ...     ????.#...#... 4,1,1
        ...     ????.######..#####. 1,6,5
        ...     ?###???????? 3,2,1
        ... '''))
        ???.### 1,1,3
        .??..??...?##. 1,1,3
        ?#?#?#?#?#?#?#? 1,3,1,6
        ????.#...#... 4,1,1
        ????.######..#####. 1,6,5
        ?###???????? 3,2,1
        """
        record_class = cls.get_record_class()
        return cls(records=list(map(record_class.from_text, text.strip().splitlines())))

    def __str__(self) -> str:
        return "\n".join(map(str, self.records))

    def get_arrangement_total(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> RecordSet.from_text('''
        ...     ???.### 1,1,3
        ...     .??..??...?##. 1,1,3
        ...     ?#?#?#?#?#?#?#? 1,3,1,6
        ...     ????.#...#... 4,1,1
        ...     ????.######..#####. 1,6,5
        ...     ?###???????? 3,2,1
        ... ''').get_arrangement_total()
        21
        """
        total = 0
        for index, record in debugger.stepping(enumerate(self.records)):
            with debugger.adding_extra_report_format(lambda _, message: f"Record {index + 1}/{len(self.records)}: {message}"):
                total += record.get_possible_arrangement_count(debugger=debugger)
        return total


@dataclass
class Record:
    sequence: str
    group_sizes: List[int]

    @classmethod
    def from_text(cls, text: str) -> "Record":
        """
        >>> print(Record.from_text("#.#.### 1,1,3"))
        #.#.### 1,1,3
        >>> print(Record.from_text("????.######..#####. 1,6,5"))
        ????.######..#####. 1,6,5
        """
        sequence, group_sizes_str = text.strip().split(" ")
        group_sizes = list(map(int, group_sizes_str.split(",")))
        return cls(sequence=sequence, group_sizes=group_sizes)

    def __str__(self) -> str:
        return f"{self.sequence} {','.join(map(str, self.group_sizes))}"

    def get_possible_arrangement_count(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> _record = Record.from_text("?###???????? 3,2,1")
        >>> _record.get_possible_arrangement_count()
        10
        """
        return sum(1 for _ in self.get_possible_arrangements(debugger=debugger))

    def get_possible_arrangements(self, debugger: Debugger = Debugger(enabled=False)) -> Iterable["Record"]:
        """
        >>> _record = Record.from_text("?###???????? 3,2,1")
        >>> print("\\n".join(map(str, _record.get_possible_arrangements())))
        .###.##.#... 3,2,1
        .###.##..#.. 3,2,1
        .###.##...#. 3,2,1
        .###.##....# 3,2,1
        .###..##.#.. 3,2,1
        .###..##..#. 3,2,1
        .###..##...# 3,2,1
        .###...##.#. 3,2,1
        .###...##..# 3,2,1
        .###....##.# 3,2,1
        """
        unknown_indexes = self.get_unknown_indexes()
        known_broken_count = self.get_known_broken_count()
        unknown_broken_count = sum(self.group_sizes) - known_broken_count
        unknown_broken_indexes_list = itertools.combinations(unknown_indexes, unknown_broken_count)
        values_list = (
            tuple(
                index in unknown_broken_indexes
                for index in unknown_indexes
            )
            for unknown_broken_indexes in unknown_broken_indexes_list
        )
        total_count = (
            math.factorial(len(unknown_indexes))
            // math.factorial(len(unknown_indexes) - unknown_broken_count)
            // math.factorial(unknown_broken_count)
        )
        for index, values in debugger.stepping(enumerate(values_list)):
            record = self.apply_indexes(values)
            if record.are_group_sizes_valid():
                yield record
            if debugger:
                debugger.default_report_if(
                    f"Candidate {index + 1}/{total_count} "
                    f"({len(unknown_indexes)} choose {unknown_broken_count}) "
                    f"for {self}"
                )

    def apply_indexes(self, values: List[bool]) -> "Record":
        sequence = self.sequence.replace("?", "{}", len(values)).format(*("#" if value else "." for value in values))
        cls = type(self)
        return cls(sequence=sequence, group_sizes=self.group_sizes)

    def get_unknown_indexes(self) -> List[int]:
        """
        >>> Record.from_text("????.######..#####. 1,6,5").get_unknown_indexes()
        [0, 1, 2, 3]
        """
        return [
            index
            for index, char in enumerate(self.sequence)
            if char == "?"
        ]

    def get_known_broken_count(self) -> int:
        """
        >>> Record.from_text("????.######..#####. 1,6,5").get_known_broken_count()
        11
        """
        return self.sequence.count("#")

    def are_group_sizes_valid(self) -> bool:
        """
        >>> Record.from_text("############ 3,2,1").are_group_sizes_valid()
        False
        >>> Record.from_text("############ 12").are_group_sizes_valid()
        True
        >>> Record.from_text("######.##### 6,5").are_group_sizes_valid()
        True
        >>> Record.from_text(".###.##.#... 3,2,1").are_group_sizes_valid()
        True
        """
        return self.get_sequence_group_sizes() == self.group_sizes

    def get_sequence_group_sizes(self) -> List[int]:
        """
        >>> Record.from_text("############ 3,2,1").get_sequence_group_sizes()
        [12]
        >>> Record.from_text("######.##### 3,2,1").get_sequence_group_sizes()
        [6, 5]
        """
        sizes = []
        size = 0
        for char in self.sequence:
            if char == "#":
                size += 1
            elif char == ".":
                if size > 0:
                    sizes.append(size)
                    size = 0
            else:
                raise Exception(f"Cannot get group sizes with non-fixed sequence: '{self.sequence}'")
        if size > 0:
            sizes.append(size)
        return sizes


Challenge.main()
challenge = Challenge()
