#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Generic, Type

from aox.utils import Timer

from utils import BaseChallenge, PolymorphicParser, Self, Cls, TV, \
    get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        317993
        """
        return InstructionSet.from_instructions_text(_input)\
            .apply(debug=debug)['a']


@dataclass
class State:
    DEFAULT_VALUES = {'a': 0, 'b': 0, 'c': 0, 'd': 0}
    values: Dict[str, int] = field(default_factory=dict)
    program_counter: int = 0

    def __post_init__(self):
        self.set_default_values()

    def set_default_values(self):
        self.values = {
            **self.DEFAULT_VALUES,
            **self.values,
        }

    def __getitem__(self, item: str) -> int:
        return self.values[item]

    def __setitem__(self, key: str, value: int):
        self.values[key] = value

    def go_to_next(self):
        self.program_counter += 1

    def jump(self, offset: int):
        self.program_counter += offset


class Value(PolymorphicParser, ABC, root=True):
    """
    >>> Value.parse('a')
    Register(target='a')
    >>> Value.parse('123')
    Constant(value=123)
    >>> Value.parse('-123')
    Constant(value=-123)
    """

    def get_value(self, state: State) -> int:
        raise NotImplementedError()

    def to_text(self) -> str:
        raise NotImplementedError()


class LValue(Value, ABC):
    pass


class RValue(Value, ABC):
    def set_value(self, state: State, value: int):
        raise NotImplementedError()


@Value.register
@dataclass
class Register(LValue, RValue):
    name = 'register'
    target: str

    re_register = re.compile(r"^([a-z])$")

    @classmethod
    def try_parse(cls: Cls['Register'], text: str
                  ) -> Optional[Self['Register']]:
        """
        >>> Register.try_parse('a')
        Register(target='a')
        >>> Register.try_parse('123')
        >>> Register.try_parse('-123')
        """
        match = cls.re_register.match(text)
        if not match:
            return None
        target, = match.groups()
        return cls(target)

    def get_value(self, state: State) -> int:
        return state[self.target]

    def set_value(self, state: State, value: int):
        state[self.target] = value

    def to_text(self):
        """
        >>> Register.try_parse('a').to_text()
        'a'
        """
        return self.target


@Value.register
@dataclass
class Constant(LValue):
    name = 'constant'
    value: int

    re_constant = re.compile(r"^(-?\d+)$")

    @classmethod
    def try_parse(cls: Cls['Constant'], text: str
                  ) -> Optional[Self['Constant']]:
        """
        >>> Constant.try_parse('a')
        >>> Constant.try_parse('123')
        Constant(value=123)
        >>> Constant.try_parse('-123')
        Constant(value=-123)
        """
        match = cls.re_constant.match(text)
        if not match:
            return None
        value_str, = match.groups()
        return cls(int(value_str))

    def get_value(self, state: State) -> int:
        return self.value

    def to_text(self) -> str:
        """
        >>> Constant.try_parse('1').to_text()
        '1'
        >>> Constant.try_parse('-1').to_text()
        '-1'
        """
        return str(self.value)


InstructionT = TV['Instruction']


@dataclass
class InstructionSet(Generic[InstructionT]):
    instructions: List[InstructionT]

    @classmethod
    def get_instruction_class(cls) -> Type[InstructionT]:
        return get_type_argument_class(cls, InstructionT)

    @classmethod
    def from_instructions_text(
            cls: Cls['InstructionSet'], instructions_text: str
    ) -> Self['InstructionSet']:
        """
        >>> InstructionSet.from_instructions_text(
        ...     "cpy 41 a\\n"
        ...     "inc a\\n"
        ...     "inc a\\n"
        ...     "dec a\\n"
        ...     "jnz a 2\\n"
        ...     "dec a\\n"
        ... )
        InstructionSet(instructions=[Cpy(source=Constant(value=41),
            destination=Register(target='a')),
            Inc(register=Register(target='a')),
            Inc(register=Register(target='a')),
            Dec(register=Register(target='a')),
            Jnz(check=Register(target='a'),
            offset=Constant(value=2)),
            Dec(register=Register(target='a'))])
        """
        instruction_class = cls.get_instruction_class()
        return cls(list(map(
            instruction_class.parse, instructions_text.splitlines())))

    def apply(self, state: Optional[State] = None, debug: bool = False) -> State:
        """
        >>> def check(instructions_text, state_values=None, program_counter=0):
        ...     _state = InstructionSet\\
        ...         .from_instructions_text(instructions_text)\\
        ...         .apply(State(state_values or {}, program_counter))
        ...     # noinspection PyUnresolvedReferences
        ...     values = {
        ...         name: value
        ...         for name, value in _state.values.items()
        ...         if value
        ...     }
        ...     return values, _state.program_counter
        >>> check(
        ...     "cpy 41 a\\n"
        ...     "inc a\\n"
        ...     "inc a\\n"
        ...     "dec a\\n"
        ...     "jnz a 2\\n"
        ...     "dec a\\n"
        ... )
        ({'a': 42}, 6)
        """
        if state is None:
            state = State()
        if debug:
            timer = Timer()
        step = 0
        while 0 <= state.program_counter < len(self.instructions):
            instruction = self.instructions[state.program_counter]
            instruction.apply(state)
            if debug:
                if step % 10000000 == 0:
                    # noinspection PyUnboundLocalVariable
                    print(
                        f"Step {step}, time: "
                        f"{timer.get_pretty_current_duration(0)}, "
                        f"values: {state.values}, pc: {state.program_counter}")
            step += 1

        return state


class Instruction(PolymorphicParser, ABC, root=True):
    """
    >>> Instruction.parse("cpy a b")
    Cpy(source=Register(target='a'),
        destination=Register(target='b'))
    >>> Instruction.parse("cpy 1 b")
    Cpy(source=Constant(value=1),
        destination=Register(target='b'))
    >>> Instruction.parse("cpy 1 2")
    Traceback (most recent call last):
    ...
    utils...CouldNotParseException: Could not parse '...'
    >>> Instruction.parse("cpy a 2")
    Traceback (most recent call last):
    ...
    utils...CouldNotParseException: Could not parse '...'
    >>> Instruction.parse("inc a")
    Inc(register=Register(target='a'))
    >>> Instruction.parse("inc 1")
    Traceback (most recent call last):
    ...
    utils...CouldNotParseException: Could not parse '...'
    >>> Instruction.parse("dec a")
    Dec(register=Register(target='a'))
    >>> Instruction.parse("dec 1")
    Traceback (most recent call last):
    ...
    utils...CouldNotParseException: Could not parse '...'
    >>> Instruction.parse("jnz 1 1")
    Jnz(check=Constant(value=1), offset=Constant(value=1))
    >>> Instruction.parse("jnz 1 b")
    Jnz(check=Constant(value=1), offset=Register(target='b'))
    >>> Instruction.parse("jnz a 1")
    Jnz(check=Register(target='a'), offset=Constant(value=1))
    >>> Instruction.parse("jnz a b")
    Jnz(check=Register(target='a'), offset=Register(target='b'))
    """

    def apply(self, state: State) -> State:
        raise NotImplementedError()


@Instruction.register
@dataclass
class Cpy(Instruction):
    name = 'cpy'

    source: LValue
    destination: RValue

    re_copy = re.compile(rf"^cpy ([^ ]+) ([^ ]+)$")

    @classmethod
    def try_parse(cls: Cls['Cpy'], text: str
                  ) -> Optional[Self['Cpy']]:
        """
        >>> Cpy.try_parse("cpy a b")
        Cpy(source=Register(target='a'),
            destination=Register(target='b'))
        >>> Cpy.try_parse("cpy 1 b")
        Cpy(source=Constant(value=1),
            destination=Register(target='b'))
        >>> Cpy.try_parse("cpy 1 2")
        Traceback (most recent call last):
        ...
        utils...CouldNotParseException: Could not parse '...'
        >>> Cpy.try_parse("cpy a 2")
        Traceback (most recent call last):
        ...
        utils...CouldNotParseException: Could not parse '...'
        >>> Cpy.try_parse("inc a")
        >>> Cpy.try_parse("inc 1")
        >>> Cpy.try_parse("inc a")
        >>> Cpy.try_parse("inc 1")
        >>> Cpy.try_parse("dec a")
        >>> Cpy.try_parse("dec 1")
        >>> Cpy.try_parse("jnz 1 1")
        >>> Cpy.try_parse("jnz 1 b")
        >>> Cpy.try_parse("jnz a 1")
        >>> Cpy.try_parse("jnz a b")
        """
        match = cls.re_copy.match(text)
        if not match:
            return None
        source_str, destination_str = match.groups()
        return cls(LValue.parse(source_str), RValue.parse(destination_str))

    def apply(self, state: State) -> State:
        """
        >>> def check(source_str, destination_str, state_values=None):
        ...     values = Cpy.parse(f"cpy {source_str} {destination_str}")\\
        ...         .apply(State(state_values or {})).values
        ...     # noinspection PyUnresolvedReferences
        ...     return {name: value for name, value in values.items() if value}
        >>> check('a', 'b')
        {}
        >>> check('a', 'b', {'a': 2})
        {'a': 2, 'b': 2}
        >>> check('a', 'b', {'b': 2})
        {}
        >>> check('a', 'b', {'c': 2})
        {'c': 2}
        >>> check('a', 'b', {'a': 2, 'b': 3})
        {'a': 2, 'b': 2}
        >>> check('a', 'b', {'a': 2, 'b': 3, 'c': 4})
        {'a': 2, 'b': 2, 'c': 4}
        """
        self.destination.set_value(state, self.source.get_value(state))
        state.go_to_next()
        return state


@Instruction.register
@dataclass
class Inc(Instruction):
    name = 'inc'

    register: Register

    re_inc = re.compile(rf"^inc ([^ ]+)$")

    @classmethod
    def try_parse(cls: Cls['Inc'], text: str
                  ) -> Optional[Self['Inc']]:
        """
        >>> Inc.try_parse("cpy a b")
        >>> Inc.try_parse("cpy 1 b")
        >>> Inc.try_parse("cpy 1 2")
        >>> Inc.try_parse("cpy a 2")
        >>> Inc.try_parse("inc a")
        Inc(register=Register(target='a'))
        >>> Inc.try_parse("inc 1")
        Traceback (most recent call last):
        ...
        utils...CouldNotParseException: Could not parse '...'
        >>> Inc.try_parse("dec a")
        >>> Inc.try_parse("dec 1")
        >>> Inc.try_parse("jnz 1 1")
        >>> Inc.try_parse("jnz 1 b")
        >>> Inc.try_parse("jnz a 1")
        >>> Inc.try_parse("jnz a b")
        """
        match = cls.re_inc.match(text)
        if not match:
            return None
        register_str, = match.groups()
        return cls(Register.parse(register_str))

    def apply(self, state: State) -> State:
        """
        >>> def check(register_str, state_values=None):
        ...     values = Inc.parse(f"inc {register_str}")\\
        ...         .apply(State(state_values or {})).values
        ...     # noinspection PyUnresolvedReferences
        ...     return {name: value for name, value in values.items() if value}
        >>> check('a')
        {'a': 1}
        >>> check('a', {'a': 2})
        {'a': 3}
        >>> check('a', {'b': 2})
        {'a': 1, 'b': 2}
        >>> check('a', {'c': 2})
        {'a': 1, 'c': 2}
        >>> check('a', {'a': 2, 'b': 3})
        {'a': 3, 'b': 3}
        """
        self.register.set_value(state, self.register.get_value(state) + 1)
        state.go_to_next()
        return state


@Instruction.register
@dataclass
class Dec(Instruction):
    name = 'dec'

    register: Register

    re_dec = re.compile(rf"^dec ([^ ]+)$")

    @classmethod
    def try_parse(cls: Cls['Dec'], text: str
                  ) -> Optional[Self['Dec']]:
        """
        >>> Dec.try_parse("cpy a b")
        >>> Dec.try_parse("cpy 1 b")
        >>> Dec.try_parse("cpy 1 2")
        >>> Dec.try_parse("cpy a 2")
        >>> Dec.try_parse("inc a")
        >>> Dec.try_parse("inc 1")
        >>> Dec.try_parse("dec a")
        Dec(register=Register(target='a'))
        >>> Dec.try_parse("dec 1")
        Traceback (most recent call last):
        ...
        utils...CouldNotParseException: Could not parse '...'
        >>> Dec.try_parse("jnz 1 1")
        >>> Dec.try_parse("jnz 1 b")
        >>> Dec.try_parse("jnz a 1")
        >>> Dec.try_parse("jnz a b")
        """
        match = cls.re_dec.match(text)
        if not match:
            return None
        register_str, = match.groups()
        return cls(Register.parse(register_str))

    def apply(self, state: State) -> State:
        """
        >>> def check(register_str, state_values=None):
        ...     values = Dec.parse(f"dec {register_str}")\\
        ...         .apply(State(state_values or {})).values
        ...     # noinspection PyUnresolvedReferences
        ...     return {name: value for name, value in values.items() if value}
        >>> check('a')
        {'a': -1}
        >>> check('a', {'a': 2})
        {'a': 1}
        >>> check('a', {'b': 2})
        {'a': -1, 'b': 2}
        >>> check('a', {'c': 2})
        {'a': -1, 'c': 2}
        >>> check('a', {'a': 2, 'b': 3})
        {'a': 1, 'b': 3}
        """
        self.register.set_value(state, self.register.get_value(state) - 1)
        state.go_to_next()
        return state


@Instruction.register
@dataclass
class Jnz(Instruction):
    name = 'jnz'

    check: LValue
    offset: LValue

    re_jnz = re.compile(rf"^jnz ([^ ]+) ([^ ]+)$")

    @classmethod
    def try_parse(cls: Cls['Jnz'], text: str
                  ) -> Optional[Self['Jnz']]:
        """
        >>> Jnz.try_parse("cpy a b")
        >>> Jnz.try_parse("cpy 1 b")
        >>> Jnz.try_parse("cpy 1 2")
        >>> Jnz.try_parse("cpy a 2")
        >>> Jnz.try_parse("inc a")
        >>> Jnz.try_parse("inc 1")
        >>> Jnz.try_parse("dec a")
        >>> Jnz.try_parse("dec 1")
        >>> Jnz.try_parse("jnz 1 1")
        Jnz(check=Constant(value=1), offset=Constant(value=1))
        >>> Jnz.try_parse("jnz 1 b")
        Jnz(check=Constant(value=1), offset=Register(target='b'))
        >>> Jnz.try_parse("jnz a 1")
        Jnz(check=Register(target='a'), offset=Constant(value=1))
        >>> Jnz.try_parse("jnz a b")
        Jnz(check=Register(target='a'), offset=Register(target='b'))
        """
        match = cls.re_jnz.match(text)
        if not match:
            return None
        check_str, offset_str, = match.groups()
        return cls(LValue.parse(check_str), LValue.parse(offset_str))

    def apply(self, state: State) -> State:
        """
        >>> def check(check_str, offset_str, state_values=None,
        ...           program_counter=0):
        ...     return Jnz.parse(f"jnz {check_str} {offset_str}")\\
        ...         .apply(State(state_values or {}, program_counter))\\
        ...         .program_counter
        >>> check('a', 'b')
        1
        >>> check('a', 'b', {'a': 1})
        0
        >>> check('a', 'b', {'a': 1, 'b': 1})
        1
        >>> check('a', 'b', {'a': 1, 'b': -2})
        -2
        >>> check('a', 'b', {'a': 1, 'b': -2}, 5)
        3
        >>> check('a', 'b', {'a': 1, 'b': 7}, 5)
        12
        >>> check('a', 'b', {'b': 7}, 5)
        6
        >>> check(1, 'b')
        0
        >>> check(1, 'b', {'b': 1})
        1
        >>> check(1, 'b', {'b': -2})
        -2
        >>> check(1, 'b', {'b': -2}, 5)
        3
        >>> check(1, 'b', {'b': 7}, 5)
        12
        >>> check(0, 'b', {'b': 7}, 5)
        6
        >>> check('a', 0)
        1
        >>> check('a', 0, {'a': 1})
        0
        >>> check('a', 1, {'a': 1})
        1
        >>> check('a', -2, {'a': 1})
        -2
        >>> check('a', -2, {'a': 1}, 5)
        3
        >>> check('a', 7, {'a': 1}, 5)
        12
        >>> check('a', 7, {}, 5)
        6
        >>> check(0, 0)
        1
        >>> check(1, 0)
        0
        >>> check(1, 1)
        1
        >>> check(1, -2)
        -2
        >>> check(1, -2, {}, 5)
        3
        >>> check(1, 7, {}, 5)
        12
        """
        if not self.check.get_value(state):
            state.go_to_next()
            return state
        state.jump(self.offset.get_value(state))
        return state


Challenge.main()
challenge = Challenge()
