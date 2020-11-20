#!/usr/bin/env python3
import itertools
import re
import string
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
        final_registers = registers
        for step, previous_registers, final_registers \
                in self.iter_run(registers, instruction_pointer):
            self.debug(step, previous_registers, final_registers,
                       debug, report_only_changes, report_count)

        return final_registers

    def iter_run(self, registers=(0,) * 6, instruction_pointer=None):
        if instruction_pointer is not None:
            self.instruction_pointer = instruction_pointer
        final_registers = registers
        for step in itertools.count():
            previous_registers = final_registers
            finished, final_registers = self.step(final_registers)
            yield step, previous_registers, final_registers
            if finished:
                break

    def debug(self, step, previous_registers, final_registers,
              debug, report_only_changes, report_count):
        should_report = self.should_output_debug(
            step, previous_registers, final_registers, debug,
            report_only_changes, report_count)
        if not should_report:
            return

        self.output_debug(step, previous_registers, final_registers)

    def output_debug(self, step, previous_registers, final_registers):
        print(step, previous_registers, final_registers)

    def should_output_debug(self, step, previous_registers, final_registers,
                            debug, report_only_changes, report_count):
        if not debug:
            return False
        elif report_only_changes is not None:
            return any(
                previous_registers[index] != final_registers[index]
                for index in report_only_changes
            )
        else:
            return step % report_count == 0

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

    def show(self):
        return "\n".join(
            instruction.show(index, self.instruction_pointer_register)
            for index, instruction in enumerate(self.instructions)
        )

    def show_with_names(self):
        return "\n".join(
            " {: >2} : {}".format(
                index,
                instruction.show_with_names(self.instruction_pointer_register)
            )
            for index, instruction in enumerate(self.instructions)
        )


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

    def show_with_names(self, instruction_pointer_register):
        raise NotImplementedError()

    def show(self, index, instruction_pointer_register):
        return " {: >2} : {: <25} # {}".format(
            index,
            self.show_instruction(index, instruction_pointer_register),
            self.show_with_names(instruction_pointer_register),
        )

    def show_instruction(self, index, instruction_pointer_register):
        raise NotImplementedError()


class ThreeOperandsInstructionExtended(
        InstructionExtended, part_a.ThreeOperandsInstruction, ABC):
    def __repr__(self):
        return f"{type(self).__name__}({self.op_a}, {self.op_b}, {self.op_c})"

    def show_with_names(self, instruction_pointer_register):
        op_a, op_b, op_c = (
            self.show_register_with_name(
                register_type, register, instruction_pointer_register)
            for register_type, register in [
                (self.op_type_a, self.op_a),
                (self.op_type_b, self.op_b),
                (self.OP_TYPE_REGISTER, self.op_c),
            ]
        )
        return f"{self.name} {op_a} {op_b} {op_c}"

    def show_register_with_name(self, register_type, register,
                                instruction_pointer_register, index=None):
        if register_type == self.OP_TYPE_REGISTER:
            if register == instruction_pointer_register:
                if index is not None:
                    return str(index)
                else:
                    return "ip"
            else:
                return string.ascii_lowercase[register]
        elif register_type == self.OP_TYPE_IMMEDIATE:
            return str(register)
        elif register_type == self.OP_TYPE_NONE:
            return "!"
        else:
            raise Exception(f"Unknown type {register_type}")


class BinaryInstruction(ThreeOperandsInstructionExtended, ABC):
    operation_display = NotImplemented

    def show_instruction(self, index, instruction_pointer_register):
        op_a, op_b, op_c = (
            self.show_register_with_name(
                register_type, register, instruction_pointer_register,
                index=show_index)
            for register_type, register, show_index in [
                (self.op_type_a, self.op_a, index),
                (self.op_type_b, self.op_b, index),
                (self.OP_TYPE_REGISTER, self.op_c, None),
            ]
        )
        if self.op_c == instruction_pointer_register:
            return f"goto {op_a} {self.operation_display} {op_b} + 1"

        if op_a == op_c:
            return f"{op_c} {self.operation_display}= {op_b}"
        else:
            return f"{op_c} = {op_a} {self.operation_display} {op_b}"


@InstructionExtended.register
class AddIExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.AddI):
    """
    >>> AddIExtended.try_parse("addi 5 16 5")
    AddIExtended(5, 16, 5)
    >>> AddIExtended.try_parse("seti 5 16 5")
    """
    operation_display = "+"


@InstructionExtended.register
class AddRExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.AddR):
    operation_display = "+"


@InstructionExtended.register
class MulIExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.MulI):
    operation_display = "*"


@InstructionExtended.register
class MulRExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.MulR):
    operation_display = "*"


@InstructionExtended.register
class BAnIExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.BAnI):
    operation_display = "&"


@InstructionExtended.register
class BAnRExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.BAnR):
    operation_display = "&"


@InstructionExtended.register
class BOrIExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.BOrI):
    operation_display = "|"


@InstructionExtended.register
class BOrRExtended(
        BinaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.BOrR):
    operation_display = "|"


class UnaryInstruction(ThreeOperandsInstructionExtended, ABC):
    def show_instruction(self, index, instruction_pointer_register):
        op_a, op_c = (
            self.show_register_with_name(
                register_type, register, instruction_pointer_register,
                index=show_index)
            for register_type, register, show_index in [
                (self.op_type_a, self.op_a, index),
                (self.OP_TYPE_REGISTER, self.op_c, None),
            ]
        )
        if self.op_c == instruction_pointer_register:
            return f"goto {op_a} + 1"

        if op_a == op_c:
            return f"noop"
        else:
            return f"{op_c} = {op_a}"


@InstructionExtended.register
class SetIExtended(
        UnaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.SetI):
    pass


@InstructionExtended.register
class SetRExtended(
        UnaryInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.SetR):
    pass


class ConditionalInstruction(ThreeOperandsInstructionExtended, ABC):
    operation_display = NotImplemented

    def show_instruction(self, index, instruction_pointer_register):
        op_a, op_b, op_c = (
            self.show_register_with_name(
                register_type, register, instruction_pointer_register,
                index=show_index)
            for register_type, register, show_index in [
                (self.op_type_a, self.op_a, index),
                (self.op_type_b, self.op_b, index),
                (self.OP_TYPE_REGISTER, self.op_c, None),
            ]
        )
        if self.op_c == instruction_pointer_register:
            return f"goto 2 if {op_a} {self.operation_display} {op_b} else goto 1"

        return f"{op_c} = 1 if {op_a} {self.operation_display} {op_b} else 0"


@InstructionExtended.register
class GTIRExtended(
        ConditionalInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.GTIR):
    operation_display = ">"


@InstructionExtended.register
class GTRIExtended(
        ConditionalInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.GTRI):
    operation_display = ">"


@InstructionExtended.register
class GTRRExtended(
        ConditionalInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.GTRR):
    operation_display = ">"


@InstructionExtended.register
class EqIRExtended(
        ConditionalInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.EqIR):
    operation_display = "=="


@InstructionExtended.register
class EqRIExtended(
        ConditionalInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.EqRI):
    operation_display = "=="


@InstructionExtended.register
class EqRRExtended(
        ConditionalInstruction, ThreeOperandsInstructionExtended,
        InstructionExtended, part_a.EqRR):
    operation_display = "=="


challenge = Challenge()
challenge.main()
