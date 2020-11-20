#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional, Iterable, get_type_hints, Type

from aox.challenge import Debugger

from utils import BaseChallenge, CouldNotParseException
from year_2016.day_12 import part_a as part_12_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        13685
        """
        return InstructionSetExtended\
            .from_instructions_text(_input)\
            .apply_extended(StateExtended({'a': 7}), debugger=debugger)\
            .values['a']

    def get_test_modules(self):
        return super().get_test_modules() + [
            part_12_a,
        ]


@dataclass
class StateExtended(part_12_a.State):
    instructions: List[Optional['InstructionExtended']] = \
        field(default_factory=list)


class InstructionSetExtended(part_12_a.InstructionSet['InstructionExtended']):
    def apply_extended(self, state: Optional[StateExtended] = None,
                       debugger: Debugger = Debugger(enabled=False),
                       ) -> StateExtended:
        """
        >>> def check(instructions_text, state_values=None, program_counter=0):
        ...     _state = InstructionSetExtended\\
        ...         .from_instructions_text(instructions_text)\\
        ...         .apply_extended(StateExtended(
        ...             state_values or {}, program_counter))
        ...     # noinspection PyUnresolvedReferences
        ...     values = {
        ...         name: value
        ...         for name, value in _state.values.items()
        ...         if value
        ...     }
        ...     return values, _state.program_counter
        >>> check(
        ...     "cpy 2 a\\n"
        ...     "tgl a\\n"
        ...     "tgl a\\n"
        ...     "tgl a\\n"
        ...     "cpy 1 a\\n"
        ...     "dec a\\n"
        ...     "dec a\\n"
        ... )
        ({'a': 3}, 7)
        """
        if state is None:
            state = StateExtended()
        state.instructions = list(self.instructions)
        debugger.reset()
        while debugger.step_if(
                0 <= state.program_counter < len(state.instructions)):
            self.step(state)
            if debugger.should_report():
                debugger.default_report(
                    f"values: {state.values}, pc: {state.program_counter}")

        return state

    def step(self, state: Optional[StateExtended] = None) -> StateExtended:
        """
        >>> instruction_set = InstructionSetExtended.from_instructions_text(
        ...     "cpy 2 a\\n"
        ...     "tgl a\\n"
        ...     "tgl a\\n"
        ...     "tgl a\\n"
        ...     "cpy 1 a\\n"
        ...     "dec a\\n"
        ...     "dec a\\n"
        ... )
        >>> _state = StateExtended(
        ...     instructions=list(instruction_set.instructions))
        >>> instruction_set.step(_state)
        StateExtended(values={'a': 2, 'b': 0, 'c': 0, 'd': 0},
            program_counter=1, instructions=[Cpy(...),
                Tgl(...), Tgl(...), Tgl(...), Cpy(...), Dec(...), Dec(...)])
        >>> instruction_set.step(_state)
        StateExtended(values={'a': 2, 'b': 0, 'c': 0, 'd': 0},
            program_counter=2, instructions=[Cpy(...),
                Tgl(...), Tgl(...), Inc(...), Cpy(...), Dec(...), Dec(...)])
        >>> instruction_set.step(_state)
        StateExtended(values={'a': 2, 'b': 0, 'c': 0, 'd': 0},
            program_counter=3, instructions=[Cpy(...),
                Tgl(...), Tgl(...), Inc(...), Jnz(...), Dec(...), Dec(...)])
        >>> instruction_set.step(_state)
        StateExtended(values={'a': 3, 'b': 0, 'c': 0, 'd': 0},
            program_counter=4, instructions=[Cpy(...),
                Tgl(...), Tgl(...), Inc(...), Jnz(...), Dec(...), Dec(...)])
        """
        if not (0 <= state.program_counter < len(state.instructions)):
            return state
        instruction = state.instructions[state.program_counter]
        if instruction.enabled:
            instruction.apply(state)

        return state


class InstructionExtended(part_12_a.Instruction, ABC, root=True):
    enabled: bool

    def reinterpret_as(self, _type: Type['InstructionExtended'],
                       ) -> 'InstructionExtended':
        """
        >>> InstructionExtended.parse("cpy a b").reinterpret_as(Jnz)
        Jnz(check=Register(target='a'), offset=Register(target='b'),
            enabled=True)
        >>> InstructionExtended.parse("jnz 1 2").reinterpret_as(Cpy)
        Cpy(source=Constant(value=1), destination=Constant(value=2),
            enabled=False)
        """
        reinterpreted = self.reinterpret(_type.name)
        if reinterpreted is None:
            # noinspection PyArgumentList
            reinterpreted = _type(*self.get_parameters(), enabled=False)

        return reinterpreted

    def reinterpret(self, name: str) -> Optional['InstructionExtended']:
        """
        >>> InstructionExtended.parse("cpy a b").reinterpret('jnz')
        Jnz(check=Register(target='a'), offset=Register(target='b'),
            enabled=True)
        >>> InstructionExtended.parse("jnz 1 2").reinterpret('cpy')
        """
        try:
            return InstructionExtended.parse(self.to_text(name))
        except CouldNotParseException:
            return None

    def to_text(self, name: Optional[str] = None) -> str:
        """
        >>> InstructionExtended.parse("cpy a b").to_text()
        'cpy a b'
        >>> InstructionExtended.parse("cpy a b").to_text('jnz')
        'jnz a b'
        >>> InstructionExtended.parse("jnz 1 2").to_text()
        'jnz 1 2'
        >>> InstructionExtended.parse("jnz 1 2").to_text('cpy')
        'cpy 1 2'
        """
        if name is None:
            name = self.name
        parameter_texts = (
            parameter.to_text()
            for parameter in self.get_parameters()
        )
        return f"{name} {' '.join(parameter_texts)}"

    def get_parameters(self) -> Iterable[part_12_a.Value]:
        return [
            getattr(self, parameter_name)
            for parameter_name in self.get_parameters_names()
        ]

    def get_parameters_names(self) -> Iterable[str]:
        return [
            field_name
            for field_name, annotation in get_type_hints(type(self)).items()
            if isinstance(annotation, type)
            and issubclass(annotation, part_12_a.Value)
            and field_name != 'enabled'
        ]


@InstructionExtended.override
@dataclass
class Cpy(part_12_a.Cpy, InstructionExtended):
    enabled: bool = True


@InstructionExtended.override
@dataclass
class Inc(part_12_a.Inc, InstructionExtended):
    enabled: bool = True


@InstructionExtended.override
@dataclass
class Dec(part_12_a.Dec, InstructionExtended):
    enabled: bool = True


@InstructionExtended.override
@dataclass
class Jnz(part_12_a.Jnz, InstructionExtended):
    enabled: bool = True


@InstructionExtended.register
@dataclass
class Tgl(InstructionExtended):
    name = 'tgl'
    offset: part_12_a.LValue
    enabled: bool = True

    re_toggle = re.compile(r"^tgl ([^ ]+)$")

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Tgl.try_parse("tgl a")
        Tgl(offset=Register(target='a'), enabled=True)
        >>> Tgl.try_parse("tgl -2")
        Tgl(offset=Constant(value=-2), enabled=True)
        >>> InstructionExtended.parse("tgl a")
        Tgl(offset=Register(target='a'), enabled=True)
        >>> InstructionExtended.parse("tgl -2")
        Tgl(offset=Constant(value=-2), enabled=True)
        """
        match = cls.re_toggle.match(text)
        if not match:
            return None
        offset_str, = match.groups()
        return cls(part_12_a.LValue.parse(offset_str))

    def apply(self, state: StateExtended) -> StateExtended:
        index = state.program_counter + self.offset.get_value(state)
        state.go_to_next()
        if not (0 <= index < len(state.instructions)):
            return state

        state.instructions[index] = \
            self.reinterpret_instruction(state.instructions[index])

        return state

    def reinterpret_instruction(self, instruction: InstructionExtended,
                                ) -> InstructionExtended:
        """
        >>> Tgl(part_12_a.Constant(0)).reinterpret_instruction(
        ...     Inc(part_12_a.Register('a')))
        Dec(register=Register(target='a'), enabled=True)
        """
        return instruction.reinterpret(
            self.REINTERPRET_MAP[type(instruction)].name)


Tgl.REINTERPRET_MAP = {
    Inc: Dec,
    Dec: Inc,
    Tgl: Inc,
    Jnz: Cpy,
    Cpy: Jnz,
}


Challenge.main()
challenge = Challenge()
