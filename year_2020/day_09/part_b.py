#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_09 import part_a


def solve(_input=None):
    """
    >>> solve()
    104800569
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    encrypted = DecoderExtended.read_encrypted_text(_input)
    return DecoderExtended(25).find_weakness(encrypted)


class DecoderExtended(part_a.Decoder):
    def find_weakness(self, encrypted):
        """
        >>> encrypted_a = (
        ...     35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182,
        ...     127, 219, 299, 277, 309, 576)
        >>> DecoderExtended(5).find_weakness(encrypted_a)
        62
        """
        number, _range = self.find_weakness_range(encrypted)
        if number is None:
            return None

        return min(_range) + max(_range)

    def find_weakness_range(self, encrypted):
        """
        >>> encrypted_a = (
        ...     35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182,
        ...     127, 219, 299, 277, 309, 576)
        >>> DecoderExtended(5).find_weakness_range(encrypted_a)
        (127, (15, 25, 47, 40))
        """
        number = self.get_first_number_that_is_not_a_sum(encrypted)
        position = encrypted.index(number)
        for start in range(0, position):
            total = encrypted[start]
            if total == number:
                return number, encrypted[start:start + 1]
            if total > number:
                continue
            for end in range(start + 1, position):
                total += encrypted[end]
                if total == number:
                    return number, encrypted[start:end + 1]
                if total > number:
                    break

        return None, None


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
