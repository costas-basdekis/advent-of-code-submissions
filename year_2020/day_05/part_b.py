#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_05 import part_a


def solve(_input=None):
    """
    >>> solve()
    617
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return BoardingPassesExtended.from_passes_text(_input)\
        .find_missing_id_with_both_neighbours()


class BoardingPassExtended(part_a.BoardingPass):
    @classmethod
    def from_id(cls, _id):
        """
        >>> BoardingPassExtended.from_id(357)
        BoardingPassExtended(name='FBFBBFFRLR')
        >>> BoardingPassExtended.from_id(28)
        BoardingPassExtended(name='FFFFFBBRLL')
        >>> BoardingPassExtended.from_id(842)
        BoardingPassExtended(name='BBFBFFBLRL')
        """
        binary_id_str = "{:010b}".format(_id, 'b')
        binary_id_part_a, binary_id_part_b = \
            binary_id_str[:-3], binary_id_str[-3:]
        name_part_a = binary_id_part_a\
            .replace("0", "F")\
            .replace("1", "B")
        name_part_b = binary_id_part_b\
            .replace("0", "L")\
            .replace("1", "R")
        return cls(f"{name_part_a}{name_part_b}")


class BoardingPassesExtended(part_a.BoardingPasses):
    boarding_pass_class = BoardingPassExtended

    @classmethod
    def from_ids(cls, ids):
        return cls(list(map(BoardingPassExtended.from_id, ids)))

    def find_missing_id_with_both_neighbours(self):
        """
        >>> BoardingPassesExtended.from_ids([2, 3, 4, 5, 7, 8, 11, 12])\\
        ...     .find_missing_id_with_both_neighbours()
        6
        >>> BoardingPassesExtended.from_ids([11, 2, 8, 5, 7, 3, 12, 4])\\
        ...     .find_missing_id_with_both_neighbours()
        6
        >>> BoardingPassesExtended.from_ids([2, 3, 5, 6, 7, 9, 10, 11])\\
        ...     .find_missing_id_with_both_neighbours()
        Traceback (most recent call last):
        ...
        Exception: Found two with both neighbours: 4 and 8
        """
        ids = set(map(part_a.BoardingPass.get_seat_id, self.passes))
        min_id = min(ids)
        max_id = max(ids)
        found = None
        for current in range(min_id, max_id + 1):
            if current in ids:
                continue
            if current - 1 not in ids:
                continue
            if current + 1 not in ids:
                continue
            if found is not None:
                raise Exception(
                    f"Found two with both neighbours: {found} and {current}")
            found = current
        if not found:
            raise Exception(f"Could not find with both neighbours")

        return found

    def triplets(self, items):
        """
        >>> list(BoardingPassesExtended([]).triplets(range(5)))
        [(0, 1, 2), (1, 2, 3), (2, 3, 4)]
        """
        triplet = ()
        for item in items:
            triplet += (item,)
            if len(triplet) == 3:
                yield triplet
                triplet = triplet[1:]


if __name__ == '__main__':
    if doctest.testmod(part_a).failed or doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
