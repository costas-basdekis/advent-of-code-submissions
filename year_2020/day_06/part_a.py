#!/usr/bin/env python3
import doctest
import functools
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    7128
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return Groups.from_groups_text(_input).get_total_common_answer_count()


class Groups:
    @classmethod
    def from_groups_text(cls, groups_text):
        """
        >>> tuple(group.answers for group in Groups.from_groups_text(
        ...     "abc\\n\\na\\nb\\nc\\n\\nab\\nac\\n\\na\\na\\na\\na\\n\\n"\\
        ...     "b\\n").groups)
        ((('a', 'b', 'c'),), (('a',), ('b',), ('c',)), (('a', 'b'), ('a', 'c')), (('a',), ('a',), ('a',), ('a',)), (('b',),))
        """
        group_texts = groups_text.split('\n\n')
        return cls(list(map(Group.from_group_text, group_texts)))

    def __init__(self, groups):
        self.groups = groups

    def get_total_common_answer_count(self):
        """
        >>> Groups.from_groups_text(
        ...     "abc\\n\\na\\nb\\nc\\n\\nab\\nac\\n\\na\\na\\na\\na\\n\\n"\\
        ...     "b\\n").get_total_common_answer_count()
        11
        """
        return sum(map(Group.get_common_answer_count, self.groups))


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

    def get_common_answer_count(self):
        return len(self.get_common_answers())

    def get_common_answers(self):
        """
        >>> Group.from_group_text("abcx\\nabcy\\nabcz").get_common_answers()
        ('a', 'b', 'c', 'x', 'y', 'z')
        """
        common_answers = functools.reduce(
            set.__or__, map(set, self.answers), set())
        return tuple(sorted(common_answers))


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
