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
from year_2022.day_20.part_a import Ciphertext, Item


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        14579387544492
        """
        return CiphertextExtended\
            .from_values_text(_input)\
            .encrypt()\
            .mix_many(10)\
            .get_grove_coordinates_sum()


class CiphertextExtended(Ciphertext):
    def encrypt(self, encryption_key: int = 811589153) -> "CiphertextExtended":
        """
        >>> CiphertextExtended.from_values([1, 2, -3, 3, -2, 0, 4]).encrypt()
        CiphertextExtended.from_values([811589153, 1623178306, -2434767459, 2434767459, -1623178306, 0, 3246356612])
        """
        return CiphertextExtended(items=[
            Item(item.value * encryption_key)
            for item in self.items
        ])

    def mix_many(self, count: int) -> "CiphertextExtended":
        """
        >>> def slide(_cipher_text: CiphertextExtended, count: int) -> "CiphertextExtended":
        ...     return CiphertextExtended(items=_cipher_text.items[-count:] + _cipher_text.items[:-count])
        >>> cipher_text = CiphertextExtended.from_values([1, 2, -3, 3, -2, 0, 4]).encrypt()
        >>> slide(cipher_text.mix_many(1), 1)
        CiphertextExtended.from_values([0, -2434767459, 3246356612, -1623178306, 2434767459, 1623178306, 811589153])
        >>> slide(cipher_text.mix_many(2), 1)
        CiphertextExtended.from_values([0, 2434767459, 1623178306, 3246356612, -2434767459, -1623178306, 811589153])
        >>> slide(cipher_text.mix_many(3), 1)
        CiphertextExtended.from_values([0, 811589153, 2434767459, 3246356612, 1623178306, -1623178306, -2434767459])
        >>> slide(cipher_text.mix_many(4), 3)
        CiphertextExtended.from_values([0, 1623178306, -2434767459, 811589153, 2434767459, 3246356612, -1623178306])
        >>> slide(cipher_text.mix_many(5), 3)
        CiphertextExtended.from_values([0, 811589153, -1623178306, 1623178306, -2434767459, 3246356612, 2434767459])
        >>> slide(cipher_text.mix_many(6), 1)
        CiphertextExtended.from_values([0, 811589153, -1623178306, 3246356612, -2434767459, 1623178306, 2434767459])
        >>> slide(cipher_text.mix_many(7), 3)
        CiphertextExtended.from_values([0, -2434767459, 2434767459, 1623178306, -1623178306, 811589153, 3246356612])
        >>> slide(cipher_text.mix_many(8), 3)
        CiphertextExtended.from_values([0, 1623178306, 3246356612, 811589153, -2434767459, 2434767459, -1623178306])
        >>> slide(cipher_text.mix_many(9), 2)
        CiphertextExtended.from_values([0, 811589153, 1623178306, -2434767459, 3246356612, 2434767459, -1623178306])
        >>> slide(cipher_text.mix_many(10), 1)
        CiphertextExtended.from_values([0, -2434767459, 1623178306, 3246356612, -1623178306, 2434767459, 811589153])
        """
        cipher_text = self.mix()
        for _ in range(count - 1):
            cipher_text.mix_inline(self.items)
        return cipher_text


Challenge.main()
challenge = Challenge()
