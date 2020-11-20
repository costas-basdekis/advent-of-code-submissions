#!/usr/bin/env python3
from dataclasses import dataclass
from hashlib import md5
from itertools import count
from typing import Optional, Tuple, Iterable

from utils import BaseChallenge, Self, Cls


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'f77a0e6e'
        """
        return Hasher(_input.strip()).get_password()


@dataclass
class Hasher:
    input: str

    @classmethod
    def from_text(cls: Cls['Hasher'], text: str) -> Self['Hasher']:
        return cls(text)

    def get_password(self, size: int = 8) -> str:
        """
        >>> Hasher('abc').get_password()
        '18f47a30'
        """
        return "".join(map("{:x}".format, self.get_digits(size)))

    def get_digits(self, _count: Optional[int] = None) -> Iterable[int]:
        """
        >>> list(Hasher('abc').get_digits(3))
        [1, 8, 15]
        """
        next_index = 0
        for digit_count in count(1):
            if _count is not None and digit_count > _count:
                break
            index, digit = self.get_next_digit(next_index)
            yield digit
            next_index = index + 1

    def get_next_digit(self, start_index: int = 0) -> Tuple[int, int]:
        """
        >>> Hasher('abc').get_next_digit()
        (3231929, 1)
        >>> Hasher('abc').get_next_digit(3231930)
        (5017308, 8)
        >>> Hasher('abc').get_next_digit(5017309)
        (5278568, 15)
        """
        for index in count(start_index):
            potential_digit = self.get_potential_digit(index)
            if potential_digit <= 0xf:
                return index, potential_digit

    def get_potential_digit(self, index: int) -> int:
        """
        >>> Hasher('abc').get_potential_digit(3231929)
        1
        >>> Hasher('abc').get_potential_digit(5017308)
        8
        >>> Hasher('abc').get_potential_digit(5278568)
        15
        """
        first_6_digits = md5(f"{self.input}{index}".encode()).digest()[:3]
        collision_index = int.from_bytes(first_6_digits, 'big')
        return collision_index


Challenge.main()
challenge = Challenge()
