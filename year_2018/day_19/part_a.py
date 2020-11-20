#!/usr/bin/env python3
import itertools
import re
from abc import ABC

import utils
from year_2018.day_16 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        2640
        """
        registers = Program.from_program_text(_input).run()
        return registers[0]


class Program:
    re_instruction_pointer_register_declaration = re.compile(r"^#ip (\d+)$")

    @classmethod
    def from_program_text(cls, program_text, instruction_pointer=0):
        """
        >>> program_a = Program.from_program_text(
        ...     "#ip 0\\n"
        ...     "seti 5 0 1\\n"
        ...     "seti 6 0 2\\n"
        ...     "addi 0 1 0\\n"
        ...     "addr 1 2 3\\n"
        ...     "setr 1 0 0\\n"
        ...     "seti 8 0 4\\n"
        ...     "seti 9 0 5\\n"
        ... )
        >>> program_a.instruction_pointer_register
        0
        >>> len(program_a.instructions)
        7
        >>> program_a.instructions[0]
        SetIExtended(5, 0, 1)
        """
        non_empty_lines = filter(None, program_text.splitlines())
        instruction_pointer_register_declaration = next(non_empty_lines)
        instruction_pointer_register_match = \
            cls.re_instruction_pointer_register_declaration.match(
                instruction_pointer_register_declaration)
        if not instruction_pointer_register_match:
            raise Exception(
                f"First line was not an instruction pointer register "
                f"declaration: "
                f"{instruction_pointer_register_declaration}")
        instruction_pointer_register_str, = \
            instruction_pointer_register_match.groups()
        instruction_pointer_register = int(instruction_pointer_register_str)
        instructions = list(map(InstructionExtended.parse, non_empty_lines))

        return cls(
            instructions, instruction_pointer_register, instruction_pointer)

    def __init__(self, instructions, instruction_pointer_register,
                 instruction_pointer=0):
        self.instructions = instructions
        self.instruction_pointer_register = instruction_pointer_register
        self.instruction_pointer = instruction_pointer

    def run(self, registers=(0,) * 6, instruction_pointer=None, debug=False,
            report_count=1000000, report_only_changes=None):
        """
        >>> Program.from_program_text(
        ...     "#ip 0\\n"
        ...     "seti 5 0 1\\n"
        ...     "seti 6 0 2\\n"
        ...     "addi 0 1 0\\n"
        ...     "addr 1 2 3\\n"
        ...     "setr 1 0 0\\n"
        ...     "seti 8 0 4\\n"
        ...     "seti 9 0 5\\n"
        ... ).run()
        (6, 5, 6, 0, 0, 9)
        """
        if instruction_pointer is not None:
            self.instruction_pointer = instruction_pointer
        final_registers = registers
        for step in itertools.count():
            previous_registers = final_registers
            finished, final_registers = self.step(final_registers)
            if finished:
                break
            if debug:
                if report_only_changes is not None:
                    should_report = any(
                        previous_registers[index] != final_registers[index]
                        for index in report_only_changes
                    )
                else:
                    should_report = step % report_count == 0
                if should_report:
                    print(step, previous_registers, final_registers)

        return final_registers

    def step(self, registers, instruction_pointer=None):
        """
        >>> Program.from_program_text(
        ...     "#ip 0\\n"
        ...     "seti 5 0 1\\n"
        ...     "seti 6 0 2\\n"
        ...     "addi 0 1 0\\n"
        ...     "addr 1 2 3\\n"
        ...     "setr 1 0 0\\n"
        ...     "seti 8 0 4\\n"
        ...     "seti 9 0 5\\n"
        ... ).step((0, 0, 0, 0, 0, 0))
        (False, (0, 5, 0, 0, 0, 0))
        >>> Program.from_program_text((
        ...     "#ip 0\\n"
        ...     "seti 5 0 1\\n"
        ...     "seti 6 0 2\\n"
        ...     "addi 0 1 0\\n"
        ...     "addr 1 2 3\\n"
        ...     "setr 1 0 0\\n"
        ...     "seti 8 0 4\\n"
        ...     "seti 9 0 5\\n"
        ... ), 6).step((5, 5, 6, 0, 0, 0))
        (False, (6, 5, 6, 0, 0, 9))
        >>> Program.from_program_text((
        ...     "#ip 0\\n"
        ...     "seti 5 0 1\\n"
        ...     "seti 6 0 2\\n"
        ...     "addi 0 1 0\\n"
        ...     "addr 1 2 3\\n"
        ...     "setr 1 0 0\\n"
        ...     "seti 8 0 4\\n"
        ...     "seti 9 0 5\\n"
        ... ), 7).step((6, 5, 6, 0, 0, 9))
        (True, (6, 5, 6, 0, 0, 9))
        """
        if instruction_pointer is not None:
            self.instruction_pointer = instruction_pointer
        if self.instruction_pointer >= len(self.instructions):
            return True, registers
        instruction = self.instructions[self.instruction_pointer]
        prepared_registers = self.prepare_registers(registers)
        new_registers = instruction.step(prepared_registers)
        self.increment_instruction_pointer(new_registers)

        return False, new_registers

    def prepare_registers(self, registers):
        """
        >>> Program([], 0, 0).prepare_registers((0, 0, 0, 0, 0, 0))
        (0, 0, 0, 0, 0, 0)
        >>> Program([], 3, 1).prepare_registers((0, 0, 0, 0, 0, 0))
        (0, 0, 0, 1, 0, 0)
        """
        return self.write_to_register(
            registers,
            self.instruction_pointer_register,
            self.instruction_pointer,
        )

    def increment_instruction_pointer(self, registers):
        """
        >>> Program([], 0).increment_instruction_pointer((0, 0, 0, 0, 0, 0))
        1
        >>> Program([], 3).increment_instruction_pointer((1, 2, 3, 4, 5, 6))
        5
        """
        self.instruction_pointer = registers[self.instruction_pointer_register]
        self.instruction_pointer += 1

        return self.instruction_pointer

    def write_to_register(self, registers, pointer, value):
        """
        >>> Program([], 0).write_to_register((0, 0, 0, 0, 0, 0), 0, 1)
        (1, 0, 0, 0, 0, 0)
        >>> Program([], 0).write_to_register((1, 2, 3, 4, 5, 6), 3, 0)
        (1, 2, 3, 0, 5, 6)
        """
        return registers[:pointer] + (value,) + registers[pointer + 1:]


class InstructionExtended(part_a.Instruction, ABC):
    instruction_classes = {}

    @classmethod
    def parse(cls, instruction_text):
        """
        >>> InstructionExtended.parse("addi 5 16 5")
        AddIExtended(5, 16, 5)
        >>> InstructionExtended.parse("seti 5 16 5")
        SetIExtended(5, 16, 5)
        """
        for instruction_class in cls.instruction_classes.values():
            parsed = instruction_class.try_parse(instruction_text)
            if parsed is not None:
                break
        else:
            raise Exception(f"Could not parse '{instruction_text}'")

        return parsed

    @classmethod
    def try_parse(cls, instruction_text):
        re_instruction = re.compile(rf"^{re.escape(cls.name)}((?: \d+)*)$")
        match = re_instruction.match(instruction_text)
        if not match:
            return None

        operand_strs, = match.groups()
        operands = tuple(map(int, operand_strs.strip().split(' ')))

        return cls(*operands)


class ThreeOperandsInstructionExtended(
        InstructionExtended, part_a.ThreeOperandsInstruction, ABC):
    def __repr__(self):
        return f"{type(self).__name__}({self.op_a}, {self.op_b}, {self.op_c})"


@InstructionExtended.register
class AddIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.AddI):
    """
    >>> AddIExtended.try_parse("addi 5 16 5")
    AddIExtended(5, 16, 5)
    >>> AddIExtended.try_parse("seti 5 16 5")
    """


@InstructionExtended.register
class AddRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.AddR):
    pass


@InstructionExtended.register
class MulIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.MulI):
    pass


@InstructionExtended.register
class MulRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.MulR):
    pass


@InstructionExtended.register
class BAnIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.BAnI):
    pass


@InstructionExtended.register
class BAnRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.BAnR):
    pass


@InstructionExtended.register
class BOrIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.BOrI):
    pass


@InstructionExtended.register
class BOrRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.BOrR):
    pass


@InstructionExtended.register
class SetIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.SetI):
    pass


@InstructionExtended.register
class SetRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.SetR):
    pass


@InstructionExtended.register
class GTIRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.GTIR):
    pass


@InstructionExtended.register
class GTRIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.GTRI):
    pass


@InstructionExtended.register
class GTRRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.GTRR):
    pass


@InstructionExtended.register
class EqIRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.EqIR):
    pass


@InstructionExtended.register
class EqRIExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.EqRI):
    pass


@InstructionExtended.register
class EqRRExtended(
        ThreeOperandsInstructionExtended, InstructionExtended, part_a.EqRR):
    pass


challenge = Challenge()
challenge.main()
