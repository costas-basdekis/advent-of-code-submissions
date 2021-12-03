#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Generic, List, Union, Type, Iterable, Dict

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        398
        """
        return Cavern.from_cavern_text(_input)\
            .find_lowest_risk_path_risk(debugger=debugger)


CavernMeasurerT = TV["CavernMeasurer"]


@dataclass
class Cavern(Generic[CavernMeasurerT]):
    risks: List[List[int]]

    @classmethod
    def get_measurer_class(cls) -> Type[CavernMeasurerT]:
        return get_type_argument_class(cls, CavernMeasurerT)

    @classmethod
    def from_cavern_text(cls, cavern_text: str) -> "Cavern":
        """
        >>> print(Cavern.from_cavern_text('''
        ...     1163751742
        ...     1381373672
        ...     2136511328
        ...     3694931569
        ...     7463417111
        ...     1319128137
        ...     1359912421
        ...     3125421639
        ...     1293138521
        ...     2311944581
        ... '''))
        1163751742
        1381373672
        2136511328
        3694931569
        7463417111
        1319128137
        1359912421
        3125421639
        1293138521
        2311944581
        """
        return cls(
            risks=[
                list(map(int, line))
                for line
                in filter(None, map(str.strip, cavern_text.splitlines()))
            ],
        )

    def __str__(self) -> str:
        return "\n".join(
            "".join(map(str, line))
            for line in self.risks
        )

    @property
    def target(self) -> Point2D:
        return Point2D(len(self.risks[-1]) - 1, len(self.risks) - 1)

    def __getitem__(self, item: Union[tuple, Point2D]) -> int:
        item = Point2D(item)
        if item not in self:
            raise KeyError(item)
        return self.risks[item.y][item.x]

    def __contains__(self, item: Union[tuple, Point2D]) -> bool:
        item = Point2D(item)
        if not (0 <= item.y < len(self.risks)):
            return False
        if not (0 <= item.x < len(self.risks[item.y])):
            return False

        return True

    def find_lowest_risk_path_risk(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> Cavern.from_cavern_text('''
        ...     1163751742
        ...     1381373672
        ...     2136511328
        ...     3694931569
        ...     7463417111
        ...     1319128137
        ...     1359912421
        ...     3125421639
        ...     1293138521
        ...     2311944581
        ... ''').find_lowest_risk_path_risk()
        40
        """
        return self.get_measurer_class()\
            .find_min_target_distance_for_cavern(self, debugger=debugger)


CavernMeasurerStateT = TV["CavernMeasurerState"]


@dataclass
class CavernMeasurer(Generic[CavernMeasurerStateT]):
    cavern: Cavern
    target: Point2D
    stack: List[CavernMeasurerStateT]
    distances: Dict[Point2D, int]

    @classmethod
    def get_state_class(cls) -> Type[CavernMeasurerStateT]:
        return get_type_argument_class(cls, CavernMeasurerStateT)

    @classmethod
    def find_min_target_distance_for_cavern(
        cls, cavern: Cavern, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        measurer = cls.from_cavern(cavern)
        return measurer.find_min_target_distance(debugger=debugger)

    @classmethod
    def from_cavern(cls, cavern: Cavern) -> "CavernMeasurer":
        state_class = cls.get_state_class()
        initial = state_class.make_initial()
        return cls(
            cavern=cavern,
            target=cavern.target,
            stack=[initial],
            distances={initial.position: 0},
        )

    def find_min_target_distance(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        self.measure_distances(debugger=debugger)
        if self.target not in self.distances:
            raise Exception(
                f"Could not find target distance, but found distances for "
                f"{len(self.distances)}, max point was {max(self.distances)}"
            )
        return self.distances[self.target]

    def measure_distances(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> None:
        while debugger.step_if(self.stack):
            debugger.default_report_if(
                f"Seen {len(self.distances)}, {len(self.stack)} in stack, "
                f"target risk is {self.distances.get(self.target)}"
            )
            state = self.stack.pop(0)

            for next_state in state.get_next_states(self):
                self.visit_state(next_state)

    def visit_state(self, state: CavernMeasurerStateT) -> bool:
        if not self.visit_for_distance(state):
            return False

        self.stack.append(state)

        return True

    def visit_for_distance(self, state: CavernMeasurerStateT) -> bool:
        if state.position in self.distances \
                and state.distance >= self.distances[state.position]:
            return False

        self.distances[state.position] = state.distance

        return True


@dataclass
class CavernMeasurerState:
    position: Point2D
    distance: int

    @classmethod
    def make_initial(cls) -> "CavernMeasurerState":
        return cls(
            position=Point2D.get_zero_point(),
            distance=0,
        )

    def get_next_states(
        self, measurer: CavernMeasurer,
    ) -> Iterable["CavernMeasurerState"]:
        cls = type(self)
        for neighbour in self.position.get_manhattan_neighbours():
            if neighbour not in measurer.cavern:
                continue
            # noinspection PyArgumentList
            yield cls(
                position=neighbour,
                distance=self.distance + measurer.cavern[neighbour],
            )


Challenge.main()
challenge = Challenge()
