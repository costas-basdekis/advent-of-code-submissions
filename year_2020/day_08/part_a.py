#!/usr/bin/env python3
import doctest
from abc import ABC

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    1446
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    runner = Program.from_program_text(_input).to_runner()
    runner.run()

    return runner.value


class ProgramRunner:
    @classmethod
    def from_program(cls, program):
        instruction_counter = 0
        value = 0
        return cls(program, instruction_counter, value)

    def __init__(self, program, instruction_counter, value,
                 visited_instruction_indexes=None):
        self.program = program
        self.instruction_counter = instruction_counter
        self.value = value
        if visited_instruction_indexes is None:
            visited_instruction_indexes = set()
        self.visited_instruction_indexes = visited_instruction_indexes

    def __repr__(self):
        return f"{type(self).__name__}({self.instruction_counter}, {self.value})"

    def run(self, prevent_infinite_loop=True):
        """
        >>> Program.from_program_text(
        ...     "nop +0\\n"
        ...     "acc +1\\n"
        ...     "jmp +4\\n"
        ...     "acc +3\\n"
        ...     "jmp -3\\n"
        ...     "acc -99\\n"
        ...     "acc +1\\n"
        ...     "jmp -4\\n"
        ...     "acc +6\\n"
        ... ).to_runner().run()
        (True, 5)
        """
        while True:
            if self.should_exit(prevent_infinite_loop=prevent_infinite_loop):
                return self.get_run_return_value()
            self.visited_instruction_indexes.add(self.instruction_counter)
            self.run_instruction()

    def get_run_return_value(self):
        return True, self.value

    def should_exit(self, prevent_infinite_loop=True):
        return prevent_infinite_loop and self.is_in_infinite_loop()

    def is_in_infinite_loop(self):
        return (
            self.instruction_counter
            in self.visited_instruction_indexes
        )

    def run_instruction(self):
        instruction = self.program.instructions[self.instruction_counter]
        self.instruction_counter, self.value = instruction.run(
            self.instruction_counter, self.value)
        return self


class Program:
    @classmethod
    def from_program_text(cls, program_text):
        """
        >>> Program.from_program_text(
        ...     "nop +0\\n"
        ...     "acc +1\\n"
        ...     "jmp +4\\n"
        ...     "acc +3\\n"
        ...     "jmp -3\\n"
        ...     "acc -99\\n"
        ...     "acc +1\\n"
        ...     "jmp -4\\n"
        ...     "acc +6\\n"
        ... )
        Program([Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1), Jmp(-4), Acc(6)])
        """
        non_empty_lines = filter(None, program_text.splitlines())

        return cls(list(map(
            Instruction.from_instruction_text, non_empty_lines)))

    def __init__(self, instructions):
        self.instructions = instructions

    def __repr__(self):
        return f"{type(self).__name__}({self.instructions})"

    def to_runner(self, runner_class=ProgramRunner):
        return runner_class.from_program(self)


class Instruction:
    key = NotImplemented

    instruction_classes = {}

    @classmethod
    def register(cls, instruction_class):
        cls.instruction_classes[instruction_class.key] = instruction_class

        return instruction_class

    @classmethod
    def from_instruction_text(cls, instruction_text):
        """
        >>> Instruction.from_instruction_text("nop +0")
        Nop(0)
        >>> Instruction.from_instruction_text("acc +1")
        Acc(1)
        >>> Instruction.from_instruction_text("jmp -4")
        Jmp(-4)
        """
        for instruction_class in cls.instruction_classes.values():
            instruction = instruction_class\
                .try_from_instruction_text(instruction_text)
            if instruction:
                return instruction

        raise Exception(f"Could not parse '{instruction_text}'")

    @classmethod
    def try_from_instruction_text(cls, instruction_text):
        raise NotImplementedError()

    def run(self, instruction_counter, value):
        raise NotImplementedError()


class InstructionWithOneIntArgument(Instruction, ABC):
    name = NotImplemented

    @classmethod
    def try_from_instruction_text(cls, instruction_text):
        prefix = f"{cls.name} "
        if not instruction_text.startswith(prefix):
            return None

        argument_str = instruction_text[len(prefix):]
        argument = int(argument_str)
        return cls(argument)

    def __init__(self, argument):
        self.argument = argument

    def __repr__(self):
        return f"{type(self).__name__}({self.argument})"


@Instruction.register
class Acc(InstructionWithOneIntArgument):
    key = "acc"
    name = "acc"

    def run(self, instruction_counter, value):
        """
        >>> Acc(5).run(0, 0)
        (1, 5)
        >>> Acc(5).run(0, -5)
        (1, 0)
        >>> Acc(5).run(0, -10)
        (1, -5)
        """
        instruction_counter += 1
        value += self.argument

        return instruction_counter, value


@Instruction.register
class Jmp(InstructionWithOneIntArgument):
    key = "jmp"
    name = "jmp"

    def run(self, instruction_counter, value):
        instruction_counter += self.argument

        return instruction_counter, value


@Instruction.register
class Nop(InstructionWithOneIntArgument):
    key = "nop"
    name = "nop"

    def run(self, instruction_counter, value):
        instruction_counter += 1

        return instruction_counter, value


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
