#!/usr/bin/env python3
from typing import Dict, Iterable, List, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, lcm
from year_2023.day_08.part_a import Network, Node


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        9606140307013
        """
        network = NetworkExtended.from_network_text(_input)
        return network.get_simultaneous_step_count()
        # return str([
        #     network.get_step_count_to_final_node(node)
        #     for node in network.get_initial_nodes()
        # ])


class NetworkExtended(Network[Node]):
    nodes: Dict[str, Node]

    def get_simultaneous_step_count(self) -> int:
        """
        >>> network = NetworkExtended.from_network_text('''
        ...     LR
        ...
        ...     11A = (11B, XXX)
        ...     11B = (XXX, 11Z)
        ...     11Z = (11B, XXX)
        ...     22A = (22B, XXX)
        ...     22B = (22C, 22C)
        ...     22C = (22Z, 22Z)
        ...     22Z = (22B, 22B)
        ...     XXX = (XXX, XXX)
        ... ''')
        >>> network.get_simultaneous_step_count()
        6
        """
        step_counts = list(map(
            self.get_step_count_to_final_node, self.get_initial_nodes(),
        ))
        return lcm(*step_counts)

    # def get_step_counts_to_final_node(
    #     self, node: Union[Node, str],
    # ) -> List[int]:
    #     counts = []
    #     current = node
    #     next_direction_index = 0
    #     while True:
    #         count, current, next_direction_index = \
    #             self.get_step_count_to_final_node(current, next_direction_index)
    #         seen_before = any(
    #             count % previous_count == 0
    #             and next_direction_index == previous_next_direction_index
    #             for previous_count, previous_next_direction_index in counts
    #         )
    #         if seen_before:
    #             break
    #         counts.append(count)
    #     return counts

    def get_step_count_to_final_node(self, node: Union[Node, str]) -> int:
        for count in self.get_step_counts_to_final_node(node):
            return count

    def get_step_counts_to_final_node(
        self, node: Union[Node, str],
    ) -> Iterable[int]:
        if isinstance(node, str):
            node = self[node]
        current = node
        count = 0
        next_direction_index = 0
        directions = self.directions
        direction_count = len(directions)
        seen: Set[Tuple[str, int]] = set()
        seen_count = 0
        while True:
            next_direction = directions[next_direction_index]
            current = current[next_direction]
            count += 1
            next_direction_index = \
                (next_direction_index + 1) % direction_count
            if self.is_node_final(current):
                seen_count += 1
                key = current.name, next_direction_index
                if key in seen:
                    break
                seen.add(key)
                yield count

    def get_initial_nodes(self) -> List[Node]:
        return list(filter(self.is_node_initial, self.nodes.values()))

    def is_node_initial(self, node: Node) -> bool:
        return node.name.endswith("A")

    def is_node_final(self, node: Node) -> bool:
        return node.name.endswith("Z")


Challenge.main()
challenge = Challenge()
