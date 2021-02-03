#!/usr/bin/env python3
import itertools
from abc import ABC

import utils
from year_2017.day_18.part_a import RegisterRValueInstruction, \
    RvalueRValueInstruction, Mul
from year_2017.day_18.part_b import ProgramExtended, InstructionExtended


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3969
        """
        return ProgramExtendedTwice.from_program_text(_input)\
            .step_and_count_instructions().get(Mul, 0)


class ProgramExtendedTwice(ProgramExtended):
    def step_and_count_instructions(self, registers=None, count=None):
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        if registers is None:
            registers = self.registers_class()
        instruction_counts = {}
        for _ in steps:
            if self.has_finished(registers):
                break
            instruction_type = \
                type(self.instructions[registers.instruction_pointer])
            instruction_counts.setdefault(instruction_type, 0)
            instruction_counts[instruction_type] += 1
            finished = self.apply(registers)
            if finished:
                break

        return instruction_counts


class InstructionExtendedTwice(InstructionExtended, ABC):
    instruction_classes = dict(InstructionExtended.instruction_classes)


ProgramExtendedTwice.instruction_class = InstructionExtendedTwice


@InstructionExtendedTwice.register
class Sub(InstructionExtendedTwice, RegisterRValueInstruction):
    name = 'sub'

    regex = RegisterRValueInstruction.make_regex(name)

    def apply(self, registers):
        registers[self.register] -= registers.resolve(self.rvalue)


@InstructionExtendedTwice.register
class Jgz(RvalueRValueInstruction):
    name = 'jnz'

    regex = RvalueRValueInstruction.make_regex(name)

    def apply(self, registers):
        if registers.resolve(self.rvalue_a) != 0:
            next_instruction_pointer = \
                registers.instruction_pointer + registers.resolve(self.rvalue_b)
        else:
            next_instruction_pointer = None

        return next_instruction_pointer


Challenge.main()
challenge = Challenge()
