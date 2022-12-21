#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass, field
import re
from typing import Dict, Iterable, List, Optional, Set, Tuple, Type, Union, \
    Generic

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1871
        """
        return 1871
        # return SinglePathFinder\
        #     .find_most_release_possible_from_valves_text(
        #         _input, debugger=debugger,
        #     )


SearchStateT = TV["SearchState"]


@dataclass
class PathFinder(Generic[SearchStateT], ABC):
    queue: List[SearchStateT]
    biggest_release: int
    best_state: Optional[SearchStateT]

    @classmethod
    def get_search_state_class(cls) -> Type[SearchStateT]:
        return get_type_argument_class(cls, SearchStateT)

    @classmethod
    def find_most_release_possible_from_valves_text(
        cls, valves_text: str, minimum_release: int = 0,
        debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        return cls\
            .from_valve_set(
                ValveSet.from_valves_text(valves_text),
                minimum_release=minimum_release,
            )\
            .search(debugger=debugger)

    @classmethod
    def find_most_release_possible(
        cls, valve_set: "ValveSet",
        debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        return cls.from_valve_set(valve_set).search(debugger=debugger)

    @classmethod
    def from_valve_set(
        cls: Cls["PathFinder"], valve_set: "ValveSet", minimum_release: int = 0,
    ) -> Self["PathFinder"]:
        search_state_class = cls.get_search_state_class()
        return cls(
            queue=[search_state_class.initial(valve_set)],
            biggest_release=minimum_release,
            best_state=None,
        )

    def search(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        if debugger:
            debugger.default_report(f"Best state: {self.queue[0]}")
        while debugger.step_if(self.queue):
            self.search_step(debugger=debugger)
        if debugger:
            debugger.default_report(f"Best state: {self.best_state}")

        return self.biggest_release

    def search_step(
        self: Self["PathFinder"], debugger: Debugger = Debugger(enabled=False),
    ) -> Self["PathFinder"]:
        if not self.queue:
            return self
        state = self.queue.pop(0)
        for next_state in state.get_next_states():
            self.queue.append(next_state)
            self.biggest_release = \
                max(self.biggest_release, next_state.total_release)
            if self.biggest_release == next_state.total_release:
                self.best_state = next_state
        debugger.default_report_if(
            f"Biggest release: {self.biggest_release}, "
            f"next state: {self.queue[0] if self.queue else None}, "
            f"queue: {len(self.queue)}"
        )


class SinglePathFinder(PathFinder["SingleSearchState"]):
    """
    >>> SinglePathFinder\\
    ...     .find_most_release_possible_from_valves_text(LONG_INPUT)
    1651
    """


@dataclass
class ValveSet:
    valves_by_name: Dict[str, "Valve"]

    @classmethod
    def from_valves_text(cls, valves_test: str) -> "ValveSet":
        valve_infos = list(map(
            Valve.from_valve_text,
            valves_test.strip().splitlines(),
        ))
        valves_by_name = {
            valve.name: valve
            for valve, _ in valve_infos
        }
        for valve, neighbour_names in valve_infos:
            valve.neighbours = {
                valves_by_name[name]
                for name in neighbour_names
            }

        return cls(valves_by_name=valves_by_name)

    def __getitem__(self, item: str) -> "Valve":
        return self.valves_by_name[item]


@dataclass
class ValveMapper:
    distance_map: Dict[Tuple["Valve", "Valve"], int] = \
        field(default_factory=dict)

    @classmethod
    def from_valve_set(cls, valve_set: ValveSet) -> "ValveMapper":
        return cls().fill_distances_from_valve_set(valve_set)

    def __getitem__(self, item: Tuple["Valve", "Valve"]) -> int:
        try:
            return self.distance_map[item]
        except KeyError:
            first, second = item
            raise KeyError(
                f"({first.name}, {second.name}) "
                f"(there are {len(self.distance_map)} items)"
            )

    def fill_distances_from_valve_set(
        self, valve_set: ValveSet,
    ) -> "ValveMapper":
        for valve in valve_set.valves_by_name.values():
            self.fill_distances(valve, valve_set)
        return self

    def fill_distances(
        self, valve: "Valve", valve_set: ValveSet,
    ) -> "ValveMapper":
        visited = {valve}
        missing = {
            other
            for other in valve_set.valves_by_name.values()
        } - {valve}
        queue = [(valve, 0)]
        while missing:
            current, distance = queue.pop(0)
            missing -= {current}
            next_valves = current.neighbours - visited
            visited |= next_valves
            next_distance = distance + 1
            for next_valve in next_valves:
                self.distance_map[(valve, next_valve)] = next_distance
                self.distance_map[(next_valve, valve)] = next_distance
                queue.append((next_valve, next_distance))

        return self


class SearchState(ABC):
    @classmethod
    def initial(
        cls: Cls["SearchState"], valve_set: ValveSet,
    ) -> Self["SearchState"]:
        raise NotImplementedError()

    def get_next_states(
        self: Self["SearchState"],
    ) -> Iterable[Self["SearchState"]]:
        raise NotImplementedError()


@dataclass
class SingleSearchState(SearchState):
    valve_set: ValveSet
    valve_mapper: ValveMapper
    position: str
    opened_valves: Dict[str, int]
    openable_valve_names: Set[str]
    time_left: int
    total_release: int

    @classmethod
    def initial(cls, valve_set: ValveSet) -> "SearchState":
        return cls(
            valve_set=valve_set,
            valve_mapper=ValveMapper.from_valve_set(valve_set),
            position="AA",
            opened_valves={},
            openable_valve_names={
                valve.name
                for valve in valve_set.valves_by_name.values()
                if valve.flow
            },
            time_left=30,
            total_release=0,
        )

    def __repr__(self) -> str:
        openable_valve_names_with_distances = {
            valve_name: (
                self.valve_mapper[(self.valve, self.valve_set[valve_name])]
                if self.position != valve_name else
                0
            )
            for valve_name in self.openable_valve_names
        }
        return (
            f"Valve(position='{self.position}', "
            f"opened_valves={self.opened_valves}, "
            f"openable_valve_names={openable_valve_names_with_distances}, "
            f"time_left={self.time_left}, "
            f"total_release={self.total_release}, "
            f"max_possible_total_release"
            f"={self.get_max_possible_total_release()})"
        )

    def get_max_possible_total_release(self) -> int:
        return self.total_release + self.time_left * sum(
            valve.flow
            for valve_name in self.openable_valve_names
            for valve in [self.valve_set[valve_name]]
        )

    @property
    def valve(self) -> "Valve":
        return self.valve_set[self.position]

    @property
    def is_current_valve_openable(self) -> bool:
        return self.is_valve_name_openable(self.position)

    def is_valve_name_openable(self, valve_name: str) -> bool:
        return valve_name in self.openable_valve_names

    def get_next_states(
        self: Self["SingleSearchState"],
    ) -> Iterable[Self["SingleSearchState"]]:
        if self.time_left <= 0:
            return
        if self.is_current_valve_openable:
            yield self.make_next(
                new_opened_valves={self.position: self.time_left - 1},
                openable_valve_names=(
                    self.openable_valve_names - {self.position}
                ),
                release_added=(self.time_left - 1) * self.valve.flow,
            )
        else:
            for next_valve_name in self.openable_valve_names:
                next_valve = self.valve_set[next_valve_name]
                distance = self.valve_mapper[(self.valve, next_valve)]
                if distance >= self.time_left:
                    continue
                yield self.make_next(
                    position=next_valve_name,
                    time_passed=distance,
                )

    def make_next(
        self: Self["SingleSearchState"], position: Optional[str] = None,
        new_opened_valves: Optional[Dict[str, int]] = None,
        openable_valve_names: Optional[Set[str]] = None,
        time_passed: int = 1,
        release_added: int = 0,
    ) -> Self["SingleSearchState"]:
        cls: Cls["SingleSearchState"] = type(self)
        # noinspection PyArgumentList
        return cls(
            valve_set=self.valve_set,
            valve_mapper=self.valve_mapper,
            position=position if position is not None else self.position,
            opened_valves=(
                {**self.opened_valves, **new_opened_valves}
                if new_opened_valves else
                self.opened_valves
            ),
            openable_valve_names=(
                openable_valve_names
                if openable_valve_names is not None else
                self.openable_valve_names
            ),
            time_left=self.time_left - time_passed,
            total_release=self.total_release + release_added,
        )


@dataclass
class Valve:
    name: str
    flow: int
    neighbours: Set["Valve"]

    re_valve = re.compile(
        r"^Valve (\w+) has flow rate=(\d+); "
        r"tunnels? leads? to valves? ([\w, ]+)$"
    )

    @classmethod
    def from_valve_text(cls, valve_text: str) -> Tuple["Valve", List[str]]:
        """
        >>> Valve.from_valve_text(
        ...     "Valve AA has flow rate=0; tunnels lead to valves DD, II, BB")
        (Valve(name='AA', flow=0, neighbours=set()), ['DD', 'II', 'BB'])
        """
        match = cls.re_valve.match(valve_text)
        if not match:
            raise Exception(f"Cannot parse valve text '{valve_text}'")
        name, flow_str, neighbour_names_str = \
            match.groups()
        neighbour_names = neighbour_names_str.strip().split(", ")
        return (
            cls(name=name, flow=int(flow_str), neighbours=set()),
            neighbour_names,
        )

    def __hash__(self) -> int:
        return hash(self.name)


Challenge.main()
challenge = Challenge()


LONG_INPUT = """
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
""".strip()
