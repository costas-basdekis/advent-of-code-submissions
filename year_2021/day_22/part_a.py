#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from typing import Generic, Iterable, List, Optional, Set, Type, Union, TypeVar

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, Point3D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        607657
        """
        return Reactor.from_steps_text(_input, debugger=debugger).cube_count


RebootStepSetT = TypeVar("RebootStepSetT", bound="RebootStepSet")


@dataclass
class Reactor(Generic[RebootStepSetT]):
    cubes: Set[Point3D] = field(default_factory=set)
    min: Point3D = Point3D(-50, -50, -50)
    max: Point3D = Point3D(50, 50, 50)

    @classmethod
    def get_steps_class(cls) -> Type[RebootStepSetT]:
        return get_type_argument_class(cls, RebootStepSetT)

    @classmethod
    def from_steps_text(
        cls, steps_text: str, debugger: Debugger = Debugger(enabled=False),
    ) -> "Reactor":
        """
        >>> Reactor.from_steps_text('''
        ...     on x=10..12,y=10..12,z=10..12
        ...     on x=11..13,y=11..13,z=11..13
        ...     off x=9..11,y=9..11,z=9..11
        ...     on x=10..10,y=10..10,z=10..10
        ... ''').cube_count
        39
        >>> Reactor.from_steps_text('''
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
        ... ''').cube_count
        590784
        """
        steps_class = cls.get_steps_class()
        steps = steps_class.from_steps_text(steps_text)
        return cls().apply(steps, debugger=debugger)

    def __getitem__(self, item: Point3D) -> bool:
        return item in self.cubes

    def __setitem__(self, key: Point3D, value: bool) -> None:
        value = bool(value)
        old_value = self[key]
        if old_value == value:
            return

        if value:
            if not key.is_bound(self.min, self.max):
                return
            self.cubes.add(key)
        else:
            self.cubes.remove(key)

    @property
    def cube_count(self) -> int:
        return len(self.cubes)

    def apply(
        self, steps: RebootStepSetT,
        debugger: Debugger = Debugger(enabled=False),
    ) -> "Reactor":
        steps.apply(self, debugger=debugger)

        return self


RebootStepT = TypeVar("RebootStepT", bound="RebootStep")


@dataclass
class RebootStepSet(Generic[RebootStepT]):
    steps: List[RebootStepT]

    @classmethod
    def get_step_class(cls) -> Type[RebootStepT]:
        return get_type_argument_class(cls, RebootStepT)

    @classmethod
    def from_steps_text(cls, steps_text: str) -> "RebootStepSet":
        """
        >>> RebootStepSet.from_steps_text('''
        ...     on x=10..12,y=10..12,z=10..12
        ...     on x=11..13,y=11..13,z=11..13
        ...     off x=9..11,y=9..11,z=9..11
        ...     on x=10..10,y=10..10,z=10..10
        ... ''')
        RebootStepSet(steps=[RebootStep(...), RebootStep(...), RebootStep(...),
            RebootStep(...)])
        """
        lines = filter(None, map(str.strip, steps_text.splitlines()))
        step_class = cls.get_step_class()
        return cls(
            steps=list(map(step_class.from_step_text, lines)),
        )

    def apply(
        self, reactor: Reactor, debugger: Debugger = Debugger(enabled=False),
    ) -> Reactor:
        for step_index, step in debugger.stepping(enumerate(self.steps, 1)):
            step.apply(reactor)
            debugger.default_report_if(
                f"After {step_index} steps: {reactor.cube_count} cubes are on"
            )
        return reactor


@dataclass
class RebootStep:
    min: Point3D
    max: Point3D
    set_to_on: bool

    re_step = re.compile(
        r"^(on|off) "
        r"x=(-?\d+)..(-?\d+),"
        r"y=(-?\d+)..(-?\d+),"
        r"z=(-?\d+)..(-?\d+)$"
    )

    SET_TO_ON_MAP = {
        "on": True,
        "off": False,
    }

    @classmethod
    def from_step_text(cls, step_text: str) -> "RebootStep":
        """
        >>> RebootStep.from_step_text("on x=-45..7,y=-17..27,z=5..49")
        RebootStep(min=Point3D(x=-45, y=-17, z=5), max=Point3D(x=7, y=27, z=49),
            set_to_on=True)
        >>> RebootStep.from_step_text("off x=-30..-17,y=-18..-5,z=-54..-31")
        RebootStep(min=Point3D(x=-30, y=-18, z=-54),
            max=Point3D(x=-17, y=-5, z=-31),
            set_to_on=False)
        """
        set_to_on_str, *min_and_max_str = \
            cls.re_step.match(step_text.strip()).groups()
        min_x, max_x, min_y, max_y, min_z, max_z = map(int, min_and_max_str)
        return cls(
            min=Point3D(min_x, min_y, min_z),
            max=Point3D(max_x, max_y, max_z),
            set_to_on=cls.SET_TO_ON_MAP[set_to_on_str],
        )

    def __iter__(self) -> Iterable[Point3D]:
        return self.iter()

    def iter(
        self, limit_min: Optional[Point3D] = None,
        limit_max: Optional[Point3D] = None,
    ) -> Iterable[Point3D]:
        if limit_min is None:
            limit_min = self.min
        if limit_max is None:
            limit_max = self.max
        xs = range(
            max(limit_min.x, self.min.x),
            min(limit_max.x, self.max.x) + 1,
        )
        ys = range(
            max(limit_min.y, self.min.y),
            min(limit_max.y, self.max.y) + 1,
        )
        zs = range(
            max(limit_min.z, self.min.z),
            min(limit_max.z, self.max.z) + 1,
        )
        for x in xs:
            for y in ys:
                for z in zs:
                    yield Point3D(x, y, z)

    def apply(self, reactor: Reactor) -> Reactor:
        for point in self.iter(limit_min=reactor.min, limit_max=reactor.max):
            reactor[point] = self.set_to_on
        return reactor


Challenge.main()
challenge = Challenge()
