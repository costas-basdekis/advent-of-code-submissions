#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Tuple

from aox.challenge import Debugger

from utils import BaseChallenge, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        20009568
        """
        return Minefield.from_rows_text(_input)\
            .add_rows(39, debugger=debugger)\
            .get_safe_tile_count()


@dataclass
class Minefield:
    rows: List[List[bool]]

    PARSE_MAP = {
        '.': False,
        '^': True,
    }

    @classmethod
    def from_rows_text(cls, rows_text: str):
        """
        >>> Minefield.from_rows_text('..^^.')
        Minefield(rows=[[False, False, True, True, False]])
        """
        return cls(list(map(cls.parse_row, rows_text.splitlines())))

    @classmethod
    def parse_row(cls, row_text: str) -> List[bool]:
        """
        >>> Minefield.parse_row('..^^.')
        [False, False, True, True, False]
        """
        return list(map(cls.PARSE_MAP.get, row_text))

    def get_safe_tile_count(self) -> int:
        """
        >>> Minefield.from_rows_text(
        ...     '.^^.^.^^^^').add_rows(9).get_safe_tile_count()
        38
        """
        return helper.iterable_length(
            1
            for row in self.rows
            for trap in row
            if not trap
        )

    def add_rows(self, count: int,
                 debugger: Debugger = Debugger(enabled=False)):
        """
        >>> print("!" + Minefield.from_rows_text('..^^.').add_rows(2).show())
        !..^^.
        .^^^^
        ^^..^
        >>> print("!" + Minefield.from_rows_text(
        ...     '.^^.^.^^^^').add_rows(9).show())
        !.^^.^.^^^^
        ^^^...^..^
        ^.^^.^.^^.
        ..^^...^^^
        .^^^^.^^.^
        ^^..^.^^..
        ^^^^..^^^.
        ^..^^^^.^^
        .^^^..^.^^
        ^^.^^^..^^
        """
        debugger.reset()
        total_target = len(self.rows) + count
        for _ in range(count):
            self.add_row()
            debugger.step()
            if debugger.should_report():
                debugger.default_report(
                    f"rows: {len(self.rows)}/{total_target}")

        return self

    def add_row(self):
        """
        >>> print("!" + Minefield.from_rows_text('..^^.').add_row().show())
        !..^^.
        .^^^^
        """
        self.rows.append(self.get_next_row(self.rows[-1]))
        return self

    def get_next_row(self, row: List[bool]) -> List[bool]:
        """
        >>> Minefield([]).get_next_row([False, False, True, True, False])
        [False, True, True, True, True]
        """
        return [
            left_trap != right_trap
            for left_trap, _, right_trap in (
                self.get_relevant_traps(row, position)
                for position in range(len(row))
            )
        ]

    def get_relevant_traps(self, row: List[bool], position: int,
                           ) -> Tuple[bool, bool, bool]:
        """
        >>> Minefield([]).get_relevant_traps([True, True, True], 0)
        (False, True, True)
        >>> Minefield([]).get_relevant_traps([True, True, True], 1)
        (True, True, True)
        >>> Minefield([]).get_relevant_traps([True, True, True], 2)
        (True, True, False)
        """
        if position == 0:
            left_trap = False
        else:
            left_trap = row[position - 1]
        middle_trap = row[position]
        if position == len(row) - 1:
            right_trap = False
        else:
            right_trap = row[position + 1]

        return left_trap, middle_trap, right_trap

    SHOW_MAP = {
        trap: content
        for content, trap in PARSE_MAP.items()
    }

    def show(self) -> str:
        """
        >>> print("!" + Minefield.from_rows_text('..^^.').show())
        !..^^.
        >>> print("!" + Minefield.from_rows_text(
        ...     '..^^.\\n'
        ...     '.^^^^\\n'
        ...     '^^..^\\n'
        ... ).show())
        !..^^.
        .^^^^
        ^^..^
        """
        return "\n".join(
            "".join(
                self.SHOW_MAP[trap]
                for trap in row
            )
            for row in self.rows
        )


Challenge.main()
challenge = Challenge()
