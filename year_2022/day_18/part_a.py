#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Iterable, Set, Union

import utils
from aox.challenge import Debugger
from utils import BaseChallenge, Point3D


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        4332
        """
        return Droplet.from_points_text(_input).get_surface_count()


@dataclass
class Droplet:
    points: Set[Point3D]

    @classmethod
    def from_points_text(cls, points_text: str) -> "Droplet":
        """
        >>> Droplet.from_points_text("2,2,2")
        Droplet(points={Point3D(x=2, y=2, z=2)})
        >>> Droplet.from_points_text(LONG_INPUT)
        Droplet(points={...Point3D(x=2, y=2, z=2), ...})
        """
        return cls(
            points={
                Point3D(coordinates)
                for point_text in points_text.strip().splitlines()
                for coordinates in [tuple(map(int, point_text.split(",")))]
            },
        )

    def get_surface_count(self) -> int:
        """
        >>> Droplet.from_points_text("2,2,2").get_surface_count()
        6
        >>> Droplet.from_points_text(LONG_INPUT).get_surface_count()
        64
        """
        return utils.iterable_length(self.iterate_surface_neighbours())

    def iterate_surface_neighbours(self) -> Iterable[Point3D]:
        """
        >>> sorted(Droplet.from_points_text(
        ...     "2,2,2").iterate_surface_neighbours())
        [Point3D(x=1, y=2, z=2), ...]
        """
        for point in self.points:
            for neighbour in point.get_manhattan_neighbours():
                if neighbour in self.points:
                    continue
                yield neighbour


Challenge.main()
challenge = Challenge()


LONG_INPUT = """
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
""".strip()
