#!/usr/bin/env python3
from itertools import combinations
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_18.part_a import SnailfishNumberSet


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        4685
        """
        return SnailfishNumberSetExtended\
            .from_numbers_text(_input)\
            .find_largest_2_sum_magnitude()


class SnailfishNumberSetExtended(SnailfishNumberSet):
    def find_largest_2_sum_magnitude(self) -> int:
        """
        >>> SnailfishNumberSetExtended.from_numbers_text('''
        ...     [[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
        ...     [[[5,[2,8]],4],[5,[[9,9],0]]]
        ...     [6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
        ...     [[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
        ...     [[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
        ...     [[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
        ...     [[[[5,4],[7,7]],8],[[8,3],8]]
        ...     [[9,3],[[9,9],[6,[4,9]]]]
        ...     [[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
        ...     [[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]
        ... ''').find_largest_2_sum_magnitude()
        3993
        """
        return max(
            (left + right).magnitude
            for first, second in combinations(self.numbers, 2)
            for left, right in [(first, second), (second, first)]
        )


Challenge.main()
challenge = Challenge()
