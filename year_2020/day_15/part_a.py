#!/usr/bin/env python3
import doctest

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    410
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return Game.from_game_text(_input).get_nth_spoken_number(2020)


class Game:
    @classmethod
    def from_game_text(cls, game_text):
        """
        >>> Game.from_game_text("0,3,6").numbers
        [0, 3, 6]
        >>> Game.from_game_text("0,3,6").indexes
        {0: 0, 3: 1, 6: 2}
        >>> Game.from_game_text("0,3,6").previous_indexes
        {}
        """
        return cls(list(map(int, game_text.strip().split(','))))

    def __init__(self, numbers):
        self.numbers = numbers
        self.indexes = {
            number: index
            for index, number in enumerate(self.numbers)
        }
        self.previous_indexes = {
            number: index
            for index, number in enumerate(self.numbers)
            if index != self.indexes[number]
        }

    def get_nth_spoken_number(self, index):
        """
        >>> Game([0, 3, 6]).get_nth_spoken_number(2020)
        436
        >>> Game([1, 3, 2]).get_nth_spoken_number(2020)
        1
        >>> Game([1, 3, 2]).get_nth_spoken_number(2020)
        1
        >>> Game([2, 1, 3]).get_nth_spoken_number(2020)
        10
        >>> Game([1, 2, 3]).get_nth_spoken_number(2020)
        27
        >>> Game([2, 3, 1]).get_nth_spoken_number(2020)
        78
        >>> Game([3, 2, 1]).get_nth_spoken_number(2020)
        438
        >>> Game([3, 1, 2]).get_nth_spoken_number(2020)
        1836
        """
        if index > len(self.numbers) - 1:
            self.add_next_numbers(index - len(self.numbers) + 1)
        return self.numbers[index - 1]

    def add_next_numbers(self, count):
        """
        >>> Game([0, 3, 6]).add_next_numbers(7).numbers
        [0, 3, 6, 0, 3, 3, 1, 0, 4, 0]
        >>> Game([0, 3, 6]).add_next_numbers(7).indexes
        {0: 9, 3: 5, 6: 2, 1: 6, 4: 8}
        >>> Game([0, 3, 6]).add_next_numbers(7).previous_indexes
        {0: 7, 3: 4}
        >>> Game([0, 3, 6]).add_next_numbers(7).numbers \\
        ...     == Game([0, 3, 6, 0, 3, 3, 1, 0, 4, 0]).numbers
        True
        >>> Game([0, 3, 6]).add_next_numbers(7).indexes \\
        ...     == Game([0, 3, 6, 0, 3, 3, 1, 0, 4, 0]).indexes
        True
        >>> Game([0, 3, 6]).add_next_numbers(7).previous_indexes \\
        ...     == Game([0, 3, 6, 0, 3, 3, 1, 0, 4, 0]).previous_indexes
        True
        """
        for _ in range(count):
            self.add_next_number()

        return self

    def add_next_number(self):
        """
        >>> Game([0, 3, 6]).add_next_number().numbers
        [0, 3, 6, 0]
        >>> Game([0, 3, 6]).add_next_number().indexes
        {0: 3, 3: 1, 6: 2}
        >>> Game([0, 3, 6]).add_next_number().previous_indexes
        {0: 0}
        """
        next_number = self.get_next_number()
        self.add_number(next_number)

        return self

    def add_number(self, number):
        """
        >>> Game([0, 3, 6]).add_number(0).numbers
        [0, 3, 6, 0]
        >>> Game([0, 3, 6]).add_number(0).indexes
        {0: 3, 3: 1, 6: 2}
        >>> Game([0, 3, 6]).add_number(0).previous_indexes
        {0: 0}
        """
        if number in self.indexes:
            self.previous_indexes[number] = self.indexes[number]

        self.indexes[number] = len(self.numbers)
        self.numbers.append(number)

        return self

    def get_next_number(self):
        """
        >>> Game([0, 3, 6]).get_next_number()
        0
        >>> Game([0, 3, 6, 0]).get_next_number()
        3
        """
        last_number = self.numbers[-1]
        last_index = self.indexes[last_number]
        previous_index = self.previous_indexes.get(last_number)
        if previous_index is None:
            return 0
        return last_index - previous_index


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
