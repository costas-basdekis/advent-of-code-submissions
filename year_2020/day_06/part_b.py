#!/usr/bin/env python3
import doctest
import functools

from utils import get_current_directory
from year_2020.day_06 import part_a


def solve(_input=None):
    """
    >>> solve()
    3640
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return GroupsExtended.from_groups_text(_input)\
        .get_total_common_answer_count()


class GroupExtended(part_a.Group):
    def get_common_answer_count(self):
        return len(self.get_common_answers())

    def get_common_answers(self):
        """
        >>> GroupExtended.from_group_text("abcx\\nabcy\\nabcz")\\
        ...     .get_common_answers()
        ('a', 'b', 'c')
        """
        common_answers = functools.reduce(set.__and__, map(set, self.answers))
        return tuple(sorted(common_answers))


class GroupsExtended(part_a.Groups):
    group_class = GroupExtended

    def get_total_common_answer_count(self):
        """
        >>> GroupsExtended.from_groups_text(
        ...     "abc\\n\\na\\nb\\nc\\n\\nab\\nac\\n\\na\\na\\na\\na\\n\\n"\\
        ...     "b\\n").get_total_common_answer_count()
        6
        """
        return sum(map(self.group_class.get_common_answer_count, self.groups))


if __name__ == '__main__':
    if doctest.testmod(part_a).failed or doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
