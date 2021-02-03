#!/usr/bin/env python3
import re

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        6323
        """
        return Cave.from_cave_description(_input).get_total_risk()


class Cave:
    re_line = re.compile(r"^([^:]+): (.+)$")
    re_target = re.compile(r"^(\d+),(\d+)$")

    TYPE_ROCKY = 'rocky'
    TYPE_WET = 'wet'
    TYPE_NARROW = 'narrow'

    @classmethod
    def from_cave_description(cls, cave_description):
        """
        >>> Cave.from_cave_description(
        ...     "depth: 510\\n"
        ...     "target: 10,10\\n"
        ... )
        Cave(depth=510, target=(10, 10))
        """
        key_value_texts = {
            key: value_str
            for key, value_str in (
                cls.re_line.match(line).groups()
                for line in filter(None, cave_description.splitlines())
            )
        }
        depth_str = key_value_texts['depth']
        depth = int(depth_str)
        target_str = key_value_texts['target']
        target_x_str, target_y_str = cls.re_target.match(target_str).groups()
        target_x, target_y = int(target_x_str), int(target_y_str)

        return cls(depth, (target_x, target_y))

    def __init__(self, depth, target, geological_indexes=None):
        self.depth = depth
        self.target = target
        self.geological_indexes = {(0, 0): 0, target: 0}
        if geological_indexes is not None:
            self.geological_indexes.update(geological_indexes)

    def __repr__(self):
        return (
            f"{type(self).__name__}(depth={self.depth}, target={self.target})"
        )

    def get_total_risk(self, max_x=None, max_y=None):
        """
        >>> Cave(510, (10, 10)).get_total_risk()
        114
        """
        if max_x is None:
            max_x, _ = self.target
        if max_y is None:
            _, max_y = self.target

        return sum(
            self.get_risk((x, y))
            for x in range(max_x + 1)
            for y in range(max_y + 1)
        )

    def get_geological_index(self, position):
        """
        >>> Cave(510, (10, 10)).get_geological_index((0, 0))
        0
        >>> Cave(510, (10, 10)).get_geological_index((10, 10))
        0
        >>> Cave(510, (10, 10)).get_geological_index((1, 0))
        16807
        """
        if position not in self.geological_indexes:
            x, y = position
            if x < 0 or y < 0:
                raise Exception(f"Position was out of bounds: {position}")

            if y == 0:
                geological_index = x * 16807
            elif x == 0:
                geological_index = y * 48271
            else:
                geological_index = (
                    self.get_erosion_level((x - 1, y))
                    * self.get_erosion_level((x, y - 1))
                )
            self.geological_indexes[position] = geological_index

        return self.geological_indexes[position]

    def get_erosion_level(self, position):
        """
        >>> Cave(510, (10, 10)).get_erosion_level((0, 0))
        510
        """
        geological_index = self.get_geological_index(position)
        return self.get_erosion_level_from_geological_index(geological_index)

    def get_erosion_level_from_geological_index(self, geological_index):
        """
        >>> Cave(510, (10, 10)).get_erosion_level_from_geological_index(0)
        510
        """
        return (geological_index + self.depth) % 20183

    def get_type(self, position):
        """
        >>> Cave(510, (10, 10)).get_type((0, 0))
        'rocky'
        """
        erosion_level = self.get_erosion_level(position)
        return self.get_type_from_erosion_level(erosion_level)

    EROSION_TYPE_MAP = {
        0: TYPE_ROCKY,
        1: TYPE_WET,
        2: TYPE_NARROW,
    }

    def get_type_from_erosion_level(self, erosion_level):
        """
        >>> Cave(510, (10, 10)).get_type_from_erosion_level(0)
        'rocky'
        """
        return self.EROSION_TYPE_MAP[erosion_level % 3]

    RISK_MAP = {
        TYPE_ROCKY: 0,
        TYPE_WET: 1,
        TYPE_NARROW: 2,
    }

    def get_risk(self, position):
        """
        >>> Cave(510, (10, 10)).get_risk((0, 0))
        0
        """
        get_type = self.get_type(position)
        return self.get_risk_from_type(get_type)

    def get_risk_from_type(self, get_type):
        """
        >>> Cave(510, (10, 10)).get_risk_from_type(Cave.TYPE_ROCKY)
        0
        """
        return self.RISK_MAP[get_type]

    SHOW_MAP = {
        TYPE_ROCKY: '.',
        TYPE_WET: '=',
        TYPE_NARROW: '|',
    }

    def show(self, max_x=None, max_y=None):
        """
        >>> print(Cave(depth=510, target=(10, 10)).show(15, 15))
        M=.|=.|.|=.|=|=.
        .|=|=|||..|.=...
        .==|....||=..|==
        =.|....|.==.|==.
        =|..==...=.|==..
        =||.=.=||=|=..|=
        |.=.===|||..=..|
        |..==||=.|==|===
        .=..===..=|.|||.
        .======|||=|=.|=
        .===|=|===T===||
        =|||...|==..|=.|
        =.=|=.=..=.||==|
        ||=|=...|==.=|==
        |=.=||===.|||===
        ||.|==.|.|.||=||
        """
        if max_x is None:
            max_x, _ = self.target
        if max_y is None:
            _, max_y = self.target

        return "\n".join(
            "".join(
                "M"
                if (x, y) == (0, 0) else
                "T"
                if (x, y) == self.target else
                self.SHOW_MAP[self.get_type((x, y))]
                for x in range(max_x + 1)
            )
            for y in range(max_y + 1)
        )


Challenge.main()
challenge = Challenge()
