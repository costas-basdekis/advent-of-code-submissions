#!/usr/bin/env python3
import itertools
import re
import string
from abc import ABC
from dataclasses import dataclass
from typing import Union

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3423
        """
        return Program.from_program_text(_input).step_and_get_first_value()


class Program:
    instruction_class = NotImplemented
    registers_class = NotImplemented

    @classmethod
    def from_program_text(cls, program_text):
        lines = program_text.strip().splitlines()
        return cls(list(map(
            cls.instruction_class.from_instruction_text, lines)))

    def __init__(self, instructions):
        self.instructions = instructions

    def step_and_get_first_value(self, registers=None, count=None):
        """
        >>> Program.from_program_text(
        ...     "set a 1\\n"
        ...     "add a 2\\n"
        ...     "mul a a\\n"
        ...     "mod a 5\\n"
        ...     "snd a\\n"
        ...     "set a 0\\n"
        ...     "rcv a\\n"
        ...     "jgz a -1\\n"
        ...     "set a 1\\n"
        ...     "jgz a -2\\n"
        ... ).step_and_get_first_value()
        4
        """
        return next(self.step_and_stream(registers, count), None)

    def step_and_stream(self, registers=None, count=None):
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        if registers is None:
            registers = self.registers_class()
        for _ in steps:
            registers.reset_recovered()
            finished = self.apply(registers)
            if finished:
                break
            if registers.last_recovered is not None:
                yield registers.last_recovered

    def apply(self, registers):
        if self.has_finished(registers):
            return True

        instruction_pointer = registers.instruction_pointer
        instruction = self.instructions[instruction_pointer]
        next_instruction_pointer = instruction.apply(registers)
        if next_instruction_pointer is None:
            next_instruction_pointer = instruction_pointer + 1

        registers.instruction_pointer = next_instruction_pointer

        return False

    def has_finished(self, registers):
        instruction_pointer = registers.instruction_pointer
        return not (0 <= instruction_pointer < len(self.instructions))


class Registers:
    def __init__(self, initial=None, default_value=0):
        self.default_value = default_value
        if initial is None:
            initial = {}
        self.registers = initial
        self.instruction_pointer = 0
        self.last_sound = None
        self.last_recovered = None

    def sound(self, value):
        self.last_sound = value

    def recover(self):
        self.last_recovered = self.last_sound

    def reset_recovered(self):
        self.last_recovered = None

    def __getitem__(self, item):
        self.check_is_register(item)
        return self.registers.get(item, self.default_value)

    def __setitem__(self, key, value):
        self.check_is_register(key)
        self.check_is_value(value)
        self.registers[key] = value

    @classmethod
    def parse_rvalue(cls, rvalue_text):
        if cls.is_register(rvalue_text):
            register = rvalue_text
            return register
        try:
            value = int(rvalue_text)
        except ValueError:
            raise Exception(
                f"Expected a register or a value, not '{rvalue_text}'")

        return value

    def resolve(self, register_or_value):
        if self.is_register(register_or_value):
            register = register_or_value
            return self[register]
        elif self.is_value(register_or_value):
            value = register_or_value
            return value
        else:
            raise Exception(
                f"Expected a register or a value, not {register_or_value}")

    def check_is_register(self, item):
        if not self.is_register(item):
            raise Exception(
                f"Expected register to be a single lowercase letter, not "
                f"{item}")

    @classmethod
    def is_register(cls, item):
        if not isinstance(item, str):
            return False
        if len(item) != 1:
            return False
        return item in string.ascii_lowercase

    def check_is_value(self, value):
        if not self.is_value(value):
            raise Exception(f"Expected value to be an int, not {value}")

    @classmethod
    def is_value(cls, value):
        is_value = isinstance(value, int)
        return is_value


Program.registers_class = Registers


class Instruction:
    name = NotImplemented

    instruction_classes = {}

    @classmethod
    def register(cls, instruction_class, override=False):
        name = instruction_class.name
        instruction_class_name = instruction_class.__name__
        if name is NotImplemented:
            raise Exception(f"{instruction_class_name} didn't set a 'name'")
        if name in cls.instruction_classes and not override:
            raise Exception(
                f"{instruction_class_name} tried to override '{name}' which "
                f"was registered by {cls.instruction_classes[name]}")
        cls.instruction_classes[name] = instruction_class

        return instruction_class

    @classmethod
    def from_instruction_text(cls, instruction_text):
        for instruction_class in cls.instruction_classes.values():
            instruction = instruction_class.try_parse(instruction_text)
            if instruction:
                break
        else:
            raise Exception(f"Could not parse '{instruction_text}'")

        return instruction

    @classmethod
    def try_parse(cls, instruction_text):
        raise NotImplementedError()

    def apply(self, registers):
        raise NotImplementedError()


Program.instruction_class = Instruction


@dataclass(init=False)
class RValueInstruction(Instruction, ABC):
    rvalue: Union[str, int]
    regex = NotImplemented

    @classmethod
    def make_regex(cls, name):
        return re.compile(rf"^{name} ([a-z]|-?\d+)$")

    @classmethod
    def try_parse(cls, instruction_text):
        match = cls.regex.match(instruction_text)
        if not match:
            return None
        rvalue_str, = match.groups()

        return cls(Registers.parse_rvalue(rvalue_str))

    def __init__(self, rvalue):
        self.rvalue = rvalue


@Instruction.register
class Sound(RValueInstruction):
    name = 'snd'

    regex = RValueInstruction.make_regex(name)

    def apply(self, registers):
        registers.sound(registers.resolve(self.rvalue))


@dataclass(init=False)
class RegisterRValueInstruction(Instruction, ABC):
    register: str
    rvalue: Union[str, int]

    regex = NotImplemented

    @classmethod
    def make_regex(cls, name):
        return re.compile(rf"^{name} ([a-z]) ([a-z]|-?\d+)$")

    @classmethod
    def try_parse(cls, instruction_text):
        match = cls.regex.match(instruction_text)
        if not match:
            return None
        register, rvalue_str = match.groups()

        return cls(register, Registers.parse_rvalue(rvalue_str))

    def __init__(self, register, rvalue):
        self.register = register
        self.rvalue = rvalue


@Instruction.register
class SetRegister(RegisterRValueInstruction):
    name = 'set'

    regex = RegisterRValueInstruction.make_regex(name)

    def apply(self, registers):
        registers[self.register] = registers.resolve(self.rvalue)


@Instruction.register
class Add(RegisterRValueInstruction):
    name = 'add'

    regex = RegisterRValueInstruction.make_regex(name)

    def apply(self, registers):
        registers[self.register] += registers.resolve(self.rvalue)


@Instruction.register
class Mul(RegisterRValueInstruction):
    name = 'mul'

    regex = RegisterRValueInstruction.make_regex(name)

    def apply(self, registers):
        registers[self.register] *= registers.resolve(self.rvalue)


@Instruction.register
class Mod(RegisterRValueInstruction):
    name = 'mod'

    regex = RegisterRValueInstruction.make_regex(name)

    def apply(self, registers):
        registers[self.register] %= registers.resolve(self.rvalue)


@dataclass(init=False)
class RegisterInstruction(Instruction, ABC):
    register: str
    regex = NotImplemented

    @classmethod
    def make_regex(cls, name):
        return re.compile(rf"^{name} ([a-z])$")

    @classmethod
    def try_parse(cls, instruction_text):
        match = cls.regex.match(instruction_text)
        if not match:
            return None
        register, = match.groups()

        return cls(register)

    def __init__(self, register):
        self.register = register


@Instruction.register
class Recover(RegisterInstruction):
    name = 'rcv'

    regex = RegisterInstruction.make_regex(name)

    def apply(self, registers):
        if registers[self.register]:
            registers.recover()


@dataclass(init=False)
class RvalueRValueInstruction(Instruction, ABC):
    rvalue_a: Union[str, int]
    rvalue_b: Union[str, int]

    regex = NotImplemented

    @classmethod
    def make_regex(cls, name):
        return re.compile(rf"^{name} ([a-z]|-?\d+) ([a-z]|-?\d+)$")

    @classmethod
    def try_parse(cls, instruction_text):
        match = cls.regex.match(instruction_text)
        if not match:
            return None
        rvalue_a_str, rvalue_b_str = match.groups()

        return cls(
            Registers.parse_rvalue(rvalue_a_str),
            Registers.parse_rvalue(rvalue_b_str),
        )

    def __init__(self, rvalue_a, rvalue_b):
        self.rvalue_a = rvalue_a
        self.rvalue_b = rvalue_b


@Instruction.register
class Jgz(RvalueRValueInstruction):
    name = 'jgz'

    regex = RvalueRValueInstruction.make_regex(name)

    def apply(self, registers):
        if registers.resolve(self.rvalue_a) > 0:
            next_instruction_pointer = \
                registers.instruction_pointer + registers.resolve(self.rvalue_b)
        else:
            next_instruction_pointer = None

        return next_instruction_pointer


challenge = Challenge()
challenge.main()
