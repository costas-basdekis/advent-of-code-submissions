#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import List, Generic, Type

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        2655
        """
        return ReindeerSet.from_reindeers_text(_input)\
            .get_furthest_distance_after(2503)


ReindeerT = TV['Reindeer']


@dataclass
class ReindeerSet(Generic[ReindeerT]):
    reindeers: List[ReindeerT]

    @classmethod
    def get_reindeer_class(cls) -> Type[ReindeerT]:
        return get_type_argument_class(cls, ReindeerT)

    @classmethod
    def from_reindeers_text(cls, reindeers_text: str):
        """
        >>> ReindeerSet.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... )
        ReindeerSet(reindeers=[Reindeer(name='Comet', speed=14, fly_time=10,
            rest_time=127),
            Reindeer(name='Dancer', speed=16, fly_time=11, rest_time=162)])
        """
        reindeer_class = cls.get_reindeer_class()
        return cls(list(map(
            reindeer_class.from_reindeer_text, reindeers_text.splitlines())))

    def get_furthest_distance_after(self, duration: int) -> ReindeerT:
        """
        >>> ReindeerSet.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_furthest_distance_after(1000)
        1120
        """
        return self.get_furthest_reindeer_after(duration)\
            .get_distance_after(duration)

    def get_furthest_reindeer_after(self, duration: int) -> ReindeerT:
        """
        >>> ReindeerSet.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_furthest_reindeer_after(1000)
        Reindeer(name='Comet', speed=14, fly_time=10, rest_time=127)
        """
        return max(
            self.reindeers,
            key=lambda reindeer: reindeer.get_distance_after(duration))


@dataclass
class Reindeer:
    name: str
    speed: int
    fly_time: int
    rest_time: int

    re_reindeer = re.compile(
        r"^(\w+) can fly (\d+) km/s for (\d+) seconds, "
        r"but then must rest for (\d+) seconds.$")

    @classmethod
    def from_reindeer_text(cls, reindeer_text: str):
        """
        >>> Reindeer.from_reindeer_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.")
        Reindeer(name='Comet', speed=14, fly_time=10, rest_time=127)
        """
        name, speed_str, fly_time_str, rest_time_str = \
            cls.re_reindeer.match(reindeer_text).groups()

        return cls(name, int(speed_str), int(fly_time_str), int(rest_time_str))

    def get_distance_after(self, duration: int) -> int:
        """
        >>> Reindeer.from_reindeer_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.").get_distance_after(1000)
        1120
        >>> Reindeer.from_reindeer_text(
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.").get_distance_after(1000)
        1056
        """
        cycle_time = self.fly_time + self.rest_time
        full_units = duration // cycle_time
        remainder_time = duration % cycle_time
        remainder_flying_time = min(remainder_time, self.fly_time)

        flying_time = full_units * self.fly_time + remainder_flying_time
        return flying_time * self.speed


Challenge.main()
challenge = Challenge()
