#!/usr/bin/env python3
from dataclasses import dataclass
import re
from enum import Enum
from itertools import chain
from typing import (
    Any, cast, ClassVar, Dict, Generic, Iterable, List, Optional, Tuple, Type,
    Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, BasePoint, Point3D,
    min_and_max_tuples, helper, iterable_length,
)


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        376
        """
        return Scanner3DSet\
            .from_scanners_text(_input)\
            .get_unique_beacon_count(debugger=debugger)


BeaconT = TypeVar("BeaconT", bound="Beacon")
ScannerT = TypeVar("ScannerT", bound="Scanner")


@dataclass
class ScannerSet(Generic[ScannerT]):
    scanners: List[ScannerT]
    min_overlap: ClassVar[int]

    @classmethod
    def get_scanner_class(cls) -> Type[ScannerT]:
        return get_type_argument_class(cls, ScannerT)

    @classmethod
    def get_beacon_class(cls) -> Type[ScannerT]:
        return cls.get_scanner_class().get_beacon_class()

    @classmethod
    def from_scanners_text(cls, scanners_text: str) -> "ScannerSet":
        """
        >>> Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,-1
        ...     -5,0
        ...     -2,1
        ... ''')
        Scanner2DSet(scanners=[Scanner2D(beacons=[Beacon2D(x=0, y=2),
            Beacon2D(x=4, y=1), Beacon2D(x=3, y=3)]),
            Scanner2D(beacons=[Beacon2D(x=-1, y=-1), Beacon2D(x=-5, y=0),
                Beacon2D(x=-2, y=1)])])
        """
        scanner_class = cls.get_scanner_class()
        return cls(
            scanners=list(map(
                scanner_class.from_scanner_text,
                scanners_text.split("\n\n"),
            )),
        )

    def get_unique_beacon_count(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,-1
        ...     -5,0
        ...     -2,1
        ... ''').get_unique_beacon_count()
        3
        >>> Scanner3DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     404,-588,-901
        ...     528,-643,409
        ...     -838,591,734
        ...     390,-675,-793
        ...     -537,-823,-458
        ...     -485,-357,347
        ...     -345,-311,381
        ...     -661,-816,-575
        ...     -876,649,763
        ...     -618,-824,-621
        ...     553,345,-567
        ...     474,580,667
        ...     -447,-329,318
        ...     -584,868,-557
        ...     544,-627,-890
        ...     564,392,-477
        ...     455,729,728
        ...     -892,524,684
        ...     -689,845,-530
        ...     423,-701,434
        ...     7,-33,-71
        ...     630,319,-379
        ...     443,580,662
        ...     -789,900,-551
        ...     459,-707,401
        ...
        ...     --- scanner 1 ---
        ...     686,422,578
        ...     605,423,415
        ...     515,917,-361
        ...     -336,658,858
        ...     95,138,22
        ...     -476,619,847
        ...     -340,-569,-846
        ...     567,-361,727
        ...     -460,603,-452
        ...     669,-402,600
        ...     729,430,532
        ...     -500,-761,534
        ...     -322,571,750
        ...     -466,-666,-811
        ...     -429,-592,574
        ...     -355,545,-477
        ...     703,-491,-529
        ...     -328,-685,520
        ...     413,935,-424
        ...     -391,539,-444
        ...     586,-435,557
        ...     -364,-763,-893
        ...     807,-499,-711
        ...     755,-354,-619
        ...     553,889,-390
        ...
        ...     --- scanner 2 ---
        ...     649,640,665
        ...     682,-795,504
        ...     -784,533,-524
        ...     -644,584,-595
        ...     -588,-843,648
        ...     -30,6,44
        ...     -674,560,763
        ...     500,723,-460
        ...     609,671,-379
        ...     -555,-800,653
        ...     -675,-892,-343
        ...     697,-426,-610
        ...     578,704,681
        ...     493,664,-388
        ...     -671,-858,530
        ...     -667,343,800
        ...     571,-461,-707
        ...     -138,-166,112
        ...     -889,563,-600
        ...     646,-828,498
        ...     640,759,510
        ...     -630,509,768
        ...     -681,-892,-333
        ...     673,-379,-804
        ...     -742,-814,-386
        ...     577,-820,562
        ...
        ...     --- scanner 3 ---
        ...     -589,542,597
        ...     605,-692,669
        ...     -500,565,-823
        ...     -660,373,557
        ...     -458,-679,-417
        ...     -488,449,543
        ...     -626,468,-788
        ...     338,-750,-386
        ...     528,-832,-391
        ...     562,-778,733
        ...     -938,-730,414
        ...     543,643,-506
        ...     -524,371,-870
        ...     407,773,750
        ...     -104,29,83
        ...     378,-903,-323
        ...     -778,-728,485
        ...     426,699,580
        ...     -438,-605,-362
        ...     -469,-447,-387
        ...     509,732,623
        ...     647,635,-688
        ...     -868,-804,481
        ...     614,-800,639
        ...     595,780,-596
        ...
        ...     --- scanner 4 ---
        ...     727,592,562
        ...     -293,-554,779
        ...     441,611,-461
        ...     -714,465,-776
        ...     -743,427,-804
        ...     -660,-479,-426
        ...     832,-632,460
        ...     927,-485,-438
        ...     408,393,-506
        ...     466,436,-512
        ...     110,16,151
        ...     -258,-428,682
        ...     -393,719,612
        ...     -211,-452,876
        ...     808,-476,-593
        ...     -575,615,604
        ...     -485,667,467
        ...     -680,325,-822
        ...     -627,-443,-432
        ...     872,-547,-609
        ...     833,512,582
        ...     807,604,487
        ...     839,-516,451
        ...     891,-625,532
        ...     -652,-548,-490
        ...     30,-46,-14
        ... ''').get_unique_beacon_count()
        79
        """
        return len(self.merge_scanners(debugger=debugger).beacons)

    def merge_scanners(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> ScannerT:
        """
        >>> print(":", Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,-1
        ...     -5,0
        ...     -2,1
        ... ''').merge_scanners())
        : ...B.
        B....
        ....B
        S....
        >>> print(":", Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,1
        ...     0,5
        ...     1,2
        ... ''').merge_scanners())
        : ...B.
        B....
        ....B
        S....
        """
        scanner_class = self.get_scanner_class()
        return scanner_class.from_positions_and_scanners(
            self.find_scanners_positions(debugger=debugger),
        )

    def find_scanners_positions(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> List[Tuple[BeaconT, ScannerT]]:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> [_position for _position, _ in Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,-1
        ...     -5,0
        ...     -2,1
        ... ''').find_scanners_positions()]
        [Beacon2D(x=0, y=0), Beacon2D(x=5, y=2)]
        """
        if not self.scanners:
            return []

        beacon_class = self.get_beacon_class()
        first_scanner = self.scanners[0]
        positions_and_scanners_by_scanner: Dict[int, Tuple[BeaconT, ScannerT]] \
            = {
                id(first_scanner):
                (beacon_class.get_zero_point(), first_scanner)
            }
        found_scanners = [first_scanner]
        remaining_scanners = self.scanners[1:]
        debugger.default_report(
            f"Looking for {len(self.scanners) - 1} positions, found "
            f"{len(found_scanners) - 1}"
        )
        while remaining_scanners:
            for other_index, other in enumerate(remaining_scanners):
                for found_index, found_scanner \
                        in debugger.step_if(enumerate(found_scanners)):
                    debugger.default_report_if(
                        f"Looking for {len(self.scanners) - 1} positions, "
                        f"found {len(found_scanners) - 1}"
                    )
                    found_position, found_reoriented = \
                        positions_and_scanners_by_scanner[id(found_scanner)]
                    position_and_scanner = \
                        found_reoriented.find_other_scanner_position(
                            other, self.min_overlap,
                        )
                    if not position_and_scanner:
                        continue

                    position, reoriented = position_and_scanner
                    position = position.offset(found_position)
                    found_scanners.append(other)
                    positions_and_scanners_by_scanner[id(other)] = \
                        position, reoriented
                    remaining_scanners.remove(other)
                    break
                else:
                    continue

                break
            else:
                raise Exception(
                    f"Could not find any remaining scanner "
                    f"({len(remaining_scanners)} remaining out of "
                    f"{len(self.scanners)})"
                )

        return [
            positions_and_scanners_by_scanner[id(scanner)]
            for scanner in self.scanners
        ]


class Scanner2DSet(ScannerSet["Scanner2D"]):
    min_overlap = 3

    def __str__(self) -> str:
        positions_and_scanners = self.find_scanners_positions()
        scanners = [
            scanner
            for _, scanner in positions_and_scanners
        ]
        positions = [
            position
            for position, _ in positions_and_scanners
        ]
        return Scanner2D.plot(scanners, positions)


class Scanner3DSet(ScannerSet["Scanner3D"]):
    min_overlap = 12


@dataclass
class Scanner(Generic[BeaconT]):
    beacons: List[BeaconT]

    re_name = re.compile(r"^--- scanner (\d+) ---$")

    @classmethod
    def get_beacon_class(cls) -> Type[BeaconT]:
        return get_type_argument_class(cls, BeaconT)

    @classmethod
    def get_orientation_class(cls) -> Type["OrientationT"]:
        return cls.get_beacon_class().get_orientation_class()

    @classmethod
    def from_scanner_text(cls, scanner_text: str) -> "Scanner":
        """
        >>> Scanner2D.from_scanner_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ... ''')
        Scanner2D(beacons=[Beacon2D(x=0, y=2), Beacon2D(x=4, y=1),
            Beacon2D(x=3, y=3)])
        >>> Scanner3D.from_scanner_text('''
        ...     --- scanner 0 ---
        ...     0,2,1
        ...     4,1,2
        ...     3,3,3
        ... ''')
        Scanner3D(beacons=[Beacon3D(x=0, y=2, z=1), Beacon3D(x=4, y=1, z=2),
            Beacon3D(x=3, y=3, z=3)])
        """
        lines = filter(None, map(str.strip, scanner_text.splitlines()))
        first_line = next(lines)
        if not cls.re_name.match(first_line):
            raise Exception(
                f"First line of scanner is not it's name: '{first_line}'"
            )

        point_class = cls.get_beacon_class()
        return cls(
            beacons=[
                point_class(tuple(map(int, line.split(","))))
                for line in lines
            ],
        )

    @classmethod
    def from_positions_and_scanners(
        cls, positions_and_scanners: Iterable[Tuple[BeaconT, "Scanner"]],
    ) -> "Scanner":
        return cls(
            beacons=sorted({
                beacon.offset(position)
                for position, scanner in positions_and_scanners
                for beacon in scanner.beacons
            }),
        )

    def find_other_scanner_position(
        self, other: "Scanner", min_overlap: int,
    ) -> Optional[Tuple[BeaconT, "Scanner"]]:
        positions_and_beacons = [
            (position, reoriented)
            for reoriented in other.get_all_orientations()
            for position in [
                self.find_other_scanner_position_at_orientation(
                    reoriented, min_overlap,
                ),
            ]
            if position
        ]
        if not positions_and_beacons:
            return None
        if len(positions_and_beacons) > 1:
            positions = [
                position
                for position, _ in positions_and_beacons
            ]
            raise Exception(
                f"Expected 1 orientation to match at least {min_overlap} "
                f"beacons, but {len(positions_and_beacons)} did "
                f"({', '.join(map(str, positions))})"
            )
        (position, orientation), = positions_and_beacons
        return position, orientation

    def find_other_scanner_position_at_orientation(
        self, other: "Scanner", min_overlap: int,
    ) -> Optional[BeaconT]:
        """
        >>> scanner_a, scanner_b = Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,-1
        ...     -5,0
        ...     -2,1
        ... ''').scanners
        >>> scanner_a.find_other_scanner_position_at_orientation(scanner_b, 3)
        Beacon2D(x=5, y=2)
        """
        offsets = (
            first_beacon.offset(second_beacon, factor=-1)
            for first_beacon in self.beacons
            for second_beacon in other.beacons
        )
        offset_counts = helper.group_by(
            offsets, values_container=iterable_length,
        )
        max_count = max(offset_counts.values())
        if max_count < min_overlap:
            return None
        offsets_with_max_count = [
            offset
            for offset, count in offset_counts.items()
            if count == max_count
        ]
        if len(offsets_with_max_count) > 1:
            raise Exception(
                f"Expected 1 offset with max count {max_count}, but got "
                f"{len(offsets_with_max_count)} ({offsets_with_max_count})"
            )
        offset, = offsets_with_max_count
        return offset

    def get_all_orientations(self) -> Iterable["Scanner"]:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> print(":", Scanner2D.from_positions_and_scanners([
        ...     (Beacon2D.get_zero_point(), scanner)
        ...     for scanner
        ...     in Scanner2D([Beacon2D(1, 2)]).get_all_orientations()
        ... ]))
        : ...B.
        B....
        ..S..
        ....B
        .B...
        """
        orientation_class = self.get_orientation_class()
        for _tuple in orientation_class.Tuples:
            yield self.reorient(*_tuple[:-1])

    def reorient(self, *args: "OrientationT") -> "Scanner":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            beacons=[
                beacon.reorient(*args)
                for beacon in self.beacons
            ]
        )


