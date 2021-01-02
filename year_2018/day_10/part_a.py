#!/usr/bin/env python3
import math
import re
import sys
from collections import namedtuple, defaultdict

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'CPJRNKCF'
        """

        return 'CPJRNKCF'

    def play(self):
        play(self.input)


def play(observations_text):
    observations = Observations.from_observations_text(observations_text)
    ranges = observations.get_positions_ranges()
    print(f"Ranges: {ranges}")
    step_count = 10345
    step = 0
    while True:
        if not step:
            print("Initially:")
        else:
            print(f"After {step} seconds:")
        best_ranges = observations\
            .get_best_positions_ranges(width=100, height=20)
        # wide_best_x_range = range(
        #     best_x_range.start - (best_x_range.stop - best_x_range.start) // 2,
        #     best_x_range.stop,
        # )
        # best_ranges = (wide_best_x_range, best_y_range)
        print(observations.show(*best_ranges))
        print(f"Step: {step} (count: {step_count})")
        print("Original ranges:", ranges)
        print("Current best ranges:", best_ranges)
        print(f"Inside that range: {observations.get_count_inside_ranges(best_ranges)}/{len(observations.observations)}")
        center = Point(*observations.get_center())
        total_distance = int(observations.get_distance_total(center))
        print("Center & total distance:", tuple(center), total_distance)
        print("Average time to center:",
              observations.get_average_time_to_point(center))
        while True:
            step_count_str = input("Continue?")
            if not step_count_str:
                break
            try:
                step_count = int(step_count_str)
                break
            except (ValueError, TypeError):
                print(f"Not an integer '{step_count_str}'")
        observations.tick(step_count)
        step += step_count


class Observations:
    @classmethod
    def from_observations_text(cls, observations_text):
        """
        >>> Observations.from_observations_text(
        ...     "position=< 9,  1> velocity=< 0,  2>\\n"
        ...     "position=< 7,  0> velocity=<-1,  0>\\n"
        ...     "position=< 3, -2> velocity=<-1,  1>\\n"
        ... ).observations
        [Observation(position=Point(x=9, y=1), velocity=Point(x=0, y=2)), \
Observation(position=Point(x=7, y=0), velocity=Point(x=-1, y=0)), \
Observation(position=Point(x=3, y=-2), velocity=Point(x=-1, y=1))]
        """
        non_empty_lines = filter(None, observations_text.splitlines())
        return cls(list(map(
            Observation.from_observation_text, non_empty_lines)))

    def __init__(self, observations):
        self.observations = observations

    def tick(self, count=1):
        """
        >>> Observations.from_observations_text(
        ...     "position=< 9,  1> velocity=< 0,  2>\\n"
        ...     "position=< 7,  0> velocity=<-1,  0>\\n"
        ...     "position=< 3, -2> velocity=<-1,  1>\\n"
        ... ).tick().observations
        [Observation(position=Point(x=9, y=3), velocity=Point(x=0, y=2)), \
Observation(position=Point(x=6, y=0), velocity=Point(x=-1, y=0)), \
Observation(position=Point(x=2, y=-1), velocity=Point(x=-1, y=1))]
        """
        self.observations = [
            observation.tick(count=count)
            for observation in self.observations
        ]

        return self

    def show(self, width_or_range=None, height_or_range=None):
        """
        >>> observations_a = Observations.from_observations_text(
        ...     "position=< 9,  1> velocity=< 0,  2>\\n"
        ...     "position=< 7,  0> velocity=<-1,  0>\\n"
        ...     "position=< 3, -2> velocity=<-1,  1>\\n"
        ...     "position=< 6, 10> velocity=<-2, -1>\\n"
        ...     "position=< 2, -4> velocity=< 2,  2>\\n"
        ...     "position=<-6, 10> velocity=< 2, -2>\\n"
        ...     "position=< 1,  8> velocity=< 1, -1>\\n"
        ...     "position=< 1,  7> velocity=< 1,  0>\\n"
        ...     "position=<-3, 11> velocity=< 1, -2>\\n"
        ...     "position=< 7,  6> velocity=<-1, -1>\\n"
        ...     "position=<-2,  3> velocity=< 1,  0>\\n"
        ...     "position=<-4,  3> velocity=< 2,  0>\\n"
        ...     "position=<10, -3> velocity=<-1,  1>\\n"
        ...     "position=< 5, 11> velocity=< 1, -2>\\n"
        ...     "position=< 4,  7> velocity=< 0, -1>\\n"
        ...     "position=< 8, -2> velocity=< 0,  1>\\n"
        ...     "position=<15,  0> velocity=<-2,  0>\\n"
        ...     "position=< 1,  6> velocity=< 1,  0>\\n"
        ...     "position=< 8,  9> velocity=< 0, -1>\\n"
        ...     "position=< 3,  3> velocity=<-1,  1>\\n"
        ...     "position=< 0,  5> velocity=< 0, -1>\\n"
        ...     "position=<-2,  2> velocity=< 2,  0>\\n"
        ...     "position=< 5, -2> velocity=< 1,  2>\\n"
        ...     "position=< 1,  4> velocity=< 2,  1>\\n"
        ...     "position=<-2,  7> velocity=< 2, -2>\\n"
        ...     "position=< 3,  6> velocity=<-1, -1>\\n"
        ...     "position=< 5,  0> velocity=< 1,  0>\\n"
        ...     "position=<-6,  0> velocity=< 2,  0>\\n"
        ...     "position=< 5,  9> velocity=< 1, -2>\\n"
        ...     "position=<14,  7> velocity=<-2,  0>\\n"
        ...     "position=<-3,  6> velocity=< 2, -1>\\n"
        ... )
        >>> print("!", observations_a.show())
        ! ........#.............
        ................#.....
        .........#.#..#.......
        ......................
        #..........#.#.......#
        ...............#......
        ....#.................
        ..#.#....#............
        .......#..............
        ......#...............
        ...#...#.#...#........
        ....#..#..#.........#.
        .......#..............
        ...........#..#.......
        #...........#.........
        ...#.......#..........
        >>> print("!", observations_a.tick().tick().tick().tick()
        ...     .show(range(-6, 16), range(-4, 12)))
        ! ......................
        ......................
        ......................
        ............#.........
        ........##...#.#......
        ......#.....#..#......
        .....#..##.##.#.......
        .......##.#....#......
        ...........#....#.....
        ..............#.......
        ....#......#...#......
        .....#.....##.........
        ...............#......
        ...............#......
        ......................
        ......................
        """
        if width_or_range is None or height_or_range is None:
            default_x_range, default_y_range = self.get_positions_ranges()
        else:
            default_x_range, default_y_range = None, None
        if isinstance(width_or_range, int):
            width = width_or_range
            x_range = range(width)
        elif width_or_range is not None:
            x_range = width_or_range
        else:
            x_range = default_x_range
        if isinstance(height_or_range, int):
            height = height_or_range
            y_range = range(height)
        elif height_or_range is not None:
            y_range = height_or_range
        else:
            y_range = default_y_range

        observations_positions = {
            observation.position
            for observation in self.observations
        }
        return "\n".join(
            "".join(
                "#"
                if (x, y) in observations_positions else
                "."
                for x in x_range
            )
            for y in y_range
        )

    def get_positions_ranges(self, bounds=None):
        if bounds is None:
            bounds = self.get_positions_bounds()
        min_x, max_x, min_y, max_y = bounds

        return range(min_x, max_x + 1), range(min_y, max_y + 1)

    def get_positions_bounds(self):
        min_x = min(observation.position.x for observation in self.observations)
        max_x = max(observation.position.x for observation in self.observations)
        min_y = min(observation.position.y for observation in self.observations)
        max_y = max(observation.position.y for observation in self.observations)

        return min_x, max_x, min_y, max_y

    def get_best_positions_ranges(self, width=50, height=50):
        return self.get_positions_ranges(
            self.get_best_positions_bounds(width=width, height=height))

    def get_best_positions_bounds(self, width=50, height=50):
        count_by_window = defaultdict(lambda: 0)
        half_width = width // 2
        half_height = height // 2
        for observation in self.observations:
            current_x_window = observation.position.x // width * width
            current_y_window = observation.position.y // height * height
            previous_x_window = current_x_window - half_width
            previous_y_window = current_y_window - half_height
            next_x_window = current_x_window + half_width
            next_y_window = current_y_window + half_height

            for x_window in (previous_x_window, current_x_window, next_x_window):
                for y_window in (previous_y_window, current_y_window, next_y_window):
                    count_by_window[(x_window, y_window)] += 1

        max_count = max(count_by_window.values())
        best_windows = (
            window
            for window, count in count_by_window.items()
            if count == max_count
        )

        best_x_window, best_y_window = next(iter(best_windows))
        min_x, max_x = best_x_window, best_x_window + width
        min_y, max_y = best_y_window, best_y_window + height

        return min_x, max_x, min_y, max_y

    def get_center(self):
        average_x = int(average(
            observation.position.x
            for observation in self.observations
        ))
        average_y = int(average(
            observation.position.y
            for observation in self.observations
        ))

        return average_x, average_y

    def get_distance_total(self, point):
        return sum(
            observation.position.get_distance(point)
            for observation in self.observations
        )

    def get_average_time_to_point(self, point):
        return average(
            observation.get_time_to_point(point)
            for observation in self.observations
        )

    def get_count_inside_ranges(self, ranges):
        x_range, y_range = ranges
        return sum(
            1
            for observation in self.observations
            if observation.position.x in x_range
            and observation.position.y in y_range
        )


def average(items):
    total = 0
    count = 0
    for item in items:
        total += item
        count += 1

    return total / count


class Observation(namedtuple("Observation", ("position", "velocity"))):
    re_observation = re.compile(r"^position=(.*) velocity=(.*)$")

    @classmethod
    def from_observation_text(cls, observation_text):
        """
        >>> Observation.from_observation_text("position=< 7,  0> velocity=<-1,  0>")
        Observation(position=Point(x=7, y=0), velocity=Point(x=-1, y=0))
        """

        position_str, velocity_str = \
            cls.re_observation.match(observation_text).groups()

        return cls(
            Point.from_point_text(position_str),
            Point.from_point_text(velocity_str))

    def tick(self, count=1):
        """
        >>> Observation(Point(3, 9), Point(1, -2)).tick()
        Observation(position=Point(x=4, y=7), velocity=Point(x=1, y=-2))
        >>> Observation(Point(3, 9), Point(1, -2)).tick().tick().tick()
        Observation(position=Point(x=6, y=3), velocity=Point(x=1, y=-2))
        """
        return self._replace(position=self.position + self.velocity * count)

    def get_time_to_point(self, other):
        if self.velocity.x == 0:
            return (other.y - self.position.y) / self.velocity.y
        elif self.velocity.y == 0:
            return (other.x - self.position.x) / self.velocity.x
        else:
            time_to_x = (other.x - self.position.x) / self.velocity.x
            time_to_y = (other.y - self.position.y) / self.velocity.y

            return (
                time_to_x * self.velocity.x
                + time_to_y * self.velocity.y
            ) / (abs(self.velocity.x) + abs(self.velocity.y))


class Point(namedtuple("Point", ("x", "y"))):
    re_point = re.compile(r"^<\s*(-?\d+),\s*(-?\d+)>$")

    @classmethod
    def from_point_text(cls, point_text):
        """
        >>> Point.from_point_text("< 9,  1>")
        Point(x=9, y=1)
        >>> Point.from_point_text("<-6, 10>")
        Point(x=-6, y=10)
        >>> Point.from_point_text("<10, -3>")
        Point(x=10, y=-3)
        """
        x_str, y_str = cls.re_point.match(point_text).groups()

        return cls(int(x_str), int(y_str))

    def __add__(self, other):
        """
        >>> Point(1, 2) + Point(-4, 5)
        Point(x=-3, y=7)
        >>> Point(0, 0) + Point(-4, 5)
        Point(x=-4, y=5)
        >>> Point(1, 2) + Point(0, 0)
        Point(x=1, y=2)
        """
        if tuple(self) == (0, 0):
            return other
        if tuple(other) == (0, 0):
            return self
        return type(self)(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return type(self)(self.x * other, self.y * other)

    def get_distance(self, other):
        d_x = self.x - other.x
        d_y = self.y - other.y
        return math.sqrt(d_x * d_x + d_y * d_y)


challenge = Challenge()
challenge.main()
