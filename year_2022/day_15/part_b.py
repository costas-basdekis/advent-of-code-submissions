#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Iterable, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D,  min_and_max_tuples
from year_2022.day_15 import part_a
from year_2022.day_15.part_a import SensorSet, LONG_INPUT


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        12630143363767
        """
        return BeaconFinder\
            .from_sensors_text(_input)\
            .find_tuning_frequency(BigLimits, debugger=debugger)


Limits = Tuple[Point2D, Point2D]
SmallLimits: Limits = (Point2D(0, 0), Point2D(20 + 1, 20 + 1))
BigLimits: Limits = (Point2D(0, 0), Point2D(4000000 + 1, 4000000 + 1))


@dataclass
class BeaconFinder:
    sensor_set: SensorSet

    @classmethod
    def from_sensors_text(cls, sensors_text: str) -> "BeaconFinder":
        return cls(sensor_set=SensorSet.from_sensors_text(sensors_text))

    def find_tuning_frequency(
        self, limits: Limits, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> BeaconFinder.from_sensors_text(LONG_INPUT)\\
        ...     .find_tuning_frequency(SmallLimits)
        56000011
        """
        position = self.find_beacon(limits, debugger=debugger)
        return position.x * 4000000 + position.y

    def find_beacon(
        self, limits: Limits, debugger: Debugger = Debugger(enabled=False),
    ) -> Point2D:
        """
        >>> BeaconFinder.from_sensors_text(LONG_INPUT).find_beacon(SmallLimits)
        Point2D(x=14, y=11)
        """
        possible_beacons = set()
        _min, _max = limits
        x_range = range(_min.x, _max.x + 1)
        y_range = range(_min.y, _max.y + 1)
        applicable_sensors = [
            sensor
            for sensor in self.sensor_set.sensors
            if self.do_ranges_touch(x_range, range(
                sensor.position.x - sensor.closest_beacon_distance,
                sensor.position.x + sensor.closest_beacon_distance + 1,
            ))
            and self.do_ranges_touch(y_range, range(
                sensor.position.y - sensor.closest_beacon_distance,
                sensor.position.y + sensor.closest_beacon_distance + 1,
            ))
        ]
        for y in debugger.stepping(y_range):
            ranges = set()
            for index, sensor in enumerate(applicable_sensors):
                debugger.default_report_if(
                    f"Checking row {y}, sensor "
                    f"{index + 1}/{len(applicable_sensors)}, "
                    f"{len(possible_beacons)} possible beacons "
                    f"(min is {min(possible_beacons, default=None)})"
                )
                _range = sensor.get_impossible_x_position_range_at_row(y)
                touching_ranges = {
                    other_range
                    for other_range in ranges
                    if self.do_ranges_touch(_range, other_range)
                }
                if not touching_ranges:
                    new_range = _range
                else:
                    touching_ranges |= {_range}
                    new_range = range(
                        min(
                            other_range.start
                            for other_range in touching_ranges
                        ),
                        max(
                            other_range.stop
                            for other_range in touching_ranges
                        ),
                    )
                    ranges -= touching_ranges
                ranges.add(new_range)
                row_is_full = (
                    new_range.start <= x_range.start
                    and x_range.stop <= new_range.stop
                )
                if row_is_full:
                    break
            limited_ranges = sorted(filter(None, (
                range(
                    max(_range.start, x_range.start),
                    min(_range.stop, x_range.stop),
                )
                for _range in ranges
            )), key=lambda _range: _range.start)
            if limited_ranges == [x_range]:
                continue
            if len(limited_ranges) == 1:
                _range, = limited_ranges
                if _range.start == x_range.start:
                    if _range.stop != x_range.stop - 1:
                        raise Exception(
                            f"Found a row with multiple holes: y={y}, "
                            f"{limited_ranges}"
                        )
                    possible_beacons.add(Point2D(x_range.stop, y))
                elif _range.stop == x_range.stop:
                    if _range.start != x_range.start + 1:
                        raise Exception(
                            f"Found a row with multiple holes: y={y}, "
                            f"{limited_ranges}"
                        )
                    possible_beacons.add(Point2D(x_range.start, y))
            elif len(limited_ranges) == 2:
                first_range, second_range = limited_ranges
                if first_range.start != x_range.start:
                    raise Exception(
                        f"Found a row with multiple holes: y={y}, "
                        f"{limited_ranges}"
                    )
                if first_range.stop != second_range.start - 1:
                    raise Exception(
                        f"Found a row with multiple holes: y={y}, "
                        f"{limited_ranges}"
                    )
                if second_range.stop != x_range.stop:
                    raise Exception(
                        f"Found a row with multiple holes: y={y}, "
                        f"{limited_ranges}"
                    )
                possible_beacons.add(Point2D(first_range.stop, y))
            else:
                raise Exception(
                    f"Found a row with multiple potential holes: y={y}, "
                    f"{limited_ranges}"
                )
        if len(possible_beacons) != 1:
            raise Exception(
                f"There wasn't exactly one possible beacon: {possible_beacons}"
            )
        beacon, = possible_beacons
        return beacon

    def do_ranges_touch(self, left: range, right: range) -> bool:
        """
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(4))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(4), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(1, 5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(1, 5), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(1, 4))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(1, 4), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(1, 6))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(1, 6), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(-1, 4))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(-1, 4), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(5, 10))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5, 10), range(5))
        True
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(6, 10))
        False
        >>> BeaconFinder(None).do_ranges_touch(range(6, 10), range(5))
        False
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(-10, -6))
        False
        >>> BeaconFinder(None).do_ranges_touch(range(-10, -6), range(5))
        False
        >>> BeaconFinder(None).do_ranges_touch(range(5), range(3, 2))
        False
        >>> BeaconFinder(None).do_ranges_touch(range(3, 2), range(5))
        False
        """
        return bool(
            left
            and right
            and right.stop >= left.start
            and left.stop >= right.start
        )


