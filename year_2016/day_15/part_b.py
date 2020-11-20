#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3208583
        """
        disc_set = part_a.DiscSet.from_discs_text(_input)
        disc_set.discs.append(part_a.Disc.from_disc_text(
            f"Disc #{len(disc_set.discs) + 1} has {11} positions; at time=0, "
            f"it is at position {0}."))
        if debug:
            print("\n".join(map(repr, disc_set.discs)))
        return disc_set.get_earliest_pass_through_time()


Challenge.main()
challenge = Challenge()