class Scanner2D(Scanner["Beacon2D"]):
    @classmethod
    def plot(
        cls, scanners: List["Scanner2D"], scanner_positions: List[Point2D],
    ) -> str:
        """
        >>> print(":", Scanner2D.plot(Scanner2DSet.from_scanners_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ...
        ...     --- scanner 1 ---
        ...     -1,-1
        ...     -5,0
        ...     -2,1
        ... ''').scanners, [Point2D(0, 0), Point2D(5, 2)]))
        : ...B..
        B....S
        ....B.
        S.....
        """
        beacons = [
            beacon.offset(position)
            for scanner, position in zip(scanners, scanner_positions)
            for beacon in scanner.beacons
        ]
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(chain(
            scanner_positions,
            beacons,
        ))
        return "\n".join(
            "".join(
                "S"
                if point in scanner_positions else
                "B"
                if point in beacons else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Beacon2D(x, y)]
            )
            for y in range(max_y, min_y - 1, -1)
        )

    def __str__(self) -> str:
        """
        >>> print(":", Scanner2D.from_scanner_text('''
        ...     --- scanner 0 ---
        ...     0,2
        ...     4,1
        ...     3,3
        ... '''))
        : ...B.
        B....
        ....B
        S....
        """
        return self.plot([self], [Point2D.get_zero_point()])


