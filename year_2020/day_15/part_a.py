#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        410
        """

        return Game.from_game_text(_input).get_nth_spoken_number(2020)


class Game:
    @classmethod
    def from_game_text(cls, game_text):
        """
        >>> Game.from_game_text("0,3,6").indexes
        {0: 0, 3: 1, 6: 2}
        >>> Game.from_game_text("0,3,6").previous_indexes
        {}
        """
        return cls(list(map(int, game_text.strip().split(','))))

    def __init__(self, numbers):
        self.numbers = numbers
        self.count = len(numbers)
        self.last_number = numbers[-1]
        self.indexes = {
            number: index
            for index, number in enumerate(numbers)
        }
        self.previous_indexes = {
            number: index
            for index, number in enumerate(numbers)
            if index != self.indexes[number]
        }

    def get_nth_spoken_number(self, index):
        """
        >>> Game([0, 3, 6]).get_nth_spoken_number(4)
        0
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
        if index <= self.count - 1:
            raise Exception(
                f"Asked for the {index}th number but can only give the "
                f"{self.count}th one")
        self.add_next_numbers(index - self.count)
        return self.last_number

    def add_next_numbers(self, count):
        """
        >>> Game([0, 3, 6]).add_next_numbers(7).count
        10
        >>> Game([0, 3, 6]).add_next_numbers(7).last_number
        0
        >>> Game([0, 3, 6]).add_next_numbers(7).indexes
        {0: 9, 3: 5, 6: 2, 1: 6, 4: 8}
        >>> Game([0, 3, 6]).add_next_numbers(7).previous_indexes
        {0: 7, 3: 4}
        >>> Game([0, 3, 6]).add_next_numbers(7).count \\
        ...     == Game([0, 3, 6, 0, 3, 3, 1, 0, 4, 0]).count
        True
        >>> Game([0, 3, 6]).add_next_numbers(7).last_number \\
        ...     == Game([0, 3, 6, 0, 3, 3, 1, 0, 4, 0]).last_number
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
        >>> Game([0, 3, 6]).add_next_number().count
        4
        >>> Game([0, 3, 6]).add_next_number().last_number
        0
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
        >>> Game([0, 3, 6]).add_number(0).count
        4
        >>> Game([0, 3, 6]).add_number(0).last_number
        0
        >>> Game([0, 3, 6]).add_number(0).indexes
        {0: 3, 3: 1, 6: 2}
        >>> Game([0, 3, 6]).add_number(0).previous_indexes
        {0: 0}
        """
        if number in self.indexes:
            self.previous_indexes[number] = self.indexes[number]

        self.indexes[number] = self.count
        self.last_number = number
        self.count += 1
        self.add_number_to_list(number)

        return self

    def add_number_to_list(self, number):
        self.numbers.append(number)

    def get_next_number(self):
        """
        >>> Game([0, 3, 6]).get_next_number()
        0
        >>> Game([0, 3, 6, 0]).get_next_number()
        3
        """
        last_index = self.indexes[self.last_number]
        previous_index = self.previous_indexes.get(self.last_number)
        if previous_index is None:
            return 0
        return last_index - previous_index


challenge = Challenge()
challenge.main()
