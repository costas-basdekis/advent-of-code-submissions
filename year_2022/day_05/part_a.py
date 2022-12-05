#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import Union, Generic, Type

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        'TDCHVHJTG'
        """
        return Procedure\
            .from_procedure_text(_input)\
            .apply_all_moves()\
            .get_stack_tops()


WarehouseT = TV["Warehouse"]
MoveSetT = TV["MoveSet"]


@dataclass
class Procedure(Generic[WarehouseT, MoveSetT]):
    warehouse: WarehouseT
    moves: MoveSetT

    @classmethod
    def get_warehouse_class(cls) -> Type[WarehouseT]:
        return get_type_argument_class(cls, WarehouseT)

    @classmethod
    def get_moves_class(cls) -> Type[MoveSetT]:
        return get_type_argument_class(cls, MoveSetT)

    @classmethod
    def from_procedure_text(
        cls: Cls["Procedure"], procedure_text: str,
    ) -> Self["Procedure"]:
        """
        >>> print(str(Procedure.from_procedure_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 \\n"
        ...     "\\n"
        ...     "move 1 from 2 to 1\\n"
        ...     "move 3 from 1 to 3\\n"
        ...     "move 2 from 2 to 1\\n"
        ...     "move 1 from 1 to 2"
        ... )))
            [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3
        <BLANKLINE>
        move 1 from 2 to 1
        move 3 from 1 to 3
        move 2 from 2 to 1
        move 1 from 1 to 2
        """
        warehouse_text, moves_text = procedure_text.rstrip().split("\n\n")
        return cls(
            warehouse=(
                cls.get_warehouse_class().from_warehouse_text(warehouse_text)
            ),
            moves=cls.get_moves_class().from_moves_text(moves_text),
        )

    def __str__(self) -> str:
        return f"{str(self.warehouse)}\n\n{str(self.moves)}"

    def get_stack_tops(self) -> str:
        """
        >>> Procedure.from_procedure_text(
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
        'CMZ'
        """
        return self.warehouse.get_stack_tops()

    def apply_all_moves(self: Self["Procedure"]) -> Self["Procedure"]:
        """
        >>> procedure = Procedure.from_procedure_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 \\n"
        ...     "\\n"
        ...     "move 1 from 2 to 1\\n"
        ...     "move 3 from 1 to 3\\n"
        ...     "move 2 from 2 to 1\\n"
        ...     "move 1 from 1 to 2"
        ... )
        >>> print(str(procedure.apply_all_moves()))
                [Z]
                [N]
                [D]
        [C] [M] [P]
         1   2   3
        <BLANKLINE>
        """
        while self.moves.has_moves():
            self.apply_next_move()
        return self

    def apply_next_move(self: Self["Procedure"]) -> Self["Procedure"]:
        """
        >>> procedure = Procedure.from_procedure_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 \\n"
        ...     "\\n"
        ...     "move 1 from 2 to 1\\n"
        ...     "move 3 from 1 to 3\\n"
        ...     "move 2 from 2 to 1\\n"
        ...     "move 1 from 1 to 2"
        ... )
        >>> print(str(procedure.apply_next_move()))
        [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3
        <BLANKLINE>
        move 3 from 1 to 3
        move 2 from 2 to 1
        move 1 from 1 to 2
        >>> print(str(procedure.apply_next_move()))
                [Z]
                [N]
            [C] [D]
            [M] [P]
         1   2   3
        <BLANKLINE>
        move 2 from 2 to 1
        move 1 from 1 to 2
        >>> print(str(procedure.apply_next_move()))
                [Z]
                [N]
        [M]     [D]
        [C]     [P]
         1   2   3
        <BLANKLINE>
        move 1 from 1 to 2
        >>> print(str(procedure.apply_next_move()))
                [Z]
                [N]
                [D]
        [C] [M] [P]
         1   2   3
        <BLANKLINE>
        """
        self.warehouse.apply_move(self.moves.pop_first())
        return self


MoveT = TV["Move"]


@dataclass
class MoveSet(Generic[MoveT]):
    moves: [MoveT]

    @classmethod
    def get_move_class(cls) -> Type[MoveT]:
        return get_type_argument_class(cls, MoveT)

    @classmethod
    def from_moves_text(
        cls: Cls["MoveSet"], moves_text: str,
    ) -> Self["MoveSet"]:
        """
        >>> MoveSet.from_moves_text(
        ...     "move 1 from 2 to 1\\n"
        ...     "move 3 from 1 to 3\\n"
        ...     "move 2 from 2 to 1\\n"
        ...     "move 1 from 1 to 2\\n"
        ... )
        MoveSet(moves=[Move(source=2, target=1, count=1), ...])
        """
        return cls(
            moves=[
                cls.get_move_class().from_move_text(line)
                for line in moves_text.strip().splitlines()
            ],
        )

    def __str__(self) -> str:
        """
        >>> print(str(MoveSet.from_moves_text(
        ...     "move 1 from 2 to 1\\n"
        ...     "move 3 from 1 to 3\\n"
        ...     "move 2 from 2 to 1\\n"
        ...     "move 1 from 1 to 2\\n"
        ... )))
        move 1 from 2 to 1
        move 3 from 1 to 3
        move 2 from 2 to 1
        move 1 from 1 to 2
        """
        return "\n".join(map(str, self.moves))

    def has_moves(self) -> bool:
        return bool(self.moves)

    def pop_first(self: Self["Move"]) -> Self["Move"]:
        return self.moves.pop(0)


@dataclass
class Move:
    source: int
    target: int
    count: int

    re_move = re.compile(r"^move (\d+) from (\d) to (\d)$")

    @classmethod
    def from_move_text(cls: Cls["Move"], move_text: str) -> Self["Move"]:
        """
        >>> Move.from_move_text("move 1 from 2 to 3")
        Move(source=2, target=3, count=1)
        """
        match = cls.re_move.match(move_text.strip())
        if not match:
            raise Exception(f"Move '{move_text}' did not match pattern")
        count_str, source_str, target_str = \
            match.groups()
        return cls(
            source=int(source_str),
            target=int(target_str),
            count=int(count_str),
        )

    def __str__(self) -> str:
        """
        >>> print(str(Move.from_move_text("move 1 from 2 to 3")))
        move 1 from 2 to 3
        """
        return f"move {self.count} from {self.source} to {self.target}"


@dataclass
class Warehouse:
    stacks: [[str]]

    re_crate = re.compile(r"^\[(\w)]$")

    @classmethod
    def from_warehouse_text(
        cls: Cls["Warehouse"], warehouse_text: str,
    ) -> Self["Warehouse"]:
        """
        >>> Warehouse.from_warehouse_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 "
        ... )
        Warehouse(stacks=[['Z', 'N'], ['M', 'C', 'D'], ['P']])
        """
        lines = list(reversed(warehouse_text.splitlines()))
        first_line = lines[0]
        first_line_length = len(first_line)
        if first_line_length % 4 != 3:
            raise Exception(
                f"Expected last line to have length a multiple of 4 minus 1, "
                f"not {first_line_length}: '{first_line}'"
            )
        stack_count = (first_line_length + 1) // 4
        expected_first_line = " ".join(
            f" {index} "
            for index in range(1, stack_count + 1)
        )
        if first_line != expected_first_line:
            raise Exception(
                f"Expected last line to be '{expected_first_line}' not "
                f"'{first_line}'"
            )
        stacks = [[] for _ in range(stack_count)]
        for line_index, line in enumerate(lines[1:]):
            if len(line) != first_line_length:
                raise Exception(
                    f"Expected crate line to be length {first_line_length} not "
                    f"{len(line)} ('{line}')"
                )
            for start_index in range(0, first_line_length, 4):
                crate_text = line[start_index:start_index + 3]
                if not crate_text.strip():
                    crate = None
                else:
                    crate, = cls.re_crate.match(crate_text).groups()
                stack_index = start_index // 4
                stack = stacks[stack_index]
                if crate and stack and not stack[-1]:
                    raise Exception(
                        f"Expected a stack with no more items, but in stack "
                        f"height {line_index + 1} stack {stack_index + 1} "
                        f"contained item {crate} while the stack so far is "
                        f"{stack}"
                    )
                stack.append(crate)
        stacks = [
            list(filter(None, stack))
            for stack in stacks
        ]
        return cls(stacks=stacks)

    def __str__(self) -> str:
        """
        >>> print(str(Warehouse.from_warehouse_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 "
        ... )))
            [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3
        """
        max_stack_length = max(map(len, self.stacks))
        return "{}\n{}".format(
            "\n".join(
                " ".join(
                    f"[{self.stacks[stack_index][crate_index]}]"
                    if crate_index < len(self.stacks[stack_index]) else
                    "   "
                    for stack_index in range(len(self.stacks))
                )
                for crate_index in range(max_stack_length - 1, -1, -1)
            ),
            " ".join(
                f" {index} "
                for index in range(1, len(self.stacks) + 1)
            ),
        )

    def apply_move(self: Self["Warehouse"], move: Move) -> Self["Warehouse"]:
        """
        >>> print(str(Warehouse.from_warehouse_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 "
        ... ).apply_move(Move.from_move_text("move 1 from 2 to 1"))))
        [D]
        [N] [C]
        [Z] [M] [P]
         1   2   3
        >>> print(str(Warehouse.from_warehouse_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 "
        ... ).apply_move(Move.from_move_text("move 3 from 2 to 1"))))
        [M]
        [C]
        [D]
        [N]
        [Z]     [P]
         1   2   3
        """
        for _ in range(move.count):
            self.stacks[move.target - 1].append(
                self.stacks[move.source - 1].pop(),
            )

        return self

    def get_stack_tops(self) -> str:
        """
        >>> Warehouse.from_warehouse_text(
        ...     "    [D]    \\n"
        ...     "[N] [C]    \\n"
        ...     "[Z] [M] [P]\\n"
        ...     " 1   2   3 "
        ... ).get_stack_tops()
        'NDP'
        """
        return "".join(
            stack[-1]
            for stack in self.stacks
        )


Challenge.main()
challenge = Challenge()
