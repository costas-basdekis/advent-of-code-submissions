#!/usr/bin/env python3
from dataclasses import dataclass
import re
from enum import Enum
from typing import Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        4734
        """
        return SignalPairSet.from_pairs_text(_input).get_in_order_index_sum()


@dataclass
class SignalPairSet:
    pairs: ["SignalPair"]

    @classmethod
    def from_pairs_text(cls, pairs_text: str) -> "SignalPairSet":
        return cls(
            pairs=list(map(
                SignalPair.from_pair_text,
                pairs_text.strip().split("\n\n"),
            )),
        )

    def get_in_order_index_sum(self) -> int:
        """
        >>> SignalPairSet.from_pairs_text(
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
        ... ).get_in_order_index_sum()
        13
        """
        return sum(self.get_in_order_indexes())

    def get_in_order_indexes(self) -> [int]:
        """
        >>> SignalPairSet.from_pairs_text(
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
        ... ).get_in_order_indexes()
        [1, 2, 4, 6]
        """
        return [
            index
            for index, pair in enumerate(self.pairs, 1)
            if pair.is_in_order()
        ]


@dataclass
class SignalPair:
    left: "SignalList"
    right: "SignalList"

    @classmethod
    def from_pair_text(cls, pair_text: str) -> "SignalPair":
        """
        >>> print(str(SignalPair.from_pair_text("[1,1,3,1,1]\\n[1,1,5,1,1]")))
        [1,1,3,1,1]
        [1,1,5,1,1]
        """
        left_str, right_str = pair_text.strip().splitlines()
        return cls(
            left=SignalList.from_signal_text(left_str),
            right=SignalList.from_signal_text(right_str),
        )

    def __str__(self) -> str:
        return "\n".join(map(str, [self.left, self.right]))

    def is_in_order(self) -> bool:
        """
        >>> SignalPair.from_pair_text(
        ...     "[1,1,3,1,1]\\n"
        ...     "[1,1,5,1,1]"
        ... ).is_in_order()
        True
        >>> SignalPair.from_pair_text(
        ...     "[[1],[2,3,4]]\\n"
        ...     "[[1],4]"
        ... ).is_in_order()
        True
        >>> SignalPair.from_pair_text(
        ...     "[9]\\n"
        ...     "[[8,7,6]]"
        ... ).is_in_order()
        False
        >>> SignalPair.from_pair_text(
        ...     "[[4,4],4,4]\\n"
        ...     "[[4,4],4,4,4]"
        ... ).is_in_order()
        True
        >>> SignalPair.from_pair_text(
        ...     "[7,7,7,7]\\n"
        ...     "[7,7,7]"
        ... ).is_in_order()
        False
        >>> SignalPair.from_pair_text(
        ...     "[]\\n"
        ...     "[3]"
        ... ).is_in_order()
        True
        >>> SignalPair.from_pair_text(
        ...     "[[[]]]\\n"
        ...     "[[]]"
        ... ).is_in_order()
        False
        >>> SignalPair.from_pair_text(
        ...     "[1,[2,[3,[4,[5,6,7]]]],8,9]\\n"
        ...     "[1,[2,[3,[4,[5,6,0]]]],8,9]"
        ... ).is_in_order()
        False
        """
        return self.compare() == SignalComparison.Before

    def compare(self) -> "SignalComparison":
        return self.left.compare(self.right)


class SignalComparison(Enum):
    Before = "before"
    Equal = "equal"
    After = "after"

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class Signal:
    @classmethod
    def from_signal_text(
        cls: Cls["Signal"], signal_text: str,
    ) -> Self["Signal"]:
        signal, remaining = cls.parse(signal_text)
        if remaining:
            raise Exception(f"There was extra input at the end: {remaining}")
        return signal

    @classmethod
    def parse(cls: Cls["Signal"], text: str) -> Self["Signal"]:
        raise NotImplementedError()

    def compare(self, other: "Signal") -> SignalComparison:
        raise NotImplementedError()


@dataclass
class SignalNumber(Signal):
    value: int

    re_number = re.compile(r"^(\d+)")

    @classmethod
    def parse(cls, text: str) -> Tuple["SignalNumber", str]:
        """
        >>> print(str(SignalNumber.from_signal_text("5")))
        5
        >>> print(str(SignalNumber.from_signal_text("123")))
        123
        >>> SignalNumber.parse("5")
        (SignalNumber(value=5), '')
        >>> SignalNumber.parse("5,6,[4,3]]")
        (SignalNumber(value=5), ',6,[4,3]]')
        """
        match = cls.re_number.match(text)
        if not match:
            raise Exception(f"Expected a number: '{text}'")
        number_str, = match.groups()
        value = int(number_str)
        remaining = text[len(number_str):]
        return cls(value=value), remaining

    def __str__(self) -> str:
        return str(self.value)

    def compare(self, other: "Signal") -> SignalComparison:
        """
        >>> SignalNumber(5).compare(SignalNumber(6))
        SignalComparison.Before
        >>> SignalNumber(5).compare(SignalNumber(5))
        SignalComparison.Equal
        >>> SignalNumber(5).compare(SignalNumber(4))
        SignalComparison.After
        >>> SignalNumber(5).compare(SignalList([SignalNumber(value=6)]))
        SignalComparison.Before
        >>> SignalNumber(5).compare(SignalList([SignalNumber(value=5)]))
        SignalComparison.Equal
        >>> SignalNumber(5).compare(SignalList([SignalNumber(value=4)]))
        SignalComparison.After
        """
        if isinstance(other, SignalNumber):
            if self.value < other.value:
                return SignalComparison.Before
            elif self.value == other.value:
                return SignalComparison.Equal
            else:
                return SignalComparison.After
        return self.to_list().compare(other)

    def to_list(self) -> "SignalList":
        """
        >>> SignalNumber(5).to_list()
        SignalList(values=[SignalNumber(value=5)])
        """
        return SignalList([self])


@dataclass
class SignalList(Signal):
    values: [Signal]

    @classmethod
    def parse(cls, text: str) -> Tuple["SignalList", str]:
        """
        >>> print(str(SignalList.from_signal_text("[[[]]]")))
        [[[]]]
        >>> print(str(SignalList.from_signal_text(
        ...     "[1,[2,[3,[4,[5,6,7]]]],8,9]")))
        [1,[2,[3,[4,[5,6,7]]]],8,9]
        >>> SignalList.parse("[]")
        (SignalList(values=[]), '')
        >>> SignalList.parse("[],4,5]")
        (SignalList(values=[]), ',4,5]')
        >>> SignalList.parse("[2,3]")
        (SignalList(values=[SignalNumber(value=2), SignalNumber(value=3)]), '')
        >>> SignalList.parse("[2,3],[],[[[]]]]")
        (SignalList(values=[SignalNumber(value=2),
            SignalNumber(value=3)]), ',[],[[[]]]]')
        >>> SignalList.parse("[2,[4,5,[6],[]],3]")
        (SignalList(values=[SignalNumber(value=2),
            SignalList(values=[SignalNumber(value=4), SignalNumber(value=5),
            SignalList(values=[SignalNumber(value=6)]),
            SignalList(values=[])]), SignalNumber(value=3)]), '')
        >>> SignalList.parse("[2,[4,5,[6],[]],3],5],6],7],8]")
        (SignalList(values=[SignalNumber(value=2),
            SignalList(values=[SignalNumber(value=4), SignalNumber(value=5),
            SignalList(values=[SignalNumber(value=6)]),
            SignalList(values=[])]), SignalNumber(value=3)]), ',5],6],7],8]')
        """
        if text[0] != "[":
            raise Exception(f"List text didn't start with '[': '{text}'")
        values = []
        remaining = text[1:]
        while True:
            if not remaining:
                raise Exception(f"Unexpected end of input")
            if remaining[0] == "]":
                remaining = remaining[1:]
                break
            if remaining[0] == ",":
                if not values:
                    raise Exception(
                        f"There was an extra ',' at the start of the text: "
                        f"'{remaining}'"
                    )
                remaining = remaining[1:]
            else:
                if values:
                    raise Exception(
                        f"Expected a comma between values, but there was one "
                        f"missing: '{remaining}'"
                    )
            if remaining[0] == "[":
                value, remaining = cls.parse(remaining)
            else:
                value, remaining = SignalNumber.parse(remaining)
            values.append(value)

        return cls(values=values), remaining

    def __str__(self) -> str:
        return "[{}]".format(",".join(map(str, self.values)))

    def compare(self, other: "Signal") -> SignalComparison:
        """
        >>> SignalList([]).compare(SignalList([SignalNumber(1)]))
        SignalComparison.Before
        >>> SignalList([]).compare(SignalList([]))
        SignalComparison.Equal
        >>> SignalList([SignalNumber(1)]).compare(SignalList([]))
        SignalComparison.After
        >>> SignalList.from_signal_text("[1,1,3,1,1]")\\
        ...     .compare(SignalList.from_signal_text("[1,1,5,1,1]"))
        SignalComparison.Before
        """
        if isinstance(other, SignalNumber):
            other = other.to_list()

        for left, right in zip(self.values, other.values):
            left: Signal
            right: Signal
            result = left.compare(right)
            if result != SignalComparison.Equal:
                return result

        if len(self.values) < len(other.values):
            return SignalComparison.Before
        elif len(self.values) == len(other.values):
            return SignalComparison.Equal
        else:
            return SignalComparison.After


Challenge.main()
challenge = Challenge()
