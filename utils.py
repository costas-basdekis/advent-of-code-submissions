import doctest
import itertools
import math
import os
import sys
import timeit
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path
from typing import Tuple, List

import click


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
        test_modules = self.get_test_modules()
        with helper.time_it() as stats:
            results = [
                (module,
                 doctest.testmod(module, optionflags=self.optionflags))
                for module in test_modules
            ]
        total_attempted = sum(result.attempted for _, result in results)
        total_failed = sum(result.failed for _, result in results)
        failed_modules = [
            module.__name__
            if module else
            'main'
            for module, result in results
            if result.failed
        ]
        if failed_modules:
            styled_test_counts = click.style(
                f'{total_failed}/{total_attempted} tests', fg='red')
            print(
                f"{styled_test_counts} "
                f"in {len(failed_modules)}/{len(test_modules)} modules "
                f"{click.style('failed', fg='red')} "
                f"in {round(stats['duration'], 2)}s"
                f": {click.style(', '.join(failed_modules), fg='red')}")
        else:
            print(
                f"{total_attempted} tests "
                f"in {len(test_modules)} modules "
                f"{click.style('passed', fg='green')} "
                f"in {round(stats['duration'], 2)}s")

    def get_test_modules(self):
        modules = [
            __import__(__name__),
            None,
        ]
        if self.part_a_for_testing:
            modules.append(self.part_a_for_testing)
        return modules

    def run(self):
        with helper.time_it() as stats:
            solution = self.default_solve()
        if solution is None:
            styled_solution = click.style(str(solution), fg='red')
        else:
            styled_solution = click.style(str(solution), fg='green')
        click.echo(
            f"Solution: {styled_solution}"
            f" (in {round(stats['duration'], 2)}s)")


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

    @contextmanager
    def time_it(self):
        start = timeit.default_timer()
        stats = {'start': start, 'end': None, 'duration': None}
        yield stats
        end = timeit.default_timer()
        stats.update({'end': end, 'duration': end - start})


class BasePointMeta(type):
    @classmethod
    def auto_assign_to(mcs, attribute):
        def decorator(method):
            method.auto_assign_to = attribute
            return method

        return decorator

    def __new__(mcs, *args, **kwargs):
        # noinspection PyPep8Naming
        Point = super().__new__(mcs, *args, **kwargs)

        mcs.assign_auto_attributes(mcs, Point)

        return Point

    # noinspection PyPep8Naming
    def assign_auto_attributes(cls, Point):
        if Point.__name__ == 'BasePoint':
            return
        for name in dir(Point):
            attribute = getattr(Point, name)
            if attribute == cls:
                continue
            auto_assign_to = getattr(attribute, 'auto_assign_to', None)
            if auto_assign_to is None:
                continue
            setattr(Point, auto_assign_to, attribute())


class BasePoint(metaclass=BasePointMeta):
    _fields: Tuple[str, ...]
    coordinates_names: Tuple[str, ...]

    @classmethod
    def from_comma_delimited_text(cls, point_text):
        """
        >>> Point4D.from_comma_delimited_text("0,-8,-4,-6")
        Point4D(x=0, y=-8, z=-4, t=-6)
        """
        parts = map(str.strip, point_text.split(","))
        return cls.from_int_texts(*parts)

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

    @classmethod
    def get_zero_point(cls):
        """
        >>> Point2D.get_zero_point()
        Point2D(x=0, y=0)
        >>> Point2D(-3, 4).get_zero_point()
        Point2D(x=0, y=0)
        """
        # noinspection PyArgumentList
        return cls(*(0,) * len(cls.coordinates_names))

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

    def offset(self, offsets):
        """
        >>> Point3D(3, -2, 4).offset((-2, -5, 3))
        Point3D(x=1, y=-7, z=7)
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls(**{
            name: coordinate + offset
            for name, coordinate, offset
            in zip(self.coordinates_names, self.coordinates, offsets)
        })

    def get_manhattan_neighbours(self):
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbours())
        [Point2D(x=-1, y=0), Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=1, y=0)]
        """
        return (
            self.offset(offset)
            for offset in self.MANHATTAN_OFFSETS
        )

    MANHATTAN_OFFSETS: List[Tuple[int, ...]]

    @classmethod
    @BasePointMeta.auto_assign_to('MANHATTAN_OFFSETS')
    def get_manhattan_offsets(cls):
        """
        >>> sorted(Point2D.MANHATTAN_OFFSETS)
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        >>> sorted(Point2D(0, 0).get_manhattan_offsets())
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        >>> # We run it twice to make sure we didn't use a read-once iterator
        >>> sorted(Point2D.MANHATTAN_OFFSETS)
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        """
        coordinate_count = len(cls.coordinates_names)
        return [
            (0,) * index + (delta,) + (0,) * (coordinate_count - index - 1)
            for index in range(coordinate_count)
            for delta in (-1, 1)
        ]

    def get_manhattan_neighbourhood(self, size):
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood(0))
        [Point2D(x=0, y=0)]
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood(1))
        [Point2D(x=-1, y=0), Point2D(x=0, y=-1), Point2D(x=0, y=0),
            Point2D(x=0, y=1), Point2D(x=1, y=0)]
        """
        return (
            self.offset(offset)
            for offset in self.get_manhattan_neighbourhood_offsets(size)
        )

    MANHATTAN_NEIGHBOUR_OFFSETS = {}

    def get_manhattan_neighbourhood_offsets(self, size):
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood_offsets(0))
        [(0, 0)]
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood_offsets(1))
        [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)]
        """
        if size not in self.MANHATTAN_NEIGHBOUR_OFFSETS:
            zero_point = self.get_zero_point()
            neighbourhood = {zero_point}
            previous_layer = [zero_point]
            for distance in range(1, size + 1):
                current_layer = []
                for point in previous_layer:
                    neighbours = \
                        set(point.get_manhattan_neighbours()) - neighbourhood
                    neighbourhood.update(neighbours)
                    current_layer.extend(neighbours)
                previous_layer = current_layer
            self.MANHATTAN_NEIGHBOUR_OFFSETS[size] = tuple(
                tuple(point.coordinates)
                for point in neighbourhood
            )

        return self.MANHATTAN_NEIGHBOUR_OFFSETS[size]


class Point2D(namedtuple("Point2D", ("x", "y")), BasePoint):
    coordinates_names = ("x", "y")


class Point3D(namedtuple("Point3D", ("x", "y", "z")), BasePoint):
    coordinates_names = ("x", "y", "z")


class Point4D(namedtuple("Point4D", ("x", "y", "z", "t")), BasePoint):
    coordinates_names = ("x", "y", "z", "t")


helper = Helper()


if __name__ == "__main__":
    if doctest.testmod(optionflags=BaseChallenge.optionflags).failed:
        print("Tests failed")
    else:
        print("Tests passed")
