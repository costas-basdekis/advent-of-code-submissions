#!/usr/bin/env python3
from dataclasses import dataclass
from itertools import chain
from typing import Generic, List, Union, Type, Iterable, Dict

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class, \
    min_and_max_tuples


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
    risks: Dict[Point2D, int]

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
        lines = filter(None, map(str.strip, cavern_text.splitlines()))
        return cls(
            risks={
                Point2D(x, y): int(risk_str)
                for y, line in enumerate(lines)
                for x, risk_str in enumerate(line)
            },
        )

    def __str__(self) -> str:
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.risks)
        return "\n".join(
            "".join(
                str(self.risks.get(Point2D(x, y), "."))
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        )

    @property
    def target(self) -> Point2D:
        return max(self.risks)

    def __getitem__(self, item: Union[tuple, Point2D]) -> int:
        return self.risks[Point2D(item)]

    def __contains__(self, item: Union[tuple, Point2D]) -> bool:
        return Point2D(item) in self.risks

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

    def __str__(self) -> str:
        max_distance = max(self.distances.values()) or 1
        state_positions = {state.position for state in self.stack}
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(chain(
            self.distances,
            state_positions,
        ))
        return "\n".join(
            "".join(
                "*"
                if point in state_positions else
                str(int(9 * self.distances[point] / max_distance))
                if point in self.distances else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(min_y, max_y + 1)
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
            should_report = debugger.should_report()
            debugger.default_report_if(
                f"Seen {len(self.distances)}, {len(self.stack)} in stack, "
                f"target risk is {self.distances.get(self.target)}"
            )
            if should_report:
                debugger.report(str(self))
            state = self.stack.pop(0)
            if state.distance > self.distances[state.position]:
                continue

            for next_state in state.get_next_states(self):
                self.visit_state(next_state)
        if debugger.enabled:
            debugger.report(str(self))

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
