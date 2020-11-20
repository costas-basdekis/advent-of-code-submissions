#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from itertools import count
from typing import List, Optional

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2016.day_12 import part_a as part_12_a
from year_2016.day_12.part_a import State


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        158
        """
        instruction_set = InstructionSetExtended.from_instructions_text(_input)
        answer = get_offset_for_alternating_binary(2572)
        if debugger:
            print("0:")
            print(instruction_set.apply_until_output_length(
                16, StateExtended({'a': 0})))
            print(f"{answer}:")
            print(instruction_set.apply_until_output_length(
                16, StateExtended({'a': answer})))
        return answer


def get_offset_for_alternating_binary(threshold: int) -> int:
    """
    >>> get_offset_for_alternating_binary(2572)
    158
    """
    return get_alternating_binary_higher_than(threshold) - threshold


def get_alternating_binary_higher_than(threshold: int) -> int:
    """
    >>> get_alternating_binary_higher_than(2572)
    2730
    """
    bit_count = len(f"{threshold:b}")
    if bit_count % 2 == 0:
        bit_count += 1
    for length in count(bit_count, 2):
        candidate = int('10' * (length // 2), 2)
        if candidate > threshold:
            return candidate


@dataclass
class StateExtended(part_12_a.State):
    output: List[int] = field(default_factory=list)

    def send(self, value: int):
        self.output.append(value)
        return self


class InstructionSetExtended(part_12_a.InstructionSet['InstructionExtended']):
    def apply_until_output_length(self, output_length: int,
                                  state: Optional[StateExtended] = None,
                                  debugger: Debugger = Debugger(enabled=False),
                                  ) -> List[int]:
        if state is None:
            state: StateExtended = StateExtended()
        # noinspection PyTypeChecker
        for state in self.apply_stream(state, debug=debugger):
            if len(state.output) == output_length:
                return state.output


class InstructionExtended(part_12_a.Instruction, ABC, root=True,
                          parse_root=part_12_a.Instruction):
    pass


@InstructionExtended.register
@dataclass
class Out(part_12_a.Instruction):
    name = 'out'
    content: part_12_a.LValue

    re_out = re.compile(r"^out ([^ ]+)$")

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Out.try_parse('out 1')
        Out(content=Constant(value=1))
        >>> Out.try_parse('out a')
        Out(content=Register(target='a'))
        >>> InstructionExtended.parse('out 1')
        Out(content=Constant(value=1))
        >>> InstructionExtended.parse('out a')
        Out(content=Register(target='a'))
        """
        match = cls.re_out.match(text)
        if not match:
            return None
        content_str, = match.groups()

        return cls(part_12_a.LValue.parse(content_str))

    def apply(self, state: StateExtended) -> State:
        state.send(self.content.get_value(state))
        state.go_to_next()
        return state


Challenge.main()
challenge = Challenge()
