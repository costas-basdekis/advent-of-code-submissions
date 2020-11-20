#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2018.day_08 import part_a


def solve(_input=None):
    """
    >>> solve()
    20839
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return NodeExtended.from_nodes_text(_input).get_value()


class NodeExtended(part_a.Node):
    def get_value(self):
        """
        >>> NodeExtended\\
        ...     .from_nodes_text("2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2")\\
        ...     .get_value()
        66
        >>> NodeExtended((), ()).get_value()
        0
        >>> NodeExtended((), (1, 2, 3)).get_value()
        6
        >>> NodeExtended((NodeExtended((), (1, 2, 3)),), (1,)).get_value()
        6
        >>> NodeExtended((NodeExtended((), (1, 2, 3)),), (1, 1)).get_value()
        12
        >>> NodeExtended((NodeExtended((), (1, 2, 3)),), (2, 1, 2)).get_value()
        6
        """
        if self.children:
            children_values = {
                index: (
                    self.children[index - 1].get_value()
                    if index - 1 < len(self.children) else
                    0
                )
                for index in set(self.metadata)
            }
            return sum(
                children_values[index]
                for index in self.metadata
            )
        else:
            return self.metadata_sum()


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
