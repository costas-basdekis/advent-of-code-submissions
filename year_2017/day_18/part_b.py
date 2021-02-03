#!/usr/bin/env python3
import itertools
from abc import ABC

import utils
from year_2017.day_18 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        7493
        """
        return ProgramExtended.from_program_text(_input)\
            .step_pair_and_get_sent_count()[1]


class ProgramExtended(part_a.Program):
    def step_pair_and_get_sent_count(
            self, registers_a=None, registers_b=None, count=None):
        """
        >>> ProgramExtended.from_program_text(
        ...     "snd 1\\n"
        ...     "snd 2\\n"
        ...     "snd p\\n"
        ...     "rcv a\\n"
        ...     "rcv b\\n"
        ...     "rcv c\\n"
        ...     "rcv d\\n"
        ... ).step_pair_and_get_sent_count()
        {0: 3, 1: 3}
        """
        counts = {0: 0, 1: 0}
        for sender, _, _ in self.step_pair_and_stream(
                registers_a, registers_b, count):
            counts[sender] += 1

        return counts

    def step_pair_and_stream(self, registers_a=None, registers_b=None,
                             count=None):
        """
        >>> list(ProgramExtended.from_program_text(
        ...     "snd 1\\n"
        ...     "snd 2\\n"
        ...     "snd p\\n"
        ...     "rcv a\\n"
        ...     "rcv b\\n"
        ...     "rcv c\\n"
        ...     "rcv d\\n"
        ... ).step_pair_and_stream())
        [(0, 1, 1), (1, 0, 1), (0, 1, 2), (1, 0, 2), (0, 1, 0), (1, 0, 1)]
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        if registers_a is None and registers_b is None:
            registers_a = self.registers_class({'p': 0})
            registers_b = self.registers_class({'p': 1})
        elif registers_a is None or registers_b is None:
            raise Exception(
                f"Either don't provide any registers or provide both")
        for _ in steps:
            registers_a.feed_mutual(registers_b)
            finished = self.apply_pair(registers_a, registers_b)
            if finished:
                break
            for value in registers_a.outbound_queue:
                yield 0, 1, value
            for value in registers_b.outbound_queue:
                yield 1, 0, value

    def are_both_finished(self, registers_a, registers_b):
        if registers_a.blocked_on_input and registers_b.blocked_on_input:
            return True

        return self.has_finished(registers_a) and self.has_finished(registers_b)

    def apply_pair(self, registers_a, registers_b):
        if self.are_both_finished(registers_a, registers_b):
            return True

        registers_a.feed_mutual(registers_b)
        self.apply(registers_a)
        self.apply(registers_b)

        return False


class RegistersExtended(part_a.Registers):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        del self.last_sound
        del self.last_recovered

        self.inbound_queue = []
        self.outbound_queue = []
        self.blocked_on_input = False

    def sound(self, value):
        raise Exception(f"Cannot make a sound")

    def recover(self):
        raise Exception(f"Cannot recover a sound")

    def reset_recovered(self):
        raise Exception(f"Cannot reset recovered sounds")

    def send(self, value):
        self.check_is_value(value)
        self.outbound_queue.append(value)

    def try_receive(self):
        if not self.inbound_queue:
            self.blocked_on_input = True
            return False, None

        self.blocked_on_input = False
        return True, self.inbound_queue.pop(0)

    def feed_mutual(self, other):
        self.feed(other)
        other.feed(self)

    def feed(self, other):
        other.inbound_queue.extend(self.outbound_queue)
        self.outbound_queue = []


ProgramExtended.registers_class = RegistersExtended


class InstructionExtended(part_a.Instruction, ABC):
    instruction_classes = dict(part_a.Instruction.instruction_classes)

    @classmethod
    def override(cls, instruction_class):
        return cls.register(instruction_class, override=True)


ProgramExtended.instruction_class = InstructionExtended


@InstructionExtended.override
class Send(InstructionExtended, part_a.RValueInstruction):
    name = 'snd'

    regex = part_a.RValueInstruction.make_regex(name)

    def apply(self, registers):
        registers.send(registers.resolve(self.rvalue))


@InstructionExtended.override
class Receive(InstructionExtended, part_a.RegisterInstruction):
    name = 'rcv'

    regex = part_a.RegisterInstruction.make_regex(name)

    def apply(self, registers):
        received, value = registers.try_receive()
        if not received:
            return registers.instruction_pointer

        registers[self.register] = value


Challenge.main()
challenge = Challenge()