class Scanner3D(Scanner["Beacon3D"]):
    pass


PointT = TypeVar("PointT", bound=BasePoint)


class Axis:
    name: str
    value: str

    @classmethod
    def get_beacon_class(cls) -> PointT:
        return get_type_argument_class(cls, PointT)

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def get(self, point: PointT) -> float:
        return getattr(point, self.value.lower())


class Axis2DEnum(Axis, Enum):
    X = "X"
    Y = "Y"

    def __invert__(self) -> "Axis2DEnum":
        """
        >>> ~Axis2DEnum.X
        Axis2DEnum.Y
        >>> ~Axis2DEnum.Y
        Axis2DEnum.X
        """
        second, = set(Axis2DEnum) - {self}

        return second


class Axis3DEnum(Axis, Enum):
    X = "X"
    Y = "Y"
    Z = "Z"

    def __xor__(self, other: "Axis3DEnum") -> "Axis3DEnum":
        """
        >>> Axis3DEnum.X ^ Axis3DEnum.Y
        Axis3DEnum.Z
        >>> Axis3DEnum.X ^ Axis3DEnum.Z
        Axis3DEnum.Y
        >>> Axis3DEnum.Y ^ Axis3DEnum.Z
        Axis3DEnum.X
        """
        if self is other:
            raise Exception(f"Cannot get third axis from the same axis")
        third, = set(Axis3DEnum) - {self, other}

        return third

    AXIS_ORDER: ClassVar[Tuple["Axis3DEnum", "Axis3DEnum", "Axis3DEnum"]]

    def is_before(self, second: "Axis3DEnum") -> bool:
        first_index = self.AXIS_ORDER.index(self)
        second_index = self.AXIS_ORDER.index(second)
        return (second_index - first_index) % 3 == 1


