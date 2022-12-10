#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
import re
from typing import ClassVar, Iterable, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        12980
        """
        instructions = InstructionSet.from_instructions(_input)
        return State().get_sum_of_signal_strengths_of(instructions)


@dataclass
class State:
    x: int = 1
    next_instruction_index: int = 0
    pending_instruction: Optional["Instruction"] = None
    pending_instruction_cycles: int = 0

    def get_sum_of_signal_strengths_of(
        self, instructions: "InstructionSet",
    ) -> int:
        """
        >>> State().get_sum_of_signal_strengths_of(
        ...     InstructionSet.from_instructions(LONG_INSTRUCTIONS_TEXT))
        13140
        """
        return sum(self.get_signal_strengths_of(instructions))

    def get_signal_strengths_of(
        self, instructions: "InstructionSet",
    ) -> Iterable[int]:
        """
        >>> list(State().get_signal_strengths_of(
        ...     InstructionSet.from_instructions(LONG_INSTRUCTIONS_TEXT)))
        [420, 1140, 1800, 2940, 2880, 3960]
        """
        return self.get_signal_strengths(self.run(instructions))

    def get_signal_strengths(self, xs: Iterable[int]) -> Iterable[int]:
        for index, x in enumerate(xs, 1):
            if index % 40 == 20:
                yield index * x

    def run(self, instructions: "InstructionSet") -> Iterable[int]:
        """
        >>> list(State().run(InstructionSet.from_instructions(
        ...     "noop\\n"
        ...     "addx 3\\n"
        ...     "addx -5"
        ... )))
        [1, 1, 1, 4, 4, -1]
        >>> list(State().run(
        ...     InstructionSet.from_instructions(LONG_INSTRUCTIONS_TEXT)))
        [1, 1, 16, 16, 5, 5, 11, 11, 8, 8, 13, 13, 12, 12, 4, 4, 17, 17, 21, 21,
            21, 20, ...]
        """
        self.next_instruction_index = 0
        self.x = 1
        yield self.x
        while self.next_instruction_index <= len(instructions.instructions):
            if self.pending_instruction_cycles == 0:
                if self.next_instruction_index \
                        == len(instructions.instructions):
                    break
                self.sequence_instruction(
                    instructions.instructions[self.next_instruction_index],
                )
                self.next_instruction_index += 1
            self.pending_instruction_cycles -= 1
            if self.pending_instruction_cycles == 0:
                self.apply_pending_instruction()
            yield self.x
        return self

    def sequence_instruction(self, instruction: "Instruction") -> "State":
        self.pending_instruction = instruction
        self.pending_instruction_cycles = instruction.cycle_count
        return self

    def apply_pending_instruction(self) -> "State":
        self.pending_instruction.apply(self)
        return self


@dataclass
class InstructionSet:
    instructions: ["Instruction"]

    @classmethod
    def from_instructions(cls, instructions_text: str) -> "InstructionSet":
        """
        >>> InstructionSet.from_instructions(
        ...     "noop\\n"
        ...     "addx 3\\n"
        ...     "addx -5"
        ... )
        InstructionSet(instructions=[Noop(), AddX(amount=3), AddX(amount=-5)])
        """
        return cls(
            instructions=[
                Instruction.parse(line)
                for line in instructions_text.strip().splitlines()
            ],
        )


@dataclass
class Instruction(PolymorphicParser, ABC, root=True):
    """
    >>> Instruction.parse("noop")
    Noop()
    >>> Instruction.parse("addx -13")
    AddX(amount=-13)
    """
    cycle_count: ClassVar[int]

    def apply(self, state: State) -> State:
        raise NotImplementedError()


@Instruction.register
@dataclass
class Noop(Instruction):
    name = "noop"
    cycle_count = 1

    re_instruction = re.compile(r"^noop$")

    @classmethod
    def try_parse(cls, text: str) -> Optional["Noop"]:
        """
        >>> Noop.try_parse("noop")
        Noop()
        """
        if not cls.re_instruction.match(text):
            return None

        return cls()

    def apply(self, state: State) -> State:
        """
        >>> Noop().apply(State())
        State(x=1, ...)
        >>> Noop().apply(State(x=2))
        State(x=2, ...)
        """
        return state


@Instruction.register
@dataclass
class AddX(Instruction):
    name = "addx"
    cycle_count = 2

    amount: int

    re_instruction = re.compile(r"^addx (-?\d+)$")

    @classmethod
    def try_parse(cls, text: str) -> Optional["AddX"]:
        """
        >>> AddX.try_parse("addx 5")
        AddX(amount=5)
        >>> AddX.try_parse("addx -25")
        AddX(amount=-25)
        """
        match = cls.re_instruction.match(text)
        if not match:
            return None

        amount_str, = match.groups()
        return cls(amount=int(amount_str))

    def apply(self, state: State) -> State:
        """
        >>> AddX(5).apply(State())
        State(x=6, ...)
        >>> AddX(-13).apply(State(x=2))
        State(x=-11, ...)
        """
        state.x += self.amount
        return state


Challenge.main()
challenge = Challenge()


LONG_INSTRUCTIONS_TEXT = """
addx 15
addx -11
addx 6
addx -3
addx 5
addx -1
addx -8
addx 13
addx 4
noop
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx 5
addx -1
addx -35
addx 1
addx 24
addx -19
addx 1
addx 16
addx -11
noop
noop
addx 21
addx -15
noop
noop
addx -3
addx 9
addx 1
addx -3
addx 8
addx 1
addx 5
noop
noop
noop
noop
noop
addx -36
noop
addx 1
addx 7
noop
noop
noop
addx 2
addx 6
noop
noop
noop
noop
noop
addx 1
noop
noop
addx 7
addx 1
noop
addx -13
addx 13
addx 7
noop
addx 1
addx -33
noop
noop
noop
addx 2
noop
noop
noop
addx 8
noop
addx -1
addx 2
addx 1
noop
addx 17
addx -9
addx 1
addx 1
addx -3
addx 11
noop
noop
addx 1
noop
addx 1
noop
noop
addx -13
addx -19
addx 1
addx 3
addx 26
addx -30
addx 12
addx -1
addx 3
addx 1
noop
noop
noop
addx -9
addx 18
addx 1
addx 2
noop
noop
addx 9
noop
noop
noop
addx -1
addx 2
addx -37
addx 1
addx 3
noop
addx 15
addx -21
addx 22
addx -6
addx 1
noop
addx 2
addx 1
noop
addx -10
noop
noop
addx 20
addx 1
addx 2
addx 2
addx -6
addx -11
noop
noop
noop
"""
