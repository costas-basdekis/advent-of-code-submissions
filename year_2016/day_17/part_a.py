#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from typing import Dict

from aox.challenge import Debugger

from utils import BaseChallenge, get_md5_hex_hash, Point2D


class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        42
        """
        return MazeSolver(_input.strip()).find_path(debugger=debugger)


@dataclass
class MazeSolver:
    passcode: str

    class Direction(Enum):
        Up = "U"
        Down = "D"
        Left = "L"
        Right = "R"

        def __repr__(self):
            return f"{type(self).__name__}.{self.name}"

        @property
        def offset(self) -> Point2D:
            """
            >>> MazeSolver.Direction.Up.offset
            Point2D(x=0, y=-1)
            """
            return self.OFFSET_MAP[self]

    Direction.OFFSET_MAP = {
        Direction.Up: Point2D(0, -1),
        Direction.Down: Point2D(0, 1),
        Direction.Left: Point2D(-1, 0),
        Direction.Right: Point2D(1, 0),
    }

    def find_path(self, start: Point2D = Point2D(0, 0),
                  finish: Point2D = Point2D(3, 3),
                  debugger: Debugger = Debugger(enabled=False)) -> str:
        """
        >>> MazeSolver('ihgpwlah').find_path()
        'DDRRRD'
        >>> MazeSolver('kglvqrro').find_path()
        'DDUDRLRRUDRD'
        >>> MazeSolver('ulqzkmiv').find_path()
        'DRURDRUDDLLDLUURRDULRLDUUDDDRR'
        """
        if start == finish:
            return ''
        stack = [('', Point2D(0, 0))]
        debugger.reset()
        while stack:
            path, position = stack.pop(0)
            path_door_states = self.get_path_door_states(path)
            for direction, door_is_open in path_door_states.items():
                if not door_is_open:
                    continue
                next_position = position.offset(direction.offset)
                if not self.is_position_valid(next_position):
                    continue
                next_path = f"{path}{direction.value}"
                if next_position == finish:
                    return next_path
                stack.append((next_path, next_position))
            if debugger.should_report():
                debugger.report(
                    f"Step: {debugger.step_count}, time: "
                    f"{debugger.pretty_duration_since_start}, stack: "
                    f"{len(stack)}, average speed: {debugger.step_frequency}, "
                    f"recent speed: "
                    f"{debugger.step_frequency_since_last_report}")

        raise Exception(f"Could not find a path from {start} to {finish}")

    def is_position_valid(self, position: Point2D) -> bool:
        """
        >>> MazeSolver('').is_position_valid(Point2D(-1, -1))
        False
        >>> MazeSolver('').is_position_valid(Point2D(-1, 0))
        False
        >>> MazeSolver('').is_position_valid(Point2D(0, -1))
        False
        >>> MazeSolver('').is_position_valid(Point2D(0, 0))
        True
        >>> MazeSolver('').is_position_valid(Point2D(1, 1))
        True
        >>> MazeSolver('').is_position_valid(Point2D(2, 2))
        True
        >>> MazeSolver('').is_position_valid(Point2D(3, 3))
        True
        >>> MazeSolver('').is_position_valid(Point2D(3, 4))
        False
        >>> MazeSolver('').is_position_valid(Point2D(4, 3))
        False
        >>> MazeSolver('').is_position_valid(Point2D(4, 4))
        False
        """
        x, y = position
        return (
            0 <= x < 4
            and 0 <= y < 4
        )

    def get_path_door_states(self, path: str) -> Dict['Direction', bool]:
        """
        >>> MazeSolver('hijkl').get_path_door_states('')
        {Direction.Up: True, Direction.Down: True, Direction.Left: True,
            Direction.Right: False}
        >>> MazeSolver('hijklD').get_path_door_states('')
        {Direction.Up: True, Direction.Down: False, Direction.Left: True,
            Direction.Right: True}
        >>> MazeSolver('hijklDR').get_path_door_states('')
        {Direction.Up: False, Direction.Down: False, Direction.Left: False,
            Direction.Right: False}
        >>> MazeSolver('hijklDU').get_path_door_states('')
        {Direction.Up: False, Direction.Down: False, Direction.Left: False,
            Direction.Right: True}
        """
        path_hash = self.get_path_hash(path)
        return {
            direction: hash_char >= 'b'
            for direction, hash_char in zip(self.Direction, path_hash)
        }

    def get_path_hash(self, path: str) -> str:
        """
        >>> MazeSolver('hijkl').get_path_hash('')
        'ced9'
        >>> MazeSolver('hijklD').get_path_hash('')
        'f2bc'
        >>> MazeSolver('hijklDR').get_path_hash('')
        '5745'
        >>> MazeSolver('hijklDU').get_path_hash('')
        '528e'
        """
        return get_md5_hex_hash(f"{self.passcode}{path}")[:4]


Challenge.main()
challenge = Challenge()
