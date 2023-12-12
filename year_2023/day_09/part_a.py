#!/usr/bin/env python3
from dataclasses import dataclass
from typing import cast, Generic, Iterable, List, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1731106378
        """
        return Report.from_report_text(_input).predict_next_sum()


SequenceT = TV["Sequence"]


@dataclass
class Report(Generic[SequenceT]):
    sequences: List[SequenceT]

    @classmethod
    def get_sequence_class(cls) -> Type[SequenceT]:
        return cast(Type[SequenceT], get_type_argument_class(cls, SequenceT))

    @classmethod
    def from_report_text(cls, report_text: str) -> "Report":
        """
        >>> Report.from_report_text('''
        ...     0 3 6 9 12 15
        ...     1 3 6 10 15 21
        ...     10 13 16 21 30 45
        ... ''')
        Report(sequences=[Sequence(values=[0, 3, 6, 9, 12, 15]), ...])
        """
        sequence_class = cls.get_sequence_class()
        return cls(
            list(map(
                sequence_class.from_sequence_text,
                report_text.strip().splitlines(),
            )),
        )

    def predict_next_sum(self) -> int:
        """
        >>> Report.from_report_text('''
        ...     0 3 6 9 12 15
        ...     1 3 6 10 15 21
        ...     10 13 16 21 30 45
        ... ''').predict_next_sum()
        114
        """
        return sum(sequence.predict_next_term() for sequence in self.sequences)


PredictorT = TV["Predictor"]


@dataclass
class Sequence(Generic[PredictorT]):
    values: List[int]

    @classmethod
    def get_predictor_class(cls) -> Type[PredictorT]:
        return cast(Type[PredictorT], get_type_argument_class(cls, PredictorT))

    @classmethod
    def from_sequence_text(cls, sequence_text: str) -> "Sequence":
        """
        >>> Sequence.from_sequence_text("0 3 6 9 12 15")
        Sequence(values=[0, 3, 6, 9, 12, 15])
        """
        return cls(list(map(int, sequence_text.strip().split(" "))))

    def __iter__(self) -> Iterable[int]:
        return iter(self.values)

    def __getitem__(self, item: int) -> int:
        return self.values[item]

    def get_difference(self) -> "Sequence":
        """
        >>> Sequence.from_sequence_text("0 3 6 9 12 15").get_difference()
        Sequence(values=[3, 3, 3, 3, 3])
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls([
            _next - current
            for current, _next in zip(self.values, self.values[1:])
        ])

    def predict_next_term(self) -> int:
        predictor_class = self.get_predictor_class()
        return predictor_class.from_sequence(self).predict_next_term()


@dataclass
class Predictor:
    levels: List[int]

    @classmethod
    def from_sequence_text(cls, sequence_text: str) -> "Predictor":
        return cls.from_sequence(Sequence.from_sequence_text(sequence_text))

    @classmethod
    def from_sequence(cls, sequence: Sequence) -> "Predictor":
        """
        >>> Predictor.from_sequence_text("0 3 6 9 12 15")
        Predictor(levels=[3, 15])
        """
        current = sequence
        levels = []
        while list(filter(None, current)):
            levels.insert(0, current[-1])
            current = current.get_difference()
        return cls(levels)

    def predict_next_term(self) -> int:
        """
        >>> Predictor.from_sequence_text("0 3 6 9 12 15").predict_next_term()
        18
        >>> Predictor.from_sequence_text("1 3 6 10 15 21").predict_next_term()
        28
        >>> Predictor.from_sequence_text(
        ...     "10 13 16 21 30 45").predict_next_term()
        68
        """
        return sum(self.levels)


Challenge.main()
challenge = Challenge()
