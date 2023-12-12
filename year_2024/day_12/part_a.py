#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """
        return Garden.from_text(_input).get_total_regions_price()


@dataclass
class Garden:
    plants: Dict[Point2D, str]

    @classmethod
    def from_text(cls, text: str) -> "Garden":
        """
        >>> print(Garden.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... '''))
        AAAA
        BBCD
        BBCC
        EEEC
        """
        return cls(plants={
            Point2D(x, y): char
            for y, line in enumerate(text.strip().splitlines())
            for x, char in enumerate(line.strip())
        })

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                self.plants[point]
                if point in self.plants else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    def show_regions(self, regions: Optional[List["Garden"]] = None) -> str:
        if regions is None:
            regions = self.get_regions()
        region_id_by_position = {
            point: index
            for index, region in enumerate(regions)
            for point in region.plants
        }
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "{}{}{}".format(
                "+{}+\n".format(
                    "+".join(
                        "-"
                        for _ in range(min_x, max_x + 1)
                    ),
                ) if y == 0 else "",
                "".join(
                    "{}{}{}".format(
                        "|" if x == 0 else "",
                        self.plants[Point2D(x, y)],
                        "|" if region_id_by_position.get(Point2D(x + 1, y)) != region_id_by_position[Point2D(x, y)] else " ",
                    )
                    for x in range(min_x, max_x + 1)
                ),
                "\n+{}".format(
                    "".join(
                        "{}{}".format(
                            (
                                "-"
                                if region_id_by_position[Point2D(x, y)] != region_id_by_position.get(Point2D(x, y + 1)) else
                                " "
                            ),
                            (
                                " "
                                if len({
                                    region_id_by_position[Point2D(x, y)],
                                    region_id_by_position.get(Point2D(x + 1, y)),
                                    region_id_by_position.get(Point2D(x, y + 1)),
                                    region_id_by_position.get(Point2D(x + 1, y + 1)),
                                }) == 1 else
                                "+"
                            ),
                        )
                        for x in range(min_x, max_x + 1)
                    )
                ),
            )
            for y in range(min_y, max_y + 1)
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.plants)

    @cached_property
    def area(self) -> int:
        return len(self.plants)

    @cached_property
    def perimeter(self) -> int:
        return sum(
            1
            for point in self.plants
            for neighbour in point.get_manhattan_neighbours()
            if neighbour not in self.plants
        )

    @cached_property
    def price(self) -> int:
        """
        >>> _garden = Garden.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''')
        >>> _regions = _garden.get_regions()
        >>> sorted(((min(_region.plants.values()), _region.area, _region.perimeter, _region.price) for _region in _regions), key=lambda item: min(item[0]))
        [('A', 4, 10, 40), ('B', 4, 8, 32), ('C', 4, 10, 40), ('D', 1, 4, 4), ('E', 3, 8, 24)]
        """
        return self.area * self.perimeter

    def get_total_regions_price(self) -> int:
        """
        >>> Garden.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''').get_total_regions_price()
        140
        >>> Garden.from_text('''
        ...     OOOOO
        ...     OXOXO
        ...     OOOOO
        ...     OXOXO
        ...     OOOOO
        ... ''').get_total_regions_price()
        772
        >>> Garden.from_text('''
        ...     RRRRIICCFF
        ...     RRRRIICCCF
        ...     VVRRRCCFFF
        ...     VVRCCCJFFF
        ...     VVVVCJJCFE
        ...     VVIVCCJJEE
        ...     VVIIICJJEE
        ...     MIIIIIJJEE
        ...     MIIISIJEEE
        ...     MMMISSJEEE
        ... ''').get_total_regions_price()
        1930
        """
        return sum(
            region.price
            for region in self.get_regions()
        )

    def get_regions(self: Self["Garden"]) -> List[Self["Garden"]]:
        """
        >>> _garden = Garden.from_text('''
        ...     AAAA
        ...     BBCD
        ...     BBCC
        ...     EEEC
        ... ''')
        >>> _regions = _garden.get_regions()
        >>> print(_garden.show_regions(regions=_regions))
        +-+-+-+-+
        |A A A A|
        +-+-+-+-+
        |B B|C|D|
        +   + +-+
        |B B|C C|
        +-+-+-+ +
        |E E E|C|
        +-+-+-+-+
        >>> print("\\n--\\n".join(sorted(map(str, _regions))))
        AAAA
        --
        BB
        BB
        --
        C.
        CC
        .C
        --
        D
        --
        EEE
        """
        start = min(self.plants)
        first_region = {start}
        regions_by_position = {start: first_region}
        regions = [first_region]
        queue = [start]
        while queue:
            position = queue.pop(0)
            region = regions_by_position[position]
            plant = self.plants[position]
            for next_position in position.get_manhattan_neighbours():
                if next_position not in self.plants:
                    continue
                if next_position in regions_by_position:
                    existing_region = regions_by_position[next_position]
                    if existing_region != region and self.plants[min(existing_region)] == plant:
                        existing_region.update(region)
                        regions_by_position.update({
                            point: existing_region
                            for point in region
                        })
                        regions.remove(region)
                        region = existing_region
                    continue
                if plant == self.plants[next_position]:
                    next_region = region
                else:
                    next_region = set()
                    regions.append(next_region)
                regions_by_position[next_position] = next_region
                next_region.add(next_position)
                queue.append(next_position)
        cls = type(self)
        return [
            cls(plants={
                point: plant
                for point in region
            })
            for region in regions
            for plant in [self.plants[min(region)]]
        ]


Challenge.main()
challenge = Challenge()
