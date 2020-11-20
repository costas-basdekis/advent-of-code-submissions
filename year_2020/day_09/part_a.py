#!/usr/bin/env python3
import doctest
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    776203571
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    encrypted = Decoder.read_encrypted_text(_input)
    return Decoder(25).get_first_number_that_is_not_a_sum(encrypted)


class Decoder(namedtuple("Decoder", ("memory_size",))):
    @classmethod
    def read_encrypted_text(cls, encrypted_text):
        """
        >>> Decoder.read_encrypted_text(
        ...     "35\\n20\\n15\\n25\\n47\\n40\\n62\\n55\\n65\\n95")
        (35, 20, 15, 25, 47, 40, 62, 55, 65, 95)
        """
        return tuple(map(int, filter(None, encrypted_text.splitlines())))

    def get_first_number_that_is_not_a_sum(self, encrypted):
        """
        >>> encrypted_a = (
        ...     35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182,
        ...     127, 219, 299, 277, 309, 576)
        >>> Decoder(5).get_first_number_that_is_not_a_sum(encrypted_a)
        127
        """
        for position in range(self.memory_size, len(encrypted)):
            found, number = self.check_position(encrypted, position)
            if found:
                return number

        return None

    def check_position(self, encrypted, position):
        """
        >>> encrypted_a = (
        ...     35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182,
        ...     127, 219, 299, 277, 309, 576)
        >>> Decoder(5).check_position(encrypted_a, 5)
        (False, None)
        >>> Decoder(5).check_position(encrypted_a, 14)
        (True, 127)
        """
        last_n_numbers = encrypted[position - self.memory_size:position]
        number = encrypted[position]
        if not self.check_number(last_n_numbers, number):
            return False, None

        return True, number

    def check_number(self, last_n_numbers, number):
        """
        >>> Decoder(5).check_number((35, 20, 15, 25, 47), 40)
        False
        >>> Decoder(5).check_number((95, 102, 117, 150, 182), 127)
        True
        """
        return not any(
            number == first + second
            for first_index, first in enumerate(last_n_numbers)
            for second in last_n_numbers[first_index + 1:]
        )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
