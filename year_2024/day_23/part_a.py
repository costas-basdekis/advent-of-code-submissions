#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, Iterable, Set, Tuple, Union

import pyperclip

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1306
        """
        return Network.from_text(_input).get_3_connected_group_count_starting_with_t()

    def play(self):
        network = Network.from_text(self.input)
        graph = "\n".join([
            f"{first}[style=filled,fillcolor=yellow];"
            for first in network.connections
            if first.startswith("t")
        ] + [
            f"{first} -- {second};"
            for first, seconds in network.connections.items()
            for second in seconds
            if first < second
        ])
        pyperclip.copy(graph)
        print(f"Copied {len(graph)} characters to clipboard, paste into https://dreampuf.github.io/GraphvizOnline/")


@dataclass
class Network:
    connections: Dict[str, Set[str]]

    @classmethod
    def from_text(cls, text: str) -> "Network":
        connections = {}
        for line in map(str.strip, text.strip().splitlines()):
            first, second = line.split("-")
            connections.setdefault(first, set()).add(second)
            connections.setdefault(second, set()).add(first)
        return cls(connections)

    def get_3_connected_group_count_starting_with_t(self) -> int:
        """
        >>> Network.from_text(EXAMPLE_TEXT).get_3_connected_group_count_starting_with_t()
        7
        """
        return sum(
            1
            for _ in self.get_3_connected_groups_starting_with_t()
        )

    def get_3_connected_groups_starting_with_t(self) -> Iterable[Tuple[str, ...]]:
        """
        >>> print("\\n".join(sorted(map(",".join, Network.from_text(EXAMPLE_TEXT).get_3_connected_groups_starting_with_t()))))
        co,de,ta
        co,ka,ta
        de,ka,ta
        qp,td,wh
        tb,vc,wq
        tc,td,wh
        td,wh,yn
        """
        for group in self.get_3_connected_groups():
            if not any(item.startswith("t") for item in group):
                continue
            yield group

    def get_3_connected_groups(self) -> Iterable[Tuple[str, ...]]:
        """
        >>> print("\\n".join(sorted(map(",".join, Network.from_text(EXAMPLE_TEXT).get_3_connected_groups()))))
        aq,cg,yn
        aq,vc,wq
        co,de,ka
        co,de,ta
        co,ka,ta
        de,ka,ta
        kh,qp,ub
        qp,td,wh
        tb,vc,wq
        tc,td,wh
        td,wh,yn
        ub,vc,wq
        """
        for first, seconds in self.connections.items():
            for second in seconds:
                if second < first:
                    continue
                for third in self.connections[second]:
                    if third < second:
                        continue
                    if third not in seconds:
                        continue
                    yield first, second, third


EXAMPLE_TEXT = """
    kh-tc
    qp-kh
    de-cg
    ka-co
    yn-aq
    qp-ub
    cg-tb
    vc-aq
    tb-ka
    wh-tc
    yn-cg
    kh-ub
    ta-co
    de-co
    tc-td
    tb-wq
    wh-td
    ta-ka
    td-qp
    aq-cg
    wq-ub
    ub-vc
    de-ta
    wq-aq
    wq-vc
    wh-yn
    ka-de
    kh-ta
    co-tc
    wh-qp
    tb-vc
    td-yn
"""


Challenge.main()
challenge = Challenge()
