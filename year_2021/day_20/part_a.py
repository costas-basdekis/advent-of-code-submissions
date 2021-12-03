#!/usr/bin/env python3
import math
from dataclasses import dataclass
from typing import cast, Dict, Set, Tuple, Union, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples

Neighbourhood = Tuple[bool, bool, bool, bool, bool, bool, bool, bool, bool]


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        algorithm, image = Image.from_mapping_and_image_text(_input)
        return image.step_many(algorithm, 2).light_pixel_count


@dataclass
class IEAlgorithm:
    mapping: Dict[Neighbourhood, bool]

    @classmethod
    def from_mapping_text(cls, mapping_text: str) -> "IEAlgorithm":
        """
        >>> algorithm = IEAlgorithm.from_mapping_text(
        ...     "..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#...."
        ...     "#..#..##..###..######.###...####..#..#####..##..#.#####...##.#"
        ...     ".#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..####"
        ...     "#.....#.#....###..#.##......#.....#..#..#..##..#...##.######.#"
        ...     "###.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.#"
        ...     "#..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#...."
        ...     ".####.#..#..#.##.#....##..#.####....##...##..#...#......#.#..."
        ...     "....#.......##..####..#...#.#.#...##..#.#..###..#####........#"
        ...     "..####......#..#"
        ... )
        >>> list(map(algorithm.__getitem__, range(5)))
        [False, False, True, False, True]
        >>> list(map(algorithm.__getitem__, range(33, 36)))
        [False, True, True]
        >>> list(map(
        ...     algorithm.__getitem__,
        ...     map(IEAlgorithm.index_to_neighbourhood, range(5)),
        ... ))
        [False, False, True, False, True]
        >>> algorithm[(False,) * 9]
        False
        >>> algorithm[(False, True,) + (False,) * 7]
        True
        """
        # if mapping_text.strip()[0] == "#":
        #     raise Exception(
        #         f"Mapping text starts with # ({mapping_text[:15]}...)"
        #     )
        return cls(
            mapping={
                cls.index_to_neighbourhood(index): value == "#"
                for index, value in enumerate(mapping_text.strip())
            },
        )

    @classmethod
    def index_to_neighbourhood(cls, index: int) -> Neighbourhood:
        """
        >>> IEAlgorithm.index_to_neighbourhood(0)
        (False, False, False, False, False, False, False, False, False)
        >>> IEAlgorithm.index_to_neighbourhood(341)
        (True, False, True, False, True, False, True, False, True)
        >>> IEAlgorithm.index_to_neighbourhood(511)
        (True, True, True, True, True, True, True, True, True)
        """
        return cast(Neighbourhood, tuple(
            digit_str == "1"
            for digit_str in f"{index:09b}"
        ))

    def __post_init__(self) -> None:
        if len(self.mapping) != 512:
            raise Exception(
                f"Expected 512 mappings, but got {len(self.mapping)}"
            )
        if self[0] and self[511]:
            raise Exception(
                f"Cannot have both an empty and a full neighbourhood result to "
                f"a light"
            )

    def __getitem__(self, item: Union[int, Neighbourhood]) -> bool:
        if not isinstance(item, tuple):
            item = self.index_to_neighbourhood(item)

        return self.mapping[item]


@dataclass
class Area:
    min: Point2D
    max: Point2D

    @classmethod
    def from_points(cls, points: Iterable[Point2D]) -> "Area":
        _min, _max = min_and_max_tuples(points)
        return cls(
            min=Point2D(_min),
            max=Point2D(_max),
        )

    def __contains__(self, item: Point2D) -> bool:
        return (
            (self.min.x <= item.x <= self.max.x)
            and (self.min.y <= item.y <= self.max.y)
        )

    def pad(self, count: int) -> "Area":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            min=Point2D(self.min.x - count, self.min.y + count),
            max=Point2D(self.max.x - count, self.max.y + count),
        )

    def __iter__(self) -> Iterable[Point2D]:
        return self.iter()

    def iter(self, pad_count: int = 0) -> Iterable[Point2D]:
        for y in self.ys(pad_count):
            for x in self.xs(pad_count):
                yield Point2D(x, y)

    def xs(self, pad_count: int = 0) -> Iterable[int]:
        yield from range(self.min.x - pad_count, self.max.x + pad_count + 1)

    def ys(self, pad_count: int = 0) -> Iterable[int]:
        yield from range(self.min.y - pad_count, self.max.y + pad_count + 1)

    @property
    def size(self) -> Point2D:
        return Point2D(self.max.x - self.min.x + 1, self.max.y - self.min.y + 1)


