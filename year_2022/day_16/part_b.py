#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, Self
from year_2022.day_16 import part_a
from year_2022.day_16.part_a import Valve


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2416
        """
        return DoublePathFinder\
            .find_most_release_possible_from_valves_text(
                _input, minimum_release=2350,
                debugger=debugger,
            )

    def play(self):
        # E: DD
        # Y: JJ
        # Y: BB
        # E: HH
        # Y: CC
        # E: EE
        # {'DD': ('y', 24), 'JJ': ('e', 23), 'BB': ('y', 19),
        return DoublePathFinder\
            .find_most_release_possible_from_valves_text_interactive(
                self.input,
                minimum_release=1651,
            )


@dataclass
class DoublePathFinder(part_a.PathFinder["DoubleSearchState"]):
    """
    >>> DoublePathFinder\\
    ...     .find_most_release_possible_from_valves_text(part_a.LONG_INPUT)
    1707
    >>> DoublePathFinder\\
    ...     .find_most_release_possible_from_valves_text(
    ...         part_a.LONG_INPUT, minimum_release=1651)
    1707
    """
    # seen_states: Set["DoubleSearchState"] = field(default_factory=set)
    best_seen_total_release: Dict[str, int] = field(default_factory=dict)
    best_seen_time_left: Dict[str, int] = field(default_factory=dict)
    step_count: int = 0
    pruned_count: int = 0

    @classmethod
    def find_most_release_possible_from_valves_text_interactive(
        cls, valves_text: str, minimum_release: int = 0,
    ) -> int:
        return cls\
            .from_valve_set(
                part_a.ValveSet.from_valves_text(valves_text),
                minimum_release=minimum_release,
            )\
            .search_interactive()

    def search_interactive(self) -> int:
        while self.queue:
            if not self.search_step_interactive():
                break
        return self.biggest_release

    def search_step_interactive(
        self: Self["DoublePathFinder"],
    ) -> bool:
        print(f"Queue: {len(self.queue)}")
        if not self.queue:
            return False
        state = self.queue.pop(0)
        print(f"State: {state}")
        next_states = sorted(
            state.get_next_states(),
            key=lambda _state: repr(_state),
        )
        if not next_states:
            return False
        for index, next_state in enumerate(next_states):
            print(f"{index + 1}. {next_state}")
        index_strs = list(map(str, range(1, len(next_states) + 1)))
        chosen_index_str = None
        while chosen_index_str not in index_strs:
            chosen_index_str = input(f"Choose an input: ").strip().lower()
            if chosen_index_str == "q":
                return False
        next_state = next_states[int(chosen_index_str) - 1]
        self.queue.append(next_state)
        self.biggest_release = max(
            self.biggest_release,
            next_state.total_release,
        )
        if self.biggest_release == next_state.total_release:
            self.best_state = next_state
        return True

    def search_step(
        self: Self["DoublePathFinder"],
        debugger: Debugger = Debugger(enabled=False),
    ) -> Self["DoublePathFinder"]:
        if not self.queue:
            return self
        self.step_count += 1
        if self.step_count % 1000 == 0:
            self.queue = sorted(self.queue, key=lambda _state: _state.time_left)
        state = self.queue.pop(0)
        for next_state in state.get_next_states():
            next_state: DoubleSearchState
            if next_state.get_max_possible_total_release() \
                    <= self.biggest_release:
                self.pruned_count += 1
                continue
            cache_key = next_state.get_cache_key()
            if self.has_seen_better_cache_key(cache_key):
                self.pruned_count += 1
                continue
            # if next_state in self.seen_states:
            #     continue
            # self.seen_states.add(next_state)
            self.see_cache_key(cache_key)
            if next_state.total_release > self.biggest_release:
                self.biggest_release = next_state.total_release
                self.best_state = next_state
                self.queue.insert(0, next_state)
            else:
                self.queue.append(next_state)
        if debugger.should_report():
            if self.best_state:
                biggest_release_info = (
                    f"{len(self.best_state.openable_valve_names)} valves left, "
                    f"{self.best_state.time_left} time left, "
                    f"{self.best_state.cooldown}/{self.best_state.elephant_cooldown} cooldown, "
                    f"{self.best_state.get_max_possible_total_release()} max possible"
                )
            else:
                biggest_release_info = "initial"
            debugger.default_report_if(
                f"Biggest release: {self.biggest_release} ({biggest_release_info}), "
                f"next state: {self.queue[0] if self.queue else None}, "
                f"queue: {len(self.queue)}, seen: {len(self.best_seen_total_release)}, "
                f"pruned: {self.pruned_count}"
            )
        return self

    def has_seen_better_cache_key(self, cache_key: Tuple[str, int, int]) -> bool:
        cache_key, total_release, time_left = cache_key
        if cache_key not in self.best_seen_total_release:
            return False
        if total_release > self.best_seen_total_release[cache_key]:
            return False
        if time_left > self.best_seen_time_left[cache_key]:
            return False

        return True

    def see_cache_key(self, cache_key: Tuple[str, int, int]):
        cache_key, total_release, time_left = cache_key
        if cache_key not in self.best_seen_total_release or total_release > self.best_seen_total_release[cache_key]:
            self.best_seen_total_release[cache_key] = total_release
        if cache_key not in self.best_seen_time_left or time_left > self.best_seen_time_left[cache_key]:
            self.best_seen_time_left[cache_key] = time_left


@dataclass
class DoubleSearchState(part_a.SearchState):
    valve_set: part_a.ValveSet  # N
    valve_mapper: part_a.ValveMapper  # N
    position: str  # Y
    elephant_position: str  # Y
    cooldown: int  # Y
    elephant_cooldown: int  # Y
    opened_valves: Dict[str, int]  # N
    openable_valve_names: Set[str]  # Y
    time_left: int  # Y
    total_release: int  # Y

    @classmethod
    def initial(cls, valve_set: part_a.ValveSet) -> "DoubleSearchState":
        return cls(
            valve_set=valve_set,
            valve_mapper=part_a.ValveMapper.from_valve_set(valve_set),
            position="AA",
            elephant_position="AA",
            cooldown=0,
            elephant_cooldown=0,
            opened_valves={},
            openable_valve_names={
                valve.name
                for valve in valve_set.valves_by_name.values()
                if valve.flow
            },
            time_left=26,
            total_release=0,
        )

    def __repr__(self) -> str:
        openable_valve_names_with_distances = {
            valve_name: (
                self.valve_mapper[(self.valve, self.valve_set[valve_name])]
                if self.position != valve_name else
                0,
                self.valve_mapper[(
                    self.elephant_valve, self.valve_set[valve_name],
                )]
                if self.elephant_position != valve_name else
                0,
            )
            for valve_name in self.openable_valve_names
        }
        return (
            f"DoubleSearchState(position='{self.position}', "
            f"can_open={self.is_current_valve_openable}, "
            f"elephant_position='{self.elephant_position}', "
            f"can_elephant_open={self.is_current_elephant_valve_openable}, "
            f"cooldown={self.cooldown}, "
            f"elephant_cooldown={self.elephant_cooldown}, "
            f"opened_valves={self.opened_valves}, "
            f"openable_valves_with_distances={openable_valve_names_with_distances}, "
            f"time_left={self.time_left}, "
            f"total_release={self.total_release}, "
            f"min_naive_total_release"
            f"max_possible_total_release"
            f"={self.get_max_possible_total_release()})"
        )

    # def __hash__(self):
    #     return hash((
    #         *sorted([
    #             (self.position, self.cooldown),
    #             (self.elephant_position, self.elephant_cooldown),
    #         ]),
    #         self.time_left,
    #         self.total_release,
    #         tuple(sorted(self.openable_valve_names)),
    #     ))

    def __eq__(self, other: "DoubleSearchState") -> bool:
        return self.get_cache_key() == other.get_cache_key()

    def get_cache_key(self) -> Tuple[str, int, int]:
        return ",".join([
            ":".join(sorted([
                f"{self.position}|{self.cooldown}",
                f"{self.elephant_position}|{self.elephant_cooldown}",
            ])),
            str(self.is_current_valve_openable),
            "|".join(sorted(self.opened_valves)),
        ]), self.total_release, self.time_left

    def get_max_possible_total_release(self) -> int:
        return self.total_release + sum(
            (self.time_left - index // 2 * 2) * flow
            for index, flow in enumerate(sorted((
                self.valve_set[valve_name].flow
                for valve_name in self.openable_valve_names
            ), reverse=True), start=min(
                self.valve_mapper[(self.valve_set[position], self.valve_set[valve_name])]
                if valve_name != position else
                0
                for valve_name in self.openable_valve_names
                for position in (self.position, self.elephant_position)
            ))
        )

    @property
    def valve(self) -> part_a.Valve:
        return self.valve_set[self.position]

    @property
    def is_current_valve_openable(self) -> bool:
        return self.is_valve_name_openable(self.position) and not self.cooldown

    @property
    def elephant_valve(self) -> part_a.Valve:
        return self.valve_set[self.elephant_position]

    @property
    def is_current_elephant_valve_openable(self) -> bool:
        return (
            self.is_valve_name_openable(self.elephant_position)
            and not self.elephant_cooldown
        )

    def is_valve_name_openable(self, valve_name: str) -> bool:
        return valve_name in self.openable_valve_names

    def get_travelable_valve_names(self) -> List[str]:
        return sorted(
            self.openable_valve_names
            - {self.position, self.elephant_position}
        )

    def get_next_states(self) -> Iterable["DoubleSearchState"]:
        if self.time_left <= 1:
            return
        for next_state in self.get_next_states_for('y'):
            for next_elephant_state in next_state.get_next_states_for('e'):
                time_passed = max(1, min(next_elephant_state.cooldown, next_elephant_state.elephant_cooldown))
                yield next_elephant_state.make_next(time_passed=time_passed)

    def get_next_states_for(self, target: str) -> Iterable["DoubleSearchState"]:
        if target == "y" and self.cooldown:
            yield self
            return
        elif target == "e" and self.elephant_cooldown:
            yield self
            return
        position = self.position if target == "y" else self.elephant_position
        valve = self.valve_set[position]
        next_positions_and_distances = [
            (next_valve_name, distance)
            for next_valve_name in self.get_travelable_valve_names()
            for distance in [self.valve_mapper[(
                valve, self.valve_set[next_valve_name],
            )]]
            if distance + 1 < self.time_left
        ]
        if not next_positions_and_distances:
            yield self
            return

        for next_valve_name, distance in next_positions_and_distances:
            yield self.make_next(
                position=next_valve_name if target == "y" else None,
                cooldown=distance + 1 if target == "y" else None,
                elephant_position=next_valve_name if target == "e" else None,
                elephant_cooldown=distance + 1 if target == "e" else None,
                new_opened_valves={
                    position: (target, self.time_left - 1 - distance)
                },
                openable_valve_names=(
                    self.openable_valve_names - {next_valve_name}
                ),
                release_added=(
                    (self.time_left - 1 - distance) * self.valve_set[next_valve_name].flow
                ),
                time_passed=0,
            )

    def get_next_positions_and_distances(self, valve: Valve) -> List[Tuple[str, int]]:
        return [
            (next_valve_name, distance)
            for next_valve_name in self.get_travelable_valve_names()
            for distance in [self.valve_mapper[(
                valve, self.valve_set[next_valve_name],
            )]]
            if distance + 1 < self.time_left
        ]

    def make_next(
        self,
        position: Optional[str] = None,
        elephant_position: Optional[str] = None,
        cooldown: Optional[int] = None,
        elephant_cooldown: Optional[int] = None,
        new_opened_valves: Optional[Dict[str, Tuple[str, int]]] = None,
        openable_valve_names: Optional[Set[str]] = None,
        time_passed: int = 1,
        release_added: int = 0,
    ) -> "DoubleSearchState":
        cls: Cls["DoubleSearchState"] = type(self)
        # noinspection PyArgumentList
        return cls(
            valve_set=self.valve_set,
            valve_mapper=self.valve_mapper,
            position=position if position is not None else self.position,
            elephant_position=(
                elephant_position
                if elephant_position is not None else
                self.elephant_position
            ),
            cooldown=(
                cooldown
                if cooldown is not None else
                max(0, self.cooldown - time_passed)
            ),
            elephant_cooldown=(
                elephant_cooldown
                if elephant_cooldown is not None else
                max(0, self.elephant_cooldown - time_passed)
            ),
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


Challenge.main()
challenge = Challenge()
