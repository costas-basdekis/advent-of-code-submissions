#!/usr/bin/env python3
import re
from collections import defaultdict
from dataclasses import field, dataclass
from itertools import permutations
from typing import Dict, Tuple, List, Iterable, Sized, Set

from aox.challenge import Debugger
from utils import BaseChallenge, get_windows


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        709
        """
        return AttendeeSet.from_happiness_listings_text(_input)\
            .get_happiest_arrangement_happiness()


@dataclass
class AttendeeSet:
    happiness_map: Dict[Tuple[str, str], int] = \
        field(default_factory=lambda: defaultdict(lambda: 0))

    re_happiness_listing = re.compile(
        r"^(\w+) would (gain|lose) (\d+) happiness units "
        r"by sitting next to (\w+).$")

    @classmethod
    def from_happiness_listings_text(cls, happiness_listings_text: str):
        """
        >>> # noinspection PyUnresolvedReferences
        >>> [(_lhs, _rhs, happiness) for (_lhs, _rhs), happiness in sorted(
        ...     AttendeeSet.from_happiness_listings_text(
        ...         "Alice would gain 54 happiness units "
        ...         "by sitting next to Bob.\\n"
        ...         "Alice would lose 79 happiness units "
        ...         "by sitting next to Carol.\\n"
        ...         "Alice would lose 2 happiness units "
        ...         "by sitting next to David.\\n"
        ...         "Bob would gain 83 happiness units "
        ...         "by sitting next to Alice.\\n"
        ...         "Bob would lose 7 happiness units "
        ...         "by sitting next to Carol.\\n"
        ...         "Bob would lose 63 happiness units "
        ...         "by sitting next to David.\\n"
        ...         "Carol would lose 62 happiness units "
        ...         "by sitting next to Alice.\\n"
        ...         "Carol would gain 60 happiness units "
        ...         "by sitting next to Bob.\\n"
        ...         "Carol would gain 55 happiness units "
        ...         "by sitting next to David.\\n"
        ...         "David would gain 46 happiness units "
        ...         "by sitting next to Alice.\\n"
        ...         "David would lose 7 happiness units "
        ...         "by sitting next to Bob.\\n"
        ...         "David would gain 41 happiness units "
        ...         "by sitting next to Carol.\\n"
        ...     ).happiness_map.items()) if _lhs < _rhs]
        [('Alice', 'Bob', 137), ...]
        """
        lines = happiness_listings_text.splitlines()
        happiness_listings = map(cls.parse_happiness_listing, lines)
        happiness_map = defaultdict(lambda: 0)
        for lhs, rhs, happiness_offset in happiness_listings:
            happiness_map[(lhs, rhs)] += happiness_offset
            happiness_map[(rhs, lhs)] += happiness_offset

        return cls(happiness_map)

    GAIN_OR_LOSE_MAP = {
        "gain": 1,
        "lose": -1,
    }

    @classmethod
    def parse_happiness_listing(cls, happiness_listing_text: str,
                                ) -> Tuple[str, str, int]:
        match = cls.re_happiness_listing.match(happiness_listing_text)
        if not match:
            raise Exception(f"Could not parse {repr(happiness_listing_text)}")
        lhs, gain_or_lose_str, happiness_offset_str, rhs = match.groups()

        gain_or_lose = int(cls.GAIN_OR_LOSE_MAP[gain_or_lose_str])
        happiness_offset = int(happiness_offset_str)
        return lhs, rhs, gain_or_lose * happiness_offset

    def get_happiest_arrangement_happiness(self) -> int:
        """
        >>> AttendeeSet.from_happiness_listings_text(
        ...     "Alice would gain 54 happiness units "
        ...     "by sitting next to Bob.\\n"
        ...     "Alice would lose 79 happiness units "
        ...     "by sitting next to Carol.\\n"
        ...     "Alice would lose 2 happiness units "
        ...     "by sitting next to David.\\n"
        ...     "Bob would gain 83 happiness units "
        ...     "by sitting next to Alice.\\n"
        ...     "Bob would lose 7 happiness units "
        ...     "by sitting next to Carol.\\n"
        ...     "Bob would lose 63 happiness units "
        ...     "by sitting next to David.\\n"
        ...     "Carol would lose 62 happiness units "
        ...     "by sitting next to Alice.\\n"
        ...     "Carol would gain 60 happiness units "
        ...     "by sitting next to Bob.\\n"
        ...     "Carol would gain 55 happiness units "
        ...     "by sitting next to David.\\n"
        ...     "David would gain 46 happiness units "
        ...     "by sitting next to Alice.\\n"
        ...     "David would lose 7 happiness units "
        ...     "by sitting next to Bob.\\n"
        ...     "David would gain 41 happiness units "
        ...     "by sitting next to Carol.\\n"
        ... ).get_happiest_arrangement_happiness()
        330
        """
        return self.get_arrangement_happiness(self.get_happiest_arrangement())

    def get_happiest_arrangement(self) -> Tuple[str, ...]:
        """
        >>> AttendeeSet.from_happiness_listings_text(
        ...     "Alice would gain 54 happiness units "
        ...     "by sitting next to Bob.\\n"
        ...     "Alice would lose 79 happiness units "
        ...     "by sitting next to Carol.\\n"
        ...     "Alice would lose 2 happiness units "
        ...     "by sitting next to David.\\n"
        ...     "Bob would gain 83 happiness units "
        ...     "by sitting next to Alice.\\n"
        ...     "Bob would lose 7 happiness units "
        ...     "by sitting next to Carol.\\n"
        ...     "Bob would lose 63 happiness units "
        ...     "by sitting next to David.\\n"
        ...     "Carol would lose 62 happiness units "
        ...     "by sitting next to Alice.\\n"
        ...     "Carol would gain 60 happiness units "
        ...     "by sitting next to Bob.\\n"
        ...     "Carol would gain 55 happiness units "
        ...     "by sitting next to David.\\n"
        ...     "David would gain 46 happiness units "
        ...     "by sitting next to Alice.\\n"
        ...     "David would lose 7 happiness units "
        ...     "by sitting next to Bob.\\n"
        ...     "David would gain 41 happiness units "
        ...     "by sitting next to Carol.\\n"
        ... ).get_happiest_arrangement()
        ('Alice', 'Bob', 'Carol', 'David')
        """
        return max(self.get_all_arrangements(),
                   key=self.get_arrangement_happiness)

    def get_all_arrangements(self) -> Iterable[Tuple[str, ...]]:
        """
        >>> list(AttendeeSet({('a', 'b'): 2, ('b', 'a'): 2, ('b', 'c'): -1,
        ...     ('c', 'a'): 5})\\
        ...     .get_all_arrangements())
        [('a', 'b', 'c'), ('a', 'c', 'b'), ('b', 'a', 'c'), ('b', 'c', 'a'),
            ('c', 'a', 'b'), ('c', 'b', 'a')]
        """
        attendees = sorted(self.get_attendees())
        return permutations(attendees, len(attendees))

    def get_attendees(self) -> Set[str]:
        """
        >>> sorted(AttendeeSet({('a', 'b'): 2, ('b', 'a'): 2, ('b', 'c'): -1,
        ...     ('c', 'a'): 5})\\
        ...     .get_attendees())
        ['a', 'b', 'c']
        """
        return {
            attendee
            for edge in self.happiness_map
            for attendee in edge
        }

    def get_arrangement_happiness(self, arrangement: Tuple[str, ...]) -> int:
        """
        >>> AttendeeSet({('a', 'b'): 2, ('b', 'a'): 2, ('b', 'c'): -1,
        ...     ('c', 'a'): 5})\\
        ...     .get_arrangement_happiness(('a', 'b'))
        2
        >>> AttendeeSet({('a', 'b'): 2, ('b', 'c'): -1, ('c', 'a'): 5})\\
        ...     .get_arrangement_happiness(('a', 'b', 'c'))
        6
        """
        if len(arrangement) < 2:
            return 0
        elif len(arrangement) == 2:
            lhs, rhs = arrangement
            return self.happiness_map[(lhs, rhs)]
        return sum(
            self.happiness_map[(lhs, rhs)]
            for lhs, rhs in get_windows(arrangement + arrangement[:1], 2)
        )


Challenge.main()
challenge = Challenge()
