#!/usr/bin/env python3
import doctest
import re

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    9879607673316
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return Program.from_program_text(_input).run_and_get_memory_checksum()


class Program:
    instruction_class = NotImplemented

    @classmethod
    def from_program_text(cls, program_text):
        """
        >>> Program.from_program_text(
        ...     "mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X\\n"
        ...     "mem[8] = 11\\n"
        ...     "mem[7] = 101\\n"
        ...     "mem[8] = 0\\n"
        ... ).instructions
        [Bitmask(66, 64), Write(8, 11), Write(7, 101), Write(8, 0)]
        """
        non_empty_lines = filter(None, program_text.splitlines())
        return cls(list(map(cls.instruction_class.parse, non_empty_lines)))

    def __init__(self, instructions):
        self.instructions = instructions

    def run_and_get_memory_checksum(self, memory=None):
        """
        >>> Program.from_program_text(
        ...     "mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X\\n"
        ...     "mem[8] = 11\\n"
        ...     "mem[7] = 101\\n"
        ...     "mem[8] = 0\\n"
        ... ).run_and_get_memory_checksum()
        165
        """
        memory = self.run(memory)
        return self.get_memory_checksum(memory)

    def run(self, memory=None):
        """
        >>> Program([]).run()
        {'bitmask': 0, 'override': 0, 'values': {}}
        >>> Program.from_program_text(
        ...     "mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X\\n"
        ...     "mem[8] = 11\\n"
        ...     "mem[7] = 101\\n"
        ...     "mem[8] = 0\\n"
        ... ).run()
        {'bitmask': 66, 'override': 64, 'values': {8: 64, 7: 101}}
        """
        if memory is None:
            memory = self.get_default_memory()

        for instruction in self.instructions:
            instruction.step(memory)

        return memory

    def get_default_memory(self):
        return {'bitmask': 0, 'override': 0, 'values': {}}

    def get_memory_checksum(self, memory):
        """
        >>> Program([]).get_memory_checksum(
        ...     {'bitmask': 66, 'override': 64, 'values': {8: 64, 7: 101}})
        165
        """
        return sum(memory['values'].values())


class Instruction:
    name = NotImplemented

    instruction_classes = {}

    @classmethod
    def register(cls, instruction_class, override=False):
        if instruction_class.name is NotImplemented:
            raise Exception(
                f"Instruction {instruction_class.__name__} didn't specify "
                f"name")
        if instruction_class.name in cls.instruction_classes and not override:
            raise Exception(
                f"Instruction {instruction_class.__name__} tried to "
                f"implicitly override {instruction_class.name}, that was "
                f"already defined by "
                f"{cls.instruction_classes[instruction_class.name].__name__}")
        cls.instruction_classes[instruction_class.name] = instruction_class

        return instruction_class

    @classmethod
    def parse(cls, instruction_text):
        for instruction_class in cls.instruction_classes.values():
            instruction = instruction_class.try_parse(instruction_text)
            if instruction:
                return instruction

        raise Exception(f"Could not parse '{instruction_text}'")

    @classmethod
    def try_parse(cls, instruction_text):
        raise NotImplementedError()

    def step(self, memory):
        raise NotImplementedError()


Program.instruction_class = Instruction


@Instruction.register
class Write(Instruction):
    name = 'write'
    re_write = re.compile(r"^mem\[(\d+)] = (\d+)$")

    @classmethod
    def try_parse(cls, instruction_text):
        """
        >>> Write\\
        ...     .try_parse("mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X")
        >>> Write\\
        ...     .try_parse("mem[8] = 11")
        Write(8, 11)
        """
        match = cls.re_write.match(instruction_text)
        if not match:
            return None
        address_str, value_str = match.groups()
        return cls(int(address_str), int(value_str))

    def __init__(self, address, value):
        self.address = address
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.address}, {self.value})"

    def step(self, memory):
        """
        >>> Write(8, 11).step({'bitmask': 0, 'override': 0, 'values': {}})
        {'bitmask': 0, 'override': 0, 'values': {8: 11}}
        >>> Write(8, 11).step({'bitmask': 66, 'override': 64, 'values': {}})
        {'bitmask': 66, 'override': 64, 'values': {8: 73}}
        >>> Write(8, 127).step({'bitmask': 66, 'override': 64, 'values': {}})
        {'bitmask': 66, 'override': 64, 'values': {8: 125}}
        >>> Write(8, 11)\\
        ...     .step({'bitmask': 0, 'override': 0, 'values': {8: 10, 9: 32}})
        {'bitmask': 0, 'override': 0, 'values': {8: 11, 9: 32}}
        >>> Write(8, 0)\\
        ...     .step({'bitmask': 0, 'override': 0, 'values': {8: 10, 9: 32}})
        {'bitmask': 0, 'override': 0, 'values': {9: 32}}
        """
        bitmask = memory['bitmask']
        override = memory['override']
        masked_value = (self.value & ~bitmask) | override
        memory['values'][self.address] = masked_value
        if masked_value == 0:
            del memory['values'][self.address]

        return memory


@Instruction.register
class Bitmask(Instruction):
    name = 'bitmask'
    re_bitmask = re.compile(r"^mask = ([01X]{36})$")

    @classmethod
    def try_parse(cls, instruction_text):
        """
        >>> Bitmask\\
        ...     .try_parse("mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X")
        Bitmask(66, 64)
        >>> Bitmask\\
        ...     .try_parse("mem[8] = 11")
        """
        match = cls.re_bitmask.match(instruction_text)
        if not match:
            return None
        bitmask_str, = match.groups()
        bitmask = int(bitmask_str.replace('0', '1').replace('X', '0'), 2)
        override = int(bitmask_str.replace('X', '0'), 2)

        return cls(bitmask, override)

    def __init__(self, bitmask, override):
        self.bitmask = bitmask
        self.override = override

    def __repr__(self):
        return f"{type(self).__name__}({self.bitmask}, {self.override})"

    def step(self, memory):
        """
        >>> Bitmask(66, 64)\\
        ...     .step({'bitmask': 0, 'override': 0, 'values': {8: 11}})
        {'bitmask': 66, 'override': 64, 'values': {8: 11}}
        """
        memory['bitmask'] = self.bitmask
        memory['override'] = self.override

        return memory


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
