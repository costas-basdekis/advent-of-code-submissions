#!/usr/bin/env python3
import itertools
import string
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        4398
        """
        return Dangers.from_dangers_text(_input)\
            .to_danger_map()\
            .fill_closest()\
            .get_largest_finite_area()


class DangerMap:
    EMPTY = 'empty'
    OVERLAP = 'overlap'

    @classmethod
    def from_dangers(cls, dangers):
        """
        >>> DangerMap.from_dangers([Danger(1, 1), Danger(2, 2)]).lines
        [['empty', 'empty', 'empty', 'empty'], ['empty', 0, 'empty', 'empty'], ['empty', 'empty', 1, 'empty'], ['empty', 'empty', 'empty', 'empty']]
        """
        min_x, max_x, min_y, max_y = cls.get_border(dangers)

        return cls(dangers, [
            [
                dangers.index(Danger(x, y))
                if Danger(x, y) in dangers else
                cls.EMPTY
                for x in range(min_x - 1, max_x + 2)
            ]
            for y in range(min_y - 1, max_y + 2)
        ])

    @classmethod
    def get_border(cls, dangers):
        min_x = min(danger.x for danger in dangers)
        max_x = max(danger.x for danger in dangers)
        min_y = min(danger.y for danger in dangers)
        max_y = max(danger.y for danger in dangers)
        return min_x, max_x, min_y, max_y

    def __init__(self, dangers, lines):
        self.dangers = dangers
        self.lines = lines

    def show(self):
        """
        >>> print("!", DangerMap.from_dangers([Danger(1, 1), Danger(2, 2)]).show())
        ! ....
        .A..
        ..B.
        ....
        >>> print("!", Dangers.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
        ... ).to_danger_map().show())
        ! ..........
        .A........
        ..........
        ........C.
        ...D......
        .....E....
        .B........
        ..........
        ..........
        ........F.
        ..........
        """
        return "\n".join(
            "".join(
                self.get_danger_show_letter(index)
                for x, index in enumerate(line)
            )
            for y, line in enumerate(self.lines)
        )

    def get_danger_show_letter(self, index):
        """
        >>> DangerMap([], []).get_danger_show_letter(DangerMap.EMPTY)
        '.'
        >>> DangerMap([], []).get_danger_show_letter(DangerMap.OVERLAP)
        '-'
        >>> DangerMap([], []).get_danger_show_letter(0)
        'A'
        >>> DangerMap([], []).get_danger_show_letter(10)
        'K'
        >>> DangerMap([], []).get_danger_show_letter(-1)
        'a'
        >>> DangerMap([], []).get_danger_show_letter(-11)
        'k'
        """
        if index == self.EMPTY:
            return "."
        if index == self.OVERLAP:
            return "-"
        if self.is_influence_index(index):
            letters = string.ascii_lowercase
            letter_index = self.influence_index_to_danger_index(index)
        else:
            letters = string.ascii_uppercase
            letter_index = index
        return letters[letter_index % len(letters)]

    def danger_index_to_influence_index(self, index):
        """
        >>> DangerMap([], []).danger_index_to_influence_index(-1)
        Traceback (most recent call last):
        ...
        Exception: An influence index was passed
        >>> DangerMap([], []).danger_index_to_influence_index(0)
        -1
        >>> DangerMap([], []).danger_index_to_influence_index(10)
        -11
        """
        if self.is_influence_index(index):
            raise Exception("An influence index was passed")
        return -index - 1

    def is_influence_index(self, index):
        """
        >>> DangerMap([], []).is_influence_index(DangerMap.EMPTY)
        False
        >>> DangerMap([], []).is_influence_index(DangerMap.OVERLAP)
        False
        >>> DangerMap([], []).is_influence_index(0)
        False
        >>> DangerMap([], []).is_influence_index(10)
        False
        >>> DangerMap([], []).is_influence_index(-1)
        True
        >>> DangerMap([], []).is_influence_index(-11)
        True
        """
        if index in (self.EMPTY, self.OVERLAP):
            return False
        return index < 0

    def influence_index_to_danger_index(self, influence_index):
        """
        >>> DangerMap([], []).influence_index_to_danger_index(0)
        Traceback (most recent call last):
        ...
        Exception: A danger index was passed
        >>> DangerMap([], []).influence_index_to_danger_index(-1)
        0
        >>> DangerMap([], []).influence_index_to_danger_index(-11)
        10
        """
        if not self.is_influence_index(influence_index):
            raise Exception("A danger index was passed")
        return -influence_index - 1

    def fill_closest(self):
        """
        >>> print(
        ...     DangerMap.from_dangers([Danger(1, 1)])
        ...     .fill_closest()
        ...     .show())
        aaa
        aAa
        aaa
        >>> print(
        ...     DangerMap.from_dangers([Danger(1, 1), Danger(2, 2)])
        ...     .fill_closest()
        ...     .show())
        aa--
        aA--
        --Bb
        --bb
        >>> print(Dangers.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
        ... ).to_danger_map().fill_closest().show())
        aaaaa-cccc
        aAaaa-cccc
        aaaddecccc
        aadddeccCc
        --dDdeeccc
        bb-deEeecc
        bBb-eeee--
        bbb-eeefff
        bbb-eeffff
        bbb-ffffFf
        bbb-ffffff
        """
        self.lines = [
            [
                self.get_closest_index(x, y)
                for x, index in enumerate(line)
            ]
            for y, line in enumerate(self.lines)
        ]
        return self

    def get_closest_index(self, x, y):
        """
        >>> DangerMap.from_dangers([Danger(1, 1)]).get_closest_index(1, 1)
        0
        >>> DangerMap.from_dangers([Danger(1, 1)]).get_closest_index(0, 1)
        -1
        """
        if not self.dangers:
            raise Exception("No dangers")

        distance_by_danger = {
            danger: danger.get_distance_from_point(x, y)
            for danger in self.dangers
        }
        min_distance = min(distance_by_danger.values())
        min_distance_dangers = [
            danger
            for danger, distance in distance_by_danger.items()
            if distance == min_distance
        ]
        if len(min_distance_dangers) > 1:
            return self.OVERLAP

        closest_danger, = min_distance_dangers
        if min_distance == 0:
            return self.dangers.index(closest_danger)

        return -1 - self.dangers.index(closest_danger)

    def get_infinite_indexes(self):
        """
        >>> sorted(Dangers.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
        ... ).to_danger_map().fill_closest().get_infinite_indexes())
        [0, 1, 2, 5]
        """
        indexes_at_borders = set(self.lines[0]) | set(self.lines[-1]) | {
            line[0]
            for line in self.lines
        } | {
            line[-1]
            for line in self.lines
        }
        indexes_at_borders -= {self.EMPTY, self.OVERLAP}
        if any(index >= 0 for index in indexes_at_borders):
            raise Exception("Some indexes at the border where of dangers")
        return {
            self.influence_index_to_danger_index(index)
            for index in indexes_at_borders
        }

    def get_areas_of_finite_influence(self):
        """
        >>> Dangers.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
        ... ).to_danger_map().fill_closest().get_areas_of_finite_influence()
        {3: 9, 4: 17}
        """
        infinite_indexes = self.get_infinite_indexes()
        return {
            index: count + 1
            for index, count in sorted(
                (self.influence_index_to_danger_index(index), len(list(items)))
                for index, items
                in itertools.groupby(sorted(
                    index
                    for index in sum(self.lines, [])
                    if index not in (self.EMPTY, self.OVERLAP)
                ))
                if self.is_influence_index(index)
            )
            if index not in infinite_indexes
        }

    def get_largest_finite_area(self):
        """
        >>> Dangers.from_tuples(
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
        ... ).to_danger_map().fill_closest().get_largest_finite_area()
        17
        """
        areas_of_finite_influence = self.get_areas_of_finite_influence()

        return max(areas_of_finite_influence.values())


class Dangers:
    @classmethod
    def from_dangers_text(cls, dangers_text):
        """
        >>> list(map(tuple, Dangers.from_dangers_text(
        ...     "1, 1\\n"
        ...     "1, 6\\n"
        ...     "8, 3\\n"
        ...     "3, 4\\n"
        ...     "5, 5\\n"
        ...     "8, 9\\n"
        ... ).dangers))
        [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]
        """
        lines = dangers_text.splitlines()
        non_empty_lines = filter(None, lines)
        return cls(list(map(Danger.from_danger_text, non_empty_lines)))

    @classmethod
    def from_tuples(cls, tuples):
        """
        >>> Dangers.from_tuples(\\
        ...     [(1, 1), (1, 6), (8, 3), (3, 4), (5, 5), (8, 9)]).dangers[:3]
        [Danger(x=1, y=1), Danger(x=1, y=6), Danger(x=8, y=3)]
        """
        return cls(list(map(Danger.from_tuple, tuples)))

    def __init__(self, dangers):
        self.dangers = dangers

    def to_danger_map(self, danger_map_class=DangerMap):
        return danger_map_class.from_dangers(self.dangers)


class Danger(namedtuple("Danger", ("x", "y"))):
    @classmethod
    def from_danger_text(cls, danger_text):
        """
        >>> Danger.from_danger_text("1, 1")
        Danger(x=1, y=1)
        >>> Danger.from_danger_text("-2, 3")
        Danger(x=-2, y=3)
        """
        x_str, y_str = danger_text.strip().split(", ")
        return cls(int(x_str), int(y_str))

    @classmethod
    def from_tuple(cls, _tuple):
        """
        >>> Danger.from_tuple((1, 1))
        Danger(x=1, y=1)
        >>> Danger.from_tuple((-2, 3))
        Danger(x=-2, y=3)
        """
        return cls(*_tuple)

    def get_distance_from_point(self, x, y):
        """
        >>> Danger(1, 1).get_distance_from_point(1, 1)
        0
        >>> Danger(1, 1).get_distance_from_point(1, 2)
        1
        >>> Danger(1, 1).get_distance_from_point(2, 1)
        1
        >>> Danger(1, 1).get_distance_from_point(-5, 4)
        9
        """
        return abs(x - self.x) + abs(y - self.y)


challenge = Challenge()
challenge.main()
