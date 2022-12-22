#!/usr/bin/env python3
from typing import Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point3D, min_and_max_tuples
from year_2022.day_18 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2524
        """
        return DropletExtended\
            .from_points_text(_input)\
            .get_exterior_surface_count()


class DropletExtended(part_a.Droplet):
    def get_exterior_surface_count(self) -> int:
        """
        >>> DropletExtended.from_points_text(
        ...     "2,2,2").get_exterior_surface_count()
        6
        >>> # print(str(DropletExtended.from_points_text(part_a.LONG_INPUT)))
        >>> # print(str(DropletExtended(DropletExtended.from_points_text(
        >>> #    part_a.LONG_INPUT).get_euclidean_surface_neighbours())))
        >>> DropletExtended.from_points_text(
        ...     part_a.LONG_INPUT).get_exterior_surface_count()
        58
        """
        surface_neighbours = self.get_exterior_surface_neighbours()
        return sum(
            len(set(point.get_manhattan_neighbours()) & surface_neighbours)
            for point in self.points
        )

    def get_interior_surface_count(self) -> int:
        """
        >>> DropletExtended.from_points_text(
        ...     "2,2,2").get_interior_surface_count()
        0
        >>> DropletExtended.from_points_text(
        ...     part_a.LONG_INPUT).get_interior_surface_count()
        6
        """
        surface_neighbours = self.get_interior_surface_neighbours()
        return sum(
            len(set(point.get_manhattan_neighbours()) & surface_neighbours)
            for point in self.points
        )

    def get_exterior_surface_neighbours(self) -> Set[Point3D]:
        return (
            self.get_surface_neighbours()
            - self.get_interior_surface_neighbours()
        )

    def get_interior_surface_neighbours(self) -> Set[Point3D]:
        surface_neighbours = self.get_euclidean_surface_neighbours()
        (min_x, _, _), _ = min_and_max_tuples(surface_neighbours)
        an_exterior_neighbour = next(
            point
            for point in surface_neighbours
            if point.x == min_x
        )
        queue = [an_exterior_neighbour]
        remaining = surface_neighbours - {an_exterior_neighbour}
        # print(min_x, queue, remaining)
        while queue and remaining:
            point = queue.pop(0)
            neighbours = set(point.get_manhattan_neighbours())
            remaining_neighbours = neighbours & remaining
            # print(" *", point, neighbours, remaining, remaining_neighbours)
            queue.extend(remaining_neighbours)
            remaining -= remaining_neighbours

        return remaining & self.get_surface_neighbours()

    def get_euclidean_surface_neighbours(self) -> Set[Point3D]:
        """
        >>> sorted(DropletExtended.from_points_text(
        ...     "2,2,2").get_euclidean_surface_neighbours())
        [Point3D(x=1, y=1, z=1), ...]
        """
        return {
            neighbour
            for point in self.points
            for neighbour in point.get_euclidean_neighbours()
        } - self.points

    def __str__(self) -> str:
        (min_x, min_y, min_z), (max_x, max_y, max_z) = \
            min_and_max_tuples(self.points)
        return "\n+{}+\n".format("-" * (max_y - min_y + 1 - 2)).join(
            "\n".join(
                "".join(
                    "X"
                    if point in self.points else
                    "."
                    for x in range(min_x, max_x + 1)
                    for point in [Point3D(x, y, z)]
                )
                for y in range(min_y, max_y + 1)
            )
            for z in range(min_z, max_z + 1)
        )


Challenge.main()
challenge = Challenge()
