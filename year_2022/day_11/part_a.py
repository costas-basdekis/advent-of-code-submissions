#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
import re
from typing import ClassVar, Dict, Optional, Tuple, Union, Pattern

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, Self, PolymorphicParser


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        110264
        """
        return MonkeySet\
            .from_monkeys_text(_input)\
            .apply_rounds(20)\
            .get_monkey_business()


@dataclass
class MonkeySet:
    monkeys_by_id: Dict[str, "Monkey"]

    @classmethod
    def from_monkeys_text(cls, monkeys_text: str) -> "MonkeySet":
        """
        >>> MonkeySet.from_monkeys_text(MONKEYS_TEST_TEXT)
        MonkeySet(monkeys_by_id={'0': Monkey(id='0',
            items=[Item(worry_level=79), Item(worry_level=98)],
            worry_level_operation=Multiplication(amount=19), test_divisor=23,
            monkey_id_if_test_true='2', monkey_id_if_test_false='3',
            inspection_count=0), ...})
        """
        return cls(
            monkeys_by_id={
                monkey.id: monkey
                for monkey in map(
                    Monkey.from_monkey_text,
                    monkeys_text.split("\n\n"),
                )
            },
        )

    def get_monkey_business(self) -> int:
        """
        >>> monkeys = MonkeySet.from_monkeys_text(MONKEYS_TEST_TEXT)
        >>> monkeys.apply_rounds(20).get_monkey_business()
        10605
        """
        busiest_monkeys = sorted(
            self.monkeys_by_id.values(),
            key=lambda monkey: monkey.inspection_count,
            reverse=True,
        )
        return (
            busiest_monkeys[0].inspection_count
            * busiest_monkeys[1].inspection_count
        )

    def apply_rounds(
        self, amount: int, debugger: Debugger = Debugger(enabled=False),
    ) -> "MonkeySet":
        for _ in range(amount):
            self.apply_round(debugger)
        return self

    def apply_round(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> "MonkeySet":
        """
        >>> monkeys = MonkeySet.from_monkeys_text(MONKEYS_TEST_TEXT)
        >>> print(monkeys.apply_round())
        Monkey 0: 20, 23, 27, 26
        Monkey 1: 2080, 25, 167, 207, 401, 1046
        Monkey 2:
        Monkey 3:
        >>> print(monkeys.apply_rounds(19))
        Monkey 0: 10, 12, 14, 26, 34
        Monkey 1: 245, 93, 53, 199, 115
        Monkey 2:
        Monkey 3:
        """
        for monkey in self.monkeys_by_id.values():
            while True:
                result = monkey.inspect_next_item()
                if not result:
                    break
                next_monkey_id, item = result
                next_monkey = self.monkeys_by_id[next_monkey_id]
                next_monkey.take(item)
                if debugger:
                    debugger.report(
                        f"{monkey.id} gives {item.worry_level} to "
                        f"{next_monkey_id}"
                    )
        return self

    def __str__(self) -> str:
        """
        >>> print(MonkeySet.from_monkeys_text(MONKEYS_TEST_TEXT))
        Monkey 0: 79, 98
        Monkey 1: 54, 65, 75, 74
        Monkey 2: 79, 60, 97
        Monkey 3: 74
        """
        return "\n".join(map(str, self.monkeys_by_id.values()))

    def display_inspection_counts(self) -> str:
        """
        >>> monkeys = MonkeySet.from_monkeys_text(MONKEYS_TEST_TEXT)
        >>> print(monkeys.apply_rounds(20).display_inspection_counts())
        Monkey 0 inspected items 101 times.
        Monkey 1 inspected items 95 times.
        Monkey 2 inspected items 7 times.
        Monkey 3 inspected items 105 times.
        """
        return "\n".join(
            monkey.display_inspection_count()
            for monkey in self.monkeys_by_id.values()
        )


@dataclass
class Monkey:
    id: str
    items: ["Item"]
    worry_level_operation: "Operation"
    test_divisor: int
    monkey_id_if_test_true: str
    monkey_id_if_test_false: str
    inspection_count: int = 0

    re_id: ClassVar[Pattern] = re.compile(r"^Monkey (.+):$")
    re_items: ClassVar[Pattern] = re.compile(r"^\s*Starting items: (.+)$")
    re_test: ClassVar[Pattern] = re.compile(r"^\s*Test: divisible by (\d+)$")
    re_if_true: ClassVar[Pattern] = \
        re.compile(r"^\s*If true: throw to monkey (.+)$")
    re_if_false: ClassVar[Pattern] = \
        re.compile(r"^\s*If false: throw to monkey (.+)$")

    @classmethod
    def from_monkey_text(cls, monkey_text: str) -> "Monkey":
        """
        >>> Monkey.from_monkey_text(
        ...     "Monkey 0:\\n"
        ...     "  Starting items: 65, 78\\n"
        ...     "  Operation: new = old * 3\\n"
        ...     "  Test: divisible by 5\\n"
        ...     "    If true: throw to monkey 2\\n"
        ...     "    If false: throw to monkey 3"
        ... )
        Monkey(id='0', items=[Item(worry_level=65), Item(worry_level=78)],
            worry_level_operation=Multiplication(amount=3), test_divisor=5,
            monkey_id_if_test_true='2', monkey_id_if_test_false='3',
            inspection_count=0)
        """
        lines = monkey_text.strip().splitlines()
        id_str, starting_items_str, operation_str, test_str, if_true_str, \
            if_false_str = lines
        _id, = cls.re_id.match(id_str).groups()
        items_str, = cls.re_items.match(starting_items_str).groups()
        items = Item.items_from_items_text(items_str)
        operation = Operation.parse(operation_str)
        test_divisor_str, = cls.re_test.match(test_str).groups()
        test_divisor = int(test_divisor_str)
        if_true, = cls.re_if_true.match(if_true_str).groups()
        if_false, = cls.re_if_false.match(if_false_str).groups()
        return cls(
            id=_id,
            items=items,
            worry_level_operation=operation,
            test_divisor=test_divisor,
            monkey_id_if_test_true=if_true,
            monkey_id_if_test_false=if_false,
        )

    def __str__(self) -> str:
        """
        >>> print(Monkey.from_monkey_text(
        ...     "Monkey 0:\\n"
        ...     "  Starting items: 65, 78\\n"
        ...     "  Operation: new = old * 3\\n"
        ...     "  Test: divisible by 5\\n"
        ...     "    If true: throw to monkey 2\\n"
        ...     "    If false: throw to monkey 3"
        ... ))
        Monkey 0: 65, 78
        """
        items_str = ', '.join(str(item.worry_level) for item in self.items)
        return f"Monkey {self.id}: {items_str}"

    def inspect_next_item(self) -> Optional[Tuple[str, "Item"]]:
        if not self.items:
            return None
        self.inspection_count += 1
        item: Item = self.items.pop(0)
        self.worry_level_operation.apply_to(item)
        item.worry_level //= 3
        test_succeeded = item.worry_level % self.test_divisor == 0
        if test_succeeded:
            return self.monkey_id_if_test_true, item
        else:
            return self.monkey_id_if_test_false, item

    def take(self, item: "Item") -> "Monkey":
        self.items.append(item)
        return self

    def display_inspection_count(self) -> str:
        return (
            f"Monkey {self.id} inspected items {self.inspection_count} times."
        )


@dataclass
class Operation(PolymorphicParser, ABC, root=True):
    amount: int
    re_operation: ClassVar[Pattern]

    @classmethod
    def make_re(cls, operation_str: str) -> Pattern:
        escaped = re.escape(operation_str)
        return re.compile(rf"^\s*Operation: new = old {escaped} (\d+)$")

    @classmethod
    def try_parse(cls: Cls["Operation"], text: str) -> Self["Operation"]:
        """
        >>> Addition.try_parse("  Operation: new = old + 8")
        Addition(amount=8)
        >>> Multiplication.try_parse("  Operation: new = old * 3")
        Multiplication(amount=3)
        >>> Operation.parse("  Operation: new = old + 8")
        Addition(amount=8)
        >>> Operation.parse("  Operation: new = old * 3")
        Multiplication(amount=3)
        >>> Operation.parse("  Operation: new = old * old")
        Exponentiation(amount=2)
        """
        match = cls.re_operation.match(text)
        if not match:
            return None
        amount_str, = match.groups()
        return cls(amount=int(amount_str))

    def apply_to(self, item: "Item") -> None:
        item.worry_level = self.apply(item.worry_level)

    def apply(self, amount: int) -> int:
        raise NotImplementedError()


@Operation.register
@dataclass
class Addition(Operation):
    name = "addition"
    re_operation = Operation.make_re("+")

    def apply(self, amount: int) -> int:
        return self.amount + amount


@Operation.register
@dataclass
class Multiplication(Operation):
    name = "multiplication"
    re_operation = Operation.make_re("*")

    def apply(self, amount: int) -> int:
        return self.amount * amount


@Operation.register
@dataclass
class Exponentiation(Operation):
    name = "exponentiation"
    re_operation = re.compile(rf"^\s*Operation: new = old \* old$")

    @classmethod
    def try_parse(cls: Cls["Operation"], text: str) -> Self["Operation"]:
        """
        >>> Exponentiation.try_parse("  Operation: new = old * old")
        Exponentiation(amount=2)
        """
        match = cls.re_operation.match(text)
        if not match:
            return None
        return cls(amount=2)

    def apply(self, amount: int) -> int:
        return amount * amount


@dataclass
class Item:
    worry_level: int

    @classmethod
    def items_from_items_text(cls, items_text: str) -> ["Item"]:
        """
        >>> Item.items_from_items_text("99")
        [Item(worry_level=99)]
        >>> Item.items_from_items_text("65, 78")
        [Item(worry_level=65), Item(worry_level=78)]
        """
        return list(map(
            cls.from_item_text,
            filter(None, items_text.strip().split(", ")),
        ))

    @classmethod
    def from_item_text(cls, item_text: str) -> "Item":
        """
        >>> Item.from_item_text("65")
        Item(worry_level=65)
        """
        return cls(worry_level=int(item_text.strip()))


Challenge.main()
challenge = Challenge()


MONKEYS_TEST_TEXT = """
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
""".strip()
