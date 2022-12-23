#!/usr/bin/env python3
import contextlib
import operator as operators
from abc import ABC
from dataclasses import dataclass
import re
from typing import Callable, ClassVar, Dict, Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        158731561459602
        """
        return MonkeySet.from_monkeys_text(_input).get_root()


@dataclass
class MonkeySet:
    monkeys_by_id: Dict[str, "Monkey"]
    cached_values: Dict[str, int]
    calculations_in_progress: Set[str]

    @classmethod
    def from_monkeys_text(cls, monkeys_text: str) -> "MonkeySet":
        """
        >>> MonkeySet.from_monkeys_text(LONG_INPUT)
        MonkeySet(monkeys_by_id={'root': OperationMonkey(...), ...},
            cached_values={}, calculations_in_progress=set())
        """
        return cls(
            monkeys_by_id={
                monkey.id: monkey
                for monkey
                in map(Monkey.parse, monkeys_text.strip().splitlines())
            },
            cached_values={},
            calculations_in_progress=set(),
        )

    def get_root(self) -> int:
        """
        >>> MonkeySet.from_monkeys_text(LONG_INPUT).get_root()
        152
        """
        return self.get("root")

    def get(self, _id: str) -> int:
        if _id not in self.cached_values:
            with self.calculating(_id):
                monkey = self.monkeys_by_id[_id]
                self.cached_values[_id] = monkey.calculate(self)

        return self.cached_values[_id]

    @contextlib.contextmanager
    def calculating(self, _id: str) -> "MonkeySet":
        if _id in self.calculations_in_progress:
            raise Exception(f"Circular reference found for {_id}")
        self.calculations_in_progress.add(_id)
        yield self
        self.calculations_in_progress.remove(_id)


@dataclass
class Monkey(PolymorphicParser, ABC, root=True):
    """
    >>> Monkey.parse("dbpl: 5")
    ConstantMonkey(id='dbpl', value=5)
    >>> Monkey.parse("root: pppw + sjmn")
    OperationMonkey(id='root', left_reference='pppw',
        right_reference='sjmn', operator=<built-in function add>)
    """
    id: str

    def calculate(self, monkeys: MonkeySet) -> int:
        raise NotImplementedError()


@Monkey.register
@dataclass
class ConstantMonkey(Monkey):
    name = "constant"
    value: int

    re_monkey = re.compile(r"^(\w+): (-?\d+)$")

    @classmethod
    def try_parse(cls, text: str) -> Optional["ConstantMonkey"]:
        """
        >>> ConstantMonkey.try_parse("dbpl: 5")
        ConstantMonkey(id='dbpl', value=5)
        """
        match = cls.re_monkey.match(text)
        if not match:
            return None
        _id, value_str = match.groups()
        return cls(
            id=_id,
            value=int(value_str),
        )

    def calculate(self, monkeys: MonkeySet) -> int:
        return self.value


Operator = Callable[[int, int], int]


@Monkey.register
@dataclass
class OperationMonkey(Monkey):
    name = "operation"
    left_reference: str
    right_reference: str
    operator: Operator

    operator_by_name: ClassVar[Dict[str, Operator]] = {
        "+": operators.add,
        "-": operators.sub,
        "*": operators.mul,
        "/": operators.floordiv,
    }
    re_monkey = re.compile(r"^(\w+): (\w+) ([-+/*]) (\w+)$")

    @classmethod
    def try_parse(cls, text: str) -> Optional["OperationMonkey"]:
        """
        >>> OperationMonkey.try_parse("root: pppw + sjmn")
        OperationMonkey(id='root', left_reference='pppw',
            right_reference='sjmn', operator=<built-in function add>)
        """
        match = cls.re_monkey.match(text)
        if not match:
            return None
        _id, left_reference, operator_str, right_reference = match.groups()
        return cls(
            id=_id,
            left_reference=left_reference,
            right_reference=right_reference,
            operator=cls.operator_by_name[operator_str],
        )

    def calculate(self, monkeys: MonkeySet) -> int:
        return self.operator(
            monkeys.get(self.left_reference),
            monkeys.get(self.right_reference),
        )


Challenge.main()
challenge = Challenge()


LONG_INPUT = """
root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32
""".strip()
