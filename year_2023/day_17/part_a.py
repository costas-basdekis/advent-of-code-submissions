#!/usr/bin/env python3
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

import utils
from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Direction, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1128
        """
        return Pool.from_map(_input).find_minimum_heat_loss(debugger=debugger)


@dataclass
class Pool:
    heat_loss_map: Dict[Point2D, int]
    width: int
    height: int
    valid_lengths: List[int]

    @classmethod
    def from_map(cls: Cls["Pool"], text: str, valid_lengths: Optional[List[int]] = None) -> Self["Pool"]:
        """
        >>> print(Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... '''))
        2413432311323
        3215453535623
        3255245654254
        3446585845452
        4546657867536
        1438598798454
        4457876987766
        3637877979653
        4654967986887
        4564679986453
        1224686865563
        2546548887735
        4322674655533
        """
        if valid_lengths is None:
            valid_lengths = [1, 2, 3]
        lines = text.strip().splitlines()
        return cls(heat_loss_map={
            Point2D(x, y): int(char)
            for y, line in enumerate(lines)
            for x, char in enumerate(line.strip())
        }, width=len(lines[0]) if lines else 0, height=len(lines), valid_lengths=valid_lengths)

    def __str__(self, path: Optional[List["StateKey"]] = None, only_path_numbers: bool = False,) -> str:
        """
        >>> _pool = Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''')
        >>> print(_pool.show_with_raw_path([
        ...     (Point2D(0, 0), Direction.Right),
        ...     (Point2D(2, 0), Direction.Down),
        ...     (Point2D(2, 1), Direction.Right),
        ...     (Point2D(5, 1), Direction.Up),
        ...     (Point2D(5, 0), Direction.Right),
        ...     (Point2D(8, 0), Direction.Down),
        ...     (Point2D(8, 2), Direction.Right),
        ...     (Point2D(10, 2), Direction.Down),
        ...     (Point2D(10, 4), Direction.Right),
        ...     (Point2D(11, 4), Direction.Down),
        ...     (Point2D(11, 7), Direction.Right),
        ...     (Point2D(12, 7), Direction.Down),
        ...     (Point2D(12, 10), Direction.Left),
        ...     (Point2D(11, 10), Direction.Down),
        ...     (Point2D(11, 12), Direction.Right),
        ...     (Point2D(12, 12), Direction.Down),
        ... ]))
        2>>34^>>>1323
        32v>>>35v5623
        32552456v>>54
        3446585845v52
        4546657867v>6
        14385987984v4
        44578769877v6
        36378779796v>
        465496798688v
        456467998645v
        12246868655<v
        25465488877v5
        43226746555v>
        """
        directions_by_position: Dict[Point2D, Set[Direction]] = {}
        if path:
            for point, direction in path:
                directions_by_position.setdefault(point, set()).add(direction)
        return "\n".join(
            "".join(
                (
                    str(self.heat_loss_map[point])
                    if not directions else
                    "*"
                    if len(directions) > 1 else
                    str(list(directions)[0])
                ) if not (path and only_path_numbers) else (
                    str(self.heat_loss_map[point])
                    if directions else
                    "."
                )
                for x in range(self.width)
                for point in [Point2D(x, y)]
                for directions in [directions_by_position.get(point)]
            )
            for y in range(self.height)
        )

    def show_with_path(self, path: List["StateKey"], only_path_numbers: bool = False) -> str:
        return self.__str__(path=path, only_path_numbers=only_path_numbers)

    def show_with_raw_path(self, raw_path: List["StateKey"], only_path_numbers: bool = False) -> str:
        return self.__str__(path=SearchState.from_raw_path(self, raw_path)[-1].get_path(), only_path_numbers=only_path_numbers)

    def find_minimum_heat_loss(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''').find_minimum_heat_loss()
        102
        """
        _, min_heat_loss = self.find_minimum_heat_loss_path(debugger=debugger)
        return min_heat_loss

    def find_minimum_heat_loss_path(self, debugger: Debugger = Debugger(enabled=False)) -> Tuple[List["StateKey"], int]:
        """
        >>> _pool = Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''')
        >>> _path = _pool.find_minimum_heat_loss_path()[0]
        >>> print(_pool.show_with_path(_path))
        2>13432311323
        3v>>>53535623
        3255v>>654254
        344658v>>5452
        45466578v7536
        14385987v>454
        445787698v766
        363787797v653
        465496798v>87
        4564679986v53
        1224686865v>3
        25465488877v5
        43226746555v>
        """
        pool_search = PoolSearch.from_pool(self).search(debugger=debugger)
        best_state = pool_search.best_state
        if not best_state:
            raise Exception(f"Could not find a path")
        return best_state.get_path(), best_state.get_heat_loss(pool_search.best_heat_loss)

    def is_point_in_bounds(self, point: Point2D) -> bool:
        return (
            0 <= point.x < self.width
            and 0 <= point.y < self.height
        )

    def get_raw_path_heat_loss(self, raw_path: List["StateKey"]) -> int:
        """
        >>> _pool = Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''')
        >>> _raw_path = [
        ...     (Point2D(0, 0), Direction.Right),
        ...     (Point2D(2, 0), Direction.Down),
        ...     (Point2D(2, 1), Direction.Right),
        ...     (Point2D(5, 1), Direction.Up),
        ...     (Point2D(5, 0), Direction.Right),
        ...     (Point2D(8, 0), Direction.Down),
        ...     (Point2D(8, 2), Direction.Right),
        ...     (Point2D(10, 2), Direction.Down),
        ...     (Point2D(10, 4), Direction.Right),
        ...     (Point2D(11, 4), Direction.Down),
        ...     (Point2D(11, 7), Direction.Right),
        ...     (Point2D(12, 7), Direction.Down),
        ...     (Point2D(12, 10), Direction.Left),
        ...     (Point2D(11, 10), Direction.Down),
        ...     (Point2D(11, 12), Direction.Right),
        ...     (Point2D(12, 12), Direction.Down),
        ... ]
        >>> print(_pool.show_with_raw_path(_raw_path, only_path_numbers=True))
        .41..3231....
        ..1545..3....
        ........542..
        ..........4..
        ..........53.
        ...........5.
        ...........6.
        ...........53
        ............7
        ............3
        ...........63
        ...........3.
        ...........33
        >>> _pool.get_raw_path_heat_loss(_raw_path)
        102
        """
        states = SearchState.from_raw_path(self, raw_path)
        best_heat_loss: Dict["StateKey", int] = {
            (states[0].position, states[0].direction): 0
        }
        for state in states[1:]:
            best_heat_loss[(state.position, state.direction)] = state.get_heat_loss(best_heat_loss)
        return states[-1].get_heat_loss(best_heat_loss)


