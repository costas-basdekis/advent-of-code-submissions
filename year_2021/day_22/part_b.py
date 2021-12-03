#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from functools import reduce
from itertools import product, starmap
from operator import mul
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Point3D, BasePoint,
    min_and_max_tuples,
)
from year_2021.day_22.part_a import RebootStepSet, RebootStep


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return len(Region3DSet.from_steps_text(_input, debugger=debugger))


RegionT = TypeVar("RegionT", bound="Region")
PointT = TypeVar("PointT", bound=BasePoint)


@dataclass
class RegionSet(Generic[RegionT]):
    regions: List["Region"] = field(default_factory=list)

    @classmethod
    def get_region_class(cls) -> Type[RegionT]:
        return get_type_argument_class(cls, RegionT)

    @classmethod
    def from_region(cls, region: RegionT) -> "RegionSet":
        return cls(regions=[region])

    def __bool__(self) -> bool:
        return any(map(bool, self.regions))

    def __len__(self) -> int:
        return sum(map(len, self.regions))

    def __iter__(self) -> Iterable[PointT]:
        """
        >>> list(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        [Point2D(x=0, y=0), Point2D(x=0, y=1), Point2D(x=1, y=0)]
        """
        for region in self.regions:
            yield from region

    def apply(
        self, step_set: RebootStepSet,
        debugger: Debugger = Debugger(enabled=False),
    ) -> "RegionSet":
        region_class = self.get_region_class()
        for index, step in debugger.stepping(enumerate(step_set.steps, 1)):
            step_region = region_class.from_step(step)
            if step.set_to_on:
                self.add(step_region)
            else:
                self.remove(step_region)
            debugger.default_report_if(
                f"Done {index}/{len(step_set.steps)}, "
                f"{len(self.regions)} regions, {len(self)} total cubes"
            )

        return self

    def add(self, region: RegionT) -> "RegionSet":
        """
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .add(Region2D(Point2D(0, 3), Point2D(1, 4)))
        ... )
        (0, 0)
        ##
        ##
        ..
        ##
        ##
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .add(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##.
        ###
        .##
        >>> Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])\\
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        Region2DSet(regions=[Region2D(min=Point2D(x=0, y=0),
            max=Point2D(x=0, y=0)),
            Region2D(min=Point2D(x=0, y=1), max=Point2D(x=0, y=1)),
            Region2D(min=Point2D(x=1, y=0), max=Point2D(x=1, y=0))])
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##
        #.
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##
        #.
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ...     .add(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##.
        ###
        .##
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .add(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##
        #.
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .add(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ...     .remove(Region2D(Point2D(1, 1), Point2D(1, 1)))
        ... )
        (0, 0)
        ##.
        #.#
        .##
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .add(Region2D(Point2D(2,2), Point2D(3, 3)))
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##..
        #...
        ...#
        ..##
        """
        regions_to_add = [region]
        while regions_to_add:
            region_to_add = regions_to_add.pop(0)
            for region in self.regions:
                new_regions = region.add(region_to_add)
                if new_regions == [region_to_add]:
                    continue
                regions_to_add.extend(new_regions)
                break
            else:
                self.regions.append(region_to_add)

        return self

    def remove(self, region: RegionT) -> "RegionSet":
        region_to_remove = region
        for region in list(self.regions):
            new_regions = region.subtract(region_to_remove)
            if new_regions == [region]:
                continue
            self.regions.remove(region)
            self.regions.extend(new_regions)

        return self


class Region2DSet(RegionSet["Region2D"]):
    def __str__(self) -> "str":
        """
        >>> print(Region2DSet())
        >>> print(Region2DSet([Region2D(Point2D(0, 0), Point2D(2, 2))]))
        (0, 0)
        ###
        ###
        ###
        """
        if not self.regions:
            return ""
        min_coordinates, _ = min_and_max_tuples(
            region.min
            for region in self.regions
        )
        min_point = Point2D(min_coordinates)
        _, max_coordinates = min_and_max_tuples(
            region.max
            for region in self.regions
        )
        max_point = Point2D(max_coordinates)
        counts = {}
        for point in self:
            counts.setdefault(point, 0)
            counts[point] += 1
        return "{min_point}\n{as_string}".format(
            min_point=tuple(min_point),
            as_string="\n".join(
                "".join(
                    "#"
                    if count == 1 else
                    str(count)
                    if count > 1 else
                    "."
                    for x in range(min_point.x, max_point.x + 1)
                    for point in [Point2D(x, y)]
                    for count in [counts.get(point, 0)]
                )
                for y in range(min_point.y, max_point.y + 1)
            ),
        )


