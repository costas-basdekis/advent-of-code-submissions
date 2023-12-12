#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass, field
import re
from math import floor
from typing import ClassVar, Dict, Generic, List, Optional, Type, Union, TypeVar

import click

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser
from year_2017.day_06.part_a import Memory


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1,7,6,5,1,0,5,0,7
        """
        return Machine.from_text(_input).run().show_output()

    def play(self):
        machine = Machine.from_opcodes([0, 1, 5, 4, 3, 0], Memory(a=2024))
        while not machine.finished:
            print(machine)
            if machine.finished:
                print(f"Finished")
                break
            print(f"Next instruction: {machine.next_instruction.name} @ {machine.next_operand}")
            click.getchar()
            machine.run_once()


MachineTypeT = TypeVar('MachineTypeT', bound=Type['Machine'])
MachineT = TypeVar('MachineT', bound='Machine')
InstructionT = TypeVar('InstructionT', bound="InstructionBase")


@dataclass
class Machine(Generic[InstructionT]):
    memory: "Memory"
    instructions: List[InstructionT]

    @classmethod
    def from_text(cls: MachineTypeT, text: str) -> MachineT:
        """
        >>> print(Machine.from_text('''
        ...     Register A: 729
        ...     Register B: 0
        ...     Register C: 0
        ...
        ...     Program: 0,1,5,4,3,0
        ... '''))
        Register A: 729
        Register B: 0
        Register C: 0
        PC: 0
        Out:
        <BLANKLINE>
        Program: 0,1,5,4,3,0
        """
        memory_str, instructions_str = text.strip().split("\n\n")
        memory = Memory.from_text(memory_str)
        opcodes = list(map(int, instructions_str.strip().split("Program: ")[1].split(",")))
        return cls.from_opcodes(opcodes, memory=memory)

    @classmethod
    def from_opcodes(cls: MachineTypeT, opcodes: List[int], memory: Optional[Memory] = None) -> MachineT:
        if memory is None:
            memory = Memory()
        instructions_by_opcode = InstructionBase.get_instructions_by_opcode()
        instructions = [
            instructions_by_opcode[opcode]
            for opcode in opcodes
        ]
        return cls(memory=memory, instructions=instructions)

    def __str__(self) -> str:
        return "\n\n".join([
            str(self.memory),
            f"Program: {','.join(map(str, (instruction.opcode for instruction in self.instructions)))}"
        ])

    @property
    def finished(self):
        return not (0 <= self.memory.pc < len(self.instructions))

    def run(self: MachineT) -> MachineT:
        """
        >>> print(Machine.from_opcodes([2, 6], Memory(c=9)).run().memory)
        Register A: 0
        Register B: 1
        Register C: 9
        PC: 2
        Out:
        >>> print(Machine.from_opcodes([5, 0, 5, 1, 5, 4], Memory(a=10)).run().show_output())
        0,1,2
        >>> print(Machine.from_opcodes([0, 1, 5, 4, 3, 0], Memory(a=2024)).run().memory)
        Register A: 0
        Register B: ...
        Register C: ...
        PC: ...
        Out: 4,2,5,6,7,7,7,7,3,1,0
        >>> print(Machine.from_opcodes([1, 7], Memory(b=29)).run().memory)
        Register A: ...
        Register B: 26
        Register C: ...
        PC: 2
        Out:
        >>> print(Machine.from_opcodes([4, 0], Memory(b=2024, c=43690)).run().memory)
        Register A: ...
        Register B: 44354
        Register C: ...
        PC: 2
        Out:
        >>> print(Machine.from_text('''
        ...     Register A: 729
        ...     Register B: 0
        ...     Register C: 0
        ...
        ...     Program: 0,1,5,4,3,0
        ... ''').run().show_output())
        4,6,3,5,6,3,5,2,1,0
        """
        while not self.finished:
            self.run_once()
        return self

    def run_once(self: MachineT) -> MachineT:
        instruction = self.next_instruction
        operand = self.next_operand
        if instruction is None or operand is None:
            return self
        new_pc = instruction.operate(self.memory, operand)
        if new_pc is None:
            new_pc = self.memory.pc + 2
        self.memory.pc = new_pc
        return self

    @property
    def next_instruction(self) -> Optional[InstructionT]:
        if self.finished:
            return None
        return self.instructions[self.memory.pc]

    @property
    def next_operand(self) -> Optional[int]:
        if self.finished:
            return None
        return self.instructions[self.memory.pc + 1].opcode

    def show_output(self) -> str:
        return ','.join(map(str, self.memory.out))


@dataclass
class Memory:
    a: int = 0
    b: int = 0
    c: int = 0
    pc: int = 0
    out: List[int] = field(default_factory=list)

    re_memory: ClassVar[re.Pattern] = re.compile(r"^Register ([ABC]): (-?\d+)$")

    @classmethod
    def from_text(cls, text: str) -> "Memory":
        registers = {"a": 0, "b": 0, "c": 0}
        for line in text.strip().splitlines():
            register_name, value_str = cls.re_memory.match(line.strip()).groups()
            registers[register_name.lower()] = int(value_str)
        return cls(**registers)

    def __str__(self) -> str:
        return "\n".join([
            f"Register A: {self.a}",
            f"Register B: {self.b}",
            f"Register C: {self.c}",
            f"PC: {self.pc}",
            f"Out: {','.join(map(str, self.out))}",
        ])

    def get_combo(self, operand: int) -> int:
        if 0 <= operand <= 3:
            return operand
        if 4 <= operand <= 6:
            return [self.a, self.b, self.c][operand - 4]
        raise Exception(f"Cannot parse combo operand {operand}")

    def write_out(self, value: int):
        self.out.append(value)


@dataclass
class InstructionBase(PolymorphicParser, ABC, root=True):
    opcode: ClassVar[int]

    @classmethod
    def try_parse(cls, text: str):
        raise Exception(f"Cannot parse instructions")

    def operate(self, memory: Memory, operand: int) -> Optional[int]:
        raise NotImplementedError()

    @classmethod
    def get_instructions_by_opcode(cls) -> Dict[int, "InstructionBase"]:
        # noinspection PyUnresolvedReferences,PyTypeChecker
        return {
            instruction_class.opcode: instruction_class()
            for instruction_class in cls.sub_classes.values()
        }


@InstructionBase.register
@dataclass
class AdvInstruction(InstructionBase):
    name = "adv"
    opcode = 0

    def operate(self, memory: Memory, operand: int):
        numerator = memory.a
        denominator = floor(2 ** memory.get_combo(operand))
        memory.a = numerator // denominator


@InstructionBase.register
@dataclass
class BxlInstruction(InstructionBase):
    name = "bxl"
    opcode = 1

    def operate(self, memory: Memory, operand: int):
        memory.b = memory.b ^ operand


@InstructionBase.register
@dataclass
class BstInstruction(InstructionBase):
    name = "bst"
    opcode = 2

    def operate(self, memory: Memory, operand: int):
        memory.b = memory.get_combo(operand) % 8


@InstructionBase.register
@dataclass
class JnzInstruction(InstructionBase):
    name = "jnz"
    opcode = 3

    def operate(self, memory: Memory, operand: int) -> Optional[int]:
        if memory.a == 0:
            return None
        return operand


@InstructionBase.register
@dataclass
class BxcInstruction(InstructionBase):
    name = "bxc"
    opcode = 4

    def operate(self, memory: Memory, operand: int):
        memory.b = memory.b ^ memory.c


@InstructionBase.register
@dataclass
class OutInstruction(InstructionBase):
    name = "out"
    opcode = 5

    def operate(self, memory: Memory, operand: int):
        memory.write_out(memory.get_combo(operand) % 8)


@InstructionBase.register
@dataclass
class BdvInstruction(InstructionBase):
    name = "bdv"
    opcode = 6

    def operate(self, memory: Memory, operand: int):
        numerator = memory.a
        denominator = floor(2 ** memory.get_combo(operand))
        memory.b = numerator // denominator


@InstructionBase.register
@dataclass
class CdvInstruction(InstructionBase):
    name = "cdv"
    opcode = 7

    def operate(self, memory: Memory, operand: int):
        numerator = memory.a
        denominator = floor(2 ** memory.get_combo(operand))
        memory.c = numerator // denominator


Challenge.main()
challenge = Challenge()
