#!/usr/bin/env python3
import itertools
from dataclasses import dataclass
from typing import List

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        5042
        """
        return Memory.from_text(_input).get_steps_until_it_repeats()


@dataclass
class Memory:
    banks: List[int]

    @classmethod
    def from_text(cls, text):
        """
        >>> Memory.from_text('0\\t2\\t7\\t0')
        Memory(banks=[0, 2, 7, 0])
        """
        return cls(list(map(int, text.strip().split('\t'))))

    def get_steps_until_it_repeats(self):
        """
        >>> memory = Memory.from_text('0\\t2\\t7\\t0')
        >>> memory.get_steps_until_it_repeats()
        5
        >>> memory
        Memory(banks=[2, 4, 1, 2])
        """
        seen = {self.get_hash()}
        for _ in itertools.count():
            self.step()
            _hash = self.get_hash()
            if _hash in seen:
                break
            seen.add(_hash)

        return len(seen)

    def get_hash(self):
        """
        >>> Memory.from_text('0\\t2\\t7\\t0').get_hash()
        (0, 2, 7, 0)
        """
        return tuple(self.banks)

    def step(self):
        """
        >>> Memory.from_text('0\\t2\\t7\\t0').step()
        Memory(banks=[2, 4, 1, 2])
        """
        bank = self.get_biggest_bank()
        amount = self.banks[bank]
        self.banks[bank] = 0
        equal_distribution = amount // len(self.banks)
        extra_count = amount % len(self.banks)
        for index in range(len(self.banks)):
            self.banks[index] += equal_distribution
            if self.should_index_get_extra(index, bank, extra_count):
                self.banks[index] += 1

        return self

    def should_index_get_extra(self, index, bank, extra_count):
        if not extra_count:
            return False
        start = (bank + 1) % len(self.banks)
        end = (bank + extra_count) % len(self.banks)
        if start > end:
            return (
                index in range(start, len(self.banks))
                or index in range(end + 1)
            )
        else:
            return index in range(start, end + 1)

    def get_biggest_bank(self):
        """
        >>> Memory.from_text('0\\t2\\t7\\t0').get_biggest_bank()
        2
        >>> Memory([3, 1, 2, 3]).get_biggest_bank()
        0
        """
        return max(range(len(self.banks)), key=self.sort_key_biggest_bank)

    def sort_key_biggest_bank(self, index):
        return self.banks[index], -index


challenge = Challenge()
challenge.main()
