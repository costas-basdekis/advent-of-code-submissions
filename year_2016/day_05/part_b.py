#!/usr/bin/env python3
from hashlib import md5
from itertools import count
from typing import Tuple, Optional, Iterable

from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '999828ec'
        """
        return HasherExtended(_input.strip()).get_password_by_position()


class HasherExtended(part_a.Hasher):
    def get_password_by_position(self, size: int = 8) -> str:
        """
        >>> HasherExtended('abc').get_password_by_position()
        '05ace8e3'
        """
        if size <= 0:
            return ""
        digits = [None] * size
        digit_count_left = size
        for digit, position in self.get_digits_and_positions(max_length=size):
            if digits[position] is not None:
                continue
            digits[position] = digit
            digit_count_left -= 1
            if digit_count_left <= 0:
                break
        return "".join(map("{:x}".format, digits))

    def get_digits_and_positions(self, _count: Optional[int] = None,
                                 max_length: int = 8,
                                 ) -> Iterable[Tuple[int, int]]:
        next_index = 0
        for digit_count in count(1):
            if _count is not None and digit_count > _count:
                break
            index, digit, position = self.get_next_digit_and_position(
                next_index, max_length=max_length)
            yield digit, position
            next_index = index + 1

    def get_next_digit_and_position(self, start_index: int = 0,
                                    max_length: int = 8
                                    ) -> Tuple[int, int, int]:
        """
        >>> HasherExtended('abc').get_next_digit_and_position()
        (3231929, 5, 1)
        >>> HasherExtended('abc').get_next_digit_and_position(3231930)
        (5357525, 14, 4)
        """
        for index in count(start_index):
            potential_digit_and_position = \
                self.get_potential_digit_and_position(index)
            if potential_digit_and_position > 0xfff:
                continue
            potential_position = (potential_digit_and_position & 0xf00) // 0x100
            if potential_position >= max_length:
                continue
            digit = (potential_digit_and_position & 0xf0) // 0x10
            return index, digit, potential_position

    def get_potential_digit_and_position(self, index: int) -> int:
        """
        >>> hex(HasherExtended('abc').get_potential_digit_and_position(3231929))
        '0x155'
        >>> hex(HasherExtended('abc').get_potential_digit_and_position(5017308))
        '0x8f8'
        >>> hex(HasherExtended('abc').get_potential_digit_and_position(5278568))
        '0xf9a'
        >>> hex(HasherExtended('abc').get_potential_digit_and_position(5357525))
        '0x4e5'
        """
        first_8_digits = md5(f"{self.input}{index}".encode()).digest()[:4]
        collision_index = int.from_bytes(first_8_digits, 'big')
        return collision_index


Challenge.main()
challenge = Challenge()