StateKey = Tuple[Point2D, Direction]


@dataclass
class PoolSearch:
    pool: Pool
    start: Point2D
    target: Point2D
    best_heat_loss: Dict[StateKey, int]
    max_heat_loss: int
    best_state: Optional["SearchState"]

    @classmethod
    def from_pool(cls, pool: Pool, start: Point2D = Point2D(0, 0), target: Optional[Point2D] = None) -> "PoolSearch":
        if not pool.is_point_in_bounds(start):
            raise Exception(f"Start {start} is out of bounds")
        if target is None:
            target = Point2D(pool.width - 1, pool.height - 1)
        elif not pool.is_point_in_bounds(target):
            raise Exception(f"Target {target} is out of bounds")
        return cls(
            pool=pool,
            start=start,
            target=target,
            best_heat_loss={},
            max_heat_loss=sum(pool.heat_loss_map.values()) + 1,
            best_state=None,
        )

    def search(self, debugger: Debugger = Debugger(enabled=False)) -> "PoolSearch":
        """
        >>> _pool = Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''')
        >>> print(_pool.show_with_path(PoolSearch.from_pool(_pool).search().best_state.get_point_path()))
        2>13432311323
        3v>>>53535623
        3255v>>654254
        344658v>>5452
        45466578v7536
        14385987v>454
        445787698v766
        363787797v653
        465496798v>87
        4564679986v53
        1224686865v>3
        25465488877v5
        43226746555v>
        """
        best_heat_loss = self.best_heat_loss
        target = self.target
        max_heat_loss = self.max_heat_loss
        best_state = self.best_state

        stack: List[SearchState] = SearchState.initial_for_pool_and_point(self.pool, self.start)
        best_heat_loss.update({
            state.key: 0
            for state in stack
        })
        while debugger.step_if(stack):
            state = stack.pop(0)
            next_states = state.get_next_states()
            for next_state in next_states:
                heat_loss = next_state.get_heat_loss(best_heat_loss)
                if heat_loss >= max_heat_loss:
                    continue
                if heat_loss >= best_heat_loss.get(next_state.key, heat_loss + 1):
                    continue
                best_heat_loss[next_state.key] = heat_loss
                if next_state.position == target:
                    if heat_loss < max_heat_loss:
                        max_heat_loss = heat_loss
                        best_state = next_state
                    continue
                stack.append(next_state)
            if debugger.should_report():
                debugger.default_report_if(
                    f"{len(stack)} items left, "
                    f"{len(best_heat_loss)} visited, "
                    f"{max_heat_loss if best_state else 'No'} best heat loss"
                )
        self.max_heat_loss = max_heat_loss
        self.best_state = best_state
        return self


