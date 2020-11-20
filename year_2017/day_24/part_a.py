#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Dict, Tuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1868
        """
        return Graph.from_graph_text(_input).find_longest_path(debug=debug)


@dataclass
class Graph:
    weights: Dict[Tuple[int, int], int]

    @classmethod
    def from_graph_text(cls, graph_text):
        """
        >>> Graph.from_graph_text(
        ...     "0/2\\n"
        ...     "2/2\\n"
        ...     "2/3\\n"
        ...     "3/4\\n"
        ...     "3/5\\n"
        ...     "0/1\\n"
        ...     "10/1\\n"
        ...     "9/10\\n"
        ... )
        Graph(weights={(0, 2): 2, (2, 0): 2, ...})
        """
        lines = graph_text.strip().splitlines()
        edges_list = list(map(cls.parse_edge, lines))
        duplicate_pairs = {
            pair
            for pair, items in utils.helper.group_by(
                pair
                for node_a, node_b, _ in edges_list
                for pair in {(node_a, node_b), (node_b, node_a)}
            ).items()
            if len(items) > 1
        }
        if duplicate_pairs:
            raise Exception(
                f"Some edges are represented multiple times: "
                f"{sorted(duplicate_pairs)}")
        weights = {
            pair: weight
            for node_a, node_b, weight in edges_list
            for pair in {(node_a, node_b), (node_b, node_a)}
        }

        return cls(weights)

    re_edge = re.compile(r"^(\d+)/(\d+)$")

    @classmethod
    def parse_edge(cls, line):
        node_a_str, node_b_str = cls.re_edge.match(line).groups()
        node_a, node_b = int(node_a_str), int(node_b_str)

        return node_a, node_b, node_a + node_b

    def find_longest_path(self, start=0, debug=False):
        return max(self.get_distances(start, debug=debug).values())

    def get_distances(self, start=0, debug=False):
        distances = {}
        stack = [(start, 0, dict(self.weights), ())]
        if debug:
            max_distance, max_path = 0, None
        while stack:
            position, distance, remaining_weights, path = stack.pop(0)
            if debug:
                if distance > max_distance:
                    max_distance, max_path = distance, path
            next_positions = {
                node_b: distance + weight
                for (node_a, node_b), weight in remaining_weights.items()
                if node_a == position
            }
            for next_position, next_distance in next_positions.items():
                distances[next_position] = \
                    max(distances.get(next_position, 0), next_distance)
                next_path = path + ((position, next_position),)
                next_remaining_weights = dict(remaining_weights)
                del next_remaining_weights[(position, next_position)]
                if next_position != position:
                    del next_remaining_weights[(next_position, position)]
                stack.append(
                    (next_position, next_distance, next_remaining_weights,
                     next_path))

        if debug:
            print(max_path, max_distance)

        return distances


challenge = Challenge()
challenge.main()
