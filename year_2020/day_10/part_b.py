#!/usr/bin/env python3
import doctest
import functools
import itertools

from utils import get_current_directory
from year_2020.day_10 import part_a


def solve(_input=None):
    """
    >>> solve()
    173625106649344
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return AdapterSetExtended.from_adapter_text(_input)\
        .get_possible_arrangement_count()


class AdapterSetExtended(part_a.AdapterSet):
    def get_possible_arrangement_count(self, outlet=0, max_gap=3):
        """
        >>> AdapterSetExtended(
        ...     [16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22])\\
        ...     .get_possible_arrangement_count()
        8
        >>> AdapterSetExtended.from_adapter_text(
        ...     "28\\n33\\n18\\n42\\n31\\n14\\n46\\n20\\n48\\n47\\n24\\n23\\n"
        ...     "49\\n45\\n19\\n38\\n39\\n11\\n1\\n32\\n25\\n35\\n8\\n17\\n7"
        ...     "\\n9\\n4\\n2\\n34\\n10\\n3\\n")\\
        ...     .get_possible_arrangement_count()
        19208
        """
        sequence = self.get_adapter_sequence(outlet, max_gap)
        removals = self.get_possible_sequence_removals(sequence, max_gap)
        removal_groups = self.group_removals(removals, max_gap)
        non_sequential_groups = [
            (group, set(
                current - previous
                for previous, current
                in zip(group, group[1:])
            ))
            for group in removal_groups
            if set(
                current - previous
                for previous, current
                in zip(group, group[1:])
            ) not in (set(), {1})
        ]
        if non_sequential_groups:
            raise Exception(f"Cannot deal with non-sequential groups: {non_sequential_groups}")
        all_groups_are_not_wider_than_max_gap = all(
            group[-1] - group[0] <= max_gap
            for group in removal_groups
        )
        if not all_groups_are_not_wider_than_max_gap:
            raise Exception("Cannot deal with too wide groups")
        non_sequential_with_neighbours_groups = [
            (sequence[sequence.index(group[0]) - 1], group,
             sequence[sequence.index(group[-1]) + 1])
            for group in removal_groups
            if sequence[sequence.index(group[0]) - 1] != group[0] - 1
            or sequence[sequence.index(group[-1]) + 1] != group[-1] + 1
        ]
        if non_sequential_with_neighbours_groups:
            raise Exception(f"Cannot deal with groups not next to neighbours: {non_sequential_with_neighbours_groups}")
        return functools.reduce(int.__mul__, (
            sum(
                sum(1 for _ in itertools.combinations(group, count))
                for count in range(max_gap)
            )
            for group in removal_groups
        ), 1)

    def group_removals(self, removals, max_gap=3):
        """
        >>> AdapterSetExtended([]).group_removals([
        ...     1, 2, 10, 11, 12, 17, 18, 19, 24, 25, 26, 31, 32, 37, 38, 39,
        ...     44, 45, 46, 55, 63, 64, 65, 73, 74, 75, 80, 81, 82, 90, 98,
        ...     99, 100, 111, 112, 113, 122, 123, 124, 129, 130, 131, 136,
        ...     137, 138, 153, 154, 159, 160, 161,
        ... ])
        [(1, 2), (10, 11, 12), (17, 18, 19), (24, 25, 26), (31, 32), \
(37, 38, 39), (44, 45, 46), (55,), (63, 64, 65), (73, 74, 75), (80, 81, 82), \
(90,), (98, 99, 100), (111, 112, 113), (122, 123, 124), (129, 130, 131), \
(136, 137, 138), (153, 154), (159, 160, 161)]
        """
        groups = []
        for removal in removals:
            if not groups:
                groups.append((removal,))
                continue
            last_group = groups[-1]
            last_removal = last_group[-1]
            if last_removal + max_gap < removal:
                groups.append((removal,))
            else:
                groups[-1] += (removal,)

        return groups

    def get_possible_sequence_removals(self, sequence, max_gap=3):
        """
        >>> AdapterSetExtended([]).get_possible_sequence_removals(
        ...     [0, 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22])
        [5, 6, 11]
        """
        return [
            current
            for previous, current, _next
            in zip(sequence, sequence[1:], sequence[2:])
            if _next - previous <= max_gap
        ]


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
