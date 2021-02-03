#!/usr/bin/env python3
import utils
from year_2017.day_12 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        202
        """
        return NetworkExtended.from_pipes_text(_input).get_group_count()


class NetworkExtended(part_a.Network):
    def get_group_count(self):
        """
        >>> NetworkExtended.from_pipes_text(
        ...     "0 <-> 2\\n"
        ...     "1 <-> 1\\n"
        ...     "2 <-> 0, 3, 4\\n"
        ...     "3 <-> 2, 4\\n"
        ...     "4 <-> 2, 3, 6\\n"
        ...     "5 <-> 6\\n"
        ...     "6 <-> 4, 5\\n"
        ... ).get_group_count()
        2
        """
        return utils.helper.iterable_length(self.get_groups())

    def get_groups(self):
        """
        >>> sorted(map(tuple, map(sorted, NetworkExtended.from_pipes_text(
        ...     "0 <-> 2\\n"
        ...     "1 <-> 1\\n"
        ...     "2 <-> 0, 3, 4\\n"
        ...     "3 <-> 2, 4\\n"
        ...     "4 <-> 2, 3, 6\\n"
        ...     "5 <-> 6\\n"
        ...     "6 <-> 4, 5\\n"
        ... ).get_groups())))
        [(0, 2, 3, 4, 5, 6), (1,)]
        """
        return {
            id(group): group
            for group in self.groups.values()
        }.values()


Challenge.main()
challenge = Challenge()
