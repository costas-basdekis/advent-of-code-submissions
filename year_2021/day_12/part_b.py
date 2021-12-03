#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Set, ClassVar

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_12 import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        140718
        """
        return CaveSystemExtended\
            .from_caves_text(_input)\
            .get_path_count(debugger)


class CaveSystemExtended(part_a.CaveSystem["CaveFinderExtended"]):
    pass


class CaveFinderExtended(part_a.CaveFinder["CaveFindingStateExtended"]):
    """
    >>> system = CaveSystemExtended.from_caves_text('''
    ...     start-A
    ...     start-b
    ...     A-c
    ...     A-b
    ...     b-d
    ...     A-end
    ...     b-end
    ... ''')
    >>> initial = CaveFindingStateExtended.make_initial()
    >>> # noinspection PyUnresolvedReferences
    >>> sorted(
    ...     state.path
    ...     for state in initial.get_next_states(system.graph)
    ... )
    [['start', 'A'], ['start', 'b']]
    >>> # noinspection PyUnresolvedReferences
    >>> sorted(
    ...     state.path
    ...     for state1 in initial.get_next_states(system.graph)
    ...     for state in state1.get_next_states(system.graph)
    ... )
    [['start', 'A', 'b'], ['start', 'A', 'c'], ['start', 'A', 'end'],
        ['start', 'b', 'A'], ['start', 'b', 'd'], ['start', 'b', 'end']]
    >>> system.get_path_count()
    36
    """


@dataclass
class CaveFindingStateExtended(part_a.CaveFindingState):
    small_visited_twice: Set[str]

    NOT_VISITABLE_TWICE: ClassVar[Set[str]] = {
        part_a.CaveSystem.START,
        part_a.CaveSystem.END,
    }

    @classmethod
    def make_initial(cls) -> "CaveFindingStateExtended":
        position = part_a.CaveSystem.START
        return cls(
            position=position,
            path=[position],
            small_visited={position},
            small_visited_twice=set(),
        )

    def __hash__(self) -> int:
        return hash(self.get_hash_key())

    def __eq__(self, other: "CaveFindingStateExtended") -> bool:
        return self.get_hash_key() == other.get_hash_key()

    def can_visit(self, cave: str) -> bool:
        if not self.is_cave_small(cave):
            return True
        if cave in self.small_visited:
            if self.small_visited_twice:
                return False
            return cave not in self.NOT_VISITABLE_TWICE
        return True

    def visit(self, next_position: str) -> "CaveFindingStateExtended":
        cls = type(self)
        next_small_visited = self.small_visited
        next_small_visited_twice = self.small_visited_twice
        if self.is_cave_small(next_position):
            if next_position in next_small_visited:
                if next_position in self.NOT_VISITABLE_TWICE:
                    raise Exception(f"Cannot visit '{next_position}' twice")
                if next_small_visited_twice:
                    raise Exception(f"Cannot visit two small caves twice")
                next_small_visited_twice = {next_position}
            else:
                next_small_visited = next_small_visited | {next_position}
        # noinspection PyArgumentList
        return cls(
            position=next_position,
            path=self.path + [next_position],
            small_visited=next_small_visited,
            small_visited_twice=next_small_visited_twice,
        )


Challenge.main()
challenge = Challenge()
