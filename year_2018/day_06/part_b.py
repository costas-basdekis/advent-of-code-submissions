#!/usr/bin/env python3
import doctest
import itertools

from utils import get_current_directory
from year_2018.day_06 import part_a


def solve(_input=None):
    """
    >>> solve()
    39560
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return ExtendedDangerMap.from_dangers_text(_input)\
        .get_point_count_with_maximum_total_distance(10000)


class ExtendedDangerMap(part_a.DangerMap):
    @classmethod
    def from_tuples(cls, tuples):
        return part_a.Dangers.from_tuples(tuples)\
            .to_danger_map(danger_map_class=cls)

    @classmethod
    def from_dangers_text(cls, dangers_text):
        return part_a.Dangers.from_dangers_text(dangers_text)\
            .to_danger_map(danger_map_class=cls)

    def get_point_count_with_maximum_total_distance(
            self, maximum_distance, max_padding=None):
        """
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance(32)
        16
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1)])\\
        ...     .get_point_count_with_maximum_total_distance(32)
        1985
        """
        return (
            self.get_point_count_with_maximum_total_distance_inside_border(
                maximum_distance)
            + self.get_point_count_with_maximum_total_distance_outside_border(
                maximum_distance, max_padding=max_padding)
        )

    def get_point_count_with_maximum_total_distance_outside_border(
            self, maximum_distance, max_padding=None):
        """
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance_outside_border(32)
        0
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1)])\\
        ...     .get_point_count_with_maximum_total_distance_outside_border(32)
        1984
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1)])\\
        ...     .get_point_count_with_maximum_total_distance_outside_border(10000, 5)
        Traceback (most recent call last):
        ...
        Exception: Too much padding: 5 exceeds 5 (previous padding count was 32)
        """
        count = 0
        padding_count = -1
        for padding in itertools.count(1):
            if max_padding is not None and padding >= max_padding:
                raise Exception(
                    f"Too much padding: {padding} exceeds {max_padding} "
                    f"(previous padding count was {padding_count})")
            padding_count = self\
                .get_point_count_with_maximum_total_distance_around_border(
                    maximum_distance, padding)
            if not padding_count:
                break
            count += padding_count

        return count

    def get_point_count_with_maximum_total_distance_around_border(
            self, maximum_distance, padding):
        """
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance_around_border(32, 0)
        0
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance_around_border(32, 1)
        0
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1)])\\
        ...     .get_point_count_with_maximum_total_distance_around_border(32, 0)
        1
        """
        border = self.get_border(self.dangers)
        return self.get_point_count_with_maximum_total_distance_in_points(
            maximum_distance,
            self.get_border_with_padding_points(border, padding))

    def get_border_with_padding_points(self, border, padding):
        """
        >>> sorted(ExtendedDangerMap([], []).get_border_with_padding_points(
        ...     (1, 2, 1, 2), 0))
        [(1, 1), (1, 2), (2, 1), (2, 2)]
        >>> sorted(ExtendedDangerMap([], []).get_border_with_padding_points(
        ...     (1, 2, 1, 2), 1))
        [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0), (1, 3), (2, 0), (2, 3), (3, 0), (3, 1), (3, 2), (3, 3)]
        >>> danger_map_a = ExtendedDangerMap.from_tuples([(1, 1)])
        >>> sorted(danger_map_a.get_border_with_padding_points(
        ...         danger_map_a.get_border(danger_map_a.dangers), 0))
        [(1, 1)]
        >>> sorted(danger_map_a.get_border_with_padding_points(
        ...         danger_map_a.get_border(danger_map_a.dangers), 1))
        [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
        """
        min_x, max_x, min_y, max_y = border
        for x in range(min_x - padding, max_x + 1 + padding):
            yield x, min_y - padding
        if max_y + padding != min_y - padding:
            for x in range(min_x - padding, max_x + 1 + padding):
                yield x, max_y + padding
        for y in range(min_y - padding + 1, max_y + 1 + padding - 1):
            yield min_x - padding, y
        if max_x + padding != min_x - padding:
            for y in range(min_y - padding + 1, max_y + 1 + padding - 1):
                yield max_x + padding, y

    def get_point_count_with_maximum_total_distance_inside_border(
            self, maximum_distance):
        """
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance_inside_border(32)
        16
        """
        min_x, max_x, min_y, max_y = self.get_border(self.dangers)
        return self.get_point_count_with_maximum_total_distance_in_points(
            maximum_distance, (
                (x, y)
                for x in range(min_x, max_x + 1)
                for y in range(min_y, max_y + 1)
            ))

    def get_point_count_with_maximum_total_distance_in_points(
            self, maximum_distance, points):
        """
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance_in_points(32, [
        ...         (3, 3), (3, 4), (4, 3), (4, 4),
        ...     ])
        4
        >>> ExtendedDangerMap.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)])\\
        ...     .get_point_count_with_maximum_total_distance_in_points(32, [
        ...         (2, 2), (2, 3), (3, 2), (3, 3),
        ...     ])
        1
        """
        return sum(
            1
            for x, y in points
            if self.get_total_distance(x, y) < maximum_distance
        )

    def get_total_distance(self, x, y):
        """
        >>> danger_map_a = ExtendedDangerMap\\
        ...     .from_dangers([part_a.Danger(1, 1)])\\
        ...     .fill_closest()
        >>> danger_map_a.get_total_distance(0, 0)
        2
        >>> danger_map_a.get_total_distance(1, 0)
        1
        >>> danger_map_a.get_total_distance(1, 1)
        0
        >>> danger_map_b = ExtendedDangerMap\\
        ...     .from_dangers([part_a.Danger(1, 1), part_a.Danger(2, 3)])\\
        ...     .fill_closest()
        >>> danger_map_b.get_total_distance(0, 0)
        7
        >>> danger_map_b.get_total_distance(1, 0)
        5
        >>> danger_map_b.get_total_distance(1, 1)
        3
        """
        return sum(
            danger.get_distance_from_point(x, y)
            for danger in self.dangers
        )


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
