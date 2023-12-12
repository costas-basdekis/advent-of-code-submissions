#!/usr/bin/env python3
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, Iterable, List, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> solution = Challenge().default_solve()
        >>> solution
        3990
        """
        return Grove.from_scan(_input).step_many(10).get_empty_count()


class Direction(Enum):
    North = "north"
    South = "south"
    West = "west"
    East = "east"


@dataclass
class Grove:
    elves: Set[Point2D]
    width: int
    height: int
    rounds: int

    proposal_offsets: ClassVar[Dict[Direction, List[Point2D]]] = {
        Direction.North: [Point2D(x, -1) for x in range(-1, 2)],
        Direction.South: [Point2D(x, 1) for x in range(-1, 2)],
        Direction.West: [Point2D(-1, y) for y in range(-1, 2)],
        Direction.East: [Point2D(1, y) for y in range(-1, 2)],
    }
    directions_per_round: ClassVar[Dict[int, List[Direction]]] = {
        0: list(Direction),
        1: list(Direction)[1:] + list(Direction)[:1],
        2: list(Direction)[2:] + list(Direction)[:2],
        3: list(Direction)[3:] + list(Direction)[:3],
    }

    @classmethod
    def from_scan(cls, text: str) -> "Grove":
        """
        >>> print("!" + str(Grove.from_scan('''
        ...     ....#..
        ...     ..###.#
        ...     #...#.#
        ...     .#...##
        ...     #.###..
        ...     ##.#.##
        ...     .#..#..
        ... ''')))
        !....#..
        ..###.#
        #...#.#
        .#...##
        #.###..
        ##.#.##
        .#..#..
        """
        lines = list(map(str.strip, text.strip().splitlines()))
        return cls(elves={
            Point2D(x, y)
            for y, line in enumerate(lines)
            for x, character in enumerate(line)
            if character == "#"
        }, width=len(lines[0]) if lines else 0, height=len(lines), rounds=0)

    PROPOSAL_PRINT_MAP: ClassVar[Dict[Point2D, str]] = {
        Point2D(0, 0): "#",
        Point2D(0, -1): "^",
        Point2D(0, 1): "v",
        Point2D(-1, 0): "<",
        Point2D(1, 0): ">",
    }

    def __str__(self, show_proposals: bool = False) -> str:
        """
        >>> print("!" + str(Grove.from_scan(".....\\n..##.\\n..#..\\n.....\\n..##.\\n.....")))
        !.....
        ..##.
        ..#..
        .....
        ..##.
        .....
        """
        return "\n".join(
            "".join(
                (
                    "#"
                    if not show_proposals else
                    self.PROPOSAL_PRINT_MAP[self.get_elf_proposal(position, self.rounds).difference(position)]
                )
                if position in self.elves else
                "."
                for x in range(0, self.width)
                for position in [Point2D(x, y)]
            )
            for y in range(0, self.height)
        )

    def show_proposals(self) -> str:
        return self.__str__(show_proposals=True)

    def get_empty_count(self) -> int:
        """
        >>> _grove = Grove.from_scan('''
        ...     ..............
        ...     ..............
        ...     .......#......
        ...     .....###.#....
        ...     ...#...#.#....
        ...     ....#...##....
        ...     ...#.###......
        ...     ...##.#.##....
        ...     ....#..#......
        ...     ..............
        ...     ..............
        ...     ..............
        ... ''')
        >>> _grove.step_many(10).get_empty_count()
        110
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.elves)
        return sum(
            1
            if Point2D(x, y) not in self.elves else
            0
            for x in range(min_x, max_x + 1)
            for y in range(min_y, max_y + 1)
        )

    def step_many(self, count: int) -> "Grove":
        """
        >>> print("!" + str(Grove.from_scan(".....\\n..##.\\n..#..\\n.....\\n..##.\\n.....").step_many(2)))
        !.....
        ..##.
        .#...
        ....#
        .....
        ..#..
        >>> print("!" + str(Grove.from_scan(".....\\n..##.\\n..#..\\n.....\\n..##.\\n.....").step_many(3)))
        !..#..
        ....#
        #....
        ....#
        .....
        ..#..
        >>> _grove = Grove.from_scan('''
        ...     ..............
        ...     ..............
        ...     .......#......
        ...     .....###.#....
        ...     ...#...#.#....
        ...     ....#...##....
        ...     ...#.###......
        ...     ...##.#.##....
        ...     ....#..#......
        ...     ..............
        ...     ..............
        ...     ..............
        ... ''')
        >>> print("!" + str(_grove.step_many(1)))
        !..............
        .......#......
        .....#...#....
        ...#..#.#.....
        .......#..#...
        ....#.#.##....
        ..#..#.#......
        ..#.#.#.##....
        ..............
        ....#..#......
        ..............
        ..............
        >>> print("!" + _grove.step_many(1).show_proposals())
        !..............
        .......#......
        .....<...>....
        ...#..#.#.....
        .......#..>...
        ....<.#.#v....
        ..<..#.#......
        ..v.v.v.vv....
        ..............
        ....#..#......
        ..............
        ..............
        >>> print("!" + str(_grove.step_many(2)))
        !..............
        .......#......
        ....#.....#...
        ...#..#.#.....
        .......#...#..
        ...#..#.#.....
        .#...#.#.#....
        ..............
        ..#.#.#.##....
        ....#..#......
        ..............
        ..............
        >>> print("!" + str(_grove.step_many(5)))
        !.......#......
        ..............
        ..#..#.....#..
        .........#....
        ......##...#..
        .#.#.####.....
        ...........#..
        ....##..#.....
        ..#...........
        ..........#...
        ....#..#......
        ..............
        >>> print("!" + str(_grove.step_many(10)))
        !.......#......
        ...........#..
        ..#.#..#......
        ......#.......
        ...#.....#..#.
        .#......##....
        .....##.......
        ..#........#..
        ....#.#..#....
        ..............
        ....#..#..#...
        ..............
        """
        grove = self
        for _ in range(count):
            previous = grove
            grove = grove.step()
            if previous == grove:
                return grove
        return grove

    def step(self) -> "Grove":
        """
        >>> print("!" + str(Grove.from_scan(".....\\n..##.\\n..#..\\n.....\\n..##.\\n.....").step()))
        !..##.
        .....
        ..#..
        ...#.
        ..#..
        .....
        """
        transitions = [
            (position, self.get_elf_proposal(position, self.rounds))
            for position in self.elves
        ]
        proposal_counts = Counter(proposal for _, proposal in transitions)
        all_overlapping = all(count > 1 for count in proposal_counts.values())
        if all_overlapping:
            new_elves = self.elves
        else:
            no_movement = all(
                position == proposal
                for position, proposal in transitions
            )
            if no_movement:
                return self
            new_elves: Set[Point2D] = {
                proposal
                if proposal_counts[proposal] == 1 else
                position
                for position, proposal in transitions
            }
        cls = type(self)
        return cls(elves=new_elves, width=self.width, height=self.height, rounds=self.rounds + 1)

    def get_elf_proposals(self, round_index: int) -> Iterable[Point2D]:
        """
        >>> grove = Grove.from_scan(".....\\n..##.\\n..#..\\n.....\\n..##.\\n.....")
        >>> sorted(grove.get_elf_proposals(0))
        [Point2D(x=2, y=0), Point2D(x=2, y=3), Point2D(x=2, y=3), Point2D(x=3, y=0), Point2D(x=3, y=3)]
        """
        for elf in self.elves:
            yield self.get_elf_proposal(elf, round_index)

    def get_elf_proposal(self, position: Point2D, round_index: int) -> Point2D:
        """
        >>> grove = Grove.from_scan('...\\n.#.\\n...')
        >>> grove.get_elf_proposal(Point2D(1, 1), 0)
        Point2D(x=1, y=1)
        >>> grove.get_elf_proposal(Point2D(1, 1), 1)
        Point2D(x=1, y=1)
        >>> grove.get_elf_proposal(Point2D(1, 1), 2)
        Point2D(x=1, y=1)
        >>> grove.get_elf_proposal(Point2D(1, 1), 3)
        Point2D(x=1, y=1)
        >>> Grove.from_scan('#..\\n.#.\\n...').get_elf_proposal(Point2D(1, 1), 0)
        Point2D(x=1, y=2)
        """
        any_elves_around = any(
            neighbour in self.elves
            for neighbour in position.get_euclidean_neighbours()
        )
        if not any_elves_around:
            return position
        directions = self.directions_per_round[round_index % 4]
        for direction in directions:
            if self.can_elf_propose_direction(position, direction):
                new_position = position.offset(self.proposal_offsets[direction][1])
                return new_position
        return position

    def can_elf_propose_direction(self, position: Point2D, direction: Direction) -> bool:
        """
        >>> Grove.from_scan('...\\n.#.\\n...').can_elf_propose_direction(Point2D(1, 1), Direction.North)
        True
        >>> Grove.from_scan('#..\\n.#.\\n...').can_elf_propose_direction(Point2D(1, 1), Direction.North)
        False
        """
        return not any(
            (position.offset(offset)) in self.elves
            for offset in self.proposal_offsets[direction]
        )


Challenge.main()
challenge = Challenge()
