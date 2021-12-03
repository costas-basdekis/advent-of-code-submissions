#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, Set, List, Iterable, Tuple, Generic, Type

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class

Graph = Dict[str, Set[str]]
Path = List[str]
Paths = List[Path]


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        4691
        """
        return CaveSystem.from_caves_text(_input).get_path_count(debugger)


CaveFinderT = TV["CaveFinder"]


@dataclass
class CaveSystem(Generic[CaveFinderT]):
    graph: Graph

    START = "start"
    END = "end"

    @classmethod
    def get_finder_class(cls) -> Type[CaveFinderT]:
        return get_type_argument_class(cls, CaveFinderT)

    @classmethod
    def from_caves_text(cls, caves_text: str) -> "CaveSystem":
        """
        >>> # noinspection PyUnresolvedReferences
        >>> sorted(
        ...     (_start, sorted(ends))
        ...     for _start, ends in CaveSystem.from_caves_text('''
        ...         start-A
        ...         start-b
        ...         A-c
        ...         A-b
        ...         b-d
        ...         A-end
        ...         b-end
        ...     ''').graph.items()
        ... )
        [('A', ['b', 'c', 'end', 'start']), ('b', ['A', 'd', 'end', 'start']),
            ('c', ['A']), ('d', ['b']), ('end', ['A', 'b']),
            ('start', ['A', 'b'])]
        """
        graph = {}
        lines = filter(None, map(str.strip, caves_text.splitlines()))
        for line in lines:
            start, end = line.strip().split("-")
            graph.setdefault(start, set()).add(end)
            graph.setdefault(end, set()).add(start)

        if cls.START not in graph or cls.END not in graph:
            raise Exception(
                f"Expected '{cls.START}' and '{cls.END}', but did not find it"
            )

        return cls(graph=graph)

    def get_path_count(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        """
        >>> CaveSystem.from_caves_text('''
        ...     start-A
        ...     start-b
        ...     A-c
        ...     A-b
        ...     b-d
        ...     A-end
        ...     b-end
        ... ''').get_path_count()
        10
        >>> CaveSystem.from_caves_text('''
        ...     dc-end
        ...     HN-start
        ...     start-kj
        ...     dc-start
        ...     dc-HN
        ...     LN-dc
        ...     HN-end
        ...     kj-sa
        ...     kj-HN
        ...     kj-dc
        ... ''').get_path_count()
        19
        >>> CaveSystem.from_caves_text('''
        ...     fs-end
        ...     he-DX
        ...     fs-he
        ...     start-DX
        ...     pj-DX
        ...     end-zg
        ...     zg-sl
        ...     zg-pj
        ...     pj-he
        ...     RW-he
        ...     fs-DX
        ...     pj-RW
        ...     zg-RW
        ...     start-pj
        ...     he-WI
        ...     zg-he
        ...     pj-fs
        ...     start-RW
        ... ''').get_path_count()
        226
        """
        return len(self.get_paths(debugger))

    def get_paths(self, debugger: Debugger = Debugger(enabled=False)) -> Paths:
        """
        >>> sorted(CaveSystem.from_caves_text('''
        ...     start-A
        ...     start-b
        ...     A-c
        ...     A-b
        ...     b-d
        ...     A-end
        ...     b-end
        ... ''').get_paths())
        [['start', 'A', 'b', 'A', 'c', 'A', 'end'],
            ['start', 'A', 'b', 'A', 'end'],
            ['start', 'A', 'b', 'end'],
            ['start', 'A', 'c', 'A', 'b', 'A', 'end'],
            ['start', 'A', 'c', 'A', 'b', 'end'],
            ['start', 'A', 'c', 'A', 'end'],
            ['start', 'A', 'end'],
            ['start', 'b', 'A', 'c', 'A', 'end'],
            ['start', 'b', 'A', 'end'],
            ['start', 'b', 'end']]
        """
        return self.get_finder_class().find_for_system(self, debugger=debugger)


CaveFinderStateT = TV["CaveFindingState"]


@dataclass
class CaveFinder(Generic[CaveFinderStateT]):
    system: CaveSystem
    paths: Paths = field(default_factory=list)
    seen: Set["CaveFindingState"] = field(default_factory=set)
    stack: List["CaveFindingState"] = field(default_factory=list)

    @classmethod
    def get_state_class(cls) -> Type[CaveFinderStateT]:
        return get_type_argument_class(cls, CaveFinderStateT)

    @classmethod
    def find_for_system(
        cls, system: CaveSystem, debugger: Debugger = Debugger(enabled=False),
    ) -> Paths:
        return cls(system=system).find(debugger=debugger)

    def find(self, debugger: Debugger = Debugger(enabled=False)) -> Paths:
        def reporting_format(_: Debugger, message: str) -> str:
            return f"{message} ({len(seen)} seen, {len(stack)} in stack)"

        paths = []
        stack: List[CaveFinderStateT] = [self.get_state_class().make_initial()]
        seen = {stack[0]}
        with debugger.adding_extra_report_format(reporting_format):
            debugger.report("Looking...")
            while debugger.step_if(stack):
                debugger.report("Looking...")
                state = stack.pop(0)
                for next_state in state.get_next_states(self.system.graph):
                    if next_state in seen:
                        continue
                    seen.add(next_state)
                    if next_state.is_terminal:
                        paths.append(next_state.path)
                        debugger.report(f"Found path {next_state.path}")
                        continue
                    stack.append(next_state)

        return paths


@dataclass
class CaveFindingState:
    position: str
    path: Path
    small_visited: Set[str]

    @classmethod
    def make_initial(cls) -> "CaveFindingState":
        position = CaveSystem.START
        return cls(
            position=position,
            path=[position],
            small_visited={position},
        )

    def __hash__(self) -> int:
        return hash(self.get_hash_key())

    def __eq__(self, other: "CaveFindingState") -> bool:
        return self.get_hash_key() == other.get_hash_key()

    def get_hash_key(self) -> Tuple[str, ...]:
        return tuple(self.path)

    def get_next_states(self, graph: Graph) -> Iterable["CaveFindingState"]:
        if self.is_terminal:
            return

        cls = type(self)
        for next_position in graph[self.position]:
            next_small_visited = self.small_visited
            if self.is_cave_small(next_position):
                if next_position in next_small_visited:
                    continue
                next_small_visited = next_small_visited | {next_position}
            next_path = self.path + [next_position]
            # noinspection PyArgumentList
            yield cls(
                position=next_position,
                path=next_path,
                small_visited=next_small_visited,
            )

    @property
    def is_terminal(self) -> bool:
        """
        >>> CaveFindingState('', ['start'], set()).is_terminal
        False
        >>> CaveFindingState('', ['start', 'end'], set()).is_terminal
        True
        """
        return self.path[-1] == CaveSystem.END

    def is_cave_small(self, cave: str) -> bool:
        """
        >>> CaveFindingState('', [], set()).is_cave_small('a')
        True
        >>> CaveFindingState('', [], set()).is_cave_small('A')
        False
        """
        return cave.lower() == cave


Challenge.main()
challenge = Challenge()
