#!/usr/bin/env python3
from typing import List

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_03.part_a import DiagnosticEntrySet, DiagnosticEntryT, \
    DiagnosticEntry


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        4481199
        """
        return DiagnosticEntrySetExtended\
            .from_entries_text(_input)\
            .get_life_support_rate()


class DiagnosticEntrySetExtended(DiagnosticEntrySet):
    def get_life_support_rate(self) -> int:
        return self.get_oxygen_rate() * self.get_co2_rate()

    def get_oxygen_rate(self) -> int:
        """
        >>> DiagnosticEntrySetExtended.from_entries_text(
        ...     "00100\\n"
        ...     "11110\\n"
        ...     "10110\\n"
        ...     "10111\\n"
        ...     "10101\\n"
        ...     "01111\\n"
        ...     "00111\\n"
        ...     "11100\\n"
        ...     "10000\\n"
        ...     "11001\\n"
        ...     "00010\\n"
        ...     "01010\\n"
        ... ).get_oxygen_rate()
        23
        """
        return self.get_reductive_rate(1)

    def get_co2_rate(self) -> int:
        """
        >>> DiagnosticEntrySetExtended.from_entries_text(
        ...     "00100\\n"
        ...     "11110\\n"
        ...     "10110\\n"
        ...     "10111\\n"
        ...     "10101\\n"
        ...     "01111\\n"
        ...     "00111\\n"
        ...     "11100\\n"
        ...     "10000\\n"
        ...     "11001\\n"
        ...     "00010\\n"
        ...     "01010\\n"
        ... ).get_co2_rate()
        10
        """
        return self.get_reductive_rate(0)

    def get_reductive_rate(self, default: int) -> int:
        entries = self.entries
        if not entries:
            raise Exception(f"No entries")
        for position in range(self.size - 1, -1, -1):
            flag = self.get_most_common_bit(entries, position, default)
            entries = self.filter_entries(entries, position, flag)
            if not entries:
                raise Exception("No entries left")
            if len(entries) == 1:
                break
        else:
            raise Exception(f"Too many entries remain ({len(entries)})")

        entry, = entries

        return entry.value

    def get_most_common_bit(
            self, entries: List[DiagnosticEntryT], position: int, default: int,
    ) -> int:
        """
        >>> DiagnosticEntrySetExtended([], 5)\\
        ...     .get_most_common_bit(list(map(
        ...         DiagnosticEntry,
        ...         [4, 30, 22, 23, 21, 15, 7, 28, 16, 25, 2, 10],
        ...     )), 4, 1)
        1
        >>> DiagnosticEntrySetExtended([], 5)\\
        ...     .get_most_common_bit(list(map(
        ...         DiagnosticEntry,
        ...         [30, 22, 23, 21, 28, 16, 25],
        ...     )), 3, 1)
        0
        >>> DiagnosticEntrySetExtended([], 5)\\
        ...     .get_most_common_bit(list(map(
        ...         DiagnosticEntry,
        ...         [22, 23, 21, 16],
        ...     )), 2, 1)
        1
        >>> DiagnosticEntrySetExtended([], 5)\\
        ...     .get_most_common_bit(list(map(
        ...         DiagnosticEntry,
        ...         [22, 23, 21],
        ...     )), 1, 1)
        1
        >>> DiagnosticEntrySetExtended([], 5)\\
        ...     .get_most_common_bit(list(map(
        ...         DiagnosticEntry,
        ...         [22, 23],
        ...     )), 0, 1)
        1
        """
        bit_count = self.count_bits_in_entries(entries, position)
        not_bit_count = len(entries) - bit_count
        if not default:
            bit_count, not_bit_count = not_bit_count, bit_count
        if bit_count == not_bit_count:
            return default
        elif bit_count > not_bit_count:
            return 1
        else:
            return 0

    def filter_entries(
            self, entries: List[DiagnosticEntryT], position: int, flag: int,
    ) -> List[DiagnosticEntryT]:
        """
        >>> _entries = DiagnosticEntrySetExtended([], 5)\\
        ...     .filter_entries(list(map(
        ...         DiagnosticEntry,
        ...         [4, 30, 22, 23, 21, 15, 7, 28, 16, 25, 2, 10],
        ...     )), 4, 1)
        >>> [entry.value for entry in _entries]
        [30, 22, 23, 21, 28, 16, 25]
        >>> _entries = DiagnosticEntrySetExtended([], 5)\\
        ...     .filter_entries(list(map(
        ...         DiagnosticEntry,
        ...         [30, 22, 23, 21, 28, 16, 25],
        ...     )), 3, 0)
        >>> [entry.value for entry in _entries]
        [22, 23, 21, 16]
        >>> _entries = DiagnosticEntrySetExtended([], 5)\\
        ...     .filter_entries(list(map(
        ...         DiagnosticEntry,
        ...         [22, 23, 21, 16],
        ...     )), 2, 1)
        >>> [entry.value for entry in _entries]
        [22, 23, 21]
        >>> _entries = DiagnosticEntrySetExtended([], 5)\\
        ...     .filter_entries(list(map(
        ...         DiagnosticEntry,
        ...         [22, 23, 21],
        ...     )), 1, 1)
        >>> [entry.value for entry in _entries]
        [22, 23]
        >>> _entries = DiagnosticEntrySetExtended([], 5)\\
        ...     .filter_entries(list(map(
        ...         DiagnosticEntry,
        ...         [22, 23],
        ...     )), 0, 1)
        >>> [entry.value for entry in _entries]
        [23]
        """
        mask = 2 ** position
        return [
            entry
            for entry in entries
            if bool(entry.value & mask) == bool(flag)
        ]


Challenge.main()
challenge = Challenge()
