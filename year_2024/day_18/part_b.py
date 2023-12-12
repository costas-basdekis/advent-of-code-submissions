#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2024.day_18 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        52,32
        """
        return ChangingSpace.from_text(_input).find_first_point_text_to_block_end(debugger=debugger)


@dataclass
class ChangingSpace:
    obstacle_list: List[Point2D]
    space: part_a.Space

    @classmethod
    def from_text(cls, text: str, limit: int = 1024, size: int = 71) -> "ChangingSpace":
        obstacle_list = [
            Point2D(int(x_str), int(y_str))
            for line in text.strip().splitlines()
            for x_str, y_str in [line.strip().split(",")]
        ]
        space = part_a.Space.from_text(text, limit=limit, size=size)
        return cls(obstacle_list=obstacle_list, space=space)

    def find_first_point_text_to_block_end(self, debugger: Debugger = Debugger(enabled=False)) -> Optional[str]:
        """
        >>> ChangingSpace.from_text(part_a.EXAMPLE_TEXT, limit=12, size=7).find_first_point_to_block_end()
        6,1
        """
        first_point = self.find_first_point_to_block_end(debugger=debugger)
        if first_point is None:
            return None
        return f"{first_point.x},{first_point.y}"

    def find_first_point_to_block_end(self, debugger: Debugger = Debugger(enabled=False)) -> Optional[Point2D]:
        """
        >>> ChangingSpace.from_text(part_a.EXAMPLE_TEXT, limit=12, size=7).find_first_point_to_block_end()
        Point2D(x=6, y=1)
        """
        if not self.is_end_reachable():
            return None
        while debugger.step_if(True):
            last_obstacle = self.drop_next_obstacle()
            if last_obstacle is None:
                break
            if not self.is_end_reachable():
                return last_obstacle
            if debugger.should_report():
                debugger.default_report_if(f"Checking {len(self.space.obstacles)}/{len(self.obstacle_list)}...")
        return None

    def drop_next_obstacle(self) -> Optional[Point2D]:
        next_obstacle_index = len(self.space.obstacles)
        if next_obstacle_index >= len(self.obstacle_list):
            return None
        next_obstacle = self.obstacle_list[next_obstacle_index]
        self.space = part_a.Space(
            obstacles=self.space.obstacles | {next_obstacle},
            size=self.space.size,
        )
        return next_obstacle

    def is_end_reachable(self) -> bool:
        try:
            self.space.find_shortest_path()
        except Exception as e:
            if e.args and isinstance(e.args[0], str) and "Could not find path from" in e.args[0]:
                return False
            raise
        return True


Challenge.main()
challenge = Challenge()
