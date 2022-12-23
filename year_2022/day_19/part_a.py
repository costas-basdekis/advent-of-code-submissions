#!/usr/bin/env python3
from dataclasses import dataclass
import re
from enum import Enum
from typing import Dict, Iterable, Optional, Set, Union, List

from aox.challenge import Debugger
from utils import BaseChallenge, Cls


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2301
        """
        return BlueprintSet\
            .get_sum_of_quality_levels_from_blueprints_text(
                _input, debugger=debugger,
            )

    def play(self):
        state = SearchState.from_blueprint_text(FIRST_INPUT)
        while state:
            print(state, state.get_robots_that_can_be_built())
            next_states = list(state.iterate_next_states())
            for index, next_state in enumerate(next_states):
                print(f" {index + 1}: {next_state}")
            indexes = set(map(str, range(1, len(next_states) + 1)))
            while True:
                choice_str = input("Choose: ").strip().lower()
                if choice_str == "q":
                    state = None
                    break
                if choice_str in indexes:
                    state = next_states[int(choice_str) - 1]
                    break


Stockpile = Dict["Resource", int]
Robot = "Robot"
Robots = Dict[Robot, int]


@dataclass
class BlueprintSet:
    blueprints: List["Blueprint"]

    @classmethod
    def get_sum_of_quality_levels_from_blueprints_text(
        cls, blueprints_text: str, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> BlueprintSet.get_sum_of_quality_levels_from_blueprints_text(
        ...     LONG_INPUT)
        33
        """
        return cls\
            .from_blueprints_text(blueprints_text)\
            .get_sum_of_quality_levels(debugger=debugger)

    @classmethod
    def from_blueprints_text(cls, blueprints_text: str) -> "BlueprintSet":
        return cls(
            blueprints=list(map(
                Blueprint.from_blueprint_text,
                blueprints_text.strip().splitlines(),
            )),
        )

    def get_sum_of_quality_levels(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        total = 0
        for index, blueprint in enumerate(self.blueprints, 1):
            debugger.report(
                f"Blueprint {index}/{len(self.blueprints)}, "
                f"sum is {total}"
            )
            best_geode_count = GeodeFinder\
                .from_blueprint(blueprint)\
                .search(debugger=debugger)
            total += blueprint.id * best_geode_count
            debugger.report(
                f"Blueprint {index}/{len(self.blueprints)}: "
                f"gave {best_geode_count}, "
                f"quality level is {blueprint.id * best_geode_count}, "
                f"sum is {total}"
            )
        return total


@dataclass
class GeodeFinder:
    queue: List["SearchState"]
    seen: Set["SearchState"]
    max_time: int
    best_geode_count: int

    @classmethod
    def get_most_geodes_from_blueprint_text(
        cls, blueprint_text: str, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> GeodeFinder.get_most_geodes_from_blueprint_text(FIRST_INPUT)
        9
        >>> GeodeFinder.get_most_geodes_from_blueprint_text(SECOND_INPUT)
        12
        """
        return cls.from_blueprint_text(blueprint_text).search(debugger=debugger)

    @classmethod
    def from_blueprint_text(cls, blueprint_text: str) -> "GeodeFinder":
        return cls.from_blueprint(Blueprint.from_blueprint_text(blueprint_text))

    @classmethod
    def from_blueprint(cls, blueprint: "Blueprint") -> "GeodeFinder":
        initial_state = SearchState.from_blueprint(blueprint)
        max_time = 24
        return cls(
            queue=[initial_state],
            seen={initial_state},
            max_time=max_time,
            best_geode_count=initial_state.get_total_geodes(max_time=max_time),
        )

    def search(self, debugger: Debugger = Debugger(enabled=True)) -> int:
        while debugger.step_if(True):
            if not self.search_step():
                break
            if debugger.should_report():
                debugger.default_report(
                    f"Queue: {len(self.queue)}, "
                    f"best geode count: {self.best_geode_count}, "
                    f"next time: {self.queue[0].time if self.queue else 'N/A'},"
                    f" "
                    f"seen: {len(self.seen)}"
                )
        debugger.default_report(
            f"Best geode count: {self.best_geode_count}, "
            f"seen: {len(self.seen)}"
        )

        return self.best_geode_count

    def search_step(self) -> bool:
        if not self.queue:
            return False
        state = self.queue.pop(0)
        if state.time >= self.max_time:
            return True
        for next_state in state.iterate_next_states():
            if next_state in self.seen:
                continue
            if next_state.get_max_possible_geodes(max_time=self.max_time) \
                    <= self.best_geode_count:
                continue
            self.queue.append(next_state)
            self.seen.add(next_state)
            self.best_geode_count = max(
                self.best_geode_count,
                next_state.get_total_geodes(max_time=self.max_time),
            )

        return True


@dataclass
class SearchState:
    time: int
    blueprint: "Blueprint"
    stockpile: Stockpile
    robots: Robots
    action: str

    @classmethod
    def from_blueprint_text(cls, blueprint_text: str) -> "SearchState":
        return cls.from_blueprint(Blueprint.from_blueprint_text(blueprint_text))

    @classmethod
    def from_blueprint(cls, blueprint: "Blueprint") -> "SearchState":
        return cls(
            time=0,
            blueprint=blueprint,
            stockpile={resource: 0 for resource in Resource},
            robots={
                **{
                    resource: 0
                    for resource in Resource
                },
                Resource.Ore: 1,
            },
            action="initial",
        )

    def __hash__(self) -> int:
        return hash(self.get_hash())

    def __eq__(self, other: "SearchState") -> bool:
        return self.get_hash() == other.get_hash()

    def get_hash(self):
        return (
            tuple(self.stockpile[resource] for resource in Resource),
            tuple(self.robots[robot] for robot in Resource),
        )

    def get_total_geodes(self, max_time: int = 24) -> int:
        return (
            self.stockpile[Resource.Geode]
            + self.robots[Resource.Geode] * max(0, max_time - self.time)
        )

    def get_max_possible_geodes(self, max_time: int = 24) -> int:
        max_new_geode_robots = max_time - self.time - 1
        if not self.robots[Resource.Obsidian]:
            max_new_geode_robots -= 1
        if not self.robots[Resource.Clay]:
            max_new_geode_robots -= 1
        max_new_geode_robots = max(0, max_new_geode_robots)
        return (
            self.get_total_geodes(max_time=max_time)
            + max_new_geode_robots * (1 + max_new_geode_robots) // 2
        )

    @property
    def geode_count(self) -> int:
        return self.stockpile[Resource.Geode]

    def iterate_next_states(self) -> Iterable["SearchState"]:
        """
        >>> list(SearchState.from_blueprint_text(
        ...     FIRST_INPUT).iterate_next_states())
        [SearchState(time=1, blueprint=Blueprint(...),
            stockpile={Resource.Ore: 1, Resource.Clay: 0, Resource.Obsidian: 0,
            Resource.Geode: 0}, robots={Resource.Ore: 1, Resource.Clay: 0,
            Resource.Obsidian: 0, Resource.Geode: 0})]
        """
        robots_that_can_be_built = self.get_robots_that_can_be_built()
        if not robots_that_can_be_built or robots_that_can_be_built \
                != self.get_robots_that_could_be_built():
            yield self.make_next(
                # action="Collect",
            )
        for robot in robots_that_can_be_built:
            yield self.make_next(
                # action=f"Build {robot}",
                start_stockpile=self.blueprint.build_robot(
                    self.stockpile, robot,
                ),
                robot_updates={
                    robot: 1,
                },
            )

    def make_next(
        self,
        # action: str,
        start_stockpile: Optional[Stockpile] = None,
        robot_updates: Optional[Robots] = None,
    ) -> "SearchState":
        cls: Cls["SearchState"] = type(self)
        if start_stockpile is None:
            start_stockpile = self.stockpile
        # noinspection PyArgumentList
        return cls(
            time=self.time + 1,
            blueprint=self.blueprint,
            stockpile={
                resource: quantity + self.robots[resource]
                for resource, quantity
                in start_stockpile.items()
            },
            robots=(
                {
                    **self.robots,
                    **{
                        robot: self.robots[robot] + new_quantity
                        for robot, new_quantity in robot_updates.items()
                    }
                }
                if robot_updates is not None else
                self.robots
            ),
            action="",
            # action=action,
        )

    def get_robots_that_can_be_built(self):
        return self.blueprint \
            .get_robots_that_can_be_built(self.stockpile)

    def get_robots_that_could_be_built(self):
        return self.blueprint \
            .get_robots_that_can_be_built({
                resource: 1000 if quantity else 0
                for resource, quantity in self.stockpile.items()
            })


@dataclass
class Blueprint:
    id: int
    robot_costs: Dict[Robot, Stockpile]

    re_blueprint = re.compile(
        r"^Blueprint (\d+):\s+"
        r"Each ore robot costs (\d+) ore.\s+"
        r"Each clay robot costs (\d+) ore.\s+"
        r"Each obsidian robot costs (\d+) ore and (\d+) clay.\s+"
        r"Each geode robot costs (\d+) ore and (\d+) obsidian.$"
    )

    @classmethod
    def from_blueprint_text(cls, blueprint_text: str) -> "Blueprint":
        """
        >>> Blueprint.from_blueprint_text(FIRST_INPUT)
        Blueprint(id=1, robot_costs={Resource.Ore: {Resource.Ore: 4},
            Resource.Clay: {Resource.Ore: 2},
            Resource.Obsidian: {Resource.Ore: 3, Resource.Clay: 14},
            Resource.Geode: {Resource.Ore: 2, Resource.Obsidian: 7}})
        """
        (
            _id, ore_ore, clay_ore, obsidian_ore,
            obsidian_clay, geode_ore, geode_obsidian,
        ) = map(int, cls.re_blueprint.match(blueprint_text).groups())
        return cls(
            id=_id,
            robot_costs={
                Resource.Ore: {Resource.Ore: ore_ore},
                Resource.Clay: {Resource.Ore: clay_ore},
                Resource.Obsidian: {
                    Resource.Ore: obsidian_ore,
                    Resource.Clay: obsidian_clay,
                },
                Resource.Geode: {
                    Resource.Ore: geode_ore,
                    Resource.Obsidian: geode_obsidian,
                },
            },
        )

    def build_robot(
        self, stockpile: Stockpile, robot: Robot,
    ) -> Stockpile:
        """
        >>> blueprint = Blueprint.from_blueprint_text(FIRST_INPUT)
        >>> blueprint.build_robot({
        ...     Resource.Ore: 20, Resource.Clay: 20, Resource.Obsidian: 20,
        ... }, Resource.Ore)
        {Resource.Ore: 16, Resource.Clay: 20, Resource.Obsidian: 20}
        >>> blueprint.build_robot({
        ...     Resource.Ore: 20, Resource.Clay: 20, Resource.Obsidian: 20,
        ... }, Resource.Clay)
        {Resource.Ore: 18, Resource.Clay: 20, Resource.Obsidian: 20}
        >>> blueprint.build_robot({
        ...     Resource.Ore: 20, Resource.Clay: 20, Resource.Obsidian: 20,
        ... }, Resource.Obsidian)
        {Resource.Ore: 17, Resource.Clay: 6, Resource.Obsidian: 20}
        >>> blueprint.build_robot({
        ...     Resource.Ore: 20, Resource.Clay: 20, Resource.Obsidian: 20,
        ... }, Resource.Geode)
        {Resource.Ore: 18, Resource.Clay: 20, Resource.Obsidian: 13}
        """
        robot_resources = self.robot_costs[robot]
        return {
            resource: quantity - robot_resources.get(resource, 0)
            for resource, quantity
            in stockpile.items()
        }

    def get_robots_that_can_be_built(self, stockpile: Stockpile) -> Set[Robot]:
        """
        >>> blueprint = Blueprint.from_blueprint_text(FIRST_INPUT)
        >>> sorted(blueprint.get_robots_that_can_be_built({}))
        []
        >>> sorted(blueprint.get_robots_that_can_be_built({
        ...     Resource.Ore: 1}))
        []
        >>> sorted(blueprint.get_robots_that_can_be_built({
        ...     Resource.Ore: 2}))
        [Resource.Clay]
        >>> sorted(blueprint.get_robots_that_can_be_built({
        ...     Resource.Ore: 20}))
        [Resource.Clay, Resource.Ore]
        >>> sorted(blueprint.get_robots_that_can_be_built({
        ...     Resource.Ore: 20, Resource.Clay: 20, Resource.Obsidian: 20}))
        [Resource.Clay, Resource.Geode, Resource.Obsidian, Resource.Ore]
        """
        return {
            robot
            for robot in Resource
            if self.can_stockpile_build(stockpile, robot)
        }

    def can_stockpile_build(
        self, stockpile: Stockpile, robot: Robot,
    ) -> bool:
        """
        >>> blueprint = Blueprint.from_blueprint_text(FIRST_INPUT)
        >>> blueprint.can_stockpile_build({}, Resource.Ore)
        False
        >>> blueprint.can_stockpile_build({Resource.Ore: 1}, Resource.Ore)
        False
        >>> blueprint.can_stockpile_build({Resource.Ore: 2}, Resource.Ore)
        False
        >>> blueprint.can_stockpile_build({}, Resource.Geode)
        False
        >>> blueprint.can_stockpile_build({Resource.Ore: 2}, Resource.Geode)
        False
        >>> blueprint.can_stockpile_build({
        ...     Resource.Obsidian: 7}, Resource.Geode)
        False
        >>> blueprint.can_stockpile_build({
        ...     Resource.Ore: 2, Resource.Obsidian: 6}, Resource.Geode)
        False
        >>> blueprint.can_stockpile_build({
        ...     Resource.Ore: 1, Resource.Obsidian: 7}, Resource.Geode)
        False
        >>> blueprint.can_stockpile_build({
        ...     Resource.Ore: 2, Resource.Obsidian: 7}, Resource.Geode)
        True
        """
        return all(
            stockpile.get(resource, 0) >= quantity
            for resource, quantity
            in self.robot_costs[robot].items()
        )


class Resource(Enum):
    Ore = "ore"
    Clay = "clay"
    Obsidian = "obsidian"
    Geode = "geode"

    def __lt__(self, other: "Resource") -> bool:
        return self.value < other.value

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


Challenge.main()
challenge = Challenge()


LONG_INPUT = """
Blueprint 1:
  Each ore robot costs 4 ore.
  Each clay robot costs 2 ore.
  Each obsidian robot costs 3 ore and 14 clay.
  Each geode robot costs 2 ore and 7 obsidian.

Blueprint 2:
  Each ore robot costs 2 ore.
  Each clay robot costs 3 ore.
  Each obsidian robot costs 3 ore and 8 clay.
  Each geode robot costs 3 ore and 12 obsidian.
""".strip().replace("\n  ", " ").replace("\n\n", "\n")
FIRST_INPUT = LONG_INPUT.splitlines()[0]
SECOND_INPUT = LONG_INPUT.splitlines()[1]
