#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge, Self
from year_2022.day_05.part_a import Warehouse, Move, Procedure, MoveSet
from year_2022.day_05 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        'NGCMPJLHV'
        """
        return ProcedureExtended\
            .from_procedure_text(_input)\
            .apply_all_moves()\
            .get_stack_tops()


class ProcedureExtended(Procedure["WarehouseExtended", MoveSet]):
    """
    >>> print(str(ProcedureExtended.from_procedure_text(
    ...     "    [D]    \\n"
    ...     "[N] [C]    \\n"
    ...     "[Z] [M] [P]\\n"
    ...     " 1   2   3 \\n"
    ...     "\\n"
    ...     "move 1 from 2 to 1\\n"
    ...     "move 3 from 1 to 3\\n"
    ...     "move 2 from 2 to 1\\n"
    ...     "move 1 from 1 to 2"
    ... ).apply_all_moves()))
            [D]
            [N]
            [Z]
    [M] [C] [P]
     1   2   3
    <BLANKLINE>
    >>> ProcedureExtended.from_procedure_text(
    ...     "    [D]    \\n"
    ...     "[N] [C]    \\n"
    ...     "[Z] [M] [P]\\n"
    ...     " 1   2   3 \\n"
    ...     "\\n"
    ...     "move 1 from 2 to 1\\n"
    ...     "move 3 from 1 to 3\\n"
    ...     "move 2 from 2 to 1\\n"
    ...     "move 1 from 1 to 2"
    ... ).apply_all_moves().get_stack_tops()
    'MCD'
    """


class WarehouseExtended(Warehouse):
    def apply_move(self: Self["Warehouse"], move: Move) -> Self["Warehouse"]:
        """
        >>> print(str(WarehouseExtended.from_warehouse_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 "
        ... ).apply_move(Move.from_move_text("move 3 from 2 to 1"))))
        [D]
        [C]
        [M]
        [N]
        [Z]     [P]
         1   2   3
        """
        buffer = []
        for _ in range(move.count):
            buffer.append(
                self.stacks[move.source - 1].pop(),
            )
        self.stacks[move.target - 1].extend(reversed(buffer))

        return self


Challenge.main()
challenge = Challenge()
