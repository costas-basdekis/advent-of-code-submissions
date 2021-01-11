import doctest
import importlib
import itertools
import math
from abc import ABC
from collections import namedtuple
from dataclasses import dataclass
from typing import Tuple, List, Any, Union, Dict, Type, Iterable

import aox


class BaseChallenge(aox.BaseChallenge, ABC):
    def get_test_modules(self):
        return super().get_test_modules() + [
            importlib.import_module(__name__),
        ]


class Helper:
    def iterable_length(self, iterable):
        return sum(1 for _ in iterable)

    def find_smallest_required_value(self, min_value, is_value_enough,
                                     debug=False):
        """
        >>> is_more_than_10 = lambda _value, **_: _value > 10
        >>> Helper().find_smallest_required_value(1, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(0, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(-2, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(-3, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(3, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(9, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(10, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(11, is_more_than_10)
        Traceback (most recent call last):
        ...
        Exception: Tried ... already enough
        >>> Helper().find_smallest_required_value(12, is_more_than_10)
        Traceback (most recent call last):
        ...
        Exception: Tried ... already enough
        """
        if is_value_enough(min_value):
            raise Exception(
                f"Tried to bisect value, but provided min_value {min_value} "
                f"was already enough")
        max_value = self.get_big_enough_value(
            start=min_value + 1, is_value_enough=is_value_enough, debug=debug)
        if debug:
            print(f"Value must be between {min_value} and {max_value}")

        while max_value > min_value + 1:
            mid_value = (max_value + min_value) // 2
            if is_value_enough(mid_value, debug=debug):
                max_value = mid_value
                if debug:
                    print(
                        f"Value {mid_value} is too much: checking between "
                        f"{min_value} and {max_value}")
            else:
                min_value = mid_value
                if debug:
                    print(
                        f"Value {mid_value} is not enough: checking between "
                        f"{min_value} and {max_value}")

        return max_value

    def get_big_enough_value(self, start, is_value_enough, debug=False):
        """
        >>> is_more_than_10 = lambda _value, **_: _value > 10
        >>> Helper().get_big_enough_value(1, is_more_than_10)
        16
        >>> Helper().get_big_enough_value(0, is_more_than_10)
        16
        >>> Helper().get_big_enough_value(-2, is_more_than_10)
        16
        >>> Helper().get_big_enough_value(-3, is_more_than_10)
        12
        >>> Helper().get_big_enough_value(3, is_more_than_10)
        12
        """
        value = start
        while not is_value_enough(value, debug=debug):
            if debug:
                print(f"Value {value} was not enough")
            if value > 0:
                value *= 2
            elif value == 0:
                value = 1
            else:
                value = -value
        if debug:
            print(f"Value {value} was enough")

        return value

    def reverse_dict(self, _dict: Dict,
                     values_container: Type[Iterable] = list):
        """
        >>> Helper().reverse_dict({'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 2})
        {1: ['a', 'c'], 2: ['b', 'e'], 3: ['d']}
        >>> Helper().reverse_dict(
        ...     {'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 2},
        ...     values_container=tuple)
        {1: ('a', 'c'), 2: ('b', 'e'), 3: ('d',)}
        """
        # noinspection PyTypeChecker
        return self.group_by(
            _dict.items(),
            key=lambda item: item[1],
            value='auto',
            values_container=values_container,
        )

    def group_by(self, iterable, key=None, value=None,
                 values_container: Type[Iterable] = list):
        """
        >>> Helper().group_by([1, 2, 1, 3, 2, 4, 1, 2])
        {1: [1, 1, 1], 2: [2, 2, 2], 3: [3], 4: [4]}
        >>> Helper().group_by([1, 2, 1, 3, 2, 4, 1, 2], values_container=tuple)
        {1: (1, 1, 1), 2: (2, 2, 2), 3: (3,), 4: (4,)}
        >>> Helper().group_by(
        ...     [1, 2, 1, 3, 2, 4, 1, 2], key=lambda item: item % 2)
        {0: [2, 2, 4, 2], 1: [1, 1, 3, 1]}
        >>> Helper().group_by(
        ...     [('a', 1), ('b', 2), ('a', 3), ('a', 4), ('c', 5)],
        ...     key=lambda item: item[0])
        {'a': [('a', 1), ('a', 3), ('a', 4)], 'b': [('b', 2)], 'c': [('c', 5)]}
        >>> Helper().group_by(
        ...     [('a', 1), ('b', 2), ('a', 3), ('a', 4), ('c', 5)],
        ...     key=lambda item: item[0], value='auto')
        {'a': [1, 3, 4], 'b': [2], 'c': [5]}
        """
        # noinspection PyArgumentList
        return {
            _key: values_container(
                (
                    item
                    if value is None else
                    self.auto_group_by_value(item, _key)
                    if value == 'auto' else
                    value(item)
                )
                for item in items
            )
            for _key, items
            in itertools.groupby(sorted(iterable, key=key), key=key)
        }

    def auto_group_by_value(self, item: Tuple, key: Union[Tuple, Any]):
        """
        >>> Helper().auto_group_by_value(('a', 'b'), 'a')
        'b'
        >>> Helper().auto_group_by_value(('a', 'b'), 'b')
        'a'
        >>> Helper().auto_group_by_value(('a', 'b'), 'b')
        'a'
        >>> Helper().auto_group_by_value(('a', 'b'), 'ab')
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), 'a')
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), 'c')
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), ('a',))
        ('b', 'c')
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), ('c',))
        ('a', 'b')
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('a', 'b'))
        ('c', 'd')
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('c', 'd'))
        ('a', 'b')
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('a', 'd'))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('a',))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b'), ('a',))
        ('b',)
        >>> Helper().auto_group_by_value(('a', 'b'), ('b',))
        ('a',)
        >>> Helper().auto_group_by_value(('a', 'b'), ('c',))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('a',))
        ('b', 'c', 'd')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('d',))
        ('a', 'b', 'c')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('b',))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('a', 'b'))
        ('c', 'd')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('c', 'd'))
        ('a', 'b')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('a', 'd'))
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if not isinstance(item, tuple):
            raise ValueError(f"Item must be a tuple")
        key_is_tuple = (
                isinstance(key, tuple)
                and item[1:] != (key,)
                and item[:1] != (key,)
        )
        if not key_is_tuple:
            key_tuple = (key,)
            if len(item) != 2:
                raise ValueError(
                    f"If key is not a tuple ({key}), then item needs to be a "
                    f"2-tuple, not a {len(item)}-tuple ({item})")
        else:
            key_tuple = key

        if item[:len(key_tuple)] == key_tuple:
            value_tuple = item[len(key_tuple):]
        elif item[-len(key_tuple):] == key_tuple:
            value_tuple = item[:-len(key_tuple)]
        else:
            raise ValueError(
                f"Key {key_tuple} is not a prefix or a suffix of item {item}")

        if key_is_tuple:
            return value_tuple
        else:
            value, = value_tuple
            return value


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

    ZERO_POINT: 'BasePoint'

    @classmethod
    @BasePointMeta.auto_assign_to('ZERO_POINT')
    def get_zero_point(cls):
        """
        >>> Point2D.get_zero_point()
        Point2D(x=0, y=0)
        >>> Point2D.ZERO_POINT
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

    def manhattan_length(self):
        """
        >>> Point3D(0, 0, 0).manhattan_length()
        0
        >>> Point3D(10, -3, -50).manhattan_length()
        63
        """
        return self.manhattan_distance(self.ZERO_POINT)

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

    def offset(self, offsets, factor=1):
        """
        >>> Point3D(3, -2, 4).offset((-2, -5, 3))
        Point3D(x=1, y=-7, z=7)
        >>> Point3D(3, -2, 4).offset((-2, -5, 3), factor=-1)
        Point3D(x=5, y=3, z=1)
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls(**{
            name: coordinate + offset * factor
            for name, coordinate, offset
            in zip(self.coordinates_names, self.coordinates, offsets)
        })

    def resize(self, factor):
        return self.ZERO_POINT.offset(self, factor)

    def difference(self, other):
        """
        >>> Point3D(3, -2, 4).difference(Point3D(-2, -5, 3))
        Point3D(x=5, y=3, z=1)
        """
        return self.offset(other, factor=-1)

    def difference_sign(self, other):
        """
        >>> Point3D(4, -2, 5).difference_sign(Point3D(1, 1, 1))
        Point3D(x=1, y=-1, z=1)
        """
        return self.difference(other).sign()

    def sign(self):
        """
        >>> Point3D(0, 0, 0).sign()
        Point3D(x=0, y=0, z=0)
        >>> Point3D(-3, 4, 0).sign()
        Point3D(x=-1, y=1, z=0)
        """
        sign_x = self.x // (abs(self.x) or 1)
        sign_y = self.y // (abs(self.y) or 1)
        sign_z = self.z // (abs(self.z) or 1)

        cls = type(self)
        return cls(sign_x, sign_y, sign_z)

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
            zero_point = self.ZERO_POINT
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

    def get_euclidean_neighbours(self):
        """
        >>> sorted(Point2D(0, 0).get_euclidean_neighbours())
        [Point2D(x=-1, y=-1), Point2D(x=-1, y=0), Point2D(x=-1, y=1),
            Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=1, y=-1), Point2D(x=1, y=0), Point2D(x=1, y=1)]
        """
        return (
            self.offset(offset)
            for offset in self.EUCLIDEAN_OFFSETS
        )

    EUCLIDEAN_OFFSETS: List[Tuple[int, ...]]

    @classmethod
    @BasePointMeta.auto_assign_to('EUCLIDEAN_OFFSETS')
    def get_euclidean_offsets(cls):
        """
        >>> sorted(Point2D.EUCLIDEAN_OFFSETS)
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        >>> sorted(Point2D(0, 0).get_euclidean_offsets())
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        >>> # We run it twice to make sure we didn't use a read-once iterator
        >>> sorted(Point2D.EUCLIDEAN_OFFSETS)
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        """
        coordinate_count = len(cls.coordinates_names)
        return [
            offsets
            for offsets
            in itertools.product((-1, 0, 1), repeat=coordinate_count)
            if any(offsets)
        ]

    def get_euclidean_neighbourhood(self, size):
        """
        >>> sorted(Point2D(0, 0).get_euclidean_neighbourhood(0))
        [Point2D(x=0, y=0)]
        >>> sorted(Point2D(0, 0).get_euclidean_neighbourhood(1))
        [Point2D(x=-1, y=-1), Point2D(x=-1, y=0), Point2D(x=-1, y=1),
            Point2D(x=0, y=-1), Point2D(x=0, y=0), Point2D(x=0, y=1),
            Point2D(x=1, y=-1), Point2D(x=1, y=0), Point2D(x=1, y=1)]
        """
        return (
            self.offset(offset)
            for offset in self.get_euclidean_neighbourhood_offsets(size)
        )

    EUCLIDEAN_NEIGHBOUR_OFFSETS = {}

    def get_euclidean_neighbourhood_offsets(self, size):
        """
        >>> sorted(Point2D(0, 0).get_euclidean_neighbourhood_offsets(0))
        [(0, 0)]
        >>> sorted(Point2D(0, 0).get_euclidean_neighbourhood_offsets(1))
        [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]
        """
        if size not in self.EUCLIDEAN_NEIGHBOUR_OFFSETS:
            zero_point = self.ZERO_POINT
            neighbourhood = {zero_point}
            previous_layer = [zero_point]
            for distance in range(1, size + 1):
                current_layer = []
                for point in previous_layer:
                    neighbours = \
                        set(point.get_euclidean_neighbours()) - neighbourhood
                    neighbourhood.update(neighbours)
                    current_layer.extend(neighbours)
                previous_layer = current_layer
            self.EUCLIDEAN_NEIGHBOUR_OFFSETS[size] = tuple(
                tuple(point.coordinates)
                for point in neighbourhood
            )

        return self.EUCLIDEAN_NEIGHBOUR_OFFSETS[size]


class Point2D(namedtuple("Point2D", ("x", "y")), BasePoint):
    coordinates_names = ("x", "y")


class Point3D(namedtuple("Point3D", ("x", "y", "z")), BasePoint):
    coordinates_names = ("x", "y", "z")


class Point4D(namedtuple("Point4D", ("x", "y", "z", "t")), BasePoint):
    coordinates_names = ("x", "y", "z", "t")


@dataclass(order=True, frozen=True)
class PointHex:
    x: int
    y: int

    E = 'e'
    NE = 'ne'
    SE = 'se'
    W = 'w'
    NW = 'nw'
    SW = 'sw'

    DIRECTIONS = [E, NE, SE, W, NW, SW]

    DIRECTION_OFFSETS = {
        0: {
            E: (1, 0),
            SE: (0, 1),
            NE: (0, -1),
            W: (-1, 0),
            NW: (-1, -1),
            SW: (-1, 1),
        },
        1: {
            E: (1, 0),
            SE: (1, 1),
            NE: (1, -1),
            W: (-1, 0),
            NW: (0, -1),
            SW: (0, 1),
        },
    }

    def __iter__(self):
        """
        >>> tuple(PointHex(2, 5))
        (2, 5)
        """
        return iter((self.x, self.y))

    def move_many(self, directions):
        """
        >>> PointHex(0, 0).move_many([PointHex.NE, PointHex.NE, PointHex.NE])
        PointHex(x=1, y=-3)
        >>> PointHex(0, 0).move_many([PointHex.NE] * 10)
        PointHex(x=5, y=-10)
        >>> PointHex(0, 0).move_many([PointHex.NW, PointHex.NW, PointHex.NW])
        PointHex(x=-2, y=-3)
        >>> PointHex(0, 0).move_many([PointHex.NW] * 10)
        PointHex(x=-5, y=-10)
        >>> PointHex(0, 0).move_many([PointHex.NE, PointHex.W, PointHex.SE])
        PointHex(x=0, y=0)
        """
        x, y = self
        for direction in directions:
            d_x, d_y = self.DIRECTION_OFFSETS[y % 2][direction]
            x += d_x
            y += d_y

        cls = type(self)
        return cls(x, y)

    def move(self, direction):
        """
        >>> PointHex(0, 0).move(PointHex.E)
        PointHex(x=1, y=0)
        >>> PointHex(0, 0).move(PointHex.W)
        PointHex(x=-1, y=0)
        >>> PointHex(0, 0).move(PointHex.NE)
        PointHex(x=0, y=-1)
        >>> PointHex(0, -1).move(PointHex.NE)
        PointHex(x=1, y=-2)
        >>> PointHex(1, -2).move(PointHex.NE)
        PointHex(x=1, y=-3)
        """
        return self.move_many((direction,))

    def step_distance(self, other):
        """
        >>> PointHex(0, 0).step_distance(PointHex(0, 0).move_many(
        ...     [PointHex.NE] * 10))
        10
        >>> PointHex(0, 0).step_distance(PointHex(0, 0).move_many(
        ...     [PointHex.NW] * 10))
        10
        >>> PointHex(0, 0).step_distance(PointHex(0, 0).move_many(
        ...     [PointHex.NW, PointHex.NE] * 5))
        10
        >>> PointHex(0, 0).step_distance(PointHex(0, 0).move_many(
        ...     [PointHex.W] * 10))
        10
        >>> PointHex(0, 0).step_distance(PointHex(0, 0).move_many(
        ...     [PointHex.W] * 5 + [PointHex.NW] * 5))
        10
        """
        d_x = other.x - self.x
        d_y = other.y - self.y

        return abs(abs(d_x) - min(abs(d_x), abs(d_y // 2))) + abs(d_y)


helper = Helper()


if __name__ == "__main__":
    if doctest.testmod(optionflags=BaseChallenge.optionflags).failed:
        print("Tests failed")
    else:
        print("Tests passed")
