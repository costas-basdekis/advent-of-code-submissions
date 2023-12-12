from enum import Enum
from functools import cached_property
from typing import Dict, List, TypeVar

from utils.method_utils import cached_classmethod
from utils.point import Point2D
from utils.typing_utils import Cls, Self


__all__ = ["DirectionBase", "Direction", "Direction8"]


DirectionBaseT = TypeVar("DirectionBaseT", bound="Direction")


class DirectionBase:
    name: str

    @classmethod
    def parse(cls: Cls["DirectionBase"], text: str) -> Self["DirectionBase"]:
        parse_map = cls.get_parse_map()
        if text not in parse_map:
            raise Exception(f"Unknown direction: '{text}', expected one of {','.join(parse_map)}")
        return parse_map[text]

    @classmethod
    def from_offset(cls: Cls["DirectionBase"], offset: Point2D) -> Self["DirectionBase"]:
        reverse_offset_map = cls.get_reverse_offset_map()
        if offset not in reverse_offset_map:
            raise Exception(f"Unknown offset: {offset}, expected one of {','.join(map(str, reverse_offset_map))}")
        return reverse_offset_map[offset]

    @classmethod
    def get_parse_map(cls: Cls["DirectionBase"]) -> Dict[str, Self["DirectionBase"]]:
        raise NotImplementedError()

    @classmethod
    def get_print_map(cls: Cls["DirectionBase"]) -> Dict[Self["DirectionBase"], str]:
        raise NotImplementedError()

    @classmethod
    def get_offset_map(cls: Cls["DirectionBase"]) -> Dict[Self["DirectionBase"], Point2D]:
        raise NotImplementedError()

    @classmethod
    @cached_classmethod
    def get_reverse_offset_map(cls: Cls["Direction"]) -> Dict[Point2D, Self["Direction"]]:
        return {
            offset: direction
            for direction, offset in cls.get_offset_map().items()
        }

    @classmethod
    def get_clockwise_list(cls: Cls["DirectionBase"]) -> List[Self["DirectionBase"]]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def __str__(self) -> str:
        return self.string_char

    def __lt__(self: DirectionBaseT, other: DirectionBaseT) -> bool:
        return self.name < other.name

    @cached_property
    def string_char(self) -> str:
        print_map = self.get_print_map()
        if self not in print_map:
            raise Exception(f"Print map is missing direction {self}, it only has {','.join(map(str, print_map))}")
        return print_map[self]

    @cached_property
    def offset(self) -> Point2D:
        offset_map = self.get_offset_map()
        if self not in offset_map:
            raise Exception(f"Offset map is missing direction {self}, it only has {','.join(map(str, offset_map))}")
        return offset_map[self]

    @cached_property
    def clockwise(self: Cls["DirectionBase"]) -> Self["DirectionBase"]:
        clockwise_list = self.get_clockwise_list()
        index = clockwise_list.index(self)
        return clockwise_list[(index + 1) % len(clockwise_list)]

    @cached_property
    def counter_clockwise(self: Cls["DirectionBase"]) -> Self["DirectionBase"]:
        clockwise_list = self.get_clockwise_list()
        index = clockwise_list.index(self)
        return clockwise_list[(index - 1) % len(clockwise_list)]

    @cached_property
    def opposite(self: Cls["DirectionBase"]) -> Self["DirectionBase"]:
        clockwise_list = self.get_clockwise_list()
        index = clockwise_list.index(self)
        return clockwise_list[(index + len(clockwise_list) // 2) % len(clockwise_list)]


class Direction(DirectionBase, Enum):
    Up = "up"
    Down = "down"
    Left = "left"
    Right = "right"

    @classmethod
    @cached_classmethod
    def get_print_map(cls: Cls["Direction"]) -> Dict[Self["Direction"], str]:
        """
        >>> str(Direction.Up)
        '^'
        """
        return {
            Direction.Up: "^",
            Direction.Down: "v",
            Direction.Left: "<",
            Direction.Right: ">",
        }

    @classmethod
    @cached_classmethod
    def get_parse_map(cls: Cls["Direction"]) -> Dict[str, Self["Direction"]]:
        """
        >>> Direction.parse('^')
        Direction.Up
        """
        return {
            string: direction
            for direction, string in cls.get_print_map().items()
        }

    @classmethod
    @cached_classmethod
    def get_offset_map(cls: Cls["Direction"]) -> Dict[Self["Direction"], Point2D]:
        """
        >>> Direction.Up.offset
        Point2D(x=0, y=-1)
        >>> Direction.from_offset(Point2D(0, -1))
        Direction.Up
        """
        return {
            Direction.Up: Point2D(0, -1),
            Direction.Down: Point2D(0, 1),
            Direction.Left: Point2D(-1, 0),
            Direction.Right: Point2D(1, 0),
        }

    @classmethod
    @cached_classmethod
    def get_clockwise_list(cls: Cls["Direction"]) -> List["Direction"]:
        """
        >>> Direction.Up.clockwise
        Direction.Right
        >>> Direction.Up.counter_clockwise
        Direction.Left
        """
        return [
            Direction.Up,
            Direction.Right,
            Direction.Down,
            Direction.Left,
        ]


class Direction8(DirectionBase, Enum):
    Up = "up"
    Down = "down"
    Left = "left"
    Right = "right"
    UpLeft = "up-left"
    UpRight = "up-right"
    DownLeft = "down-left"
    DownRight = "down-right"

    @classmethod
    @cached_classmethod
    def get_print_map(cls: Cls["Direction8"]) -> Dict[Self["Direction8"], str]:
        """
        >>> str(Direction8.Up)
        '^'
        """
        return {
            Direction8.Up: "^",
            Direction8.Down: "v",
            Direction8.Left: "<",
            Direction8.Right: ">",
            Direction8.UpLeft: "F",
            Direction8.UpRight: "¬",
            Direction8.DownLeft: "L",
            Direction8.DownRight: "J",
        }

    @classmethod
    @cached_classmethod
    def get_parse_map(cls: Cls["Direction8"]) -> Dict[str, Self["Direction8"]]:
        """
        >>> Direction8.parse('^')
        Direction8.Up
        """
        return {
            string: direction
            for direction, string in cls.get_print_map().items()
        }

    @classmethod
    @cached_classmethod
    def get_offset_map(cls: Cls["Direction8"]) -> Dict[Self["Direction8"], Point2D]:
        """
        >>> Direction8.Up.offset
        Point2D(x=0, y=-1)
        >>> Direction8.from_offset(Point2D(0, -1))
        Direction8.Up
        """
        return {
            Direction8.Up: Point2D(0, -1),
            Direction8.Down: Point2D(0, 1),
            Direction8.Left: Point2D(-1, 0),
            Direction8.Right: Point2D(1, 0),
            Direction8.UpLeft: Point2D(-1, -1),
            Direction8.UpRight: Point2D(1, -1),
            Direction8.DownLeft: Point2D(-1, 1),
            Direction8.DownRight: Point2D(1, 1),
        }

    @classmethod
    @cached_classmethod
    def get_clockwise_list(cls: Cls["Direction8"]) -> List["Direction8"]:
        """
        >>> Direction8.Up.clockwise
        Direction8.UpRight
        >>> Direction8.Up.counter_clockwise
        Direction8.UpLeft
        """
        return [
            Direction8.Up,
            Direction8.UpRight,
            Direction8.Right,
            Direction8.DownRight,
            Direction8.Down,
            Direction8.DownLeft,
            Direction8.Left,
            Direction8.UpLeft,
        ]