Axis3DEnum.AXIS_ORDER = tuple(Axis3DEnum)


AxisT = TypeVar("AxisT", bound=Axis)


@dataclass(frozen=True, eq=True)
class Orientation(Generic[AxisT]):
    axis: AxisT
    positive: bool

    Tuples: ClassVar[List[Tuple["Orientation", ...]]]
    STATIC_MAP: ClassVar[Dict["Orientation", "Orientation"]]

    @classmethod
    def get_axis_class(cls) -> Type[AxisT]:
        return get_type_argument_class(cls, AxisT)

    @classmethod
    def set_tuples(cls) -> None:
        raise NotImplementedError()

    def __new__(cls, *args, **kwargs) -> "Orientation3D":
        """
        >>> Orientation3D(Axis3DEnum.X, True) is Orientation3D.PositiveX
        True
        >>> Orientation3D(Axis3DEnum.X, True) \\
        ...     is Orientation3D(Axis3DEnum.X, True)
        True
        >>> Orientation2D(Axis2DEnum.X, True) is Orientation2D.PositiveX
        True
        >>> Orientation2D(Axis2DEnum.X, True) \\
        ...     is Orientation2D(Axis2DEnum.X, True)
        True
        """
        value = super().__new__(cls)
        # noinspection PyArgumentList
        value.__init__(*args, **kwargs)
        if value not in cls.STATIC_MAP:
            cls.STATIC_MAP[value] = value
        else:
            value = cls.STATIC_MAP[value]

        return value

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}."
            f"{'Positive' if self.positive else 'Negative'}"
            f"{self.axis.value}"
        )

    @property
    def is_identity(self) -> bool:
        cls = type(self)
        # noinspection PyTypeChecker
        return self is next(cls)