@dataclass
class Image:
    light_pixels: Set[Point2D]
    boundary: Area
    default_out_of_boundary: bool

    @classmethod
    def from_mapping_and_image_text(
        cls, text: str,
    ) -> Tuple[IEAlgorithm, "Image"]:
        mapping_text, image_text = text.strip().split("\n\n")
        return (
            IEAlgorithm.from_mapping_text(mapping_text),
            cls.from_image_text(image_text),
        )

    @classmethod
    def from_image_text(cls, image_text: str) -> "Image":
        """
        >>> print(":", Image.from_image_text('''
        ...     #..#.
        ...     #....
        ...     ##..#
        ...     ..#..
        ...     ..###
        ... '''))
        : .......
        .#..#..
        .#.....
        .##..#.
        ...#...
        ...###.
        .......
        """
        lines = filter(None, map(str.strip, image_text.splitlines()))
        light_pixels = {
            point
            for y, line in enumerate(lines)
            for x, character in enumerate(line)
            for point in [Point2D(x, y)]
            if character == "#"
        }
        return cls(
            light_pixels=light_pixels,
            boundary=Area.from_points(light_pixels),
            default_out_of_boundary=False,
        )

    def __str__(self) -> str:
        if not self.light_pixels:
            return ""

        return "\n".join(
            "".join(
                "#"
                if self[point] else
                "."
                for x in self.boundary.xs(1)
                for point in [Point2D(x, y)]
            )
            for y in self.boundary.ys(1)
        )

    def __getitem__(self, item: Point2D) -> bool:
        if item in self.boundary:
            return item in self.light_pixels
        else:
            return self.default_out_of_boundary

    def step_many(
        self, algorithm: IEAlgorithm, count: int,
        debugger: Debugger = Debugger(enabled=False),
    ) -> "Image":
        """
        >>> _algorithm = IEAlgorithm.from_mapping_text(
        ...     "..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#...."
        ...     "#..#..##..###..######.###...####..#..#####..##..#.#####...##.#"
        ...     ".#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..####"
        ...     "#.....#.#....###..#.##......#.....#..#..#..##..#...##.######.#"
        ...     "###.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.#"
        ...     "#..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#...."
        ...     ".####.#..#..#.##.#....##..#.####....##...##..#...#......#.#..."
        ...     "....#.......##..####..#...#.#.#...##..#.#..###..#####........#"
        ...     "..####......#..#"
        ... )
        >>> image = Image.from_image_text('''
        ...     #..#.
        ...     #....
        ...     ##..#
        ...     ..#..
        ...     ..###
        ... ''')
        >>> print(":", image.step_many(_algorithm, 1))
        : .........
        ..##.##..
        .#..#.#..
        .##.#..#.
        .####..#.
        ..#..##..
        ...##..#.
        ....#.#..
        .........
        >>> print(":", image.step_many(_algorithm, 2))
        : ...........
        ........#..
        ..#..#.#...
        .#.#...###.
        .#...##.#..
        .#.....#.#.
        ..#.#####..
        ...#.#####.
        ....##.##..
        .....###...
        ...........
        """
        result = self
        debugger.default_report(f"Stepping {count} times")
        for step in debugger.stepping(range(count)):
            result = result.step(algorithm)
            debugger.default_report_if(
                f"Stepped {step}/{count} times, {result.light_pixel_count} "
                f"lights in result, size of {tuple(result.boundary.size)}"
            )

        return result

    def step(self, algorithm: IEAlgorithm) -> "Image":
        """
        >>> _algorithm = IEAlgorithm.from_mapping_text(
        ...     "..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#...."
        ...     "#..#..##..###..######.###...####..#..#####..##..#.#####...##.#"
        ...     ".#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..####"
        ...     "#.....#.#....###..#.##......#.....#..#..#..##..#...##.######.#"
        ...     "###.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.#"
        ...     "#..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#...."
        ...     ".####.#..#..#.##.#....##..#.####....##...##..#...#......#.#..."
        ...     "....#.......##..####..#...#.#.#...##..#.#..###..#####........#"
        ...     "..####......#..#"
        ... )
        >>> image = Image.from_image_text('''
        ...     #..#.
        ...     #....
        ...     ##..#
        ...     ..#..
        ...     ..###
        ... ''')
        >>> print(":", image.step(_algorithm))
        : .........
        ..##.##..
        .#..#.#..
        .##.#..#.
        .####..#.
        ..#..##..
        ...##..#.
        ....#.#..
        .........
        """
        cls = type(self)
        light_pixels = {
            point
            for point in self.boundary.iter(1)
            if algorithm[self.get_neighbourhood(point)]
        }
        # noinspection PyArgumentList
        return cls(
            light_pixels=light_pixels,
            boundary=Area.from_points(light_pixels),
            default_out_of_boundary=(
                algorithm[511 if self.default_out_of_boundary else 0]
            ),
        )

    NEIGHBOURHOOD_OFFSETS = [
        Point2D(x, y)
        for y in [-1, 0, 1]
        for x in [-1, 0, 1]
    ]

    def get_neighbourhood(self, point: Point2D) -> Neighbourhood:
        return cast(Neighbourhood, tuple(
            self[point.offset(neighbour_offset)]
            for neighbour_offset in self.NEIGHBOURHOOD_OFFSETS
        ))

    @property
    def light_pixel_count(self) -> Union[int, float]:
        """
        >>> _algorithm = IEAlgorithm.from_mapping_text(
        ...     "..#.#..#####.#.#.#.###.##.....###.##.#..###.####..#####..#...."
        ...     "#..#..##..###..######.###...####..#..#####..##..#.#####...##.#"
        ...     ".#..#.##..#.#......#.###.######.###.####...#.##.##..#..#..####"
        ...     "#.....#.#....###..#.##......#.....#..#..#..##..#...##.######.#"
        ...     "###.####.#.#...#.......#..#.#.#...####.##.#......#..#...##.#.#"
        ...     "#..#...##.#.##..###.#......#.#.......#.#.#.####.###.##...#...."
        ...     ".####.#..#..#.##.#....##..#.####....##...##..#...#......#.#..."
        ...     "....#.......##..####..#...#.#.#...##..#.#..###..#####........#"
        ...     "..####......#..#"
        ... )
        >>> image = Image.from_image_text('''
        ...     #..#.
        ...     #....
        ...     ##..#
        ...     ..#..
        ...     ..###
        ... ''')
        >>> image.step_many(_algorithm, 2).light_pixel_count
        35
        """
        if self.default_out_of_boundary:
            return math.inf
        return len(self.light_pixels)


Challenge.main()
challenge = Challenge()
