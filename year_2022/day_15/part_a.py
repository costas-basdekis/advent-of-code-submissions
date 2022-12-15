#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import Iterable, List, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        4919281
        """
        return SensorSet\
            .from_sensors_text(_input)\
            .get_impossible_position_count_at_row(2000000)


@dataclass
class SensorSet:
    sensors: List["Sensor"]

    @classmethod
    def from_sensors_text(cls, sensors_text: str) -> "SensorSet":
        """
        >>> SensorSet.from_sensors_text(LONG_INPUT)
        SensorSet(sensors=[Sensor(position=Point2D(x=2, y=18),
            closest_beacon_position=Point2D(x=-2, y=15)), ...])
        """
        return cls(
            sensors=list(map(
                Sensor.from_sensor_text,
                sensors_text.strip().splitlines(),
            )),
        )

    def get_impossible_position_count_at_row(self, y: int) -> int:
        """
        >>> sensors = SensorSet.from_sensors_text(LONG_INPUT)
        >>> sensors.get_impossible_position_count_at_row(10)
        26
        """
        _range = self.get_impossible_y_positions_at_row_including_beacons(y)
        beacons_in_row_range = [
            beacon
            for beacon in self.get_beacons()
            if beacon.y == y
            and beacon.x in _range
        ]
        return len(_range) - len(beacons_in_row_range)

    def get_impossible_y_positions_at_row_including_beacons(
        self, y: int,
    ) -> range:
        # TODO: This is wrong!
        ranges = filter(None, (
            sensor.get_impossible_x_position_range_at_row(y)
            for sensor in self.sensors
        ))
        for _range in ranges:
            min_x, max_x = _range.start, _range.stop - 1
            break
        else:
            return range(-1)
        for _range in ranges:
            range_min, range_max = _range.start, _range.stop - 1
            min_x = min(min_x, range_min)
            max_x = max(max_x, range_max)
        return range(min_x, max_x + 1)

    def get_beacons(self) -> Set[Point2D]:
        return {
            sensor.closest_beacon_position
            for sensor in self.sensors
        }


@dataclass
class Sensor:
    position: Point2D
    closest_beacon_position: Point2D

    re_sensor = re.compile(
        r"^Sensor at x=(-?\d+), y=(-?\d+): "
        r"closest beacon is at x=(-?\d+), y=(-?\d+)$"
    )

    @classmethod
    def from_sensor_text(cls, sensor_text: str) -> "Sensor":
        """
        >>> Sensor.from_sensor_text(
        ...     "Sensor at x=2, y=18: closest beacon is at x=-2, y=15")
        Sensor(position=Point2D(x=2, y=18),
            closest_beacon_position=Point2D(x=-2, y=15))
        """
        position_strs = cls.re_sensor.match(sensor_text).groups()
        position_x, position_y, beacon_x, beacon_y = map(int, position_strs)
        return cls(
            position=Point2D(position_x, position_y),
            closest_beacon_position=Point2D(beacon_x, beacon_y),
        )

    def get_impossible_positions(self) -> Iterable[Point2D]:
        closest_beacon_distance = self.closest_beacon_distance
        ys = range(
            self.position.y - closest_beacon_distance,
            self.position.y + closest_beacon_distance + 1,
        )
        for y in ys:
            yield from self.get_impossible_positions_at_row(y)

    def get_impossible_positions_at_row(self, y: int) -> Iterable[Point2D]:
        """
        >>> sensor = Sensor.from_sensor_text(
        ...     "Sensor at x=8, y=7: closest beacon is at x=2, y=10"
        ... )
        >>> list(sensor.get_impossible_positions_at_row(16))
        [Point2D(x=8, y=16)]
        >>> list(sensor.get_impossible_positions_at_row(-2))
        [Point2D(x=8, y=-2)]
        >>> list(sensor.get_impossible_positions_at_row(15))
        [Point2D(x=7, y=15), Point2D(x=8, y=15), Point2D(x=9, y=15)]
        >>> list(sensor.get_impossible_positions_at_row(17))
        []
        """
        for x in self.get_impossible_x_position_range_at_row(y):
            yield Point2D(x, y)

    def get_impossible_x_position_range_at_row(self, y: int) -> range:
        """
        >>> sensor = Sensor.from_sensor_text(
        ...     "Sensor at x=8, y=7: closest beacon is at x=2, y=10"
        ... )
        >>> sensor.get_impossible_x_position_range_at_row(16)
        range(8, 9)
        >>> sensor.get_impossible_x_position_range_at_row(-2)
        range(8, 9)
        >>> sensor.get_impossible_x_position_range_at_row(15)
        range(7, 10)
        >>> sensor.get_impossible_x_position_range_at_row(17)
        range(0, -1)
        >>> Sensor.from_sensor_text(
        ...     "Sensor at x=14, y=3: closest beacon is at x=15, y=3"
        ... ).get_impossible_x_position_range_at_row(3)
        range(13, 16)
        """
        closest_beacon_distance = self.closest_beacon_distance
        row_distance = abs(self.position.y - y)
        difference = closest_beacon_distance - row_distance
        if difference < 0:
            return range(-1)
        start_x = self.position.x - difference
        end_x = self.position.x + difference
        return range(start_x, end_x + 1)

    @property
    def closest_beacon_distance(self) -> int:
        return self.position.manhattan_distance(self.closest_beacon_position)

    def is_row_out_of_range(self, y: int) -> bool:
        row_distance = abs(self.position.y - y)
        return row_distance > self.closest_beacon_distance


Challenge.main()
challenge = Challenge()


LONG_INPUT = """
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
""".strip()
