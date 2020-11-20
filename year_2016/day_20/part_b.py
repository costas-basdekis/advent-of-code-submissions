#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        109
        """
        return FirewallExtended.from_ranges_text(_input)\
            .get_allowed_values_count()


class FirewallExtended(part_a.Firewall):
    def get_allowed_values_count(self) -> int:
        return len(self.total_range) - sum(map(len, self.blocked_ranges))


Challenge.main()
challenge = Challenge()