class Region3DSet(RegionSet["Region3D"]):
    @classmethod
    def from_steps_text(
        cls, steps_text: str, debugger: Debugger = Debugger(enabled=False),
    ) -> "Region3DSet":
        """
        >>> len(Region3DSet.from_steps_text('''
        ...     on x=10..12,y=10..12,z=10..12
        ...     on x=11..13,y=11..13,z=11..13
        ...     off x=9..11,y=9..11,z=9..11
        ...     on x=10..10,y=10..10,z=10..10
        ... '''))
        39
        >>> len(Region3DSet.from_steps_text('''
        ...     on x=-20..26,y=-36..17,z=-47..7
        ...     on x=-20..33,y=-21..23,z=-26..28
        ...     on x=-22..28,y=-29..23,z=-38..16
        ...     on x=-46..7,y=-6..46,z=-50..-1
        ...     on x=-49..1,y=-3..46,z=-24..28
        ...     on x=2..47,y=-22..22,z=-23..27
        ...     on x=-27..23,y=-28..26,z=-21..29
        ...     on x=-39..5,y=-6..47,z=-3..44
        ...     on x=-30..21,y=-8..43,z=-13..34
        ...     on x=-22..26,y=-27..20,z=-29..19
        ...     off x=-48..-32,y=26..41,z=-47..-37
        ...     on x=-12..35,y=6..50,z=-50..-2
        ...     off x=-48..-32,y=-32..-16,z=-15..-5
        ...     on x=-18..26,y=-33..15,z=-7..46
        ...     off x=-40..-22,y=-38..-28,z=23..41
        ...     on x=-16..35,y=-41..10,z=-47..6
        ...     off x=-32..-23,y=11..30,z=-14..3
        ...     on x=-49..-5,y=-3..45,z=-29..18
        ...     off x=18..30,y=-20..-8,z=-3..13
        ...     on x=-41..9,y=-7..43,z=-33..15
        ...     on x=-54112..-39298,y=-85059..-49293,z=-27449..7877
        ...     on x=967..23432,y=45373..81175,z=27513..53682
        ... '''))
        2758514936282235
        """
        steps = RebootStepSet.from_steps_text(steps_text)
        return cls().apply(steps, debugger=debugger)


