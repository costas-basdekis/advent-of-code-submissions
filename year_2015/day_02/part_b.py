#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        3812909
        """
        return PresentSetExtended.from_presents_text(_input)\
            .get_ribbon_requirement()


class PresentSetExtended(part_a.PresentSet['PresentExtended']):
    def get_ribbon_requirement(self) -> int:
        """
        >>> PresentSetExtended([]).get_ribbon_requirement()
        0
        >>> PresentSetExtended.from_presents_text("2x3x4\\n1x1x10\\n")\\
        ...     .get_ribbon_requirement()
        48
        """
        return sum(
            present.get_ribbon_requirement()
            for present in self.presents
        )


class PresentExtended(part_a.Present):
    def get_ribbon_requirement(self) -> int:
        """
        >>> PresentExtended.from_present_text("2x3x4").get_ribbon_requirement()
        34
        >>> PresentExtended.from_present_text("1x1x10").get_ribbon_requirement()
        14
        """
        a, b, c = self.dimensions

        return 2 * a + 2 * b + a * b * c


Challenge.main()
challenge = Challenge()
