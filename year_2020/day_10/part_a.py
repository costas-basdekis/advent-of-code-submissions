#!/usr/bin/env python3
import doctest
import itertools

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    2232
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    diff_1_count, diff_3_count = AdapterSet.from_adapter_text(_input)\
        .get_adapter_sequence_1_and_3_difference_count()

    return diff_1_count * diff_3_count


class AdapterSet:
    @classmethod
    def from_adapter_text(cls, adapter_text):
        """
        >>> AdapterSet.from_adapter_text(
        ...     "16\\n10\\n15\\n5\\n1\\n11\\n7\\n19\\n6\\n12\\n4").adapters
        [16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22]
        """
        adapters = list(map(int, filter(None, adapter_text.splitlines())))
        builtin_adapter = max(adapters) + 3
        return cls(adapters + [builtin_adapter])

    def __init__(self, adapters):
        self.adapters = adapters

    def get_adapter_sequence_1_and_3_difference_count(
            self, outlet=0, max_gap=3):
        """
        >>> AdapterSet.from_adapter_text(
        ...     "28\\n33\\n18\\n42\\n31\\n14\\n46\\n20\\n48\\n47\\n24\\n23\\n"
        ...     "49\\n45\\n19\\n38\\n39\\n11\\n1\\n32\\n25\\n35\\n8\\n17\\n7"
        ...     "\\n9\\n4\\n2\\n34\\n10\\n3\\n")\\
        ...     .get_adapter_sequence_1_and_3_difference_count()
        (22, 10)
        """
        sequence = self.get_adapter_sequence(outlet, max_gap)
        return self.get_sequence_1_and_3_difference_count(sequence)

    def get_adapter_sequence(self, outlet=0, max_gap=3):
        """
        >>> AdapterSet([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22])\\
        ...     .get_adapter_sequence()
        [0, 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22]
        >>> AdapterSet([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22])\\
        ...     .get_adapter_sequence(1)
        [1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22]
        >>> AdapterSet([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22])\\
        ...     .get_adapter_sequence(-5)
        [-5]
        >>> AdapterSet([16, 10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22])\\
        ...     .get_adapter_sequence(3)
        [3, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22]
        >>> AdapterSet([10, 15, 5, 1, 11, 7, 19, 6, 12, 4, 22])\\
        ...     .get_adapter_sequence(11)
        [11, 12, 15]
        """
        sequence = sorted(self.adapters)
        if sequence[0] > outlet + max_gap:
            return [outlet]

        too_big_gap_indexes = (
            index
            for index, (previous, current)
            in enumerate(zip(sequence, sequence[1:]), 1)
            if current - previous > max_gap
        )
        first_big_gap_index = next(iter(too_big_gap_indexes), None)
        if first_big_gap_index is not None:
            sequence = sequence[:first_big_gap_index]

        reachable_indexes = (
            index
            for index, adapter in enumerate(sequence)
            if 0 <= (adapter - outlet) <= max_gap
        )
        first_reachable_index = next(iter(reachable_indexes), None)
        if first_reachable_index is None:
            return [outlet]
        sequence = sequence[first_reachable_index:]

        return sorted(set([outlet] + sequence))

    def get_sequence_1_and_3_difference_count(self, sequence):
        """
        >>> AdapterSet([]).get_sequence_1_and_3_difference_count(
        ...     [0, 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, 22])
        (7, 5)
        """
        difference_counts = {
            difference: sum(1 for _ in values)
            for difference, values in itertools.groupby(sorted(
                current - previous
                for previous, current in zip(sequence, sequence[1:])
            ))
        }

        return difference_counts.get(1, 0), difference_counts.get(3, 0)


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
