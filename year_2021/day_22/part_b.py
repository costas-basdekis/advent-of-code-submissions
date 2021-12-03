#!/usr/bin/env python3
from dataclasses import dataclass, field
from functools import reduce
from itertools import product, starmap, chain, combinations
from operator import mul
from typing import (
    Generic, Iterable, List, Optional, Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, Point3D, BasePoint,
    min_and_max_tuples,
)
from year_2021.day_22.part_a import RebootStepSet, RebootStep, Reactor


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1187742789778677
        """
        return len(Region3DSet.from_steps_text(_input, debugger=debugger))

    def play(self) -> None:
        lines = list(filter(None, map(str.strip, """
        on x=-46..7,y=-6..46,z=-50..-1
        on x=-49..1,y=-3..46,z=-24..28
        on x=2..47,y=-22..22,z=-23..27
        on x=-27..23,y=-28..26,z=-21..29
        on x=-39..5,y=-6..47,z=-3..44
        on x=-30..21,y=-8..43,z=-13..34
        on x=-22..26,y=-27..20,z=-29..19
        off x=-48..-32,y=26..41,z=-47..-37
        """.splitlines())))

        texts = map("\n".join, chain(*[
            combinations(lines, length)
            for length in range(len(lines) + 1)
        ]))
        original_constraint = Region3D(
            Point3D(-50, -50, -50),
            Point3D(50, 50, 50)
        )
        mismatching_texts_and_values = (
            (text, old_value, new_value)
            for text in texts
            for old_value in [Reactor.from_steps_text(text).cube_count]
            for new_value in [
                len(
                    Region3DSet.from_steps_text(text)
                    .intersect(original_constraint)
                ),
            ]
            if old_value != new_value
        )
        first_mismatching_text_and_values = \
            next(mismatching_texts_and_values, None)
        if not first_mismatching_text_and_values:
            print("All match!")
            return

        (
            first_mismatching_text,
            first_mismatching_old_value,
            first_mismatching_new_value,
        ) = first_mismatching_text_and_values

        print(
            f"New {first_mismatching_new_value} "
            f"!= old {first_mismatching_old_value}"
        )
        print(first_mismatching_text)


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
        """
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
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(2, 2))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(2, 4)))
        ... )
        (0, 0)
        ###
        #..
        #..
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(2, 2))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(1, 4)))
        ... )
        (0, 0)
        ###
        #.#
        #.#
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(2, 2))])
        ...     .remove(Region2D(Point2D(1, -4), Point2D(1, 1)))
        ... )
        (0, 0)
        #.#
        #.#
        ###
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(2, 2))])
        ...     .remove(Region2D(Point2D(1, 1), Point2D(1, 1)))
        ... )
        (0, 0)
        ###
        #.#
        ###
        """
        region_to_remove = region
        for region in list(self.regions):
            new_regions = region.subtract(region_to_remove)
            if new_regions == [region]:
                continue
            self.regions.remove(region)
            self.regions.extend(new_regions)

        return self

    def intersect(self, region: RegionT) -> "RegionSet":
        """
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .intersect(Region2D(Point2D(1, 1), Point2D(2, 2)))
        ... )
        (1, 1)
        #
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .intersect(Region2D(Point2D(-1, -1), Point2D(2, 2)))
        ... )
        (0, 0)
        ##
        ##
        >>> print(
        ...     Region2DSet([Region2D(Point2D(0, 0), Point2D(1, 1))])
        ...     .add(Region2D(Point2D(0, 3), Point2D(1, 5)))
        ...     .intersect(Region2D(Point2D(1, 1), Point2D(3, 3)))
        ... )
        (1, 1)
        #
        .
        #
        """
        region_to_intersect = region
        for region in list(self.regions):
            overlap = region.get_overlap(region_to_intersect)
            if overlap == region:
                continue
            self.regions.remove(region)
            if overlap:
                self.regions.append(overlap)

        return self


class Region2DSet(RegionSet["Region2D"]):
    @classmethod
    def from_steps_text(
        cls, steps_text: str, debugger: Debugger = Debugger(enabled=False),
    ) -> "Region2DSet":
        steps = RebootStepSet.from_steps_text(steps_text)
        return cls().apply(steps, debugger=debugger)

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
        ...     on x=-46..7,y=-6..46,z=-50..-1
        ...     off x=-48..-32,y=26..41,z=-47..-37
        ... '''))
        140460
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
        ... ''').intersect(
        ...     Region3D(Point3D(-50, -50, -50), Point3D(50, 50, 50)),
        ... ))
        590784
        >>> len(Region3DSet.from_steps_text('''
        ...     on x=-5..47,y=-31..22,z=-19..33
        ...     on x=-44..5,y=-27..21,z=-14..35
        ...     on x=-49..-1,y=-11..42,z=-10..38
        ...     on x=-20..34,y=-40..6,z=-44..1
        ...     off x=26..39,y=40..50,z=-2..11
        ...     on x=-41..5,y=-41..6,z=-36..8
        ...     off x=-43..-33,y=-45..-28,z=7..25
        ...     on x=-33..15,y=-32..19,z=-34..11
        ...     off x=35..47,y=-46..-34,z=-11..5
        ...     on x=-14..36,y=-6..44,z=-16..29
        ...     on x=-57795..-6158,y=29564..72030,z=20435..90618
        ...     on x=36731..105352,y=-21140..28532,z=16094..90401
        ...     on x=30999..107136,y=-53464..15513,z=8553..71215
        ...     on x=13528..83982,y=-99403..-27377,z=-24141..23996
        ...     on x=-72682..-12347,y=18159..111354,z=7391..80950
        ...     on x=-1060..80757,y=-65301..-20884,z=-103788..-16709
        ...     on x=-83015..-9461,y=-72160..-8347,z=-81239..-26856
        ...     on x=-52752..22273,y=-49450..9096,z=54442..119054
        ...     on x=-29982..40483,y=-108474..-28371,z=-24328..38471
        ...     on x=-4958..62750,y=40422..118853,z=-7672..65583
        ...     on x=55694..108686,y=-43367..46958,z=-26781..48729
        ...     on x=-98497..-18186,y=-63569..3412,z=1232..88485
        ...     on x=-726..56291,y=-62629..13224,z=18033..85226
        ...     on x=-110886..-34664,y=-81338..-8658,z=8914..63723
        ...     on x=-55829..24974,y=-16897..54165,z=-121762..-28058
        ...     on x=-65152..-11147,y=22489..91432,z=-58782..1780
        ...     on x=-120100..-32970,y=-46592..27473,z=-11695..61039
        ...     on x=-18631..37533,y=-124565..-50804,z=-35667..28308
        ...     on x=-57817..18248,y=49321..117703,z=5745..55881
        ...     on x=14781..98692,y=-1341..70827,z=15753..70151
        ...     on x=-34419..55919,y=-19626..40991,z=39015..114138
        ...     on x=-60785..11593,y=-56135..2999,z=-95368..-26915
        ...     on x=-32178..58085,y=17647..101866,z=-91405..-8878
        ...     on x=-53655..12091,y=50097..105568,z=-75335..-4862
        ...     on x=-111166..-40997,y=-71714..2688,z=5609..50954
        ...     on x=-16602..70118,y=-98693..-44401,z=5197..76897
        ...     on x=16383..101554,y=4615..83635,z=-44907..18747
        ...     off x=-95822..-15171,y=-19987..48940,z=10804..104439
        ...     on x=-89813..-14614,y=16069..88491,z=-3297..45228
        ...     on x=41075..99376,y=-20427..49978,z=-52012..13762
        ...     on x=-21330..50085,y=-17944..62733,z=-112280..-30197
        ...     on x=-16478..35915,y=36008..118594,z=-7885..47086
        ...     off x=-98156..-27851,y=-49952..43171,z=-99005..-8456
        ...     off x=2032..69770,y=-71013..4824,z=7471..94418
        ...     on x=43670..120875,y=-42068..12382,z=-24787..38892
        ...     off x=37514..111226,y=-45862..25743,z=-16714..54663
        ...     off x=25699..97951,y=-30668..59918,z=-15349..69697
        ...     off x=-44271..17935,y=-9516..60759,z=49131..112598
        ...     on x=-61695..-5813,y=40978..94975,z=8655..80240
        ...     off x=-101086..-9439,y=-7088..67543,z=33935..83858
        ...     off x=18020..114017,y=-48931..32606,z=21474..89843
        ...     off x=-77139..10506,y=-89994..-18797,z=-80..59318
        ...     off x=8476..79288,y=-75520..11602,z=-96624..-24783
        ...     on x=-47488..-1262,y=24338..100707,z=16292..72967
        ...     off x=-84341..13987,y=2429..92914,z=-90671..-1318
        ...     off x=-37810..49457,y=-71013..-7894,z=-105357..-13188
        ...     off x=-27365..46395,y=31009..98017,z=15428..76570
        ...     off x=-70369..-16548,y=22648..78696,z=-1892..86821
        ...     on x=-53470..21291,y=-120233..-33476,z=-44150..38147
        ...     off x=-93533..-4276,y=-16170..68771,z=-104985..-24507
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
            Region3D(min=Point3D(x=2, y=0, z=0), max=Point3D(x=2, y=2, z=2))]
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .subtract(Region3D(Point3D(0, 0, 0), Point3D(1, 1, 1)))
        [Region3D(min=Point3D(x=0, y=0, z=2), max=Point3D(x=1, y=1, z=2)),
            Region3D(min=Point3D(x=0, y=2, z=0), max=Point3D(x=1, y=2, z=2)),
            Region3D(min=Point3D(x=2, y=0, z=0), max=Point3D(x=2, y=2, z=2))]
        >>> Region2D(Point2D(0, 0), Point2D(1, 1))\\
        ...     .subtract(Region2D(Point2D(1, 1), Point2D(2, 2)))
        [Region2D(min=Point2D(x=0, y=0), max=Point2D(x=0, y=1)),
            Region2D(min=Point2D(x=1, y=0), max=Point2D(x=1, y=0))]
        >>> Region2D(Point2D(0, 0), Point2D(2, 2))\\
        ...     .subtract(Region2D(Point2D(1, 1), Point2D(1, 4)))
        [Region2D(min=Point2D(x=0, y=0), max=Point2D(x=0, y=2)),
            Region2D(min=Point2D(x=1, y=0), max=Point2D(x=1, y=0)),
            Region2D(min=Point2D(x=2, y=0), max=Point2D(x=2, y=2))]
        """
        overlap = self.get_overlap(other)
        if not overlap:
            return [self]

        point_class = self.get_point_class()
        cls = type(self)

        axis_ranges_list = sorted([
            (axis, self.get_coordinate_ranges(overlap, axis))
            for axis in range(len(point_class.coordinates_names))
        ], key=len)
        sub_regions = {self}
        for axis, axis_ranges in axis_ranges_list:
            # noinspection PyArgumentList
            sub_regions = {
                new_sub_region
                for sub_region in sub_regions
                for new_sub_region in (
                    [
                        cls(
                            min=point_class(
                                sub_region.min[:axis] + (min_axis,)
                                + sub_region.min[axis + 1:]
                            ),
                            max=point_class(
                                sub_region.max[:axis] + (max_axis,)
                                + sub_region.max[axis + 1:]
                            ),
                        )
                        for min_axis, max_axis in axis_ranges
                    ]
                    if sub_region.overlaps_with(overlap) else
                    [sub_region]
                )
            }
        sub_regions.remove(overlap)

        return sorted(filter(None, sub_regions))

    def get_coordinate_ranges(
        self, overlap: "Region", axis: int,
    ) -> List[Tuple[int, int]]:
        """
        >>> region_a = Region2D(Point2D(0, 0), Point2D(2, 2))
        >>> region_b = Region2D(Point2D(1, 1), Point2D(1, 4))
        >>> _overlap = region_a.get_overlap(region_b)
        >>> region_a.get_coordinate_ranges(_overlap, 0)
        [(0, 0), (1, 1), (2, 2)]
        """
        if self.min[axis] == overlap.min[axis]:
            ranges = [
                (self.min[axis], overlap.max[axis]),
            ]
            if overlap.max[axis] < self.max[axis]:
                ranges.append((overlap.max[axis] + 1, self.max[axis]))
        elif self.max[axis] == overlap.max[axis]:
            ranges = [
                (overlap.min[axis], self.max[axis]),
            ]
            if overlap.min[axis] > self.min[axis]:
                ranges.insert(0, (self.min[axis], overlap.min[axis] - 1))
        elif (
            self.min[axis] < overlap.min[axis]
            and overlap.max[axis] < self.max[axis]
        ):
            return [
                (self.min[axis], overlap.min[axis] - 1),
                (overlap.min[axis], overlap.max[axis]),
                (overlap.max[axis] + 1, self.max[axis]),
            ]
        else:
            raise Exception(f"Impossible overlap {overlap} for {self}")

        return ranges

    def overlaps_with(self, other: "Region") -> bool:
        return bool(self.get_overlap(other))

    def get_overlap(self, other: "Region") -> Optional["Region"]:
        """
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(1, 1, 1), Point3D(3, 3, 3)))
        Region3D(min=Point3D(x=1, y=1, z=1), max=Point3D(x=2, y=2, z=2))
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(-1, -1, -1), Point3D(3, 3, 3)))
        Region3D(min=Point3D(x=0, y=0, z=0), max=Point3D(x=2, y=2, z=2))
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(1, 1, 1), Point3D(2, 2, 2)))
        Region3D(min=Point3D(x=1, y=1, z=1), max=Point3D(x=2, y=2, z=2))
        >>> Region3D(Point3D(0, 0, 0), Point3D(2, 2, 2))\\
        ...     .get_overlap(Region3D(Point3D(3, 3, 3), Point3D(5, 5, 5)))
        >>> Region2D(Point2D(0, 0), Point2D(2, 2))\\
        ...     .get_overlap(Region2D(Point2D(1, 1), Point2D(1, 4)))
        Region2D(min=Point2D(x=1, y=1), max=Point2D(x=1, y=2))
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
