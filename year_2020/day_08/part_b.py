#!/usr/bin/env python3
import utils

from year_2020.day_08 import part_a
from year_2020.day_08.part_a import Acc, Jmp, Nop


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1403
        """
        infinite_loop, value = DeCorruption()\
            .de_corrupt_program(part_a.Program.from_program_text(_input))\
            .to_runner(ProgramRunner2)\
            .run()
        if infinite_loop:
            raise Exception("Got infinite loop")

        return value


class DeCorruption:
    def de_corrupt_program(self, program):
        """
        >>> DeCorruption().de_corrupt_program(part_a.Program.from_program_text(
        ...     "nop +0\\n"
        ...     "acc +1\\n"
        ...     "jmp +4\\n"
        ...     "acc +3\\n"
        ...     "jmp -3\\n"
        ...     "acc -99\\n"
        ...     "acc +1\\n"
        ...     "jmp -4\\n"
        ...     "acc +6\\n"
        ... ))
        Program([Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1), Nop(-4), Acc(6)])
        """
        for de_corrupted_program in self.get_de_corruption_attempts(program):
            if self.is_program_de_corrupted(de_corrupted_program):
                return de_corrupted_program

        raise Exception("Could not de-corrupt")

    def get_de_corruption_attempts(self, program):
        """
        >>> list(DeCorruption().get_de_corruption_attempts(part_a.Program([
        ...     Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1),
        ...     Jmp(-4), Acc(6)])))[-1]
        Program([Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1), Nop(-4), Acc(6)])
        """
        corruptible_indexes = self.get_corruptible_indexes(program)
        if not corruptible_indexes:
            yield program
            return

        for index in corruptible_indexes:
            yield self.de_corrupt_program_at_index(program, index)

    def is_program_de_corrupted(self, program):
        """
        >>> DeCorruption().is_program_de_corrupted(part_a.Program([
        ...     Jmp(0), Acc(1), Nop(4), Acc(3), Nop(-3), Acc(-99), Acc(1),
        ...     Nop(-4), Acc(6)]))
        False
        >>> DeCorruption().is_program_de_corrupted(part_a.Program([
        ...     Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1),
        ...     Jmp(-4), Acc(6)]))
        False
        >>> DeCorruption().is_program_de_corrupted(part_a.Program([
        ...     Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1),
        ...     Nop(-4), Acc(6)]))
        True
        """
        infinite_loop, _ = ProgramRunner2.from_program(program).run()
        return not infinite_loop

    def de_corrupt_program_at_index(self, program, index):
        """
        >>> DeCorruption().de_corrupt_program_at_index(part_a.Program.from_program_text(
        ...     "nop +0\\n"
        ...     "acc +1\\n"
        ...     "jmp +4\\n"
        ...     "acc +3\\n"
        ...     "jmp -3\\n"
        ...     "acc -99\\n"
        ...     "acc +1\\n"
        ...     "jmp -4\\n"
        ...     "acc +6\\n"
        ... ), 7)
        Program([Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1), Nop(-4), Acc(6)])
        """
        de_corrupted_instructions = list(program.instructions)
        de_corrupted_instructions[index] = self\
            .de_corrupt_instruction(de_corrupted_instructions[index])
        program_class = type(program)
        de_corrupted_program = program_class(de_corrupted_instructions)
        return de_corrupted_program

    def get_corruptible_indexes(self, program):
        """
        >>> DeCorruption().get_corruptible_indexes(part_a.Program.from_program_text(
        ...     "nop +0\\n"
        ...     "acc +1\\n"
        ...     "jmp +4\\n"
        ...     "acc +3\\n"
        ...     "jmp -3\\n"
        ...     "acc -99\\n"
        ...     "acc +1\\n"
        ...     "jmp -4\\n"
        ...     "acc +6\\n"
        ... ))
        [0, 2, 4, 7]
        >>> DeCorruption().get_corruptible_indexes(part_a.Program([
        ...     Nop(0), Acc(1), Jmp(4), Acc(3), Jmp(-3), Acc(-99), Acc(1),
        ...     Jmp(-4), Acc(6)]))
        [0, 2, 4, 7]
        """
        return [
            index
            for index, instruction in enumerate(program.instructions)
            if isinstance(instruction, (part_a.Jmp, part_a.Nop))
        ]

    def de_corrupt_instruction(self, corrupted_instruction):
        """
        >>> DeCorruption().de_corrupt_instruction(part_a.Jmp(5))
        Nop(5)
        >>> DeCorruption().de_corrupt_instruction(part_a.Nop(-5))
        Jmp(-5)
        """
        if isinstance(corrupted_instruction, part_a.Jmp):
            de_corrupted_instruction =\
                part_a.Nop(corrupted_instruction.argument)
        elif isinstance(corrupted_instruction, part_a.Nop):
            de_corrupted_instruction =\
                part_a.Jmp(corrupted_instruction.argument)
        else:
            raise Exception(
                f"Instruction {corrupted_instruction} not of "
                f"corruptible type")
        return de_corrupted_instruction


class ProgramRunner2(part_a.ProgramRunner):
    """
    >>> ProgramRunner2.from_program(part_a.Program.from_program_text(
    ...     "nop +0\\n"
    ...     "acc +1\\n"
    ...     "jmp +4\\n"
    ...     "acc +3\\n"
    ...     "jmp -3\\n"
    ...     "acc -99\\n"
    ...     "acc +1\\n"
    ...     "nop -4\\n"
    ...     "acc +6\\n"
    ... )).run()
    (False, 8)
    """
    def get_run_return_value(self):
        return not self.has_reached_end(), self.value

    def should_exit(self, prevent_infinite_loop=True):
        return (
            super().should_exit(prevent_infinite_loop)
            or self.has_reached_end()
        )

    def has_reached_end(self):
        return self.instruction_counter == len(self.program.instructions)


Challenge.main()
challenge = Challenge()
