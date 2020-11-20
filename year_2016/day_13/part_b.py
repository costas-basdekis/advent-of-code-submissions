#!/usr/bin/env python3
from collections import Set

from aox.utils import Timer

from utils import BaseChallenge, Point2D
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        135
        """
        maze = part_a.Maze(int(_input))
        if debug:
            for depth in [0, 1, 2, 49]:
                seen = MazeSolverExtended()\
                    .flood(maze, Point2D(1, 1), depth, debug=debug)
                print(f"Depth: {depth}, seen: {len(seen)}")
                print(maze.show(solution=seen))
        seen_50 = MazeSolverExtended()\
            .flood(maze, Point2D(1, 1), 50, debug=debug)
        if debug:
            print(f"Depth: 50, seen: {len(seen_50)}")
            print(maze.show(solution=seen_50))
        return len(seen_50)


class MazeSolverExtended(part_a.MazeSolver):
    def flood(self, maze: part_a.Maze, start: part_a.Position, depth: int,
              debug: bool = False) -> Set[part_a.Position]:
        if depth <= 0:
            maze.get(start)
            return {start}
        stack = [(0, start)]
        seen = {start}
        if debug:
            step = 0
            timer = Timer()
        while stack:
            distance, position = stack.pop(0)
            next_distance = distance + 1
            neighbours = position.get_manhattan_neighbours()
            for neighbour in neighbours:
                if not maze.is_position_valid(neighbour):
                    continue
                if neighbour in seen:
                    continue
                if maze.get(neighbour):
                    continue
                seen.add(neighbour)
                if next_distance >= depth:
                    continue
                stack.append((next_distance, neighbour))

            if debug:
                step += 1
                if step % 1000 == 0:
                    print(
                        f"Step: {step}, time: "
                        f"{timer.get_pretty_current_duration(0)}, seen: "
                        f"{len(seen)}, stack: {len(stack)}")
                    print(maze.show(solution=seen))

        return seen


Challenge.main()
challenge = Challenge()
