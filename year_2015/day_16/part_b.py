#!/usr/bin/env python3
from typing import List

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        260
        """
        sample = SampleExtended.from_sample_text(
            "children: 3, cats: 7, samoyeds: 2, pomeranians: 3, akitas: 0, "
            "vizslas: 0, goldfish: 5, trees: 3, cars: 2, perfumes: 1")
        return AuntSetExtended.from_aunt_sues_text(_input)\
            .get_matching_aunt_id(sample)


class AuntSetExtended(part_a.AuntSet['SampleExtended']):
    pass


class SampleExtended(part_a.Sample):
    GREATER_THAN_FIELD_NAMES = {'cats', 'trees'}
    LESS_THAN_FIELD_NAMES = {'pomeranians', 'goldfish'}

    def is_value_from_sample_for(self, field_name: str,
                                 from_sample: int, from_other: int) -> bool:
        if field_name in self.GREATER_THAN_FIELD_NAMES:
            return from_other > from_sample
        elif field_name in self.LESS_THAN_FIELD_NAMES:
            return from_other < from_sample
        else:
            return super().is_value_from_sample_for(
                field_name, from_sample, from_other)


Challenge.main()
challenge = Challenge()
