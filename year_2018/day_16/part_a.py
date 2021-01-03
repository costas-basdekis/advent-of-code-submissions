#!/usr/bin/env python3
import re
from abc import ABC
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        636
        """

        return SampleSet.from_samples_and_program_text(_input)\
            .get_sample_count_with_3_or_more_candidates()


class SampleSet:
    sample_class = NotImplemented

    @classmethod
    def from_samples_and_program_text(cls, samples_and_program_text):
        """
        >>> SampleSet.from_samples_and_program_text(
        ...     "Before: [2, 3, 0, 2]\\n"
        ...     "5 2 3 2\\n"
        ...     "After:  [2, 3, 1, 2]\\n"
        ...     "\\n"
        ...     "Before: [2, 0, 3, 0]\\n"
        ...     "13 0 3 1\\n"
        ...     "After:  [2, 1, 3, 0]\\n"
        ...     "\\n"
        ...     "\\n"
        ...     "\\n"
        ...     "3 3 0 1\\n"
        ...     "0 2 0 3\\n"
        ... ).samples
        [Sample(before=(2, 3, 0, 2), instruction=(5, 2, 3, 2), after=(2, 3, 1, 2)), \
Sample(before=(2, 0, 3, 0), instruction=(13, 0, 3, 1), after=(2, 1, 3, 0))]
        """
        samples_text, _ = samples_and_program_text.split('\n' * 4)
        return cls.from_samples_text(samples_text)

    @classmethod
    def from_samples_text(cls, samples_text):
        """
        >>> SampleSet.from_samples_text(
        ...     "Before: [2, 3, 0, 2]\\n"
        ...     "5 2 3 2\\n"
        ...     "After:  [2, 3, 1, 2]\\n"
        ...     "\\n"
        ...     "Before: [2, 0, 3, 0]\\n"
        ...     "13 0 3 1\\n"
        ...     "After:  [2, 1, 3, 0]\\n"
        ... ).samples
        [Sample(before=(2, 3, 0, 2), instruction=(5, 2, 3, 2), after=(2, 3, 1, 2)), \
Sample(before=(2, 0, 3, 0), instruction=(13, 0, 3, 1), after=(2, 1, 3, 0))]
        """
        sample_texts = filter(None, samples_text.strip().split('\n\n'))
        return cls(list(map(cls.sample_class.from_sample_text, sample_texts)))

    def __init__(self, samples):
        self.samples = samples

    def get_sample_count_with_3_or_more_candidates(self):
        """
        >>> SampleSet.from_samples_text(
        ...     "Before: [2, 3, 0, 2]\\n"
        ...     "5 2 3 2\\n"
        ...     "After:  [2, 3, 1, 2]\\n"
        ...     "\\n"
        ...     "Before: [2, 0, 3, 0]\\n"
        ...     "13 0 3 1\\n"
        ...     "After:  [2, 1, 3, 0]\\n"
        ...     "\\n"
        ...     "Before: [3, 2, 1, 1]\\n"
        ...     "9 2 1 2\\n"
        ...     "After:  [3, 2, 2, 1]\\n"
        ... ).get_sample_count_with_3_or_more_candidates()
        1
        """
        return sum(
            1
            for sample in self.samples
            if len(sample.get_instruction_candidates()) >= 3
        )

    def get_sample_candidates_counts(self):
        import itertools
        return {
            candidates_counts: len(list(values))
            for candidates_counts, values in itertools.groupby(sorted(
                len(sample.get_instruction_candidates())
                for sample in self.samples
            ))
        }


class Sample(namedtuple("Sample", ("before", "instruction", "after"))):
    re_sample = re.compile((
        r"^"
        r"Before: \[(\d+), (\d+), (\d+), (\d+)]\n"
        r"(\d+) (\d+) (\d+) (\d+)\n"
        r"After:  \[(\d+), (\d+), (\d+), (\d+)]"
        r"$"
    ), re.MULTILINE)

    @classmethod
    def from_sample_text(cls, sample_text):
        """
        >>> Sample.from_sample_text(
        ...     "Before: [3, 2, 1, 1]\\n"
        ...     "9 2 1 2\\n"
        ...     "After:  [3, 2, 2, 1]\\n"
        ... )
        Sample(before=(3, 2, 1, 1), instruction=(9, 2, 1, 2), after=(3, 2, 2, 1))
        """
        match = cls.re_sample.match(sample_text.strip())
        if not match:
            raise Exception(f"Could not parse {sample_text}")
        numbers = tuple(map(int, match.groups()))
        return cls(numbers[:4], numbers[4:8], numbers[8:])

    @property
    def instruction_operands(self):
        return self.instruction[1:]

    def get_instruction_candidates(self):
        """
        >>> sorted(ic.name for ic in Sample.from_sample_text(
        ...     "Before: [3, 2, 1, 1]\\n"
        ...     "9 2 1 2\\n"
        ...     "After:  [3, 2, 2, 1]\\n"
        ... ).get_instruction_candidates())
        ['addi', 'mulr', 'seti']
        """
        return [
            instruction_class
            for instruction_class in Instruction.instruction_classes.values()
            if instruction_class(*self.instruction_operands)
            .step(self.before)
            == self.after
        ]


SampleSet.sample_class = Sample


class InstructionException(Exception):
    pass


class Instruction:
    name = NotImplemented

    instruction_classes = {}

    @classmethod
    def register(cls, instruction_class, override=False):
        if instruction_class.name is NotImplemented:
            raise Exception(
                f"Instruction class {instruction_class.__name__} did not set "
                f"name")
        if instruction_class.name in cls.instruction_classes and not override:
            raise Exception(
                f"Tried to implicitly override '{instruction_class.name}' "
                f"with {instruction_class.__name__} - previous was "
                f"{cls.instruction_classes[instruction_class.name].__name__}")
        cls.instruction_classes[instruction_class.name] = instruction_class
        return instruction_class

    OP_TYPE_IMMEDIATE = 'immediate'
    OP_TYPE_REGISTER = 'register'
    OP_TYPE_NONE = 'none'

    def step(self, registers):
        raise NotImplementedError()

    def try_step(self, registers):
        try:
            return self.step(registers)
        except InstructionException:
            return None

    def get_value(self, op, op_type, registers):
        if op_type == self.OP_TYPE_IMMEDIATE:
            value = op
            if not isinstance(value, int):
                raise Exception(f"Only integers are allowed, not '{value}'")
            return value
        elif op_type == self.OP_TYPE_REGISTER:
            if not (0 <= op < len(registers)):
                raise InstructionException(
                    f"Requested non existing register {op}: only "
                    f"{len(registers)} exist")
            value = registers[op]
            if not isinstance(value, int):
                raise Exception(f"Only integers are allowed, not '{value}'")
            return value
        elif op_type == self.OP_TYPE_NONE:
            return None
        else:
            raise Exception(f"Unknown register type '{op_type}'")

    def set_value(self, target, value, registers):
        if not (0 <= target < len(registers)):
            raise InstructionException(
                f"Requested non existing register {target}: only "
                f"{len(registers)} exist")
        if not isinstance(value, int):
            raise Exception(f"Only integers are allowed, not '{value}'")
        return registers[:target] + (value,) + registers[target + 1:]


class ThreeOperandsInstruction(Instruction, ABC):
    op_type_a = NotImplemented
    op_type_b = NotImplemented

    def __init__(self, op_a, op_b, op_c):
        self.op_a = op_a
        self.op_b = op_b
        self.op_c = op_c

    def step(self, registers):
        value_a = self.get_value(self.op_a, self.op_type_a, registers)
        value_b = self.get_value(self.op_b, self.op_type_b, registers)
        value_c = self.do_operation(value_a, value_b)
        return self.set_value(self.op_c, value_c, registers)

    def do_operation(self, lhs, rhs):
        raise NotImplementedError()


class AddInstruction(ThreeOperandsInstruction):
    op_type_a = Instruction.OP_TYPE_REGISTER

    do_operation = staticmethod(int.__add__)


@Instruction.register
class AddI(AddInstruction):
    """
    >>> AddI(0, 5, 3).step((10, None, None, None))
    (10, None, None, 15)
    """
    name = 'addi'
    op_type_b = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class AddR(AddInstruction):
    """
    >>> AddR(0, 2, 3).step((10, None, 12, None))
    (10, None, 12, 22)
    """
    name = 'addr'
    op_type_b = Instruction.OP_TYPE_REGISTER


class MultiplyInstruction(ThreeOperandsInstruction):
    op_type_a = Instruction.OP_TYPE_REGISTER

    do_operation = staticmethod(int.__mul__)


@Instruction.register
class MulI(MultiplyInstruction):
    """
    >>> MulI(0, 5, 3).step((10, None, None, None))
    (10, None, None, 50)
    """
    name = 'muli'
    op_type_b = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class MulR(MultiplyInstruction):
    """
    >>> MulR(0, 2, 3).step((10, None, 12, None))
    (10, None, 12, 120)
    """
    name = 'mulr'
    op_type_b = Instruction.OP_TYPE_REGISTER


class BitwiseAndInstruction(ThreeOperandsInstruction):
    op_type_a = Instruction.OP_TYPE_REGISTER

    do_operation = staticmethod(int.__and__)


@Instruction.register
class BAnI(BitwiseAndInstruction):
    """
    >>> BAnI(0, 5, 3).step((10, None, None, None))
    (10, None, None, 0)
    >>> BAnI(0, 8, 3).step((10, None, None, None))
    (10, None, None, 8)
    >>> BAnI(0, 10, 3).step((10, None, None, None))
    (10, None, None, 10)
    >>> BAnI(0, 14, 3).step((10, None, None, None))
    (10, None, None, 10)
    """
    name = 'bani'
    op_type_b = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class BAnR(BitwiseAndInstruction):
    """
    >>> BAnR(0, 2, 3).step((10, None, 5, None))
    (10, None, 5, 0)
    >>> BAnR(0, 2, 3).step((10, None, 8, None))
    (10, None, 8, 8)
    >>> BAnR(0, 2, 3).step((10, None, 10, None))
    (10, None, 10, 10)
    >>> BAnR(0, 2, 3).step((10, None, 14, None))
    (10, None, 14, 10)
    """
    name = 'banr'
    op_type_b = Instruction.OP_TYPE_REGISTER


class BitwiseOrInstruction(ThreeOperandsInstruction):
    op_type_a = Instruction.OP_TYPE_REGISTER

    do_operation = staticmethod(int.__or__)


@Instruction.register
class BOrI(BitwiseOrInstruction):
    """
    >>> BOrI(0, 5, 3).step((10, None, None, None))
    (10, None, None, 15)
    >>> BOrI(0, 10, 3).step((10, None, None, None))
    (10, None, None, 10)
    >>> BOrI(0, 0, 3).step((10, None, None, None))
    (10, None, None, 10)
    >>> BOrI(0, 9, 3).step((10, None, None, None))
    (10, None, None, 11)
    """
    name = 'bori'
    op_type_b = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class BOrR(BitwiseOrInstruction):
    """
    >>> BOrR(0, 2, 3).step((10, None, 5, None))
    (10, None, 5, 15)
    >>> BOrR(0, 2, 3).step((10, None, 10, None))
    (10, None, 10, 10)
    >>> BOrR(0, 2, 3).step((10, None, 0, None))
    (10, None, 0, 10)
    >>> BOrR(0, 2, 3).step((10, None, 9, None))
    (10, None, 9, 11)
    """
    name = 'borr'
    op_type_b = Instruction.OP_TYPE_REGISTER


class AssignmentInstruction(ThreeOperandsInstruction):
    op_type_b = Instruction.OP_TYPE_NONE

    def do_operation(self, lhs, rhs):
        return lhs


@Instruction.register
class SetI(AssignmentInstruction):
    """
    >>> SetI(0, None, 3).step((None, None, None, None))
    (None, None, None, 0)
    >>> SetI(10, None, 3).step((None, None, None, None))
    (None, None, None, 10)
    >>> SetI(33, None, 3).step((None, None, None, None))
    (None, None, None, 33)
    """
    name = 'seti'
    op_type_a = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class SetR(AssignmentInstruction):
    """
    >>> SetR(0, None, 3).step((0, None, None, None))
    (0, None, None, 0)
    >>> SetR(0, None, 3).step((10, None, None, None))
    (10, None, None, 10)
    >>> SetR(0, None, 3).step((33, None, None, None))
    (33, None, None, 33)
    """
    name = 'setr'
    op_type_a = Instruction.OP_TYPE_REGISTER


class GreaterThanInstruction(ThreeOperandsInstruction):
    def do_operation(self, lhs, rhs):
        if lhs > rhs:
            return 1
        else:
            return 0


@Instruction.register
class GTIR(GreaterThanInstruction):
    """
    >>> GTIR(0, 0, 3).step((10, None, None, None))
    (10, None, None, 0)
    >>> GTIR(10, 0, 3).step((10, None, None, None))
    (10, None, None, 0)
    >>> GTIR(20, 0, 3).step((10, None, None, None))
    (10, None, None, 1)
    """
    name = 'gtir'
    op_type_a = Instruction.OP_TYPE_IMMEDIATE
    op_type_b = Instruction.OP_TYPE_REGISTER


@Instruction.register
class GTRI(GreaterThanInstruction):
    """
    >>> GTRI(0, 0, 3).step((10, None, None, None))
    (10, None, None, 1)
    >>> GTRI(0, 10, 3).step((10, None, None, None))
    (10, None, None, 0)
    >>> GTRI(0, 20, 3).step((10, None, None, None))
    (10, None, None, 0)
    """
    name = 'gtri'
    op_type_a = Instruction.OP_TYPE_REGISTER
    op_type_b = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class GTRR(GreaterThanInstruction):
    """
    >>> GTRR(0, 1, 3).step((10, 0, None, None))
    (10, 0, None, 1)
    >>> GTRR(0, 1, 3).step((10, 10, None, None))
    (10, 10, None, 0)
    >>> GTRR(0, 1, 3).step((10, 20, None, None))
    (10, 20, None, 0)
    """
    name = 'gtrr'
    op_type_a = Instruction.OP_TYPE_REGISTER
    op_type_b = Instruction.OP_TYPE_REGISTER


class EqualToInstruction(ThreeOperandsInstruction):
    def do_operation(self, lhs, rhs):
        if lhs == rhs:
            return 1
        else:
            return 0


@Instruction.register
class EqIR(EqualToInstruction):
    """
    >>> EqIR(0, 0, 3).step((10, None, None, None))
    (10, None, None, 0)
    >>> EqIR(10, 0, 3).step((10, None, None, None))
    (10, None, None, 1)
    >>> EqIR(20, 0, 3).step((10, None, None, None))
    (10, None, None, 0)
    """
    name = 'eqir'
    op_type_a = Instruction.OP_TYPE_IMMEDIATE
    op_type_b = Instruction.OP_TYPE_REGISTER


@Instruction.register
class EqRI(EqualToInstruction):
    """
    >>> EqRI(0, 0, 3).step((10, None, None, None))
    (10, None, None, 0)
    >>> EqRI(0, 10, 3).step((10, None, None, None))
    (10, None, None, 1)
    >>> EqRI(0, 20, 3).step((10, None, None, None))
    (10, None, None, 0)
    """
    name = 'eqri'
    op_type_a = Instruction.OP_TYPE_REGISTER
    op_type_b = Instruction.OP_TYPE_IMMEDIATE


@Instruction.register
class EqRR(EqualToInstruction):
    """
    >>> EqRR(0, 1, 3).step((10, 0, None, None))
    (10, 0, None, 0)
    >>> EqRR(0, 1, 3).step((10, 10, None, None))
    (10, 10, None, 1)
    >>> EqRR(0, 1, 3).step((10, 20, None, None))
    (10, 20, None, 0)
    """
    name = 'eqrr'
    op_type_a = Instruction.OP_TYPE_REGISTER
    op_type_b = Instruction.OP_TYPE_REGISTER


challenge = Challenge()
challenge.main()
