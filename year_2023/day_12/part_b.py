#!/usr/bin/env python3
from typing import Dict, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_12 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        527570479489
        """
        return RecordSetExtended.from_text(_input)\
            .unfold(5)\
            .get_arrangement_total({}, debugger=debugger)


class RecordSetExtended(part_a.RecordSet["RecordExtended"]):
    def unfold(self, count: int = 5) -> "RecordSetExtended":
        pass
        """
        >>> RecordSetExtended.from_text('''
        ...     ???.### 1,1,3
        ...     .??..??...?##. 1,1,3
        ...     ?#?#?#?#?#?#?#? 1,3,1,6
        ...     ????.#...#... 4,1,1
        ...     ????.######..#####. 1,6,5
        ...     ?###???????? 3,2,1
        ... ''').unfold().get_arrangement_total()
        525152
        """
        cls = type(self)
        return cls(records=[record.unfold(count) for record in self.records])

    def get_arrangement_total(self, cache: Optional[Dict[Tuple[str, Tuple[int, ...]], int]] = None, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> RecordSetExtended.from_text('''
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
                total += record.get_possible_arrangement_count(cache, debugger=debugger)
        if cache is not None:
            debugger.default_report(f"Cache size: {len(cache)}")
        return total


class RecordExtended(part_a.Record):
    @classmethod
    def empty(cls) -> "RecordExtended":
        return cls(sequence="", group_sizes=[])

    @classmethod
    def from_sequence(cls, sequence: str) -> "RecordExtended":
        record = cls(sequence=sequence, group_sizes=[])
        record.group_sizes.extend(record.get_sequence_group_sizes())
        return record

    def __add__(self, other: "RecordExtended") -> "RecordExtended":
        cls = type(self)
        return cls(sequence=self.sequence + other.sequence, group_sizes=self.group_sizes + other.group_sizes)

    def get_possible_arrangement_count(self, cache: Optional[Dict[Tuple[str, Tuple[int, ...]], int]] = None, debugger: Debugger = Debugger(enabled=False)) -> int:
        if cache is None:
            cache = {}
        return self.get_possible_arrangement_count_recursive(cache, debugger=debugger)

    def get_possible_arrangement_count_recursive(self, cache: Dict[Tuple[str, Tuple[int, ...]], int], debugger: Debugger = Debugger(enabled=False)) -> int:
        key = (self.sequence, tuple(self.group_sizes))
        if key in cache:
            return cache[key]
        debugger.step()
        prefix, rest = self.get_prefix()
        if debugger.should_report():
            debugger.default_report_if(f"({len(cache)} cached items) Checking recursively for {self}: {prefix} + {rest}")
        if prefix == self:
            cache[key] = 1
            return 1
        if prefix.group_sizes and prefix.group_sizes != self.group_sizes[:len(prefix.group_sizes)]:
            cache[key] = 0
            return 0
        unknown_broken_count = sum(rest.group_sizes) - rest.get_known_broken_count()
        if unknown_broken_count < 0:
            cache[key] = 0
            return 0
        unknown_indexes = rest.get_unknown_indexes()
        if unknown_broken_count > len(unknown_indexes):
            cache[key] = 0
            return 0
        if unknown_broken_count == 0:
            result = rest.apply_indexes([False] * len(unknown_indexes))
            are_group_sizes_valid = result.are_group_sizes_valid()
            cache[key] = 1 if are_group_sizes_valid else 0
            return 1 if are_group_sizes_valid else 0
        broken_prefix_count = len(rest.sequence) - len(rest.sequence.lstrip("#"))
        if broken_prefix_count > rest.group_sizes[0]:
            cache[key] = 0
            return 0
        count = 0
        values = [True, False]
        if broken_prefix_count == rest.group_sizes[0]:
            values.remove(True)
        for value in values:
            count += rest.apply_indexes([value]).get_possible_arrangement_count_recursive(cache, debugger=debugger)
        cache[key] = count
        return count

    def get_prefix(self) -> Tuple["RecordExtended", "RecordExtended"]:
        cls = type(self)
        if "?" not in self.sequence:
            group_sizes = self.get_sequence_group_sizes()
            if group_sizes == self.group_sizes:
                return self, cls.empty()
            return cls(sequence=self.sequence, group_sizes=group_sizes), cls(sequence="", group_sizes=self.group_sizes[len(group_sizes):])
        first_unknown_index = self.sequence.find("?")
        prefix_sequence = self.sequence[:first_unknown_index].rstrip("#")
        if not prefix_sequence:
            return cls.empty(), self
        first_part = cls.from_sequence(prefix_sequence)
        second_part = cls(sequence=self.sequence[len(prefix_sequence):], group_sizes=self.group_sizes[len(first_part.group_sizes):])
        return first_part, second_part

    def strip(self) -> "RecordExtended":
        """
        >>> print(RecordExtended.from_text("..??##.??#.. 1,2,3").strip())
        ??##.??# 1,2,3
        """
        cls = type(self)
        return cls(sequence=self.sequence.strip("."), group_sizes=self.group_sizes)

    def unfold(self, count: int = 5) -> "RecordExtended":
        """
        >>> print(RecordExtended.from_text(".# 1").unfold())
        .#?.#?.#?.#?.# 1,1,1,1,1
        """
        cls = type(self)
        return cls(sequence="?".join([self.sequence] * count), group_sizes=self.group_sizes * count)


Challenge.main()
challenge = Challenge()
