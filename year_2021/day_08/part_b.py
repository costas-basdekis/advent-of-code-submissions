#!/usr/bin/env python3
from dataclasses import dataclass
from functools import reduce
from typing import Dict, Set, Tuple, List, cast, Optional, Type

from aox.challenge import Debugger
from utils import BaseChallenge, helper
from year_2021.day_08 import part_a
from year_2021.day_08.part_a import SIGNALS_BY_DIGIT, Display, Entry, Signals, \
    DIGITS_BY_SIGNALS, EntrySet


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1043101
        """
        return EntrySetExtended.from_entries_text(_input).decoded_output


DIGITS_BY_SIGNAL: Dict[str, Set[int]] = helper.group_by(
    (
        (digit, signal)
        for digit, signals in SIGNALS_BY_DIGIT.items()
        for signal in signals
    ),
    key=lambda digit_and_signal: digit_and_signal[1],
    value="auto",
)


class EntrySetExtended(EntrySet["EntryExtended"]):
    @property
    def decoded_output(self) -> int:
        """
        >>> EntrySetExtended.from_entries_text('''
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
        ... ''').decoded_output
        61229
        """
        return sum(
            entry.decoded_output
            for entry in self.entries
        )


@dataclass
class EntrySolver:
    entry: "EntryExtended"
    decoder: Dict[str, str]
    encoder: Dict[str, str]
    signals_d_g: Optional[Set[str]]
    signals_c_f: Optional[Set[str]]
    signals_f_g: Optional[Set[str]]
    displays_by_digit: Dict[int, List["DisplayExtended"]]
    displays_by_length: Dict[int, List["DisplayExtended"]]

    @classmethod
    def solve_entry(cls, entry: "EntryExtended") -> Dict[str, str]:
        return cls.from_entry(entry).solve()

    @classmethod
    def from_entry(cls, entry: "EntryExtended") -> "EntrySolver":
        return cls(
            entry=entry,
            decoder={},
            encoder={},
            signals_d_g=None,
            signals_c_f=None,
            signals_f_g=None,
            displays_by_digit=helper.group_by(
                (
                    display
                    for display in entry.inputs
                    if display.try_get_digit_by_length() is not None
                ),
                key=lambda display: display.try_get_digit_by_length(),
            ),
            displays_by_length=helper.group_by(
                entry.inputs,
                key=lambda display: len(display.signals),
            ),
        )

    def solve(self) -> Dict[str, str]:
        """
        >>> EntryExtended.from_entry_text(
        ...     "acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab"
        ...     " | cdfeb fcadb cdfeb cdbaf"
        ... ).solve()
        {'d': 'a', 'e': 'b', 'g': 'e', 'b': 'f', 'c': 'g', 'a': 'c', 'f': 'd'}
        """
        self.solve_signal('a', self.get_signal_for_a())
        self.signals_c_f = self.get_signals_for_c_and_f()
        self.signals_d_g = self.get_signals_for_d_and_g()
        self.solve_signal('b', self.get_signal_for_b())
        self.solve_signal('e', self.get_signal_for_e())
        self.signals_f_g = self.get_signals_for_f_and_g()
        self.solve_signal('f', self.get_signal_for_f())
        self.solve_signal('g', self.get_signal_for_g())
        self.solve_signal('c', self.get_signal_for_c())
        self.solve_signal('d', self.get_signal_for_d())

        return self.decoder

    def get_signal_for_d(self) -> str:
        signal_d_candidates = self.signals_d_g - {self.encoder['g']}
        return self.get_check_single_signal(signal_d_candidates, 'd')

    def get_signal_for_c(self) -> str:
        signal_c_candidates = self.signals_c_f - {self.encoder['f']}
        return self.get_check_single_signal(signal_c_candidates, 'c')

    def get_signal_for_g(self) -> str:
        signal_g_candidates = self.signals_f_g & self.signals_d_g
        return self.get_check_single_signal(signal_g_candidates, 'g')

    def get_signal_for_f(self) -> str:
        signal_f_candidates = self.signals_f_g & self.signals_c_f
        return self.get_check_single_signal(signal_f_candidates, 'f')

    def get_signals_for_f_and_g(self) -> Set[str]:
        signals_for_length_6: Set[str] = cast(
            Set[str],
            reduce(set.intersection, (
                set(display.signals)
                for display in self.displays_by_length[6]
            )),
        )
        signals_f_g = (
            signals_for_length_6
            - {self.encoder['a'], self.encoder['b']}
        )
        if len(signals_f_g) != 2:
            raise Exception(
                f"Expected 2 candidates for signals 'f' and 'g', but got "
                f"{len(signals_f_g)}"
            )

        return signals_f_g

    def get_signal_for_e(self) -> str:
        signal_e_candidates = (
            set('abcdefg')
            - {self.encoder['a'], self.encoder['b']}
            - self.signals_c_f
            - self.signals_d_g
        )
        return self.get_check_single_signal(signal_e_candidates, 'e')

    def get_signal_for_b(self) -> str:
        signals_for_length_6: Set[str] = cast(
            Set[str],
            reduce(set.intersection, (
                set(display.signals)
                for display in self.displays_by_length[6]
            )),
        )
        signal_b_candidates = (
            signals_for_length_6
            - {self.encoder['a']}
            - self.signals_d_g
            - self.signals_c_f
        )
        return self.get_check_single_signal(signal_b_candidates, 'b')

    def get_signals_for_d_and_g(self) -> Set[str]:
        signals_for_length_5: Set[str] = cast(
            Set[str],
            reduce(set.intersection, (
                set(display.signals)
                for display in self.displays_by_length[5]
            )),
        )
        signals_d_g = signals_for_length_5 - {self.encoder['a']}
        if len(signals_d_g) != 2:
            raise Exception(
                f"Expected 2 candidates for signals 'd' and 'g', but got "
                f"{len(signals_d_g)}"
            )

        return signals_d_g

    def get_signals_for_c_and_f(self) -> Set[str]:
        signals_1, signals_7 = self.get_signals_for_1_and_7(
            self.displays_by_digit
        )
        signals_c_f = set(signals_7) & set(signals_1)
        if len(signals_c_f) != 2:
            raise Exception(
                f"Expected 2 candidates for signals 'c' and 'f', but got "
                f"{len(signals_c_f)}"
            )

        return signals_c_f

    def get_signal_for_a(self) -> str:
        signals_1, signals_7 = self.get_signals_for_1_and_7(
            self.displays_by_digit,
        )
        signals_a_candidates = set(signals_7) - set(signals_1)
        return self.get_check_single_signal(signals_a_candidates, 'a')

    def get_check_single_signal(self, candidates: Set[str], signal: str) -> str:
        if len(candidates) != 1:
            raise Exception(
                f"Expected one candidate for signal '{signal}', but got "
                f"{len(candidates)}"
            )
        signal_for, = candidates

        return signal_for

    def solve_signal(self, signal: str, signal_for: str) -> None:
        if signal_for in self.decoder:
            raise Exception(
                f"Expected signal for '{signal}' to be unique, but "
                f"{signal_for} was already assigned to "
                f"{self.decoder[signal_for]}"
            )
        self.decoder[signal_for] = signal
        if self.encoder.get(signal, signal_for) != signal_for:
            raise Exception(
                f"Expected {signal} to encode to {signal_for}, but it already "
                f"encodes to {self.encoder[signal]}"
            )
        self.encoder[signal] = signal_for

    def get_signals_for_1_and_7(
        self, displays_by_digit: Dict[int, List["DisplayExtended"]],
    ) -> Tuple[Signals, Signals]:
        displays_1 = displays_by_digit.get(1, [])
        displays_7 = displays_by_digit.get(7, [])
        if not displays_1 or not displays_7:
            raise Exception(
                f"Expected to have both 1 (actually {len(displays_1)} of them)"
                f" and 7 (actually {len(displays_7)} of them) displays"
            )
        displays_1_signals = set(display.signals for display in displays_1)
        if len(displays_1_signals) != 1:
            raise Exception(
                f"Expected to have one signal configuration for 1, but had "
                f"{len(displays_1_signals)}",
            )
        signals_1, = displays_1_signals
        displays_7_signals = set(display.signals for display in displays_7)
        if len(displays_7_signals) != 1:
            raise Exception(
                f"Expected to have one signal configuration for 7, but had "
                f"{len(displays_7_signals)}",
            )
        signals_7, = displays_7_signals

        return signals_1, signals_7


class EntryExtended(Entry["DisplayExtended"]):
    def solve(self) -> Dict[str, str]:
        return EntrySolver.solve_entry(self)

    @property
    def decoded_output(self) -> int:
        """
        >>> EntryExtended.from_entry_text(
        ...     "acedgfb cdfbe gcdfa fbcad dab cefabd cdfgeb eafb cagedb ab"
        ...     " | cdfeb fcadb cdfeb cdbaf"
        ... ).decoded_output
        5353
        """
        decoder = self.solve()
        return int("".join(map(str, (
            display.get_decoded_value(decoder)
            for display in self.outputs
        ))), 10)


class DisplayExtended(Display):
    def get_decoded_value(self, decoder: Dict[str, str]) -> int:
        """
        >>> DisplayExtended.from_display_text("cdfeb").get_decoded_value({
        ...     'd': 'a', 'e': 'b', 'g': 'e', 'b': 'f',
        ...     'c': 'g', 'a': 'c', 'f': 'd'
        ... })
        5
        """
        return self.decode(decoder).value

    def decode(self, decoder: Dict[str, str]) -> "DisplayExtended":
        """
        >>> DisplayExtended.from_display_text("cdfeb").decode({
        ...     'd': 'a', 'e': 'b', 'g': 'e', 'b': 'f',
        ...     'c': 'g', 'a': 'c', 'f': 'd'
        ... })
        DisplayExtended(signals=('a', 'b', 'd', 'f', 'g'))
        """
        cls: Type["DisplayExtended"] = type(self)
        # noinspection PyArgumentList
        return cls(
            signals=tuple(sorted(
                decoder[signal]
                for signal in self.signals
            )),
        )

    @property
    def value(self) -> int:
        """
        >>> DisplayExtended.from_display_text("cdfeb").decode({
        ...     'd': 'a', 'e': 'b', 'g': 'e', 'b': 'f',
        ...     'c': 'g', 'a': 'c', 'f': 'd'
        ... }).value
        5
        """
        return DIGITS_BY_SIGNALS[self.signals]


Challenge.main()
challenge = Challenge()
