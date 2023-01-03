from operator import le, lt

import itertools
import math
from collections import namedtuple
from dataclasses import dataclass
from typing import Tuple, List, Union, Iterable, Dict, ClassVar
from .typing_utils import Self, Cls

__all__ = ['BasePoint', 'Point2D', 'Point3D', 'Point4D', 'PointHex']


class BasePointMeta(type):
    @classmethod
    def auto_assign_to(mcs, attribute):
        def decorator(method):
            method.auto_assign_to = attribute
            return method

        return decorator

    def __new__(mcs, *args, **kwargs):
        # noinspection PyPep8Naming
        Point = super().__new__(mcs, *args)

        if not kwargs.get("abstract", False):
            # noinspection PyArgumentList
            mcs.assign_auto_attributes(mcs, Point)

        return Point

    # noinspection PyPep8Naming
    def assign_auto_attributes(cls, Point):
        for name in dir(Point):
            attribute = getattr(Point, name)
            if attribute == cls:
                continue
            auto_assign_to = getattr(attribute, 'auto_assign_to', None)
            if auto_assign_to is None:
                continue
            setattr(Point, auto_assign_to, attribute())


ClsBP = Cls["BasePoint"]
SelfBP = Self["BasePoint"]


class BasePoint(metaclass=BasePointMeta, abstract=True):
    _fields: Tuple[str, ...]
    coordinates_names: Tuple[str, ...]

    @classmethod
    def from_comma_delimited_text(cls: ClsBP, point_text: str) -> SelfBP:
        """
        >>> Point4D.from_comma_delimited_text("0,-8,-4,-6")
        Point4D(x=0, y=-8, z=-4, t=-6)
        """
        parts = map(str.strip, point_text.split(","))
        return cls.from_int_texts(*parts)

    @classmethod
    def from_int_texts(
        cls: ClsBP, *coordinate_strs: str,
        **named_coordinate_strs: str,
    ) -> SelfBP:
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
    def for_new(cls: ClsBP, new_method, args, kwargs) -> SelfBP:
        if len(args) == 1:
            if isinstance(args[0], cls):
                if not kwargs:
                    return args[0]
                args = args[0]
            if isinstance(args[0], tuple):
                args = args[0]
        return new_method(cls, *args, **kwargs)

    ZERO_POINT: 'BasePoint'

    @classmethod
    @BasePointMeta.auto_assign_to('ZERO_POINT')
    def get_zero_point(cls: ClsBP) -> SelfBP:
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
    def coordinates(self: SelfBP) -> SelfBP:
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

    def distance(self: SelfBP, other: SelfBP) -> float:
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

    def manhattan_length(self) -> float:
        """
        >>> Point3D(0, 0, 0).manhattan_length()
        0
        >>> Point3D(10, -3, -50).manhattan_length()
        63
        """
        return self.manhattan_distance(self.ZERO_POINT)

    def manhattan_distance(self: SelfBP, other: SelfBP) -> float:
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

    def offset(
        self: SelfBP, offsets: Union[SelfBP, Tuple[float, ...]],
        factor: float = 1,
    ) -> SelfBP:
        """
        >>> Point3D(3, -2, 4).offset((-2, -5, 3))
        Point3D(x=1, y=-7, z=7)
        >>> Point3D(3, -2, 4).offset((-2, -5, 3), factor=-1)
        Point3D(x=5, y=3, z=1)
        """
        if factor == 0:
            return self
        cls = type(self)
        # noinspection PyArgumentList
        return cls(**{
            name: coordinate + offset * factor
            for name, coordinate, offset
            in zip(self.coordinates_names, self.coordinates, offsets)
        })

    def resize(self: SelfBP, factor: float) -> SelfBP:
        return self.ZERO_POINT.offset(self, factor)

    def difference(self: SelfBP, other: SelfBP) -> SelfBP:
        """
        >>> Point3D(3, -2, 4).difference(Point3D(-2, -5, 3))
        Point3D(x=5, y=3, z=1)
        """
        return self.offset(other, factor=-1)

    def difference_sign(self: SelfBP, other: SelfBP) -> SelfBP:
        """
        >>> Point3D(4, -2, 5).difference_sign(Point3D(1, 1, 1))
        Point3D(x=1, y=-1, z=1)
        """
        return self.difference(other).sign()

    def sign(self: SelfBP) -> SelfBP:
        """
        >>> Point3D(0, 0, 0).sign()
        Point3D(x=0, y=0, z=0)
        >>> Point3D(-3, 4, 0).sign()
        Point3D(x=-1, y=1, z=0)
        """
        coordinates = tuple(
            coordinate // (abs(coordinate or 1))
            for coordinate in self.coordinates
        )

        cls = type(self)
        # noinspection PyArgumentList
        return cls(coordinates)

    def get_manhattan_neighbours(self: SelfBP) -> Iterable[SelfBP]:
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbours())
        [Point2D(x=-1, y=0), Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=1, y=0)]
        """
        return (
            self.offset(offset)
            for offset in self.MANHATTAN_OFFSETS
        )

    MANHATTAN_OFFSETS: List[Tuple[float, ...]]

    @classmethod
    @BasePointMeta.auto_assign_to('MANHATTAN_OFFSETS')
    def get_manhattan_offsets(cls) -> List[Tuple[float, ...]]:
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

    def get_manhattan_neighbourhood(
        self: SelfBP, size: int,
    ) -> Iterable[SelfBP]:
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

    MANHATTAN_NEIGHBOUR_OFFSETS: Dict[int, Tuple[Tuple[float, ...], ...]] = {}

    def get_manhattan_neighbourhood_offsets(
        self, size: int,
    ) -> Tuple[Tuple[float, ...], ...]:
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

    def get_euclidean_neighbours(self: SelfBP) -> Iterable[SelfBP]:
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

    EUCLIDEAN_OFFSETS: List[Tuple[float, ...]]

    @classmethod
    @BasePointMeta.auto_assign_to('EUCLIDEAN_OFFSETS')
    def get_euclidean_offsets(cls) -> List[Tuple[int, ...]]:
        """
        >>> sorted(Point2D.EUCLIDEAN_OFFSETS)
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        >>> sorted(Point2D(0, 0).get_euclidean_offsets())
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        >>> # We run it twice to make sure we didn't use a read-once iterator
        >>> sorted(Point2D.EUCLIDEAN_OFFSETS)
        [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        """
        return cls.get_euclidean_offsets_of(1)

    @classmethod
    def get_euclidean_offsets_of(cls, distance: int) -> List[Tuple[int, ...]]:
        """
        >>> sorted(Point2D(0, 0).get_euclidean_offsets_of(1))
        [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]
        >>> sorted(Point3D(0, 0, 0).get_euclidean_offsets_of(1))
        [(-1, -1, -1), (-1, -1, 0), (-1, -1, 1),
            (-1, 0, -1), (-1, 0, 0), (-1, 0, 1),
            (-1, 1, -1), (-1, 1, 0), (-1, 1, 1),
            (0, -1, -1), (0, -1, 0), (0, -1, 1),
            (0, 0, -1), (0, 0, 1),
            (0, 1, -1), (0, 1, 0), (0, 1, 1),
            (1, -1, -1), (1, -1, 0), (1, -1, 1),
            (1, 0, -1), (1, 0, 0), (1, 0, 1),
            (1, 1, -1), (1, 1, 0), (1, 1, 1)]
        >>> sorted(Point2D(0, 0).get_euclidean_offsets_of(2))
        [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
            (-1, -2), (-1, 2),
            (0, -2), (0, 2),
            (1, -2), (1, 2),
            (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]
        """
        return cls.get_euclidean_offsets_between(distance, distance)

    @classmethod
    def get_euclidean_offsets_between(
        cls, min_distance: int, max_distance: int,
    ) -> List[Tuple[int, ...]]:
        """
        >>> sorted(Point2D(0, 0).get_euclidean_offsets_between(1, 1))
        [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)]
        >>> sorted(Point2D(0, 0).get_euclidean_offsets_between(0, 1))
        [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]
        >>> sorted(Point2D(0, 0).get_euclidean_offsets_between(1, 2))
        [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
            (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
            (0, -2), (0, -1), (0, 1), (0, 2),
            (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
            (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]
        >>> sorted(Point2D(0, 0).get_euclidean_offsets_between(0, 2))
        [(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2),
            (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
            (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
            (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
            (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)]
        """
        coordinate_count = len(cls.coordinates_names)
        coordinate_range = tuple(range(-max_distance, max_distance + 1))
        return [
            offsets
            for offsets
            in itertools.product(coordinate_range, repeat=coordinate_count)
            if min_distance <= max(map(abs, offsets)) <= max_distance
        ]

    def get_euclidean_neighbourhood(
        self: SelfBP, size: int,
    ) -> Iterable[SelfBP]:
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

    EUCLIDEAN_NEIGHBOUR_OFFSETS: Dict[int, Tuple[Tuple[float, ...], ...]] = {}

    def get_euclidean_neighbourhood_offsets(
        self, size: int,
    ) -> Tuple[Tuple[float, ...], ...]:
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

    def is_bound(
        self: SelfBP, min_value: SelfBP, max_value: SelfBP,
        min_inclusive: bool = True, max_inclusive: bool = True,
    ) -> bool:
        """
        >>> Point2D(2, 2).is_bound(Point2D(0, 0), Point2D(4, 4))
        True
        >>> Point2D(2, 2).is_bound(Point2D(2, 2), Point2D(4, 4))
        True
        >>> Point2D(2, 2).is_bound(Point2D(0, 0), Point2D(2, 2))
        True
        >>> Point2D(2, 2).is_bound(
        ...     Point2D(0, 0), Point2D(4, 4), max_inclusive=False)
        True
        >>> Point2D(2, 2).is_bound(
        ...     Point2D(2, 2), Point2D(4, 4), min_inclusive=False)
        False
        >>> Point2D(2, 2).is_bound(
        ...     Point2D(0, 0), Point2D(2, 2), max_inclusive=False)
        False
        >>> Point2D(2, 5).is_bound(Point2D(0, 0), Point2D(4, 4))
        False
        >>> Point2D(2, 5).is_bound(Point2D(2, 2), Point2D(4, 4))
        False
        >>> Point2D(2, 5).is_bound(Point2D(0, 0), Point2D(2, 2))
        False
        >>> Point3D(2, 2, 2).is_bound(Point3D(0, 0, 0), Point3D(4, 4, 4))
        True
        >>> Point4D(2, 2, 2, 2).is_bound(
        ...     Point4D(0, 0, 0, 0), Point4D(4, 4, 4, 4))
        True
        """
        if min_inclusive:
            min_operator = le
        else:
            min_operator = lt
        if max_inclusive:
            max_operator = le
        else:
            max_operator = lt

        # noinspection PyTypeChecker
        return all(
            min_operator(min_value, value)
            and max_operator(value, max_value)
            for value, min_value, max_value in zip(self, min_value, max_value)
        )


class Point2D(namedtuple("Point2D", ("x", "y")), BasePoint):
    coordinates_names = ("x", "y")

    def __new__(cls, *args, **kwargs):
        return cls.for_new(super().__new__, args, kwargs)


class Point3D(namedtuple("Point3D", ("x", "y", "z")), BasePoint):
    coordinates_names = ("x", "y", "z")

    def __new__(cls, *args, **kwargs):
        return cls.for_new(super().__new__, args, kwargs)


class Point4D(namedtuple("Point4D", ("x", "y", "z", "t")), BasePoint):
    coordinates_names = ("x", "y", "z", "t")

    def __new__(cls, *args, **kwargs):
        return cls.for_new(super().__new__, args, kwargs)


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

    DIRECTIONS: ClassVar[List[str]] = [E, NE, SE, W, NW, SW]

    DIRECTION_OFFSETS: ClassVar[Dict[int, Dict[str, Tuple[int, int]]]] = {
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

    def __iter__(self) -> Iterable[int]:
        """
        >>> tuple(PointHex(2, 5))
        (2, 5)
        """
        return iter((self.x, self.y))

    def move_many(
        self: Self["PointHex"], directions: Iterable[str],
    ) -> Self["PointHex"]:
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
        # noinspection PyArgumentList
        return cls(x, y)

    def move(self: Self["PointHex"], direction: str)-> Self["PointHex"]:
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

    def step_distance(self: Self["PointHex"], other: Self["PointHex"]) -> int:
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
