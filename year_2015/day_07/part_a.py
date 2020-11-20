#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from typing import Dict, List, get_type_hints, Generic, Type, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        46065
        """
        harness = ConnectionSet.from_connections_text(_input).apply()
        if debugger:
            print(harness.show())
        return harness['a']


@dataclass
class Harness:
    wires: Dict[str, int] = field(default_factory=dict)

    def __contains__(self, item: str) -> bool:
        if not isinstance(item, str):
            raise TypeError(f"Expected str but got {repr(item)}")
        return item in self.wires

    def __getitem__(self, item: str) -> int:
        if not isinstance(item, str):
            raise TypeError(f"Expected str but got {repr(item)}")
        return self.wires[item]

    def __setitem__(self, key: str, value: int):
        if not isinstance(key, str):
            raise TypeError(f"Expected str but got {repr(key)}")
        if not isinstance(value, int):
            raise TypeError(f"Expected int but got {repr(value)}")
        if key in self.wires:
            raise Exception(f"Wire {key} already has a value")
        self.wires[key] = value

    def show(self) -> str:
        """
        >>> print(Harness({'a': 1, 'c': 3, 'b': 2}).show())
        a: 1
        b: 2
        c: 3
        """
        return "\n".join(
            f"{name}: {value}"
            for name, value in sorted(self.wires.items())
        )


class Value(PolymorphicParser, ABC, root=True):
    def can_get_value(self, harness: Harness) -> bool:
        raise NotImplementedError()

    def get_value(self, harness: Harness) -> int:
        raise NotImplementedError()


class LValue(Value, ABC):
    pass


class RValue(Value, ABC):
    def set_value(self, harness: Harness, value: int):
        raise NotImplementedError()


@Value.register
@dataclass(frozen=True)
class Wire(LValue, RValue):
    name = 'wire'

    target: str

    re_wire = re.compile(r"^([a-z]+)$")

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Wire.try_parse('a')
        Wire(target='a')
        >>> Value.parse('a')
        Wire(target='a')
        """
        match = cls.re_wire.match(text)
        if not match:
            return None
        target, = match.groups()
        return cls(target)

    def can_get_value(self, harness: Harness) -> bool:
        return self.target in harness

    def get_value(self, harness: Harness) -> int:
        return harness[self.target]

    def set_value(self, harness: Harness, value: int):
        harness[self.target] = value


@Value.register
@dataclass(frozen=True)
class Constant(LValue):
    name = 'constant'

    value: int

    re_constant = re.compile(r"^(\d+)$")

    @classmethod
    def try_parse(cls, text: str):
        """
        >>> Constant.try_parse('123')
        Constant(value=123)
        >>> Value.parse('123')
        Constant(value=123)
        """
        match = cls.re_constant.match(text)
        if not match:
            return None
        value_str, = match.groups()
        return cls(int(value_str))

    def can_get_value(self, harness: Harness) -> bool:
        return True

    def get_value(self, harness: Harness) -> int:
        return self.value


ConnectionT = TV['Connection']
HarnessT = TV['Harness']


@dataclass
class ConnectionSet(Generic[ConnectionT, HarnessT]):
    connections: List[ConnectionT]

    @classmethod
    def get_connection_class(cls) -> Type[ConnectionT]:
        return get_type_argument_class(cls, ConnectionT)

    @classmethod
    def get_harness_class(cls) -> Type[HarnessT]:
        return get_type_argument_class(cls, HarnessT)

    @classmethod
    def from_connections_text(cls, connections_text: str):
        """
        >>> ConnectionSet.from_connections_text("123 -> x\\n123 AND b -> a\\n")
        ConnectionSet(connections=[PassThrough(source=Constant(value=123),
            destination=Wire(target='x')),
            And(lhs=Constant(value=123), rhs=Wire(target='b'),
                destination=Wire(target='a'))])
        """
        connection_class = cls.get_connection_class()
        return cls(list(map(
            connection_class.parse, connections_text.splitlines())))

    def apply(self, harness: Optional[HarnessT] = None) -> HarnessT:
        """
        >>> print(ConnectionSet.from_connections_text(
        ...     "123 -> x\\n"
        ...     "456 -> y\\n"
        ...     "x AND y -> d\\n"
        ...     "x OR y -> e\\n"
        ...     "x LSHIFT 2 -> f\\n"
        ...     "y RSHIFT 2 -> g\\n"
        ...     "NOT x -> h\\n"
        ...     "NOT y -> i\\n"
        ... ).apply().show())
        d: 72
        e: 507
        f: 492
        g: 114
        h: 65412
        i: 65079
        x: 123
        y: 456
        """
        if harness is None:
            harness_class = self.get_harness_class()
            harness = harness_class()
        remaining = set(self.connections)
        while remaining:
            applicable = {
                connection
                for connection in remaining
                if connection.can_apply(harness)
            }
            if not applicable:
                raise Exception(
                    f"Could not find any more applicable to harness {harness} "
                    f"from {remaining}")
            for connection in applicable:
                connection.apply(harness)
            remaining -= applicable

        return harness


class Connection(PolymorphicParser, ABC, root=True):
    def get_input_names(self) -> List[str]:
        return [
            field_name
            for field_name, annotation in get_type_hints(type(self)).items()
            if isinstance(annotation, type)
            and issubclass(annotation, LValue)
        ]

    def get_inputs(self) -> List[Value]:
        return [
            getattr(self, input_name)
            for input_name in self.get_input_names()
        ]

    def can_apply(self, harness: Harness) -> bool:
        return all(
            _input.can_get_value(harness)
            for _input in self.get_inputs()
        )

    def apply(self, harness: Harness) -> Harness:
        raise NotImplementedError()


