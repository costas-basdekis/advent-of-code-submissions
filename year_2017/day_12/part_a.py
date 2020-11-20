#!/usr/bin/env python3
import functools
import re
from dataclasses import dataclass
from typing import Dict, Set

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        113
        """
        return Network.from_pipes_text(_input).get_group_size(0)


@dataclass
class Network:
    groups: Dict[int, Set[int]]

    re_pipe = re.compile(r'^(\d+) <-> ((?:\d+)(?:, \d+)*)$')

    @classmethod
    def from_pipes_text(cls, pipes_text):
        groups = {}
        for line in pipes_text.strip().splitlines():
            main_str, pipes_str = cls.re_pipe.match(line).groups()
            main = int(main_str)
            pipes = set(map(int, pipes_str.split(', ')))
            programs = pipes | {main}
            programs_groups = [
                groups[program]
                for program in programs
                if program in groups
            ] + [programs]
            group = functools.reduce(set.__or__, programs_groups)
            groups.update({
                program: group
                for program in group
            })

        return cls(groups)

    def get_group_size(self, program):
        """
        >>> Network.from_pipes_text(
        ...     "0 <-> 2\\n"
        ...     "1 <-> 1\\n"
        ...     "2 <-> 0, 3, 4\\n"
        ...     "3 <-> 2, 4\\n"
        ...     "4 <-> 2, 3, 6\\n"
        ...     "5 <-> 6\\n"
        ...     "6 <-> 4, 5\\n"
        ... ).get_group_size(0)
        6
        """
        return len(self.get_group(program))

    def get_group(self, program):
        """
        >>> sorted(Network.from_pipes_text(
        ...     "0 <-> 2\\n"
        ...     "1 <-> 1\\n"
        ...     "2 <-> 0, 3, 4\\n"
        ...     "3 <-> 2, 4\\n"
        ...     "4 <-> 2, 3, 6\\n"
        ...     "5 <-> 6\\n"
        ...     "6 <-> 4, 5\\n"
        ... ).get_group(0))
        [0, 2, 3, 4, 5, 6]
        """
        return self.groups[program]


challenge = Challenge()
challenge.main()