@dataclass(frozen=True)
class Region(Generic[PointT]):
    min: PointT
    max: PointT

    @classmethod
    def get_point_class(cls) -> Type[PointT]:
        point_class = get_type_argument_class(cls, PointT)
        if point_class is BasePoint:
            raise Exception(
                f"Generic Region has not been subclassed: {cls.__name__}"
            )
        return point_class

    @classmethod
    def from_step(cls, step: RebootStep) -> "Region":
        point_class = cls.get_point_class()
        return cls(
            min=point_class(step.min[:len(point_class.coordinates_names)]),
            max=point_class(step.max[:len(point_class.coordinates_names)]),
        )

    def __bool__(self) -> bool:
        return all(
            min_value <= max_value
            for min_value, max_value in zip(self.min, self.max)
        )

    def __lt__(self, other: "Region") -> bool:
        return (self.min, self.max) < (other.min, other.max)

    def __iter__(self) -> Iterable[PointT]:
        """
        >>> sorted(Region2D(Point2D(0, 0), Point2D(1, 1)))
        [Point2D(x=0, y=0), Point2D(x=0, y=1), Point2D(x=1, y=0),
            Point2D(x=1, y=1)]
        >>> list(map(list, [
        ...     Region2D(min=Point2D(x=0, y=0), max=Point2D(x=0, y=0)),
        ...     Region2D(min=Point2D(x=0, y=1), max=Point2D(x=0, y=1)),
        ...     Region2D(min=Point2D(x=1, y=0), max=Point2D(x=1, y=0)),
        ... ]))
        [[Point2D(x=0, y=0)], [Point2D(x=0, y=1)], [Point2D(x=1, y=0)]]
        """
        point_class = self.get_point_class()
        return map(point_class, product(*[
            range(min_value, max_value + 1)
            for min_value, max_value in zip(self.min, self.max)
        ]))

    def __len__(self) -> int:
        """
        >>> len(Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2)))
        27
        """
        return reduce(mul, (
            max_value - min_value + 1
            for min_value, max_value in zip(self.min, self.max)
        ))

    def add(self, other: "Region") -> List["Region"]:
        overlap = self.get_overlap(other)
        if not overlap:
            return [other]

        return other.subtract(overlap)

    def subtract(self, other: "Region") -> List["Region"]:
        """
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .subtract(Region3D(Point3D(4, 4, 4), Point3D(6, 6, 6)))
        [Region3D(min=Point3D(x=0, y=0, z=0), max=Point3D(x=2, y=2, z=2))]
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .subtract(Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2)))
        []
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .subtract(Region3D(Point3D(0, 0, 0), Point3D(1, 2, 2)))
        [Region3D(min=Point3D(x=2, y=0, z=0), max=Point3D(x=2, y=2, z=2))]
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .subtract(Region3D(Point3D(0, 0, 0), Point3D(1, 1, 2)))
        [Region3D(min=Point3D(x=0, y=2, z=0), max=Point3D(x=1, y=2, z=2)),
            Region3D(min=Point3D(x=2, y=0, z=0), max=Point3D(x=2, y=1, z=2)),
            Region3D(min=Point3D(x=2, y=2, z=0), max=Point3D(x=2, y=2, z=2))]
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .subtract(Region3D(Point3D(0, 0, 0), Point3D(1, 1, 1)))
        [Region3D(min=Point3D(x=0, y=0, z=2), max=Point3D(x=1, y=1, z=2)),
            Region3D(min=Point3D(x=0, y=2, z=0), max=Point3D(x=1, y=2, z=1)),
            Region3D(min=Point3D(x=0, y=2, z=2), max=Point3D(x=1, y=2, z=2)),
            Region3D(min=Point3D(x=2, y=0, z=0), max=Point3D(x=2, y=1, z=1)),
            Region3D(min=Point3D(x=2, y=0, z=2), max=Point3D(x=2, y=1, z=2)),
            Region3D(min=Point3D(x=2, y=2, z=0), max=Point3D(x=2, y=2, z=1)),
            Region3D(min=Point3D(x=2, y=2, z=2), max=Point3D(x=2, y=2, z=2))]
        >>> Region2D(Point2D(0, 0), Point2D(1, 1))\\
        ...     .subtract(Region2D(Point2D(1, 1), Point2D(2, 2)))
        [Region2D(min=Point2D(x=0, y=0), max=Point2D(x=0, y=0)),
            Region2D(min=Point2D(x=0, y=1), max=Point2D(x=0, y=1)),
            Region2D(min=Point2D(x=1, y=0), max=Point2D(x=1, y=0))]
        """
        overlap = self.get_overlap(other)
        if not overlap:
            return [self]

        point_class = self.get_point_class()

        cls = type(self)
        # noinspection PyArgumentList
        sub_regions = {
            cls(
                min=point_class(min_value),
                max=point_class(max_value),
            )
            for ranges in product(*[
                self.get_coordinate_ranges(overlap, index)
                for index in range(len(point_class.coordinates_names))
            ])
            for min_value, max_value in [zip(*ranges)]
        } - {overlap}

        return sorted(filter(None, sub_regions))

    def get_coordinate_ranges(
        self, overlap: "Region", axis: int,
    ) -> List[Tuple[int, int]]:
        if self.min[axis] == overlap.min[axis]:
            ranges = [
                (self.min[axis], overlap.max[axis]),
            ]
            if overlap.max[axis] < self.max[axis]:
                ranges.append((overlap.max[axis] + 1, self.max[axis]))
        else:
            ranges = [
                (overlap.min[axis], self.max[axis]),
            ]
            if overlap.min[axis] > self.min[axis]:
                ranges.insert(0, (self.min[axis], overlap.min[axis] - 1))

        return ranges

    def get_overlap(self, other: "Region") -> Optional["Region"]:
        """
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(1, 1, 1), Point3D(3, 3, 3)))
        Region3D(min=Point3D(x=1, y=1, z=1), max=Point3D(x=2, y=2, z=2))
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(1, 1, 1), Point3D(2, 2, 2)))
        Region3D(min=Point3D(x=1, y=1, z=1), max=Point3D(x=2, y=2, z=2))
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(3, 3, 3), Point3D(5, 5, 5)))
        """
        point_class = self.get_point_class()
        cls = type(self)
        # noinspection PyArgumentList
        overlap = cls(
            min=point_class(tuple(starmap(max, zip(self.min, other.min)))),
            max=point_class(tuple(starmap(min, zip(self.max, other.max)))),
        )
        if not overlap:
            return None

        return overlap


class Region2D(Region[Point2D]):
    pass


class Region3D(Region[Point3D]):
    pass


Challenge.main()
challenge = Challenge()
