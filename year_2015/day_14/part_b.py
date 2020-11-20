#!/usr/bin/env python3
from typing import Tuple, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1059
        """
        return ReindeerSetExtended.from_reindeers_text(_input)\
            .get_highest_points_until(2503)


class ReindeerSetExtended(part_a.ReindeerSet):
    def get_highest_points_until(self, duration: int) -> int:
        """
        >>> ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_highest_points_until(3)
        3
        >>> ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_highest_points_until(1000)
        689
        """
        return max(self.get_total_points_until(duration))

    def get_total_points_until(self, duration: int) -> Tuple[int, ...]:
        """
        >>> ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_total_points_until(3)
        (0, 3)
        >>> ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_total_points_until(1000)
        (312, 689)
        """
        points = [0] * len(self.reindeers)
        for partial_points in self.get_all_points_for_distances_until(duration):
            for index, partial_point in enumerate(partial_points):
                points[index] += partial_point

        return tuple(points)

    def get_all_points_for_distances_until(self, duration: int,
                                           ) -> Iterable[Tuple[int, ...]]:
        """
        >>> list(ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_all_points_for_distances_until(3))
        [(0, 1), (0, 1), (0, 1)]
        """
        return map(
            self.get_points_for_distances,
            self.get_all_distance_tuples_until(duration))

    def get_all_distance_tuples_until(self, duration: int,
                                      ) -> Iterable[Tuple[int, ...]]:
        """
        >>> list(ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_all_distance_tuples_until(3))
        [(14, 16), (28, 32), (42, 48)]
        """
        for partial_duration in range(1, duration + 1):
            yield self.get_all_distances_after(partial_duration)

    def get_points_for_distances(self, distances: Tuple[int, ...],
                                 ) -> Tuple[int, ...]:
        """
        >>> ReindeerSetExtended([]).get_points_for_distances((0, 0, 0))
        (1, 1, 1)
        >>> ReindeerSetExtended([]).get_points_for_distances((5, 10, 10))
        (0, 1, 1)
        >>> ReindeerSetExtended([]).get_points_for_distances((15, 10, 10))
        (1, 0, 0)
        """
        max_distance = max(distances)
        return tuple(
            1
            if distance == max_distance else
            0
            for distance in distances
        )

    def get_all_distances_after(self, duration: int) -> Tuple[int, ...]:
        """
        >>> ReindeerSetExtended.from_reindeers_text(
        ...     "Comet can fly 14 km/s for 10 seconds, "
        ...     "but then must rest for 127 seconds.\\n"
        ...     "Dancer can fly 16 km/s for 11 seconds, "
        ...     "but then must rest for 162 seconds.\\n"
        ... ).get_all_distances_after(0)
        (0, 0)
        """
        return tuple(
            reindeer.get_distance_after(duration)
            for reindeer in self.reindeers
        )


Challenge.main()
challenge = Challenge()
