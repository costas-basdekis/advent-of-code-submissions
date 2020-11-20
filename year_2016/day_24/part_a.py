#!/usr/bin/env python3
import itertools
import string
from dataclasses import dataclass
from typing import Set, Dict, Tuple, Optional, Iterable, TypeVar

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples, \
    all_possible_permutations, get_windows


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        502
        """
        layout = Layout.from_layout_text(_input)
        graph = layout.to_graph()
        if debugger:
            print(graph.show())
        return graph.get_minimum_step_count(debugger=debugger)


T = TypeVar('T')


@dataclass
class Graph:
    edges: Dict[Tuple[int, int], int]

    def get_minimum_step_count(self, start: int = 0,
                               return_to_start: bool = False,
                               debugger: Debugger = Debugger(enabled=False),
                               ) -> int:
        """
        >>> Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8, (4, 3): 8,
        ... }).get_minimum_step_count()
        14
        """
        nodes = self.get_nodes()
        if start not in nodes:
            raise Exception(f"Start {start} is not in nodes {nodes}")
        other_nodes = set(nodes) - {start}
        prefix = (start,)
        if return_to_start:
            suffix = prefix
        else:
            suffix = ()
        visit_orders = (
            prefix + permutation + suffix
            for permutation in itertools.permutations(other_nodes)
        )
        min_distance = None
        trip_distances_cache = {}
        for visit_order in debugger.stepping(visit_orders):
            distance = sum(
                self.get_shortest_distance(
                    node_a, node_b, nodes,
                    trip_distances_cache=trip_distances_cache)
                for node_a, node_b in get_windows(visit_order, 2)
            )
            if min_distance is None or distance < min_distance:
                min_distance = distance
            if debugger.should_report():
                debugger.default_report(f"min distance: {min_distance}")

        return min_distance

    def get_shortest_distance(self, start: int, end: int,
                              nodes: Optional[Set[int]] = None,
                              trip_distances_cache:
                              Optional[Dict[Tuple[int, ...], int]] = None,
                              ) -> Optional[int]:
        shortest_trip, shortest_distance = \
            self.get_shortest_trip_and_distance(
                start, end, nodes, trip_distances_cache=trip_distances_cache)
        if shortest_trip is None:
            return None

        return shortest_distance

    def get_shortest_trip_and_distance(self, start: int, end: int,
                                       nodes: Optional[Set[int]] = None,
                                       trip_distances_cache:
                                       Optional[Dict[Tuple[int, ...], int]]
                                       = None,
                                       ) -> Optional[Tuple[int, ...]]:
        """
        >>> graph = Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8, (4, 3): 8,
        ... })
        >>> graph.get_shortest_trip_and_distance(0, 1)
        ((0, 1), 2)
        """
        possible_trips_and_distances = \
            self.get_all_possible_trips_and_distances(
                start, end, nodes, trip_distances_cache=trip_distances_cache)
        return min(
            possible_trips_and_distances,
            key=lambda trip_and_distance: trip_and_distance[1],
            default=None,
        )

    def get_all_possible_trips_and_distances(
            self, start: int, end: int, nodes: Optional[Set[int]] = None,
            trip_distances_cache: Optional[Dict[Tuple[int, ...], int]] = None,
    ) -> Iterable[Tuple[Tuple[int, ...], int]]:
        """
        >>> sorted(Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8, (4, 3): 8,
        ... }).get_all_possible_trips_and_distances(0, 1))
        [((0, 1), 2), ((0, 4, 3, 2, 1), 18)]
        """
        trips = self.get_all_trips(start, end, nodes)
        trips_and_distances = (
            (trip, self.get_trip_distance(
                trip, trip_distances_cache=trip_distances_cache))
            for trip in trips
        )
        return (
            (trip, distance)
            for trip, distance in trips_and_distances
            if distance is not None
        )

    def get_all_trips(self, start: int, end: int,
                      nodes: Optional[Set[int]] = None,
                      ) -> Iterable[Tuple[int, ...]]:
        """
        >>> sorted(Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8, (4, 3): 8,
        ... }).get_all_trips(0, 1))
        [(0, 1), (0, 2, 1), (0, 2, 3, 1), (0, 2, 3, 4, 1), (0, 2, 4, 1),
            (0, 2, 4, 3, 1), (0, 3, 1), (0, 3, 2, 1), (0, 3, 2, 4, 1),
            (0, 3, 4, 1), (0, 3, 4, 2, 1), (0, 4, 1), (0, 4, 2, 1),
            (0, 4, 2, 3, 1), (0, 4, 3, 1), (0, 4, 3, 2, 1)]
        """
        if nodes is None:
            nodes = self.get_nodes()
        if start not in nodes or end not in nodes:
            raise Exception(f"Either {start} or {end} are not nodes: {nodes}")
        other_nodes = sorted(nodes - {start, end})
        return (
            (start,) + partial_trip + (end,)
            for partial_trip in all_possible_permutations(other_nodes)
        )

    def get_trip_distance(
            self, trip: Iterable[int],
            trip_distances_cache: Optional[Dict[Tuple[int, ...], int]] = None,
    ) -> Optional[int]:
        """
        >>> Graph({}).get_trip_distance(())
        >>> Graph({}).get_trip_distance((1,))
        >>> Graph({}).get_trip_distance((1, 2))
        >>> Graph({(1, 3): 3, (3, 2): 4}).get_trip_distance((1, 2))
        >>> Graph({(2, 1): 3}).get_trip_distance((1, 2))
        >>> Graph({(1, 2): 3}).get_trip_distance((1, 2))
        3
        >>> Graph({(1, 2): 3, (2, 4): 4}).get_trip_distance((1, 2, 3))
        >>> Graph({(1, 2): 3, (3, 2): 4}).get_trip_distance((1, 2, 3))
        >>> Graph({}).get_trip_distance((1, 2, 3))
        >>> Graph({(1, 2): 3, (2, 3): 4}).get_trip_distance((1, 2, 3))
        7
        """
        if trip_distances_cache is None:
            trip_distances_cache = {}
        if trip in trip_distances_cache:
            return trip_distances_cache[trip]
        total_distance = 0
        at_least_2_nodes = False
        for pair in get_windows(trip, 2):
            pair: Tuple[int, int]
            distance = self.edges.get(pair)
            if distance is None:
                trip_distances_cache[trip] = None
                return None
            at_least_2_nodes = True
            total_distance += distance

        if not at_least_2_nodes:
            trip_distances_cache[trip] = None
            return None

        trip_distances_cache[trip] = total_distance
        return total_distance

    def is_bidirectional(self) -> bool:
        """
        >>> Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8, (4, 3): 8,
        ... }).is_bidirectional()
        True
        >>> Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8,
        ... }).is_bidirectional()
        False
        """
        return all(
            (node_b, node_a) in self.edges
            for node_a, node_b in self.edges
        )

    def show(self) -> str:
        """
        >>> print(Graph({
        ...     (0, 1): 2, (1, 0): 2,
        ...     (0, 4): 2, (4, 0): 2,
        ...     (1, 2): 6, (2, 1): 6,
        ...     (2, 3): 2, (3, 2): 2,
        ...     (3, 4): 8, (4, 3): 8,
        ... }).show())
          0 1 2 3 4
        0   2     2
        1 2   6
        2   6   2
        3     2   8
        4 2     8
        """
        if not self.edges:
            return ""
        nodes = sorted(self.get_nodes())
        max_distance = max(self.edges.values())
        max_distance_str_length = len(str(max_distance))
        distance_template = f"{{: >{max_distance_str_length}}}"
        return "{}\n{}".format(
            "  {}".format(
                " ".join(
                    distance_template.format(node_b)
                    for node_b in nodes
                ),
            ).rstrip(),
            "\n".join(
                "{} {}".format(
                    node_a,
                    " ".join(
                        distance_template.format(
                            self.edges.get((node_a, node_b), ''))
                        for node_b in nodes
                    ).rstrip(),
                )
                for node_a in nodes
            ),
        )

    def get_nodes(self) -> Set[int]:
        return {
            node
            for nodes in self.edges
            for node in nodes
        }


@dataclass
class Layout:
    spaces: Set[Point2D]
    locations: Dict[int, Point2D]

    @classmethod
    def from_layout_text(cls, layout_text: str):
        """
        >>> Layout.from_layout_text(
        ...     "###########\\n"
        ...     "#0.1.....2#\\n"
        ...     "#.#######.#\\n"
        ...     "#4.......3#\\n"
        ...     "###########\\n"
        ... )
        Layout(spaces={...}, locations={0: Point2D(x=1, y=1),
            1: Point2D(x=3, y=1), 2: Point2D(x=9, y=1),
            4: Point2D(x=1, y=3), 3: Point2D(x=9, y=3)})
        """
        spaces = set()
        locations = {}
        for y, row in enumerate(layout_text.splitlines()):
            for x, content in enumerate(row):
                position = Point2D(x, y)
                if content == "#":
                    continue
                elif content == ".":
                    spaces.add(position)
                    continue
                elif content in string.digits:
                    spaces.add(position)
                    location = int(content)
                    if location in locations:
                        raise Exception(
                            f"Location {location} was specified twice: once in "
                            f"{locations[location]} and once in {position}")
                    locations[location] = position
                else:
                    raise Exception(
                        f"Unknown content '{content}' at {position}")

        return cls(spaces, locations)

    def to_graph(self) -> Graph:
        """
        >>> print(Layout.from_layout_text(
        ...     "###########\\n"
        ...     "#0.1.....2#\\n"
        ...     "#.#######.#\\n"
        ...     "#4.......3#\\n"
        ...     "###########\\n"
        ... ).to_graph().show())
          0 1 2 3 4
        0   2     2
        1 2   6
        2   6   2
        3     2   8
        4 2     8
        >>> print(Layout.from_layout_text(
        ...     "#####\\n"
        ...     "#0.1#\\n"
        ...     "#.#.#\\n"
        ...     "#2..#\\n"
        ...     "#####\\n"
        ... ).to_graph().show())
          0 1 2
        0   2 2
        1 2   4
        2 2 4
        """
        total_edges = {}
        for location in self.locations:
            edges, _ = self.traverse_layout(location)
            for edge, distance in edges.items():
                existing_distance = total_edges.get(edge)
                if existing_distance is None or distance < existing_distance:
                    total_edges[edge] = distance
        return Graph(total_edges)

    def traverse_layout(self, start: int = 0,
                        ) -> Tuple[Dict[Tuple[int, int], int], Set[Point2D]]:
        """
        >>> sorted(map(tuple, Layout.from_layout_text(
        ...     "#####\\n"
        ...     "#0.1#\\n"
        ...     "#.#.#\\n"
        ...     "#2..#\\n"
        ...     "#####\\n"
        ... ).traverse_layout()[1]))
        [(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)]
        """
        edges = {}
        start_position = self.locations[start]
        stack = [(start_position, start_position, 0)]
        seen = {start_position}
        reverse_locations = self.get_reverse_locations()
        while stack:
            position, source_position, distance = stack.pop(0)
            source_location = reverse_locations[source_position]
            for neighbour in position.get_manhattan_neighbours():
                if neighbour not in self.spaces:
                    continue
                if neighbour == source_position:
                    continue

                new_position = neighbour
                if new_position in reverse_locations:
                    new_location = reverse_locations[new_position]
                    edges[(source_location, new_location)] = \
                        edges[(new_location, source_location)] = distance + 1
                    new_source_position = new_position
                    new_distance = 0
                else:
                    new_source_position = source_position
                    new_distance = distance + 1

                if new_position in seen:
                    continue
                seen.add(new_position)
                stack.append((new_position, new_source_position, new_distance))

        return edges, seen

    def show(self) -> str:
        """
        >>> print(Layout.from_layout_text(
        ...     "###########\\n"
        ...     "#0.1.....2#\\n"
        ...     "#.#######.#\\n"
        ...     "#4.......3#\\n"
        ...     "###########\\n"
        ... ).show())
        ###########
        #0.1.....2#
        #.#######.#
        #4.......3#
        ###########
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.spaces)
        reverse_locations = self.get_reverse_locations()
        return "\n".join(
            "".join(
                str(reverse_locations[position])
                if position in reverse_locations else
                "."
                if position in self.spaces else
                "#"
                for position in (
                    Point2D(x, y)
                    for x in range(min_x - 1, max_x + 2)
                )
            )
            for y in range(min_y - 1, max_y + 2)
        )

    def get_reverse_locations(self):
        return {
            position: location
            for location, position in self.locations.items()
        }


Challenge.main()
challenge = Challenge()
