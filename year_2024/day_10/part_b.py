#!/usr/bin/env python3
from typing import Dict, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2024.day_10 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1609
        """
        return IslandExtended.from_text(_input).get_all_trailhead_ratings()


class IslandExtended(part_a.Island):
    def get_all_trailhead_ratings(self) -> int:
        """
        >>> IslandExtended.from_text('''
        ...     10..9..
        ...     2...8..
        ...     3...7..
        ...     4567654
        ...     ...8..3
        ...     ...9..2
        ...     .....01
        ... ''').get_all_trailhead_ratings()
        3
        >>> IslandExtended.from_text('''
        ...     89010123
        ...     78121874
        ...     87430965
        ...     96549874
        ...     45678903
        ...     32019012
        ...     01329801
        ...     10456732
        ... ''').get_all_trailhead_ratings()
        81
        """
        return sum(map(self.get_trailhead_rating, self.heights))

    def get_trailhead_rating(self, trailhead: Point2D) -> int:
        """
        >>> IslandExtended.from_text('''
        ...     .....0.
        ...     ..4321.
        ...     ..5..2.
        ...     ..6543.
        ...     ..7..4.
        ...     ..8765.
        ...     ..9....
        ... ''').get_trailhead_rating(Point2D(5, 0))
        3
        >>> IslandExtended.from_text('''
        ...     ..90..9
        ...     ...1.98
        ...     ...2..7
        ...     6543456
        ...     765.987
        ...     876....
        ...     987....
        ... ''').get_trailhead_rating(Point2D(3, 0))
        13
        >>> IslandExtended.from_text('''
        ...     012345
        ...     123456
        ...     234567
        ...     345678
        ...     4.6789
        ...     56789.
        ... ''').get_trailhead_rating(Point2D(0, 0))
        227
        """
        if self.heights.get(trailhead) != 0:
            return 0
        queue = [trailhead]
        paths_by_position: Dict[Point2D, Set[Tuple[Point2D, ...]]] = {trailhead: {(trailhead,)}}
        peaks = set()
        while queue:
            position = queue.pop(0)
            height = self.heights[position]
            for next_position in position.get_manhattan_neighbours():
                if next_position in paths_by_position:
                    paths_by_position[next_position].update(
                        path + (next_position,)
                        for path in paths_by_position[position]
                        if next_position not in path
                    )
                    continue
                next_height = self.heights.get(next_position)
                if next_height != height + 1:
                    continue
                paths_by_position[next_position] = {
                    path + (next_position,)
                    for path in paths_by_position[position]
                    if next_position not in path
                }
                if next_height == 9:
                    peaks.add(next_position)
                    continue
                queue.append(next_position)
        # for target, paths in paths_by_position.items():
        #     print(f"For target {target} {len(paths)} paths:")
        #     for path in paths:
        #         print(f" * {path}")
        # print(IslandExtended(heights={
        #     target: len(paths)
        #     for target, paths in paths_by_position.items()
        # }))
        return sum(
            len(paths_by_position[peak])
            for peak in peaks
        )


Challenge.main()
challenge = Challenge()
