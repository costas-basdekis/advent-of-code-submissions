import doctest
import math
import os
import sys
from collections import namedtuple
from pathlib import Path


def get_current_directory(file_path):
    return Path(os.path.dirname(os.path.realpath(file_path)))


def get_input(module_file):
    return get_current_directory(module_file)\
        .joinpath("part_a_input.txt")\
        .read_text()


class BaseChallenge:
    part_a_for_testing = None
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

    def __init__(self):
        self.module = sys.modules[self.__module__]
        self.input = self.get_input()

    def get_input(self):
        return get_input(self.module.__file__)

    def main(self, sys_args=None):
        main_module = sys.modules.get('__main__')
        if self.module != main_module:
            return
        arguments = self.get_main_arguments(sys_args=sys_args)
        self.run_main_arguments(arguments)

    def get_main_arguments(self, sys_args=None):
        if sys_args is None:
            sys_args = sys.argv
        if len(sys_args) > 2:
            raise Exception(
                "Only 1 optional argument is acceptable: run, test, play")
        if len(sys_args) == 2:
            argument = sys_args[1]
            if argument not in ('run', 'test', 'play'):
                raise Exception(
                    f"Only 1 optional argument is acceptable: run, test, play "
                    f"- not {argument}")
        else:
            argument = None

        return [argument]

    def run_main_arguments(self, arguments):
        argument, = arguments
        if argument in (None, 'test'):
            self.test()
        if argument in (None, 'run'):
            self.run()
        if argument == 'play':
            self.play()

    def default_solve(self, _input=None):
        if _input is None:
            _input = self.input
        return self.solve(_input)

    def solve(self, _input):
        raise NotImplementedError()

    def play(self):
        raise Exception(f"Challenge has not implemented play")

    def test(self):
        failed = sum(
            doctest.testmod(module, optionflags=self.optionflags).failed
            for module in self.get_test_modules()
        )
        if failed:
            print("Tests failed")
        else:
            print("Tests passed")

    def get_test_modules(self):
        modules = [
            __import__(__name__),
            None,
        ]
        if self.part_a_for_testing:
            modules.append(self.part_a_for_testing)
        return modules

    def run(self):
        print("Solution:", self.default_solve())


class Helper:
    MANHATTAN_OFFSETS = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    def get_manhattan_neighbours(self, position):
        """
        >>> sorted(Helper().get_manhattan_neighbours((0, 0)))
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        >>> sorted(Helper().get_manhattan_neighbours((-3, 5)))
        [(-4, 5), (-3, 4), (-3, 6), (-2, 5)]
        """
        return [
            self.add_points(position, offset)
            for offset in self.MANHATTAN_OFFSETS
        ]

    def add_points(self, lhs, rhs):
        """
        >>> Helper().add_points((0, 0), (0, 0))
        (0, 0)
        >>> Helper().add_points((1, -4), (-2, 5))
        (-1, 1)
        """
        l_x, l_y = lhs
        r_x, r_y = rhs

        return l_x + r_x, l_y + r_y

    def iterable_length(self, iterable):
        return sum(1 for _ in iterable)


class BasePoint:
    _fields = NotImplemented
    coordinates_names = NotImplemented

    @classmethod
    def from_int_texts(cls, *coordinate_strs, **named_coordinate_strs):
        """
        >>> Point3D.from_int_texts("1", "2", "3")
        Point3D(x=1, y=2, z=3)
        >>> Point3D.from_int_texts(x="1", y="2", z="3")
        Point3D(x=1, y=2, z=3)
        >>> Point3D.from_int_texts("1", y="2", z="3")
        Point3D(x=1, y=2, z=3)
        >>> Point3D.from_int_texts("1", z="3", y="2")
        Point3D(x=1, y=2, z=3)
        """
        coordinate_strs = coordinate_strs + tuple(
            named_coordinate_strs.pop(name)
            for name in cls.coordinates_names[len(coordinate_strs):]
        )
        if named_coordinate_strs:
            raise Exception(
                f"Too many arguments: {sorted(named_coordinate_strs)}")
        if len(coordinate_strs) != len(cls.coordinates_names):
            raise Exception(
                f"Expected {len(cls.coordinates_names)} coordinates but got "
                f"{len(coordinate_strs)}")
        # noinspection PyArgumentList
        return cls(*map(int, coordinate_strs))

    @property
    def coordinates(self):
        """
        >>> Point3D(1, 2, 3).coordinates
        Point3D(x=1, y=2, z=3)
        >>> tuple(zip(
        ...     Point3D(1, 2, 3).coordinates, Point3D(4, 5, 6).coordinates))
        ((1, 4), (2, 5), (3, 6))
        """
        if self.coordinates_names is NotImplemented:
            raise Exception(
                f"{type(self).__name__} did not specify 'coordinates_names'")
        # noinspection PyUnresolvedReferences
        if self.coordinates_names == self._fields:
            return self
        # noinspection PyTypeChecker
        return tuple(
            getattr(self, coordinate_name)
            for coordinate_name in self.coordinates_names
        )

    def distance(self, other):
        """
        >>> Point3D(0, 0, 0).distance(Point3D(0, 0, 0))
        0.0
        >>> Point3D(0, 0, 0).distance(Point3D(2, 3, -4))
        5.385164807134504
        >>> Point3D(0, 0, 0).distance(Point3D(0, 3, -4))
        5.0
        """
        return math.sqrt(sum(
            (my_coordinate - other_coordinate) ** 2
            for my_coordinate, other_coordinate
            in zip(self.coordinates, other.coordinates)
        ))

    def manhattan_distance(self, other):
        """
        >>> Point3D(0, 0, 0).manhattan_distance(Point3D(0, 0, 0))
        0
        >>> Point3D(0, 0, 0).manhattan_distance(Point3D(2, 3, -4))
        9
        """
        return sum(
            abs(my_coordinate - other_coordinate)
            for my_coordinate, other_coordinate
            in zip(self.coordinates, other.coordinates)
        )


class Point2D(namedtuple("Point2D", ("x", "y")), BasePoint):
    coordinates_names = ("x", "y")


class Point3D(namedtuple("Point3D", ("x", "y", "z")), BasePoint):
    coordinates_names = ("x", "y", "z")


helper = Helper()


if __name__ == "__main__":
    if doctest.testmod(optionflags=BaseChallenge.optionflags).failed:
        print("Tests failed")
    else:
        print("Tests passed")
