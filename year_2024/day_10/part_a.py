#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        754
        """
        return Island.from_text(_input).get_all_trailhead_scores()


@dataclass
class Island:
    heights: Dict[Point2D, int]

    @classmethod
    def from_text(cls, text: str) -> "Island":
        """
        >>> print(Island.from_text('''
        ...     0123
        ...     1234
        ...     8765
        ...     9876
        ... '''))
        0123
        1234
        8765
        9876
        """
        return cls(heights={
            Point2D(x, y): int(char)
            for y, line in enumerate(text.strip().splitlines())
            for x, char in enumerate(line.strip())
            if char != "."
        })

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = self.boundaries
        return "\n".join(
            "".join(
                str(self.heights[point])
                if point in self.heights else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
        )

    @cached_property
    def boundaries(self) -> Tuple[Point2D, Point2D]:
        return min_and_max_tuples(self.heights)

    def get_all_trailhead_scores(self) -> int:
        """
        >>> Island.from_text('''
        ...     10..9..
        ...     2...8..
        ...     3...7..
        ...     4567654
        ...     ...8..3
        ...     ...9..2
        ...     .....01
        ... ''').get_all_trailhead_scores()
        3
        >>> Island.from_text('''
        ...     89010123
        ...     78121874
        ...     87430965
        ...     96549874
        ...     45678903
        ...     32019012
        ...     01329801
        ...     10456732
        ... ''').get_all_trailhead_scores()
        36
        """
        return sum(map(self.get_trailhead_score, self.heights))

    def get_trailhead_score(self, trailhead: Point2D) -> int:
        """
        >>> Island.from_text('''
        ...     0123
        ...     1234
        ...     8765
        ...     9876
        ... ''').get_trailhead_score(Point2D(0, 0))
        1
        >>> Island.from_text('''
        ...     ...0...
        ...     ...1...
        ...     ...2...
        ...     6543456
        ...     7.....7
        ...     8.....8
        ...     9.....9
        ... ''').get_trailhead_score(Point2D(3, 0))
        2
        >>> Island.from_text('''
        ...     ..90..9
        ...     ...1.98
        ...     ...2..7
        ...     6543456
        ...     765.987
        ...     876....
        ...     987....
        ... ''').get_trailhead_score(Point2D(3, 0))
        4
        """
        if self.heights.get(trailhead) != 0:
            return 0
        seen = {trailhead}
        queue = [trailhead]
        peak_count = 0
        while queue:
            position = queue.pop()
            height = self.heights[position]
            for next_position in position.get_manhattan_neighbours():
                if next_position in seen:
                    continue
                next_height = self.heights.get(next_position)
                if next_height != height + 1:
                    continue
                seen.add(next_position)
                if next_height == 9:
                    peak_count += 1
                    continue
                queue.append(next_position)
        return peak_count


Challenge.main()
challenge = Challenge()