@dataclass
class SearchState:
    pool: Pool
    parent: Optional["SearchState"]
    position: Point2D
    direction: Direction

    @classmethod
    def initial_for_pool_and_point(cls, pool: Pool, start: Point2D) -> List["SearchState"]:
        return [
            cls(
                pool=pool,
                parent=None,
                position=start,
                direction=direction,
            )
            for direction in Direction
            if pool.is_point_in_bounds(start.offset(direction.offset))
        ]

    @classmethod
    def from_raw_path(cls, pool: Pool, raw_path: List[StateKey]) -> List["SearchState"]:
        state = SearchState(pool=pool, parent=None, position=raw_path[0][0], direction=raw_path[0][1])
        states: List[SearchState] = [state]
        for position, direction in raw_path[1:]:
            state = SearchState(pool=pool, parent=state, position=position, direction=direction)
            states.append(state)
        return states

    @cached_property
    def key(self) -> StateKey:
        return self.position, self.direction

    def get_heat_loss(self, best_heat_loss: Dict[StateKey, int]) -> int:
        if not self.parent:
            return 0
        heat_loss = best_heat_loss[(self.parent.position, self.parent.direction)]
        heat_loss += self.get_heat_loss_between(self.parent.position, self.position)
        return heat_loss

    def get_heat_loss_between(self, start: Point2D, end: Point2D) -> int:
        """
        >>> _pool = Pool.from_map('''
        ...     2413432311323
        ...     3215453535623
        ...     3255245654254
        ...     3446585845452
        ...     4546657867536
        ...     1438598798454
        ...     4457876987766
        ...     3637877979653
        ...     4654967986887
        ...     4564679986453
        ...     1224686865563
        ...     2546548887735
        ...     4322674655533
        ... ''')
        >>> _raw_path = [
        ...     (Point2D(0, 0), Direction.Right),
        ...     (Point2D(2, 0), Direction.Down),
        ...     (Point2D(2, 1), Direction.Right),
        ...     (Point2D(5, 1), Direction.Up),
        ...     (Point2D(5, 0), Direction.Right),
        ...     (Point2D(8, 0), Direction.Down),
        ...     (Point2D(8, 2), Direction.Right),
        ...     (Point2D(10, 2), Direction.Down),
        ...     (Point2D(10, 4), Direction.Right),
        ...     (Point2D(11, 4), Direction.Down),
        ...     (Point2D(11, 7), Direction.Right),
        ...     (Point2D(12, 7), Direction.Down),
        ...     (Point2D(12, 10), Direction.Left),
        ...     (Point2D(11, 10), Direction.Down),
        ...     (Point2D(11, 12), Direction.Right),
        ...     (Point2D(12, 12), Direction.Down),
        ... ]
        >>> _states = SearchState.from_raw_path(_pool, _raw_path)
        >>> [_state.get_heat_loss_between(_state.parent.position, _state.position) for _state in _states[1:]]
        [5, 1, 14, 3, 6, 8, 6, 9, 3, 16, 3, 13, 6, 6, 3]
        """
        points = self.get_points_between(start, end)
        return sum(
            self.pool.heat_loss_map[point]
            for point in points
        )

    @classmethod
    def get_points_between(cls, start: Point2D, end: Point2D) -> Iterable[Point2D]:
        """
        >>> list(SearchState.get_points_between(Point2D(5, 0), Point2D(5, 1)))
        [Point2D(x=5, y=1)]
        >>> list(SearchState.get_points_between(Point2D(5, 1), Point2D(5, 0)))
        [Point2D(x=5, y=0)]
        >>> list(SearchState.get_points_between(Point2D(0, 5), Point2D(1, 5)))
        [Point2D(x=1, y=5)]
        >>> list(SearchState.get_points_between(Point2D(1, 5), Point2D(0, 5)))
        [Point2D(x=0, y=5)]
        """
        x_offset = utils.sign(end.x - start.x)
        y_offset = utils.sign(end.y - start.y)
        if x_offset:
            points = (
                Point2D(x, start.y)
                for x in range(start.x + x_offset, end.x + x_offset, x_offset)
            )
        else:
            points = (
                Point2D(start.x, y)
                for y in range(start.y + y_offset, end.y + y_offset, y_offset)
            )
        return points

    def _change(self, position: Point2D, direction: "Direction",) -> "SearchState":
        cls = type(self)
        return cls(
            pool=self.pool,
            parent=self,
            position=position,
            direction=direction,
        )

    def get_next_states(self) -> List["SearchState"]:
        next_states = []
        next_states.extend([
            self._change(position=new_position, direction=new_direction)
            for distance in self.pool.valid_lengths
            for new_position in [self.position.offset(self.direction.offset.resize(distance))]
            if self.pool.is_point_in_bounds(new_position)
            for new_direction in [self.direction.clockwise, self.direction.counter_clockwise]
        ])
        return next_states

    def get_path(self) -> List[StateKey]:
        raw_path = []
        state = self
        while state:
            raw_path.insert(0, (state.position, state.direction))
            state = state.parent
        path = []
        for (position_from, direction_from), (position_to, direction_to) in zip(raw_path, raw_path[1:]):
            if position_from.x == position_to.x:
                y_offset = utils.sign(position_to.y - position_from.y)
                for y in range(position_from.y + y_offset, position_to.y + y_offset, y_offset):
                    path.append((Point2D(position_from.x, y), direction_from))
            else:
                x_offset = utils.sign(position_to.x - position_from.x)
                for x in range(position_from.x + x_offset, position_to.x + x_offset, x_offset):
                    path.append((Point2D(x, position_from.y), direction_from))
        return path


Challenge.main()
challenge = Challenge()
