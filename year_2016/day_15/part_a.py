#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Generic, List, Type

from utils import BaseChallenge, Cls, Self, TV, get_type_argument_class, \
    solve_linear_congruence_system


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> solution = Challenge().default_solve()
        >>> 318577 > solution > 9190
        True
        >>> solution
        122318
        """
        disc_set = DiscSet.from_discs_text(_input)
        if debug:
            print("\n".join(map(repr, disc_set.discs)))
        return disc_set.get_earliest_pass_through_time()


DiscT = TV['Disc']


@dataclass
class DiscSet(Generic[DiscT]):
    discs: List[DiscT]

    @classmethod
    def get_disc_class(cls) -> Type[DiscT]:
        return get_type_argument_class(cls, DiscT)

    @classmethod
    def from_discs_text(cls: Cls['DiscSet'], discs_text: str,
                        ) -> Self['DiscSet']:
        """
        >>> DiscSet.from_discs_text(
        ...     "Disc #1 has 5 positions; at time=0, it is at position 4.\\n"
        ...     "Disc #2 has 2 positions; at time=0, it is at position 1.\\n"
        ... )
        DiscSet(discs=[Disc(position=0, size=5), Disc(position=1, size=2)])
        """
        disc_class = cls.get_disc_class()
        return cls(list(map(
            disc_class.from_disc_text, discs_text.splitlines())))

    def get_earliest_pass_through_time(self) -> int:
        """
        >>> DiscSet.from_discs_text(
        ...     "Disc #1 has 5 positions; at time=0, it is at position 4.\\n"
        ...     "Disc #2 has 2 positions; at time=0, it is at position 1.\\n"
        ... ).get_earliest_pass_through_time()
        5
        """
        return solve_linear_congruence_system([
            (disc.size, disc.size - disc.position)
            for disc in self.discs
        ])


@dataclass
class Disc:
    position: int
    size: int

    re_disc = re.compile(
        r"^Disc #(\d+) has (\d+) positions; "
        r"at time=(\d+), "
        r"it is at position (\d+).$")

    @classmethod
    def from_disc_text(cls: Cls['Disc'], disc_text: str) -> Self['Disc']:
        """
        >>> Disc.from_disc_text(
        ...     'Disc #1 has 13 positions; at time=0, it is at position 12.')
        Disc(position=0, size=13)
        >>> Disc.from_disc_text(
        ...     'Disc #2 has 13 positions; at time=0, it is at position 11.')
        Disc(position=0, size=13)
        >>> Disc.from_disc_text(
        ...     'Disc #1 has 13 positions; at time=1, it is at position 0.')
        Disc(position=0, size=13)
        """
        offset_position_str, size_str, offset_time_str, position_str = \
            cls.re_disc.match(disc_text).groups()
        size = int(size_str)
        position = (
            int(position_str)
            + int(offset_position_str)
            - int(offset_time_str)
        ) % size
        return Disc(position, size)


Challenge.main()
challenge = Challenge()
