#!/usr/bin/env python3
import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, Self
from year_2022.day_16 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> solution = Challenge().default_solve()
        >>> 1651 > solution > 2350
        True
        >>> solution
        42
        """
        return DoublePathFinder\
            .find_most_release_possible_from_valves_text(
                _input, minimum_release=1651,
                debugger=debugger,
            )
        # return DoublePathFinder\
        #     .find_most_release_possible_from_valves_text(
        #         _input, minimum_release=1871 * 0 + 2350, debugger=debugger
        #     )

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
                part_a.LONG_INPUT,
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
    seen_states: Set["DoubleSearchState"] = field(default_factory=set)

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
        state = self.queue.pop(0)
        for next_state in state.get_next_states():
            next_state: DoubleSearchState
            if next_state in self.seen_states:
                continue
            if next_state.get_max_possible_total_release() \
                    <= self.biggest_release:
                continue
            self.seen_states.add(next_state)
            self.queue.append(next_state)
            self.biggest_release = max(
                self.biggest_release,
                next_state.total_release,
                next_state.get_min_naive_total_release() - 1,
            )
            if self.biggest_release == next_state.total_release:
                self.best_state = next_state
        if debugger.should_report():
            openable_valve_count = (
                len(self.best_state.openable_valve_names)
                if self.best_state else
                'N/A'
            )
            debugger.default_report_if(
                f"Biggest release: {self.biggest_release} "
                f"({openable_valve_count} valves left), "
                f"next state: {self.queue[0] if self.queue else None}, "
                f"queue: {len(self.queue)}, seen: {len(self.seen_states)}"
            )


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
            f"cooldown='{self.cooldown}', "
            f"elephant_cooldown='{self.elephant_cooldown}', "
            f"opened_valves={self.opened_valves}, "
            f"openable_valve_names={openable_valve_names_with_distances}, "
            f"time_left={self.time_left}, "
            f"total_release={self.total_release}, "
            f"min_naive_total_release"
            f"={self.get_min_naive_total_release()}, "
            f"max_possible_total_release"
            f"={self.get_max_possible_total_release()})"
        )

    def __hash__(self):
        return hash((
            *sorted([
                (self.position, self.cooldown),
                (self.elephant_position, self.elephant_cooldown),
            ]),
            self.time_left,
            self.total_release,
            tuple(sorted(self.openable_valve_names)),
        ))

    def __eq__(self, other: "DoubleSearchState") -> bool:
        return hash(self) == hash(other)

    def get_max_possible_total_release(self) -> int:
        return self.total_release + self.time_left * sum(
            valve.flow
            for valve_name in self.openable_valve_names
            for valve in [self.valve_set[valve_name]]
        )

    def get_min_naive_total_release(self) -> int:
        state: DoubleSearchState = self
        min_total_release = state.total_release
        while state:
            min_total_release = state.total_release
            state = max(
                state.get_next_states(),
                key=lambda next_state: next_state.total_release,
                default=None,
            )
        return min_total_release

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
        if self.time_left <= 0:
            return
        can_open_valve = self.is_current_valve_openable
        can_open_elephant_valve = self.is_current_elephant_valve_openable
        can_open_any_valve = can_open_valve or can_open_elephant_valve
        if can_open_any_valve:
            next_state = self
            if can_open_valve:
                next_state = next_state.make_next(
                    new_opened_valves={
                        next_state.position: ('y', next_state.time_left - 1)
                    },
                    openable_valve_names=(
                        next_state.openable_valve_names - {next_state.position}
                    ),
                    release_added=(
                        (next_state.time_left - 1) * next_state.valve.flow
                    ),
                    time_passed=0,
                )
            if can_open_elephant_valve:
                next_state = next_state.make_next(
                    new_opened_valves={
                        next_state.elephant_position:
                        ('e', next_state.time_left - 1)
                    },
                    openable_valve_names=(
                        next_state.openable_valve_names
                        - {next_state.elephant_position}
                    ),
                    release_added=(
                        (next_state.time_left - 1)
                        * next_state.elephant_valve.flow
                    ),
                    time_passed=0,
                )
            travelable_positions = next_state.get_travelable_valve_names()
            can_move = (
                not can_open_valve
                and not self.cooldown
                and travelable_positions
            )
            can_elephant_move = (
                not can_open_elephant_valve
                and not self.elephant_cooldown
                and travelable_positions
            )
            if can_move:
                for next_valve_name in travelable_positions:
                    next_valve = next_state.valve_set[next_valve_name]
                    distance = next_state.valve_mapper[(
                        next_state.valve, next_valve,
                    )]
                    if distance >= next_state.time_left:
                        continue
                    yield next_state.make_next(
                        position=next_valve_name,
                        cooldown=distance - 1,
                        time_passed=1,
                    )
            elif can_elephant_move:
                for next_elephant_valve_name in travelable_positions:
                    next_elephant_valve = \
                        next_state.valve_set[next_elephant_valve_name]
                    elephant_distance = next_state.valve_mapper[(
                        next_state.elephant_valve, next_elephant_valve,
                    )]
                    if elephant_distance >= next_state.time_left:
                        continue
                    yield next_state.make_next(
                        elephant_position=next_elephant_valve_name,
                        elephant_cooldown=elephant_distance - 1,
                        time_passed=1,
                    )
            else:
                yield next_state.make_next(time_passed=1)
        else:
            travelable_positions = self.get_travelable_valve_names()
            if not self.cooldown and not self.elephant_cooldown \
                    and len(travelable_positions) >= 2:
                next_valve_names = set(itertools.chain(
                    itertools.combinations(travelable_positions, 2),
                    itertools.combinations(
                        list(reversed(travelable_positions)), 2,
                    ),
                ))

                for next_valve_name, next_elephant_valve_name \
                        in next_valve_names:
                    next_valve = self.valve_set[next_valve_name]
                    distance = self.valve_mapper[(self.valve, next_valve)]
                    next_elephant_valve = \
                        self.valve_set[next_elephant_valve_name]
                    elephant_distance = self.valve_mapper[(
                        self.elephant_valve, next_elephant_valve,
                    )]
                    if distance < self.time_left \
                            and elephant_distance < self.time_left:
                        time_passed = min(distance, elephant_distance)
                        yield self.make_next(
                            position=next_valve_name,
                            elephant_position=next_elephant_valve_name,
                            cooldown=distance - time_passed,
                            elephant_cooldown=elephant_distance - time_passed,
                            time_passed=time_passed,
                        )
                    elif distance < self.time_left:
                        yield self.make_next(
                            position=next_valve_name,
                            time_passed=distance,
                        )
                    elif elephant_distance < self.time_left:
                        yield self.make_next(
                            elephant_position=next_elephant_valve_name,
                            time_passed=elephant_distance,
                        )
            elif not self.cooldown and travelable_positions:
                for next_valve_name in travelable_positions:
                    next_valve = self.valve_set[next_valve_name]
                    distance = self.valve_mapper[(self.valve, next_valve)]
                    if distance >= self.time_left:
                        continue
                    yield self.make_next(
                        position=next_valve_name,
                        time_passed=distance,
                    )
            elif not self.elephant_cooldown and travelable_positions:
                for next_elephant_valve_name in travelable_positions:
                    next_elephant_valve = \
                        self.valve_set[next_elephant_valve_name]
                    elephant_distance = self.valve_mapper[(
                        self.elephant_valve, next_elephant_valve,
                    )]
                    if elephant_distance >= self.time_left:
                        continue
                    yield self.make_next(
                        elephant_position=next_elephant_valve_name,
                        time_passed=elephant_distance,
                    )
            elif self.cooldown and not travelable_positions:
                yield self.make_next(
                    time_passed=self.cooldown,
                )
            elif self.elephant_cooldown and not travelable_positions:
                yield self.make_next(
                    time_passed=self.elephant_cooldown,
                )
            else:
                if travelable_positions or self.cooldown \
                        or self.elephant_cooldown:
                    raise Exception(
                        f"There are openable positions or cool-downs: {self}"
                    )

    def make_next(
        self,
        position: Optional[str] = None,
        elephant_position: Optional[str] = None,
        cooldown: Optional[int] = None,
        elephant_cooldown: Optional[int] = None,
        new_opened_valves: Optional[Dict[str, int]] = None,
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
