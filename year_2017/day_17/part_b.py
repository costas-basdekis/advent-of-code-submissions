#!/usr/bin/env python3
import utils
from year_2017.day_17 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        27650600
        """
        return SpinlockExtended.from_spinlock_text(_input)\
            .step_fake_many(50000000, 0, debug=debug)


class SpinlockExtended(part_a.Spinlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = range(len(self.buffer))

    def step_fake_many(self, count, expected_previous_position,
                       debug=False, report_count=1000000):
        value_after_expected_position = None
        for step in range(count):
            previous_position, new_value = self.step_fake()
            if previous_position == expected_previous_position:
                value_after_expected_position = new_value
            if debug:
                if step % report_count == 0:
                    print(step, f"{1000 * step // count / 10}%")

        if value_after_expected_position is None:
            raise Exception(
                f"No value was inserted after {expected_previous_position}")

        return value_after_expected_position

    def step_fake(self):
        self.position = (self.position + self.skip_count) % len(self.buffer)
        previous_position = self.position
        new_value = len(self.buffer)
        self.buffer = range(len(self.buffer) + 1)
        self.position += 1

        return previous_position, new_value


challenge = Challenge()
challenge.main()
