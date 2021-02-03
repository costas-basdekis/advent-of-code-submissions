#!/usr/bin/env python3
import functools
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        7128
        """
        return Groups.from_groups_text(_input)\
            .get_total_collective_answer_count()


class Group(namedtuple("Group", ("answers",))):
    @classmethod
    def from_group_text(cls, group_text):
        """
        >>> Group.from_group_text("abcx\\nabcy\\nabcz").answers
        (('a', 'b', 'c', 'x'), ('a', 'b', 'c', 'y'), ('a', 'b', 'c', 'z'))
        >>> Group.from_group_text("abcx\\nabcy\\nabcz\\n").answers
        (('a', 'b', 'c', 'x'), ('a', 'b', 'c', 'y'), ('a', 'b', 'c', 'z'))
        >>> Group.from_group_text("abcx\\nabcy\\n\\nabcz\\n").answers
        Traceback (most recent call last):
        ...
        Exception: Some answers where empty
        """
        lines = group_text.splitlines()
        answers = tuple(map(tuple, lines))
        if not all(answers):
            raise Exception("Some answers where empty")

        return cls(answers)

    def get_collective_answer_count(self):
        return len(self.get_collective_answers())

    def get_collective_answers(self):
        """
        >>> Group.from_group_text("abcx\\nabcy\\nabcz").get_collective_answers()
        ('a', 'b', 'c', 'x', 'y', 'z')
        """
        common_answers = functools.reduce(set.__or__, map(set, self.answers))
        return tuple(sorted(common_answers))


class Groups:
    group_class = Group

    @classmethod
    def from_groups_text(cls, groups_text):
        """
        >>> tuple(group.answers for group in Groups.from_groups_text(
        ...     "abc\\n\\na\\nb\\nc\\n\\nab\\nac\\n\\na\\na\\na\\na\\n\\n"\\
        ...     "b\\n").groups)
        ((('a', 'b', 'c'),), (('a',), ('b',), ('c',)), (('a', 'b'), ('a', 'c')), (('a',), ('a',), ('a',), ('a',)), (('b',),))
        """
        group_texts = groups_text.split('\n\n')
        return cls(list(map(cls.group_class.from_group_text, group_texts)))

    def __init__(self, groups):
        self.groups = groups

    def get_total_collective_answer_count(self):
        """
        >>> Groups.from_groups_text(
        ...     "abc\\n\\na\\nb\\nc\\n\\nab\\nac\\n\\na\\na\\na\\na\\n\\n"\\
        ...     "b\\n").get_total_collective_answer_count()
        11
        """
        return sum(map(self.group_class.get_collective_answer_count, self.groups))


Challenge.main()
challenge = Challenge()
