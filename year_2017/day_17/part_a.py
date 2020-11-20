#!/usr/bin/env python3
from dataclasses import dataclass

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1282
        """
        spinlock = Spinlock.from_spinlock_text(_input)
        spinlock.step_many(2017)
        return spinlock.buffer[spinlock.buffer.index(2017) + 1]


class Spinlock:
    @classmethod
    def from_spinlock_text(cls, spinlock_text):
        return cls(int(spinlock_text.strip()))

    def __init__(self, skip_count, buffer=(0,), position=0):
        self.skip_count = skip_count
        self.buffer = list(buffer)
        self.position = position

    def step_many(self, count, debug=False, report_count=100000):
        """
        >>> print(Spinlock(3).step_many(9).show())
        0 (9) 5  7  2  4  3  8  6  1
        >>> Spinlock(3).step_many(2017).show()
        '... 1512  1134  151 (2017) 638  1513  851 ...'
        """
        for step in range(count):
            self.step()
            if debug:
                if step % report_count == 0:
                    print(step, f"{1000 * step // count / 10}%")

        return self

    def step(self):
        """
        >>> print(Spinlock(3).step().show())
        0 (1)
        """
        self.position = (self.position + self.skip_count) % len(self.buffer)
        self.buffer.insert(self.position + 1, len(self.buffer))
        self.position += 1

        return self

    def show(self):
        """
        >>> print(Spinlock(3).show())
        (0)
        """
        return " ".join(
            (
                "({})"
                if index == self.position else
                " {} "
            ).format(value)
            for index, value in enumerate(self.buffer)
        )


challenge = Challenge()
challenge.main()