class OrientationMeta(type):
    def __new__(
        mcs: Type["OrientationMeta"], cls: str,
        bases: Tuple[Type, ...], classdict: Dict[str, Any],
    ) -> Type:
        _class: Type[Orientation] = \
            cast(Type[Orientation], super().__new__(mcs, cls, bases, classdict))

        _class.STATIC_MAP = {}
        _class.set_tuples()

        return _class

    def __iter__(cls: Type[Orientation]):
        return iter(cls.STATIC_MAP)


class Orientation2D(Orientation[Axis2DEnum], metaclass=OrientationMeta):
    PositiveX: "Orientation2D"
    NegativeX: "Orientation2D"
    PositiveY: "Orientation2D"
    NegativeY: "Orientation2D"

    @classmethod
    def set_tuples(cls) -> None:
        """
        >>> len(Orientation2D.Tuples)
        4
        """
        cls.PositiveX = cls(Axis2DEnum.X, True)
        cls.NegativeX = cls(Axis2DEnum.X, False)
        cls.PositiveY = cls(Axis2DEnum.Y, True)
        cls.NegativeY = cls(Axis2DEnum.Y, False)
        cls.POSITIVE_SECONDS = (
            cls.PositiveX,
            cls.NegativeY,
        )
        cls.Tuples = [
            (first, ~first)
            for first in cls
        ]

    POSITIVE_SECONDS: ClassVar[Tuple["Orientation2D", ...]]

    def __invert__(self) -> "Orientation2D":
        """
        >>> ~Orientation2D.PositiveX
        Orientation2D.PositiveY
        >>> ~Orientation2D.PositiveY
        Orientation2D.NegativeX
        >>> ~Orientation2D.NegativeX
        Orientation2D.NegativeY
        >>> ~Orientation2D.NegativeY
        Orientation2D.PositiveX
        """
        second_axis = ~self.axis
        second_positive = self in self.POSITIVE_SECONDS
        cls = type(self)
        return cls(second_axis, second_positive)


class Orientation3D(Orientation[Axis3DEnum], metaclass=OrientationMeta):
    PositiveX: "Orientation3D"
    NegativeX: "Orientation3D"
    PositiveY: "Orientation3D"
    NegativeY: "Orientation3D"
    PositiveZ: "Orientation3D"
    NegativeZ: "Orientation3D"

    @classmethod
    def set_tuples(cls) -> None:
        """
        >>> len(Orientation3D.Tuples)
        24
        """
        cls.PositiveX = cls(Axis3DEnum.X, True)
        cls.NegativeX = cls(Axis3DEnum.X, False)
        cls.PositiveY = cls(Axis3DEnum.Y, True)
        cls.NegativeY = cls(Axis3DEnum.Y, False)
        cls.PositiveZ = cls(Axis3DEnum.Z, True)
        cls.NegativeZ = cls(Axis3DEnum.Z, False)
        cls.Tuples = [
            (first, second, first ^ second)
            for first in cls
            for second in cls
            if first.axis is not second.axis
        ]

    def __xor__(self, other: "Orientation3D") -> "Orientation3D":
        """
        >>> Orientation3D.PositiveX ^ Orientation3D.PositiveY
        Orientation3D.PositiveZ
        >>> Orientation3D.PositiveX ^ Orientation3D.NegativeY
        Orientation3D.NegativeZ
        >>> Orientation3D.PositiveX ^ Orientation3D.PositiveZ
        Orientation3D.NegativeY
        >>> Orientation3D.PositiveX ^ Orientation3D.NegativeZ
        Orientation3D.PositiveY
        >>> Orientation3D.PositiveY ^ Orientation3D.PositiveZ
        Orientation3D.PositiveX
        >>> Orientation3D.PositiveZ ^ Orientation3D.PositiveX
        Orientation3D.PositiveY
        """
        do_xor = self.axis.is_before(other.axis)
        third_axis = self.axis ^ other.axis
        third_positive = self.positive ^ other.positive ^ do_xor
        cls = type(self)
        return cls(third_axis, third_positive)


