#!/usr/bin/env python3
from itertools import groupby
from typing import Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2024.day_14 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        7520
        """
        return SpaceExtended.from_text(_input).find_step_count_for_tree(debugger=debugger)

    def play(self):
        space = SpaceExtended.from_text(self.input)
        time = 0
        while True:
            print(space)
            print(f"At time {time}, left for {time - 1} and right for {time + 1}, f to find")
            char = click.getchar()
            if char == '\x1b[D':
                time -= 1
                offset = -1
                space = space.move(offset)
            elif char == '\x1b[C':
                time += 1
                offset = 1
                space = space.move(offset)
            elif char == "f":
                max_region_count = space.get_largest_region_count()
                print(f"Searching from time {time}, with largest region count {max_region_count}")
                while True:
                    time += 1
                    space = space.move(1)
                    largest_region_count = space.get_largest_region_count()
                    if largest_region_count > max_region_count:
                        max_region_count = largest_region_count
                        print(space)
                        print(f"At time {time}, with largest region count {max_region_count}")
                    if time % 10000 == 0:
                        print(f" * Searching at time {time}, current largest region count {largest_region_count}...")
            else:
                print(f"Unknown key {repr(char)}")
                continue


class SpaceExtended(part_a.Space):
    def find_step_count_for_tree(self, min_region_count: int = 100, start_step_count: int = 1, step_advance_count: int = 103, debugger: Debugger = Debugger(enabled=False)) -> int:
        space = self
        step_count = 0
        if start_step_count != 0:
            space = space.move(start_step_count)
            step_count += start_step_count
        max_region_count = space.get_largest_region_count()
        while debugger.step_if(True):
            largest_region_count = space.get_largest_region_count()
            if largest_region_count >= min_region_count:
                break
            if largest_region_count > max_region_count:
                max_region_count = largest_region_count
            step_count += step_advance_count
            space = space.move(step_advance_count)
            if debugger.should_report():
                debugger.default_report_if(f"Looking at step count {step_count}, largest region count: {largest_region_count}")
        return step_count

    def get_largest_region_count(self) -> int:
        queue = [robot.position for robot in self.robots]
        regions_by_position = {}
        regions = []
        by_position = lambda robot: robot.position
        counts_by_position = {
            position: len(list(items))
            for position, items in groupby(sorted(self.robots, key=by_position), by_position)
        }
        while queue:
            position = queue.pop(0)
            region = regions_by_position.get(position)
            if region is None:
                region = regions_by_position[position] = {position}
                regions.append(region)
            for next_position in position.get_euclidean_neighbours():
                next_position = Point2D(
                    next_position.x % self.width,
                    next_position.y % self.height,
                )
                if next_position not in counts_by_position:
                    continue
                next_region = regions_by_position.get(next_position)
                if next_region:
                    if next_region == region:
                        continue
                    region.update(next_region)
                    regions_by_position.update({
                        other: region
                        for other in next_region
                    })
                    regions.remove(next_region)
                else:
                    region.add(next_position)
                    regions_by_position[next_position] = region
                    queue.append(next_position)
        return max(map(len, regions))


Challenge.main()
challenge = Challenge()
