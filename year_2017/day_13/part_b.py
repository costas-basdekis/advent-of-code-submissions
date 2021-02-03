#!/usr/bin/env python3
import functools
import math

import utils
from year_2017.day_13 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3913186
        """
        return FirewallExtended.from_firewall_text(_input)\
            .get_minimum_safe_delay()


class FirewallExtended(part_a.Firewall):
    def get_minimum_safe_delay(self):
        """
        >>> FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).get_minimum_safe_delay()
        10
        """
        scanner_lengths = {
            layer: self.get_scanner_length(_range)
            for layer, _range in self.layers.items()
        }
        scanner_period = functools.reduce(
            math.lcm, set(scanner_lengths.values()))
        scanners_0_steps = [
            range((length - layer) % length, scanner_period, length)
            for layer, length in scanner_lengths.items()
        ]
        safe_delays = (
            delay
            for delay in range(scanner_period)
            if not any(
                delay in scanner_0_steps
                for scanner_0_steps in scanners_0_steps
            )
        )
        return next(safe_delays)

    def delay(self, count):
        """
        >>> print(FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).delay(0).show())
         0   1   2   3   4   5   6
        [S] [S] ... ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        >>> print(FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).delay(1).show())
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        >>> print(FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).delay(3).show())
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... [ ]
        [S] [S]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [S]     [S]
        >>> print(FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).delay(4).show())
         0   1   2   3   4   5   6
        [S] [S] ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [ ]             [S]     [S]
                        [ ]     [ ]
        >>> print(FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).delay(5).show())
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        >>> print(FirewallExtended.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).delay(10).show())
         0   1   2   3   4   5   6
        [ ] [S] ... ... [ ] ... [ ]
        [ ] [ ]         [ ]     [ ]
        [S]             [S]     [S]
                        [ ]     [ ]
        """
        packet = self.packet
        for _ in range(count):
            self.step()
            self.packet = packet

        return self


Challenge.main()
challenge = Challenge()
