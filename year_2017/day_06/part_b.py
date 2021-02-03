#!/usr/bin/env python3
import itertools

import utils
from year_2017.day_06 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1086
        """
        _, loop_size = MemoryExtended.from_text(_input)\
            .get_steps_and_loop_size_until_it_repeats()

        return loop_size


class MemoryExtended(part_a.Memory):
    def get_steps_and_loop_size_until_it_repeats(self):
        """
        >>> memory = MemoryExtended.from_text('0\\t2\\t7\\t0')
        >>> memory.get_steps_and_loop_size_until_it_repeats()
        (5, 4)
        >>> memory
        MemoryExtended(banks=[2, 4, 1, 2])
        """
        seen = [self.get_hash()]
        for _ in itertools.count():
            self.step()
            _hash = self.get_hash()
            if _hash in seen:
                break
            seen.append(_hash)
        else:
            raise Exception(f"Infinite loop")

        return len(seen), len(seen) - seen.index(_hash)


Challenge.main()
challenge = Challenge()
