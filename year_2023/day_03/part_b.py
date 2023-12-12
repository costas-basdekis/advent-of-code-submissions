#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)
from year_2023.day_03.part_a import Schematic, Item, Symbol, ItemT


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        78236071
        """
        return SchematicExtended.from_schematic_text(_input).get_gear_ratio_sum()


class SchematicExtended(Schematic["SymbolExtended", Item]):
    def get_gear_ratio_sum(self) -> int:
        """
        >>> SchematicExtended.from_schematic_text('''
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
        ... ''').get_gear_ratio_sum()
        467835
        """
        return sum((
            self.get_gear_ratio(pair)
            for pair in self.get_gear_pairs()
        ), 0)

    def get_gear_ratio(self, pair: Tuple[Item, Item]) -> int:
        first, second = pair
        return first.number * second.number

    def get_gear_pairs(self) -> List[Tuple[Item, Item]]:
        gear_symbols: List[SymbolExtended] = [
            symbol
            for symbol in self.symbols
            if symbol.text == "*"
        ]
        item_sets_next_to_gear_symbols = [
            tuple(
                item
                for item in self.items
                if symbol.is_next_to_item(item)
            )
            for symbol in gear_symbols
        ]
        return [
            cast(Tuple[Item, Item], items)
            for items in item_sets_next_to_gear_symbols
            if len(items) == 2
        ]


class SymbolExtended(Symbol):
    def is_next_to_item(self, item: Item) -> bool:
        return any(
            position.chebyshev_distance(self.position) <= 1
            for position in item.positions
        )


Challenge.main()
challenge = Challenge()
