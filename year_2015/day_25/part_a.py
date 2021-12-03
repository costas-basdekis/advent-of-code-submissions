#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from typing import Dict

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        19980801
        """
        return Grid().get_code_for_coordinates(
            Coordinates.from_manual_text(_input),
            debugger=debugger,
        )


@dataclass
class Coordinates:
    column: int
    row: int

    re_manual = re.compile(
        r"^\s*To continue, please consult the code grid in the manual."
        r"\s*Enter the code at row (\d+), column (\d+).\s*$"
    )

    @classmethod
    def from_manual_text(cls, manual_text: str) -> "Coordinates":
        """
        >>> Coordinates.from_manual_text('''
        ...     To continue, please consult the code grid in the manual.
        ...     Enter the code at row 2947, column 3029.
        ... ''')
        Coordinates(column=3029, row=2947)
        """
        row, column = map(int, cls.re_manual.match(manual_text).groups())
        return cls(column=column, row=row)

    @property
    def index(self) -> int:
        """
        >>> Coordinates(1, 1).index
        1
        >>> Coordinates(1, 2).index
        2
        >>> Coordinates(2, 1).index
        3
        >>> Coordinates(1, 3).index
        4
        >>> Coordinates(2, 2).index
        5
        >>> Coordinates(3, 1).index
        6
        """
        distance = self.row + self.column - 2
        if distance == 0:
            return 1
        first_index_of_distance = 1 + distance * (1 + distance) // 2
        return first_index_of_distance + self.column - 1


@dataclass
class Grid:
    multiplier: int = 252533
    modulo: int = 33554393
    pre_computed_codes: Dict[int, int] = field(default_factory=lambda: {
        Coordinates(1, 1).index: 20151125,
        Coordinates(6, 6).index: 27995004,
    })

    def get_code_for_coordinates(
        self, coordinates: Coordinates,
        debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> [
        ...     Grid().get_code_for_coordinates(_coordinates)
        ...     for _coordinates in [
        ...         Coordinates(1, 1), Coordinates(1, 2),
        ...         Coordinates(2, 1), Coordinates(1, 3),
        ...     ]
        ... ]
        [20151125, 31916031, 18749137, 16080970]
        >>> Grid().get_code_for_coordinates(Coordinates(6, 6))
        27995004
        >>> Grid().get_code_for_coordinates(Coordinates(7, 5))
        20175176
        """
        return self.get_code(coordinates.index, debugger=debugger)

    def get_code(
        self, index: int,
        debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> list(map(Grid().get_code, range(1, 5)))
        [20151125, 31916031, 18749137, 16080970]
        """
        max_precomputed_index = self.get_max_precomputed_index(index)
        code = self.pre_computed_codes[max_precomputed_index]
        for computing_index \
                in debugger.stepping(range(index - max_precomputed_index)):
            debugger.default_report_if(computing_index)
            code *= self.multiplier
            code %= self.modulo

        return code

    def get_max_precomputed_index(self, index: int) -> int:
        return max(
            precomputed_index
            for precomputed_index in self.pre_computed_codes
            if precomputed_index <= index
        )


Challenge.main()
challenge = Challenge()
