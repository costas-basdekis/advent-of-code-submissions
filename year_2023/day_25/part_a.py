#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union

import pyperclip

from aox.challenge import Debugger
from utils import BaseChallenge, product


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        544523
        """
        return Apparatus.from_text(_input)\
            .get_size_product_of_3_connection_components()

    def play(self):
        example_text = """
        jqt: rhn xhk nvd
        rsh: frs pzl lsr
        xhk: hfx
        cmg: qnr nvd lhk bvb
        rhn: xhk bvb hfx
        bvb: xhk hfx
        pzl: lsr hfx nvd
        qnr: nvd
        ntq: jqt hfx bvb xhk
        nvd: lhk
        lsr: lhk
        rzs: qnr cmg lsr rsh
        frs: qnr lhk lsr
        """
        apparatus = Apparatus.from_text(example_text)
        critical_connections = apparatus.find_3_critical_connections()
        print(critical_connections)

    def copy_graph(self, apparatus: "Apparatus") -> None:
        graph = "\n".join([
            f"{left} -> {', '.join(actual_rights)};"
            for left, rights in apparatus.connections.items()
            for actual_rights in [[right for right in rights if left < right]]
            if actual_rights
        ])
        pyperclip.copy(graph)
        print(f"Copied {len(graph)} characters to clipboard")
        print("Visit https://dreampuf.github.io/GraphvizOnline/")

    def print_distance_differences(self, apparatus: "Apparatus") -> None:
        item = min(apparatus.connections)
        original_distances = apparatus.get_distances(item)
        connections = {
            (left, right)
            for left, rights in apparatus.connections.items()
            for right in rights
            if left < right
        }
        distance_differences = {}
        for connection in connections:
            new_apparatus = apparatus.cut([connection])
            new_distances = new_apparatus.get_distances(item)
            for other, distance in original_distances.items():
                if other not in new_distances:
                    new_distance = 1000000
                else:
                    new_distance = new_distances[other]
                distance_difference = new_distance - distance
                if other not in distance_differences:
                    distance_differences[other] = (connection, distance_difference)
                else:
                    _, best_distance_difference = distance_differences[other]
                    if distance_difference > best_distance_difference:
                        distance_differences[other] = (connection, distance_difference)
        print(item)
        for other, (connection, distance_difference) in distance_differences.items():
            print(f" * To {other} removing {connection} changes {original_distances[other]} -> {original_distances[other] + distance_difference}")


@dataclass
class Apparatus:
    connections: Dict[str, Set[str]]

    @classmethod
    def from_text(cls, text: str) -> "Apparatus":
        connections = {}
        for line in text.strip().splitlines():
            left, rights = line.strip().split(": ")
            for right in rights.split(" "):
                connections.setdefault(left, set()).add(right)
                connections.setdefault(right, set()).add(left)
        return cls(connections=connections)

    def cut(self, connections: List[Tuple[str, str]]) -> "Apparatus":
        bilateral_connections = {
            connection
            for left, right in connections
            for connection in [(left, right), (right, left)]
        }
        cls = type(self)
        # noinspection PyArgumentList
        return cls(connections={
            left: {
                right
                for right in rights
                if (left, right) not in bilateral_connections
            }
            for left, rights in self.connections.items()
        })

    def get_components(self) -> List["Apparatus"]:
        """
        >>> _components = Apparatus.from_text('''
        ...     jqt: rhn xhk nvd
        ...     rsh: frs pzl lsr
        ...     xhk: hfx
        ...     cmg: qnr nvd lhk bvb
        ...     rhn: xhk bvb hfx
        ...     bvb: xhk hfx
        ...     pzl: lsr hfx nvd
        ...     qnr: nvd
        ...     ntq: jqt hfx bvb xhk
        ...     nvd: lhk
        ...     lsr: lhk
        ...     rzs: qnr cmg lsr rsh
        ...     frs: qnr lhk lsr
        ... ''').cut([('hfx', 'pzl'), ('bvb', 'cmg'), ('nvd', 'jqt')]).get_components()
        >>> sorted(len(component.connections) for component in _components)
        [6, 9]
        """
        remaining = {
            item
            for left, rights in self.connections.items()
            for items in [{left}, rights]
            for item in items
        }
        components = []
        while remaining:
            stack = [min(remaining)]
            component = {stack[0]}
            while stack:
                item = stack.pop(0)
                next_items = self.connections.get(item, set()) & remaining
                remaining -= next_items
                stack.extend(next_items)
                component.update(next_items)
            components.append(Apparatus(connections={
                item: self.connections.get(item, set()) & component
                for item in component
            }))
        return components

    def get_shortest_path_to_furthest_node(self, start: str) -> List[str]:
        path_map, distances = self.get_path_map_and_distances(start)
        max_distance, furthest_node = max(
            (distance, node)
            for node, distance in distances.items()
        )
        path = [furthest_node]
        while path[0] in path_map:
            path.insert(0, path_map[path[0]])
        return path

    def get_path(self, start: str, end: str) -> Optional[List[str]]:
        path_map, _ = self.get_path_map_and_distances(start)
        if end not in path_map:
            return None
        path = [end]
        while path[0] in path_map:
            path.insert(0, path_map[path[0]])
        return path

    def find_critical_connection_in_path(self, path: List[str]) -> Optional[Tuple[str, str]]:
        for connection in zip(path, path[1:]):
            next_apparatus = self.cut([connection])
            path = next_apparatus.get_path(path[0], path[-1])
            if not path:
                return connection
        return None

    def get_size_product_of_3_connection_components(self) -> int:
        """
        >>> Apparatus.from_text('''
        ...     jqt: rhn xhk nvd
        ...     rsh: frs pzl lsr
        ...     xhk: hfx
        ...     cmg: qnr nvd lhk bvb
        ...     rhn: xhk bvb hfx
        ...     bvb: xhk hfx
        ...     pzl: lsr hfx nvd
        ...     qnr: nvd
        ...     ntq: jqt hfx bvb xhk
        ...     nvd: lhk
        ...     lsr: lhk
        ...     rzs: qnr cmg lsr rsh
        ...     frs: qnr lhk lsr
        ... ''').get_size_product_of_3_connection_components()
        54
        """
        critical_connections = self.find_3_critical_connections()
        components = self.cut(critical_connections).get_components()
        if len(components) < 2:
            raise Exception(
                f"Expected to get at least 2 components "
                f"after cutting {', '.join(map(' ->'.join, critical_connections))}, "
                f"but got {len(critical_connections)}"
            )
        return product(len(component.connections) for component in components)

    def find_3_critical_connections(self) -> List[Tuple[str, str]]:
        start = min(self.connections)
        path_1 = self.get_shortest_path_to_furthest_node(start)
        end = path_1[-1]
        apparatus_1 = self.cut(list(zip(path_1, path_1[1:])))
        path_2 = apparatus_1.get_path(start, end)
        if not path_2:
            raise Exception(f"Could not find 2nd path from {start} to {end}")
        apparatus_2 = apparatus_1.cut(list(zip(path_2, path_2[1:])))
        path_3 = apparatus_2.get_path(start, end)
        if not path_3:
            raise Exception(f"Could not find 3rd path from {start} to {end}")
        apparatus_3 = apparatus_2.cut(list(zip(path_3, path_3[1:])))
        path_4 = apparatus_3.get_path(start, end)
        if path_4:
            raise Exception(f"Found more than 3 paths from {start} to {end}")
        # print(f"Found exactly 3 paths from {start} to {end}")
        # for path in [path_1, path_2, path_3]:
        #     print(f" * {' -> '.join(path)}")
        critical_connection_3 = apparatus_2.find_critical_connection_in_path(path_3)
        if not critical_connection_3:
            raise Exception(f"Could not find a critical connections in path {' -> '.join(path_3)}")
        # print(f"Connection {' -> '.join(critical_connection_3)} is critical")
        apparatus_with_2 = apparatus_1.cut([critical_connection_3])
        critical_connection_2 = apparatus_with_2.find_critical_connection_in_path(path_2)
        if not critical_connection_2:
            raise Exception(f"Could not find a critical connections in path {' -> '.join(path_2)}")
        # print(f"Connection {' -> '.join(critical_connection_2)} is critical")
        apparatus_with_1 = self.cut([critical_connection_2, critical_connection_3])
        critical_connection_1 = apparatus_with_1.find_critical_connection_in_path(path_1)
        if not critical_connection_1:
            raise Exception(f"Could not find a critical connections in path {' -> '.join(path_1)}")
        # print(f"Connection {' -> '.join(critical_connection_1)} is critical")
        return [critical_connection_1, critical_connection_2, critical_connection_3]

    def get_distances(self, start: str) -> Dict[str, int]:
        _, distances = self.get_path_map_and_distances(start)
        return distances

    def get_path_map(self, start: str) -> Dict[str, str]:
        path_map, _ = self.get_path_map_and_distances(start)
        return path_map

    def get_path_map_and_distances(self, start: str) -> Tuple[Dict[str, str], Dict[str, int]]:
        distances = {start: 0}
        path_map = {}
        stack = [start]
        while stack:
            item = stack.pop(0)
            next_items = self.connections.get(item, set()) - set(distances)
            for next_item in next_items:
                path_map[next_item] = item
                distances[next_item] = distances[item] + 1
            stack.extend(next_items)
        return path_map, distances


Challenge.main()
challenge = Challenge()
