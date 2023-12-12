#!/usr/bin/env python3
import string
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self, TV,
)


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        533775
        """
        return Schematic.from_schematic_text(_input).get_sum_of_part_numbers()


SymbolT = TV["Symbol"]
ItemT = TV["Item"]


@dataclass
class Schematic(Generic[SymbolT, ItemT]):
    symbols: List[SymbolT]
    items: List[ItemT]

    non_symbols = string.digits + "."

    @classmethod
    def get_symbol_class(cls) -> Type[SymbolT]:
        return get_type_argument_class(cls, SymbolT)

    @classmethod
    def get_item_class(cls) -> Type[ItemT]:
        return get_type_argument_class(cls, ItemT)

    @classmethod
    def from_schematic_text(cls, schematic_text: str) -> "Schematic":
        """
        >>> Schematic.from_schematic_text('''
        ...     467..114..
        ...     ...*......
        ...     ..35..633.
        ...     ......#...
        ...     617*......
        ...     .....+.58.
        ...     ..592.....
        ...     ......755.
        ...     ...$.*....
        ...     .664.598..
        ... ''')
        Schematic(symbols=[Symbol(position=Point2D(x=3, y=1), text='*'),
            Symbol(position=Point2D(x=6, y=3), text='#'), ...,
            Symbol(position=Point2D(x=5, y=8), text='*')],
            items=[Item(number=467, positions=[Point2D(x=0, y=0),
                Point2D(x=1, y=0), Point2D(x=2, y=0)], is_part=True), ...])
        """
        lines = list(map(str.strip, schematic_text.strip().splitlines()))
        symbol_cls = cls.get_symbol_class()
        symbols = [
            symbol_cls(Point2D(x, y), lines[y][x])
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char not in cls.non_symbols
        ]
        item_cls = cls.get_item_class()
        items = [
            item_cls.from_line_and_start(x, y, line, symbols)
            for y, line in enumerate(lines)
            for x, char in enumerate(line)
            if char in string.digits
            and (x == 0 or line[x - 1] not in string.digits)
        ]
        return cls(symbols, items)

    def get_sum_of_part_numbers(self) -> int:
        """
        >>> Schematic.from_schematic_text('''
        ...     467..114..
        ...     ...*......
        ...     ..35..633.
        ...     ......#...
        ...     617*......
        ...     .....+.58.
        ...     ..592.....
        ...     ......755.
        ...     ...$.*....
        ...     .664.598..
        ... ''').get_sum_of_part_numbers()
        4361
        """
        return sum((
            item.number
            for item in self.items
            if item.is_part
        ), 0)


@dataclass
class Symbol:
    position: Point2D
    text: str


@dataclass
class Item:
    number: int
    positions: List[Point2D]
    is_part: bool

    @classmethod
    def from_line_and_start(
        cls, x: int, y: int, line: str, symbols: List[SymbolT],
    ) -> "Item":
        """
        >>> Item.from_line_and_start(0, 0, "467..114..", [])
        Item(number=467, positions=[Point2D(x=0, y=0), Point2D(x=1, y=0),
            Point2D(x=2, y=0)], is_part=False)
        >>> Item.from_line_and_start(0, 0, "467..114..", [Symbol(Point2D(2, 2), "*")])
        Item(number=467, positions=[Point2D(x=0, y=0), Point2D(x=1, y=0),
            Point2D(x=2, y=0)], is_part=False)
        >>> Item.from_line_and_start(0, 0, "467..114..", [Symbol(Point2D(5, 5), "*")])
        Item(number=467, positions=[Point2D(x=0, y=0), Point2D(x=1, y=0),
            Point2D(x=2, y=0)], is_part=False)
        >>> Item.from_line_and_start(0, 0, "467..114..", [Symbol(Point2D(1, 1), "*")])
        Item(number=467, positions=[Point2D(x=0, y=0), Point2D(x=1, y=0),
            Point2D(x=2, y=0)], is_part=True)
        >>> Item.from_line_and_start(0, 0, "467..114..", [Symbol(Point2D(3, 1), "*")])
        Item(number=467, positions=[Point2D(x=0, y=0), Point2D(x=1, y=0),
            Point2D(x=2, y=0)], is_part=True)
        """
        number_str = cls.get_number_text_at_line_and_start(x, line)
        number = int(number_str)
        positions: List[Point2D] = [
            Point2D(char_x, y)
            for char_x in range(x, x + len(number_str))
        ]
        is_part = any(
            position.chebyshev_distance(symbol.position) <= 1
            for position in positions
            for symbol in symbols
        )
        return cls(number, positions, is_part)

    @classmethod
    def get_number_text_at_line_and_start(cls, x: int, line: str) -> str:
        """
        >>> Item.get_number_text_at_line_and_start(0, "467..114..")
        '467'
        >>> Item.get_number_text_at_line_and_start(5, "467..114..")
        '114'
        """
        position = x
        while position < len(line) and line[position] in string.digits:
            position += 1
        return line[x:position]


Challenge.main()
challenge = Challenge()