OrientationT = TypeVar("OrientationT", bound=Orientation)


class Beacon(Generic[OrientationT], BasePoint, abstract=True):
    @classmethod
    def get_orientation_class(cls) -> Type[OrientationT]:
        return get_type_argument_class(cls, OrientationT)

    def reorient(self, *args: OrientationT) -> "Beacon":
        raise NotImplementedError()

    def __getitem__(self, item: Union[int, OrientationT]) -> float:
        if not isinstance(item, Orientation):
            # noinspection PyUnresolvedReferences
            return super().__getitem__(item)
        value = item.axis.get(self)
        if not item.positive:
            value *= -1

        return value

    def get_all_orientations(self) -> Iterable["Beacon"]:
        """
        >>> print(":", Scanner2D(list(Beacon2D(1, 2).get_all_orientations())))
        : ...B.
        B....
        ..S..
        ....B
        .B...
        >>> len(set(Beacon3D(1, 2, 3).get_all_orientations()))
        24
        >>> len(set(Beacon3D(1, 0, 0).get_all_orientations()))
        6
        """
        orientation_class = self.get_orientation_class()
        for _tuple in orientation_class.Tuples:
            yield self.reorient(*_tuple[:-1])


class Beacon2D(Beacon[Orientation2D], Point2D):
    def reorient(self, first: Orientation2D) -> "Beacon2D":
        """
        >>> Beacon2D((1, 2)).reorient(Orientation2D.PositiveX)
        Beacon2D(x=1, y=2)
        >>> Beacon2D((1, 2)).reorient(Orientation2D.PositiveY)
        Beacon2D(x=2, y=-1)
        >>> Beacon2D((1, 2)).reorient(Orientation2D.NegativeX)
        Beacon2D(x=-1, y=-2)
        >>> Beacon2D((1, 2)).reorient(Orientation2D.NegativeY)
        Beacon2D(x=-2, y=1)
        """
        if first is Orientation2D.PositiveX:
            return self

        return self._make((
            self[first],
            self[~first],
        ))


class Beacon3D(Beacon[Orientation3D], Point3D):
    def reorient(
        self, first: Orientation3D, second: Orientation3D,
    ) -> "Beacon3D":
        """
        >>> Beacon3D((1, 2, 3)).reorient(
        ...     Orientation3D.PositiveX, Orientation3D.PositiveY,
        ... )
        Beacon3D(x=1, y=2, z=3)
        >>> Beacon3D((1, 2, 3)).reorient(
        ...     Orientation3D.PositiveY, Orientation3D.PositiveZ,
        ... )
        Beacon3D(x=2, y=3, z=1)
        >>> Beacon3D((1, 2, 3)).reorient(
        ...     Orientation3D.PositiveZ, Orientation3D.PositiveX,
        ... )
        Beacon3D(x=3, y=1, z=2)
        >>> Beacon3D((1, 2, 3)).reorient(
        ...     Orientation3D.PositiveZ, Orientation3D.PositiveY,
        ... )
        Beacon3D(x=3, y=2, z=-1)
        """
        if (first, second) \
                == (Orientation3D.PositiveX, Orientation3D.PositiveY):
            return self

        if first.axis is second.axis:
            raise Exception(f"Can't use the same axis twice ({first.axis})")

        return self._make((
            self[first],
            self[second],
            self[first ^ second],
        ))


Challenge.main()
challenge = Challenge()
