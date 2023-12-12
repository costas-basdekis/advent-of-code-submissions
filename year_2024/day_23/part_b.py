#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_23 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        'bd,dk,ir,ko,lk,nn,ob,pt,te,tl,uh,wj,yl'
        """
        return NetworkExtended.from_text(_input).find_password()


class NetworkExtended(part_a.Network):
    def find_password(self) -> str:
        """
        >>> NetworkExtended.from_text(part_a.EXAMPLE_TEXT).find_password()
        'co,de,ka,ta'
        """
        return ",".join(sorted(self.get_largest_clique()))

    def get_largest_clique(self) -> Set[str]:
        """
        >>> sorted(NetworkExtended.from_text(part_a.EXAMPLE_TEXT).get_largest_clique())
        ['co', 'de', 'ka', 'ta']
        """
        clique_cache = CliqueCache()
        return max((
            self.get_largest_clique_with_computers([computer], clique_cache=clique_cache)
            for computer in self.connections
        ), key=len, default=set())

    def get_largest_clique_with_computers(self, computers: List[str], clique_cache: Optional["CliqueCache"] = None) -> Set[str]:
        """
        >>> sorted(NetworkExtended.from_text(part_a.EXAMPLE_TEXT).get_largest_clique_with_computers(['co', 'de', 'ka']))
        ['co', 'de', 'ka', 'ta']
        >>> sorted(NetworkExtended.from_text(part_a.EXAMPLE_TEXT).get_largest_clique_with_computers(['co', 'de']))
        ['co', 'de', 'ka', 'ta']
        >>> sorted(NetworkExtended.from_text(part_a.EXAMPLE_TEXT).get_largest_clique_with_computers(['co']))
        ['co', 'de', 'ka', 'ta']
        """
        if clique_cache is None:
            clique_cache = CliqueCache()
        if computers in clique_cache:
            return clique_cache[computers]
        common = self.get_common_neighbours(computers)
        clique = set(computers) | max((
            self.get_largest_clique_with_computers(computers + [other], clique_cache=clique_cache)
            for other in common
        ), key=len, default=set())
        clique_cache[computers] = clique
        return clique

    def get_common_neighbours(self, computers: List[str]) -> Set[str]:
        """
        >>> sorted(NetworkExtended.from_text(part_a.EXAMPLE_TEXT).get_common_neighbours(['co', 'de', 'ka']))
        ['ta']
        """
        common: Optional[Set] = None
        for computer in computers:
            if common is None:
                common = self.connections[computer]
                continue
            common = common & self.connections[computer]
            if not common:
                break
        return common or set()


@dataclass
class CliqueCache:
    cache: Dict[Tuple[str, ...], Set[str]] = field(default_factory=dict)

    def __getitem__(self, computers: Iterable[str]) -> Set[str]:
        computers = tuple(sorted(computers))
        return self.cache[computers]

    def __setitem__(self, computers: Iterable[str], value: Set[str]):
        computers = tuple(sorted(computers))
        self.cache[computers] = value

    def __contains__(self, computers: Iterable[str]) -> bool:
        computers = tuple(sorted(computers))
        return computers in self.cache


Challenge.main()
challenge = Challenge()