@dataclass(frozen=True)
class UnaryConnection(Connection, ABC):
    source: LValue
    destination: RValue

    re_unary = NotImplemented
    RE_UNARY_TEMPLATE = r"^{}([^ ]+) -> ([^ ]+)$"

    @classmethod
    def try_parse(cls, text: str):
        match = cls.re_unary.match(text)
        if not match:
            return None
        source_str, destination_str = match.groups()
        return cls(LValue.parse(source_str), RValue.parse(destination_str))

    def apply(self, harness: Harness) -> Harness:
        value = self.source.get_value(harness)
        if not isinstance(value, int):
            raise TypeError(
                f"Expected int from source {self.source} with {harness}, but "
                f"got {repr(value)}")
        self.destination.set_value(
            harness,
            self.apply_to_value(value),
        )
        return harness

    def apply_to_value(self, value: int) -> int:
        raise NotImplementedError()


@Connection.register
class Not(UnaryConnection):
    """
    >>> Not.try_parse("NOT 123 -> x")
    Not(source=Constant(value=123), destination=Wire(target='x'))
    >>> Connection.parse("NOT 123 -> x")
    Not(source=Constant(value=123), destination=Wire(target='x'))
    """
    name = "not"

    re_unary = re.compile(UnaryConnection.RE_UNARY_TEMPLATE.format("NOT "))

    MASK = 2 ** 16 - 1

    def apply_to_value(self, value: int) -> int:
        """
        >>> print(Not.parse("NOT x -> h").apply(Harness({'x': 123})).show())
        h: 65412
        x: 123
        """
        return self.MASK & ~value


@Connection.register
class PassThrough(UnaryConnection):
    """
    >>> PassThrough.try_parse("123 -> x")
    PassThrough(source=Constant(value=123), destination=Wire(target='x'))
    >>> Connection.parse("123 -> x")
    PassThrough(source=Constant(value=123), destination=Wire(target='x'))
    """
    name = "pass-through"

    re_unary = re.compile(UnaryConnection.RE_UNARY_TEMPLATE.format(""))

    def apply_to_value(self, value: int) -> int:
        return value


@dataclass(frozen=True)
class BinaryConnection(Connection, ABC):
    lhs: LValue
    rhs: LValue
    destination: RValue

    re_binary = NotImplemented
    RE_BINARY_TEMPLATE = r"^([^ ]+) {} ([^ ]+) -> ([^ ]+)$"

    @classmethod
    def try_parse(cls, text: str):
        match = cls.re_binary.match(text)
        if not match:
            return None
        lhs_str, rhs_str, destination_str = match.groups()
        return cls(
            LValue.parse(lhs_str), LValue.parse(rhs_str),
            RValue.parse(destination_str))

    def apply(self, harness: Harness) -> Harness:
        lhs = self.lhs.get_value(harness)
        if not isinstance(lhs, int):
            raise TypeError(
                f"Expected int from lhs {self.lhs} with {harness}, but got "
                f"{repr(lhs)}")
        rhs = self.rhs.get_value(harness)
        if not isinstance(rhs, int):
            raise TypeError(
                f"Expected int from rhs {self.rhs} with {harness}, but got "
                f"{repr(rhs)}")
        self.destination.set_value(
            harness,
            self.apply_to_values(lhs, rhs),
        )
        return harness

    def apply_to_values(self, lhs: int, rhs: int) -> int:
        raise NotImplementedError()


@Connection.register
class And(BinaryConnection):
    """
    >>> And.try_parse("123 AND b -> a")
    And(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    >>> Connection.parse("123 AND b -> a")
    And(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    """
    name = "and"

    re_binary = re.compile(BinaryConnection.RE_BINARY_TEMPLATE.format("AND"))

    apply_to_values = staticmethod(int.__and__)


@Connection.register
class Or(BinaryConnection):
    """
    >>> Or.try_parse("123 OR b -> a")
    Or(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    >>> Connection.parse("123 OR b -> a")
    Or(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    """
    name = "or"

    re_binary = re.compile(BinaryConnection.RE_BINARY_TEMPLATE.format("OR"))

    apply_to_values = staticmethod(int.__or__)


@Connection.register
class LShift(BinaryConnection):
    """
    >>> LShift.try_parse("123 LSHIFT b -> a")
    LShift(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    >>> Connection.parse("123 LSHIFT b -> a")
    LShift(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    """
    name = "lshift"

    re_binary = re.compile(BinaryConnection.RE_BINARY_TEMPLATE.format("LSHIFT"))

    apply_to_values = staticmethod(int.__lshift__)


@Connection.register
class RShift(BinaryConnection):
    """
    >>> RShift.try_parse("123 RSHIFT b -> a")
    RShift(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    >>> Connection.parse("123 RSHIFT b -> a")
    RShift(lhs=Constant(value=123), rhs=Wire(target='b'),
        destination=Wire(target='a'))
    """
    name = "rshift"

    re_binary = re.compile(BinaryConnection.RE_BINARY_TEMPLATE.format("RSHIFT"))

    apply_to_values = staticmethod(int.__rshift__)


Challenge.main()
challenge = Challenge()
