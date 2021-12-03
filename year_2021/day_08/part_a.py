#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Tuple, Dict, Generic, Type, List, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        445
        """
        return EntrySet\
            .from_entries_text(_input)\
            .get_output_count_with_1_4_7_8()


Signals = Tuple[str, ...]


SIGNALS_BY_DIGIT: Dict[int, Signals] = {
    0: ('a', 'b', 'c', 'e', 'f', 'g'),
    1: ('c', 'f'),
    2: ('a', 'c', 'd', 'e', 'g'),
    3: ('a', 'c', 'd', 'f', 'g'),
    4: ('b', 'c', 'd', 'f'),
    5: ('a', 'b', 'd', 'f', 'g'),
    6: ('a', 'b', 'd', 'e', 'f', 'g'),
    7: ('a', 'c', 'f'),
    8: ('a', 'b', 'c', 'd', 'e', 'f', 'g'),
    9: ('a', 'b', 'c', 'd', 'f', 'g'),
}
DIGITS_BY_SIGNALS: Dict[Signals, int] = {
    signals: digit
    for digit, signals in SIGNALS_BY_DIGIT.items()
}
DIGITS_BY_SIGNAL_LENGTH = helper.group_by(
    DIGITS_BY_SIGNALS,
    key=len,
    value=DIGITS_BY_SIGNALS.__getitem__,
)


EntryT = TV["Entry"]


@dataclass
class EntrySet(Generic[EntryT]):
    entries: List[EntryT]

    @classmethod
    def get_entry_class(cls) -> Type[EntryT]:
        return get_type_argument_class(cls, EntryT)

    @classmethod
    def from_entries_text(cls, entries_text: str) -> "EntrySet":
        """
        >>> EntrySet.from_entries_text('''
        ...     be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
        ...     edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
        ... ''')
        EntrySet(entries=[Entry(inputs=[Display(signals=('b', 'e')), ...],
            outputs=[Display(signals=('a', 'b', 'c', 'd', 'e', 'f', 'g')),
            ...]), ...])
        """
        entry_class = cls.get_entry_class()
        return cls(
            entries=list(map(
                entry_class.from_entry_text,
                filter(None, map(str.strip, entries_text.splitlines())),
            )),
        )

    def get_output_count_with_1_4_7_8(self) -> int:
        """
        >>> EntrySet.from_entries_text('''
        ...     be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb | fdgacbe cefdb cefbgd gcbe
        ...     edbfga begcd cbg gc gcadebf fbgde acbgfd abcde gfcbed gfec | fcgedb cgb dgebacf gc
        ...     fgaebd cg bdaec gdafb agbcfd gdcbef bgcad gfac gcb cdgabef | cg cg fdcagb cbg
        ...     fbegcd cbd adcefb dageb afcb bc aefdc ecdab fgdeca fcdbega | efabcd cedba gadfec cb
        ...     aecbfdg fbg gf bafeg dbefa fcge gcbea fcaegb dgceab fcbdga | gecf egdcabf bgf bfgea
        ...     fgeab ca afcebg bdacfeg cfaedg gcfdb baec bfadeg bafgc acf | gebdcfa ecba ca fadegcb
        ...     dbcfg fgd bdegcaf fgec aegbdf ecdfab fbedc dacgb gdcebf gf | cefg dcbef fcge gbcadfe
        ...     bdfegc cbegaf gecbf dfcage bdacg ed bedf ced adcbefg gebcd | ed bcgafe cdgba cbgef
        ...     egadfb cdbfeg cegd fecab cgb gbdefca cg fgcdab egfdb bfceg | gbdfcae bgc cg cgb
        ...     gcafb gcf dcaebfg ecagb gf abcdeg gaef cafbge fdbac fegbdc | fgae cfgab fg bagce
        ... ''').get_output_count_with_1_4_7_8()
        26
        """
        return sum(
            entry.get_output_count_with_1_4_7_8()
            for entry in self.entries
        )


DisplayT = TV["Display"]


@dataclass
class Entry(Generic[DisplayT]):
    inputs: List[DisplayT]
    outputs: List[DisplayT]

    @classmethod
    def get_display_class(cls) -> Type[DisplayT]:
        return get_type_argument_class(cls, DisplayT)

    @classmethod
    def from_entry_text(cls, entry_text: str) -> "Entry":
        """
        >>> Entry.from_entry_text(
        ...     "acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab"
        ...     " | cdfeb fcadb cdfeb cdbaf")
        Entry(inputs=[Display(signals=('a', 'b', 'c', 'd', 'e', 'f', 'g')),
            ...], outputs=[Display(signals=('b', 'c', 'd', 'e', 'f')), ...])
        """
        inputs_str, outputs_str = entry_text.strip().split(" | ")
        display_class = cls.get_display_class()
        return cls(
            inputs=list(map(
                display_class.from_display_text,
                inputs_str.split(" "),
            )),
            outputs=list(map(
                display_class.from_display_text,
                outputs_str.split(" "),
            )),
        )

    def get_output_count_with_1_4_7_8(self) -> int:
        """
        >>> Entry.from_entry_text(
        ...     "be cfbegad cbdgef fgaecd cgeb fdcge agebfd fecdb fabcd edb"
        ...     " | fdgacbe cefdb cefbgd gcbe"
        ... ).get_output_count_with_1_4_7_8()
        2
        """
        return sum(
            1
            for display in self.outputs
            if display.try_get_digit_by_length() in (1, 4, 7, 8)
        )


@dataclass
class Display:
    signals: Signals

    @classmethod
    def from_display_text(cls, display_text: str) -> "Display":
        """
        >>> Display.from_display_text("gcbe")
        Display(signals=('b', 'c', 'e', 'g'))
        """
        return cls(signals=tuple(sorted(display_text.strip())))

    def try_get_digit_by_length(self) -> Optional[int]:
        """
        >>> Display.from_display_text("fdgacbe").try_get_digit_by_length()
        8
        >>> Display.from_display_text("gcbe").try_get_digit_by_length()
        4
        >>> Display.from_display_text("cefdb").try_get_digit_by_length()
        """
        digits = DIGITS_BY_SIGNAL_LENGTH[len(self.signals)]
        if len(digits) > 1:
            return None
        digit, = digits
        return digit


Challenge.main()
challenge = Challenge()
