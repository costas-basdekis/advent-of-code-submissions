#!/usr/bin/env python3
import re
from abc import ABC
from typing import List

import utils
from year_2017.day_09 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        7314
        """
        return NodeExtended.from_node_text(_input.strip()).get_garbage_count()


class NodeExtended(part_a.Node, ABC):
    garbage_class = NotImplemented
    group_class = NotImplemented

    def get_garbage_count(self):
        raise NotImplementedError()


class GarbageExtended(NodeExtended, part_a.Garbage):
    def get_garbage_count(self):
        """
        >>> GarbageExtended.parse('<>')[0].get_garbage_count()
        0
        >>> GarbageExtended.parse('<random characters>')[0].get_garbage_count()
        17
        >>> GarbageExtended.parse('<<<<>')[0].get_garbage_count()
        3
        >>> GarbageExtended.parse('<{!>}>')[0].get_garbage_count()
        2
        >>> GarbageExtended.parse('<!!>')[0].get_garbage_count()
        0
        >>> GarbageExtended.parse('<!!!>>')[0].get_garbage_count()
        0
        >>> GarbageExtended.parse('<{o"i!a,<{i<a>')[0].get_garbage_count()
        10
        """
        return len(re.sub(rf"{self.ESCAPE}.", '', self.contents))


NodeExtended.garbage_class = GarbageExtended


class GroupExtended(NodeExtended, part_a.Group):
    contents: List['GroupExtended']

    def get_garbage_count(self):
        return sum(
            content.get_garbage_count()
            for content in self.contents
        )


NodeExtended.group_class = GroupExtended


challenge = Challenge()
challenge.main()
