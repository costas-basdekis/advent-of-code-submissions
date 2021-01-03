#!/usr/bin/env python3
import itertools
import re
from abc import ABC

import utils

from year_2020.day_14 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3435342392262
        """

        return ProgramExtended.from_program_text(_input)\
            .run_and_get_memory_checksum()


class InstructionExtended(part_a.Instruction, ABC):
    instruction_classes = dict(part_a.Instruction.instruction_classes)

    @classmethod
    def override(cls, instruction_class):
        return cls.register(instruction_class, override=True)


@InstructionExtended.override
class BitmaskExtended(InstructionExtended):
    name = 'bitmask'
    re_bitmask = re.compile(r"^mask = ([01X]{36})$")

    @classmethod
    def try_parse(cls, instruction_text):
        """
        >>> BitmaskExtended\\
        ...     .try_parse("mask = 000000000000000000000000000000X1001X")
        BitmaskExtended(18, 33)
        >>> BitmaskExtended\\
        ...     .try_parse("mask = 000000000000000000000000000000X1001X")
        BitmaskExtended(18, 33)
        >>> BitmaskExtended\\
        ...     .try_parse("mask = 00000000000000000000000000000000X0XX")
        BitmaskExtended(0, 11)
        >>> BitmaskExtended\\
        ...     .try_parse("mem[8] = 11")
        """
        match = cls.re_bitmask.match(instruction_text)
        if not match:
            return None
        bitmask_str, = match.groups()
        bitmask = int(bitmask_str.replace('X', '0'), 2)
        floating = int(bitmask_str.replace('1', '0').replace('X', '1'), 2)

        return cls(bitmask, floating)

    def __init__(self, bitmask, floating):
        self.bitmask = bitmask
        self.floating = floating

    def __repr__(self):
        return f"{type(self).__name__}({self.bitmask}, {self.floating})"

    def step(self, memory):
        """
        >>> BitmaskExtended(18, 33)\\
        ...     .step({'bitmask': 0, 'floating': 0, 'values': {8: 11}})
        {'bitmask': 18, 'floating': 33, 'values': {8: 11}}
        >>> BitmaskExtended(0, 11)\\
        ...     .step({'bitmask': 16, 'floating': 33, 'values': {8: 11}})
        {'bitmask': 0, 'floating': 11, 'values': {8: 11}}
        """
        memory['bitmask'] = self.bitmask
        memory['floating'] = self.floating

        return memory


@InstructionExtended.override
class WriteExtended(part_a.Write):
    def step(self, memory):
        """
        >>> dict(sorted(WriteExtended(42, 100).step(
        ...     {'bitmask': 18, 'floating': 33, 'values': {}}
        ... )['values'].items()))
        {26: 100, 27: 100, 58: 100, 59: 100}
        >>> dict(sorted(WriteExtended(26, 1).step(
        ...     {'bitmask': 0, 'floating': 11, 'values': {}}
        ... )['values'].items()))
        {16: 1, 17: 1, 18: 1, 19: 1, 24: 1, 25: 1, 26: 1, 27: 1}
        """
        for address in self.get_masked_addresses(memory):
            memory['values'][address] = self.value
            if self.value == 0:
                del memory['values'][address]

        return memory

    def get_masked_addresses(self, memory):
        """
        >>> sorted(WriteExtended(42, 100).get_masked_addresses(
        ...     {'bitmask': 18, 'floating': 33}))
        [26, 27, 58, 59]
        >>> sorted(WriteExtended(26, 1).get_masked_addresses(
        ...     {'bitmask': 0, 'floating': 11}))
        [16, 17, 18, 19, 24, 25, 26, 27]
        """
        bitmask = memory['bitmask']
        floating = memory['floating']
        masked_address = self.address | bitmask
        floating_powers = self.get_floating_powers(floating)
        if not floating_powers:
            return
        floating_mask = sum(floating_powers)
        bits_combinations = \
            itertools.product(*(((0, 1),) * len(floating_powers)))
        for bits in bits_combinations:
            combination_floating_mask = sum(
                power
                for bit, power in zip(bits, floating_powers)
                if bit
            )
            combination_floating_mask = (
                (masked_address & ~floating_mask)
                | combination_floating_mask
            )
            yield combination_floating_mask

    def get_floating_powers(self, floating):
        """
        >>> WriteExtended(0, 0).get_floating_powers(0)
        []
        >>> WriteExtended(0, 0).get_floating_powers(33)
        [1, 32]
        """
        binary_floating = reversed(bin(floating).replace('0b', ''))
        return [
            2 ** index
            for index, bit in enumerate(binary_floating)
            if bit == '1'
        ]


class ProgramExtended(part_a.Program):
    """
    >>> ProgramExtended([
    ...     BitmaskExtended(18, 33),
    ... ]).run()
    {'bitmask': 18, 'floating': 33, 'values': {}}
    >>> ProgramExtended.from_program_text(
    ...     "mask = 000000000000000000000000000000X1001X\\n"
    ... ).run()
    {'bitmask': 18, 'floating': 33, 'values': {}}
    >>> ProgramExtended.from_program_text(
    ...     "mask = 000000000000000000000000000000X1001X\\n"
    ...     "mem[42] = 100\\n"
    ...     "mask = 00000000000000000000000000000000X0XX\\n"
    ...     "mem[26] = 1\\n"
    ... ).run_and_get_memory_checksum()
    208
    """
    instruction_class = InstructionExtended

    def get_default_memory(self):
        return {'bitmask': 0, 'floating': 0, 'values': {}}


challenge = Challenge()
challenge.main()
