#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1591
        """
        return Ciphertext\
            .from_values_text(_input)\
            .mix()\
            .get_grove_coordinates_sum()


@dataclass
class Ciphertext:
    items: List["Item"]

    @classmethod
    def from_values_text(cls, values_text: str) -> "Ciphertext":
        """
        >>> Ciphertext.from_values_text("1\\n2\\n-3\\n3\\n-2\\n0\\n4")
        Ciphertext.from_values([1, 2, -3, 3, -2, 0, 4])
        """
        return cls.from_values(map(int, values_text.strip().splitlines()))

    @classmethod
    def from_values(cls, values: Iterable[int]) -> "Ciphertext":
        return cls(items=list(map(Item, values)))

    def __repr__(self) -> str:
        item_values = [item.value for item in self.items]
        return f"{type(self).__name__}.from_values({item_values})"

    def get_grove_coordinates_sum(self) -> int:
        """
        >>> Ciphertext.from_values_text("1\\n2\\n-3\\n3\\n-2\\n0\\n4").mix()\\
        ...     .get_grove_coordinates_sum()
        3
        """
        return sum(self.get_grove_coordinates())

    def get_grove_coordinates(self) -> Tuple[int, int, int]:
        """
        >>> Ciphertext.from_values_text("1\\n2\\n-3\\n3\\n-2\\n0\\n4").mix()\\
        ...     .get_grove_coordinates()
        (4, -3, 2)
        """
        return (
            self.get_nth_value_after_value(0, 1000),
            self.get_nth_value_after_value(0, 2000),
            self.get_nth_value_after_value(0, 3000),
        )

    def get_nth_value_after_value(self, value: int, offset: int) -> int:
        """
        >>> ciphertext = Ciphertext.from_values([1, 2, -3, 4, 0, 3, -2])
        >>> ciphertext.get_nth_value_after_value(0, 1000)
        4
        >>> ciphertext.get_nth_value_after_value(0, 2000)
        -3
        >>> ciphertext.get_nth_value_after_value(0, 3000)
        2
        """
        index = self.items.index(self.find_first_item(value))
        return self.items[(index + offset) % len(self.items)].value

    def find_first_item(self, value: int) -> "Item":
        return next(
            _item
            for _item in self.items
            if _item.value == value
        )

    def mix(self) -> "Ciphertext":
        """
        >>> Ciphertext.from_values([1, 2, -3, 3, -2, 0, 4]).mix()
        Ciphertext.from_values([1, 2, -3, 4, 0, 3, -2])
        """
        cls = type(self)
        # noinspection PyArgumentList
        mixed = cls(items=list(self.items))
        return mixed.mix_inline(self.items)

    def mix_inline(self, original_items: Optional[List] = None) -> "Ciphertext":
        if original_items is None:
            original_items = list(self.items)
        for item in original_items:
            self.mix_item_inline(item)
        return self

    def mix_item_inline(self, item: "Item") -> "Ciphertext":
        """
        >>> ciphertext = Ciphertext.from_values([1, 2, -3, 3, -2, 0, 4])
        >>> def mix_value(value: int) -> Ciphertext:
        ...     return ciphertext.mix_item_inline(
        ...         ciphertext.find_first_item(value))
        >>> mix_value(1)
        Ciphertext.from_values([2, 1, -3, 3, -2, 0, 4])
        >>> mix_value(2)
        Ciphertext.from_values([1, -3, 2, 3, -2, 0, 4])
        >>> mix_value(-3)
        Ciphertext.from_values([1, 2, 3, -2, -3, 0, 4])
        >>> mix_value(3)
        Ciphertext.from_values([1, 2, -2, -3, 0, 3, 4])
        >>> mix_value(-2)
        Ciphertext.from_values([1, 2, -3, 0, 3, 4, -2])
        >>> mix_value(0)
        Ciphertext.from_values([1, 2, -3, 0, 3, 4, -2])
        >>> mix_value(4)
        Ciphertext.from_values([1, 2, -3, 4, 0, 3, -2])
        >>> ciphertext = Ciphertext.from_values([1, 2, 3, 1, 4, 5])
        >>> first_item = ciphertext.items[0]
        >>> fourth_item = ciphertext.items[3]
        >>> first_item == fourth_item
        False
        >>> ciphertext.mix_item_inline(first_item)
        Ciphertext.from_values([2, 1, 3, 1, 4, 5])
        >>> ciphertext.mix_item_inline(fourth_item)
        Ciphertext.from_values([2, 1, 3, 4, 1, 5])
        """
        index = self.items.index(item)
        intermediate_length = len(self.items) - 1
        new_index = (
            (index + item.value + intermediate_length)
            % intermediate_length
        )
        if new_index == 0:
            new_index = intermediate_length
        if index == new_index:
            return self
        self.items.pop(index)
        self.items.insert(new_index, item)

        return self


@dataclass(eq=False)
class Item:
    value: int


Challenge.main()
challenge = Challenge()