@dataclass
class SensorVisualiser:
    sensors: Set[Point2D]
    beacons: Set[Point2D]
    empty: Set[Point2D]

    @classmethod
    def from_sensors_text(
        cls, sensors_text: str,
        limits: Limits = SmallLimits,
    ) -> "SensorVisualiser":
        """
        >>> print(str(SensorVisualiser.from_sensors_text(LONG_INPUT)))
        ##S###################
        ####################S#
        #############S########
        ##############SB######
        ######################
        ######################
        ######################
        ########S#######S#####
        ######################
        ######################
        ##B###################
        S#############.#######
        ######################
        ######################
        ############S#######S#
        ######################
        #########SB###########
        ##############S#######
        ##S###################
        ######################
        ##########S######S####
        ######################
        """
        return cls.from_sensor_set(
            SensorSet.from_sensors_text(sensors_text),
            limits=limits,
        )

    @classmethod
    def from_sensor_set(
        cls, sensor_set: SensorSet,
        limits: Limits = SmallLimits,
    ) -> "SensorVisualiser":
        sensors = set(cls.limit_set((
            sensor.position
            for sensor in sensor_set.sensors
        ), limits=limits))
        beacons = set(cls.limit_set((
            sensor.closest_beacon_position
            for sensor in sensor_set.sensors
        ), limits=limits))
        empty = set(cls.limit_set((
            position
            for sensor in sensor_set.sensors
            for position in sensor.get_impossible_positions()
        ), limits=limits)) - sensors - beacons
        return cls(sensors=sensors, beacons=beacons, empty=empty)

    @classmethod
    def limit_set(
        cls, items: Iterable[Point2D],
        limits: Limits = SmallLimits,
    ) -> Iterable[Point2D]:
        _min, _max = limits
        return (
            item
            for item in items
            if _min.x <= item.x <= _max.x
            and _min.y <= item.y <= _max.y
        )

    def find_non_empty_position(self) -> Point2D:
        """
        >>> SensorVisualiser.from_sensors_text(LONG_INPUT)\\
        ...     .find_non_empty_position()
        Point2D(x=14, y=11)
        """
        (min_x, min_y), (max_x, max_y) = \
            min_and_max_tuples(self.sensors | self.beacons | self.empty)
        positions = (
            position
            for y in range(min_y, max_y + 1)
            for x in range(min_x, max_x + 1)
            for position in [Point2D(x, y)]
            if position not in self.sensors
            and position not in self.beacons
            and position not in self.empty
        )
        for position in positions:
            break
        else:
            raise Exception(f"No non-empty positions found")
        for _ in positions:
            raise Exception(f"Multiple non-empty positions found")
        return position

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = \
            min_and_max_tuples(self.sensors | self.beacons | self.empty)
        return "\n".join(
            "".join(
                "S"
                if position in self.sensors else
                "B"
                if position in self.beacons else
                "#"
                if position in self.empty else
                "."
                for x in range(min_x, max_x + 1)
                for position in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )


Challenge.main()
challenge = Challenge()
