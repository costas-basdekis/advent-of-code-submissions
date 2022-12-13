#!/usr/bin/env python3
from dataclasses import dataclass
from typing import ClassVar, Iterable, List, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_13 import part_a
from year_2022.day_13.part_a import Signal, SignalList


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        21836
        """
        return SignalSet.from_signals_text(_input).decode()


@dataclass
class SignalSet:
    signals: [Signal]

    @classmethod
    def from_signals_text(cls, signals_text: str) -> "SignalSet":
        return cls(
            signals=list(map(
                SignalList.from_signal_text,
                filter(None, signals_text.strip().splitlines()),
            )),
        )

    def __str__(self) -> "str":
        return "\n".join(map(str, self.signals))

    def sort(self) -> "SignalSet":
        """
        >>> print(str(SignalSet.from_signals_text(
        ...     "[1,1,3,1,1]\\n"
        ...     "[1,1,5,1,1]\\n"
        ...     "\\n"
        ...     "[[1],[2,3,4]]\\n"
        ...     "[[1],4]\\n"
        ...     "\\n"
        ...     "[9]\\n"
        ...     "[[8,7,6]]\\n"
        ...     "\\n"
        ...     "[[4,4],4,4]\\n"
        ...     "[[4,4],4,4,4]\\n"
        ...     "\\n"
        ...     "[7,7,7,7]\\n"
        ...     "[7,7,7]\\n"
        ...     "\\n"
        ...     "[]\\n"
        ...     "[3]\\n"
        ...     "\\n"
        ...     "[[[]]]\\n"
        ...     "[[]]\\n"
        ...     "\\n"
        ...     "[1,[2,[3,[4,[5,6,7]]]],8,9]\\n"
        ...     "[1,[2,[3,[4,[5,6,0]]]],8,9]\\n"
        ...     "[[2]]\\n"
        ...     "[[6]]"
        ... ).sort()))
        []
        [[]]
        [[[]]]
        [1,1,3,1,1]
        [1,1,5,1,1]
        [[1],[2,3,4]]
        [1,[2,[3,[4,[5,6,0]]]],8,9]
        [1,[2,[3,[4,[5,6,7]]]],8,9]
        [[1],4]
        [[2]]
        [3]
        [[4,4],4,4]
        [[4,4],4,4,4]
        [[6]]
        [7,7,7]
        [7,7,7,7]
        [[8,7,6]]
        [9]
        """
        self.signals.sort()
        return self

    def decode(self) -> int:
        """
        >>> SignalSet.from_signals_text(
        ...     "[1,1,3,1,1]\\n"
        ...     "[1,1,5,1,1]\\n"
        ...     "\\n"
        ...     "[[1],[2,3,4]]\\n"
        ...     "[[1],4]\\n"
        ...     "\\n"
        ...     "[9]\\n"
        ...     "[[8,7,6]]\\n"
        ...     "\\n"
        ...     "[[4,4],4,4]\\n"
        ...     "[[4,4],4,4,4]\\n"
        ...     "\\n"
        ...     "[7,7,7,7]\\n"
        ...     "[7,7,7]\\n"
        ...     "\\n"
        ...     "[]\\n"
        ...     "[3]\\n"
        ...     "\\n"
        ...     "[[[]]]\\n"
        ...     "[[]]\\n"
        ...     "\\n"
        ...     "[1,[2,[3,[4,[5,6,7]]]],8,9]\\n"
        ...     "[1,[2,[3,[4,[5,6,0]]]],8,9]"
        ... ).decode()
        140
        """
        return self.add_divider_packets().sort().get_decoder_key()

    def get_decoder_key(self) -> int:
        first_index, second_index = self.get_divider_packets_indexes()
        return first_index * second_index

    def get_divider_packets_indexes(self) -> Tuple[int, int]:
        first_divider, second_divider = self.divider_packets
        first_index = self.signals.index(first_divider) + 1
        second_index = self.signals.index(second_divider) + 1
        return first_index, second_index

    divider_packets: ClassVar[List[Signal]] = [
        SignalList.from_signal_text("[[2]]"),
        SignalList.from_signal_text("[[6]]"),
    ]

    def add_divider_packets(self) -> "SignalSet":
        """
        >>> print(str(SignalSet.from_signals_text(
        ...     "[1,1,3,1,1]\\n"
        ...     "[1,1,5,1,1]\\n"
        ...     "\\n"
        ...     "[[1],[2,3,4]]\\n"
        ...     "[[1],4]\\n"
        ...     "\\n"
        ...     "[9]\\n"
        ...     "[[8,7,6]]\\n"
        ...     "\\n"
        ...     "[[4,4],4,4]\\n"
        ...     "[[4,4],4,4,4]\\n"
        ...     "\\n"
        ...     "[7,7,7,7]\\n"
        ...     "[7,7,7]\\n"
        ...     "\\n"
        ...     "[]\\n"
        ...     "[3]\\n"
        ...     "\\n"
        ...     "[[[]]]\\n"
        ...     "[[]]\\n"
        ...     "\\n"
        ...     "[1,[2,[3,[4,[5,6,7]]]],8,9]\\n"
        ...     "[1,[2,[3,[4,[5,6,0]]]],8,9]"
        ... ).add_divider_packets().sort()))
        []
        [[]]
        [[[]]]
        [1,1,3,1,1]
        [1,1,5,1,1]
        [[1],[2,3,4]]
        [1,[2,[3,[4,[5,6,0]]]],8,9]
        [1,[2,[3,[4,[5,6,7]]]],8,9]
        [[1],4]
        [[2]]
        [3]
        [[4,4],4,4]
        [[4,4],4,4,4]
        [[6]]
        [7,7,7]
        [7,7,7,7]
        [[8,7,6]]
        [9]
        """
        self.extend(self.divider_packets)
        return self

    def extend(self, signals: Iterable[Signal]) -> "SignalSet":
        self.signals.extend(signals)
        return self


Challenge.main()
challenge = Challenge()
