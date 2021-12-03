#!/usr/bin/env python3
from typing import Generic, Type, List, Tuple

import math
from dataclasses import dataclass

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        3320834
        """
        return DiagnosticEntrySet\
            .from_entries_text(_input)\
            .get_power_consumption()


DiagnosticEntryT = TV["DiagnosticEntry"]


@dataclass
class DiagnosticEntrySet(Generic[DiagnosticEntryT]):
    entries: List[DiagnosticEntryT]
    size: int

    @classmethod
    def get_entry_class(cls) -> Type[DiagnosticEntryT]:
        return get_type_argument_class(cls, DiagnosticEntryT)

    @classmethod
    def from_entries_text(cls, entries_text: str) -> "DiagnosticEntrySet":
        """
        >>> DiagnosticEntrySet.from_entries_text(
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
        ... )
        DiagnosticEntrySet(entries=[...4), ...30), ...], size=5)
        """
        entry_class = cls.get_entry_class()
        entries = list(map(
            entry_class.from_entry_text,
            entries_text.splitlines(),
        ))
        size = max(entry.size for entry in entries)

        return cls(entries=entries, size=size)

    def count_bits(self, position: int) -> int:
        return self.count_bits_in_entries(self.entries, position)

    def count_bits_in_entries(
            self, entries: List[DiagnosticEntryT], position: int,
    ) -> int:
        mask = 2 ** position
        return sum(
            1
            for entry in entries
            if entry.has_bit(mask)
        )

    def get_power_consumption(self) -> int:
        gamma_rate, epsilon_rate = self.get_gamma_and_epsilon_rate()
        return gamma_rate * epsilon_rate

    def get_gamma_and_epsilon_rate(self) -> Tuple[int, int]:
        """
        >>> DiagnosticEntrySet.from_entries_text(
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
        ... ).get_gamma_and_epsilon_rate()
        (22, 9)
        """
        gamma_rate = self.get_gamma_rate()
        epsilon_rate = self.get_epsilon_rate(gamma_rate)
        return gamma_rate, epsilon_rate

    def get_gamma_rate(self) -> int:
        binary_str = ""
        min_bits = math.ceil(len(self.entries) / 2)
        for position in range(self.size):
            bit_count = self.count_bits(position)
            if bit_count > min_bits:
                digit = "1"
            else:
                digit = "0"
            binary_str = digit + binary_str
        return int(binary_str, 2)

    def get_epsilon_rate(self, gamma_rate) -> int:
        total = (2 ** self.size) - 1
        return total - gamma_rate


@dataclass
class DiagnosticEntry:
    value: int

    @classmethod
    def from_entry_text(cls, entry_txt: str) -> "DiagnosticEntry":
        """
        >>> DiagnosticEntry.from_entry_text("00100")
        DiagnosticEntry(value=4)
        """
        return DiagnosticEntry(int(entry_txt, 2))

    @property
    def size(self) -> int:
        """
        >>> DiagnosticEntry.from_entry_text("00100").size
        3
        """
        return math.ceil(math.log2(self.value + 1))

    def has_bit(self, mask: int) -> bool:
        """
        >>> DiagnosticEntry(4).has_bit(1)
        False
        >>> DiagnosticEntry(4).has_bit(2)
        False
        >>> DiagnosticEntry(4).has_bit(4)
        True
        >>> DiagnosticEntry(4).has_bit(8)
        False
        """
        return bool(self.value & mask)


Challenge.main()
challenge = Challenge()
