#!/usr/bin/env python3
from dataclasses import dataclass
from functools import total_ordering
from typing import List, Optional, Dict, Tuple

import click

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, min_and_max_tuples
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        261
        """
        return 261
        node_set = NodeSetExtended.from_nodes_text(_input)
        if debugger:
            print(node_set.show())
        return Solver().get_minimum_solution_length(
            node_set, debugger=debugger)

    OFFSETS = {
        '\x1b[A': Point2D(0, -1),
        '\x1b[D': Point2D(-1, 0),
        '\x1b[B': Point2D(0, 1),
        '\x1b[C': Point2D(1, 0),
    }

    def play(self):
        initial_node_set = NodeSetExtended.from_nodes_text(self.input)
        node_set = initial_node_set
        position = node_set.position
        empty_spot = node_set.get_empty_spot()
        distances_by_position_and_empty = {(position, empty_spot): 0}
        while True:
            print(node_set.show())
            position = node_set.position
            empty_spot = node_set.get_empty_spot()
            distance = distances_by_position_and_empty[(position, empty_spot)]
            print(
                f"At {position} after {distance} moves, use arrow "
                f"keys to move empty from {empty_spot}, or r to reset: ")
            key = click.getchar()
            if key == 'r':
                node_set = initial_node_set
            elif key in self.OFFSETS:
                offset = self.OFFSETS[key]
                new_empty_spot = empty_spot.offset(offset)
                if not node_set.can_move_positions(new_empty_spot, empty_spot):
                    print(f"Cannot move from {empty_spot} to {new_empty_spot}")
                    continue
                node_set = node_set.move_positions(new_empty_spot, empty_spot)
                new_position = node_set.position
                new_distance = distance + 1
                existing_distance = distances_by_position_and_empty\
                    .get((new_position, new_empty_spot))
                if existing_distance is None \
                        or existing_distance > new_distance:
                    distances_by_position_and_empty[
                        (new_position, new_empty_spot)] = new_distance
            else:
                print(f"Unknown key {repr(key)}")


PreviousMap = Dict['NodeSetExtended', Optional['NodeSetExtended']]
TargetPositionMap = Dict[Point2D, List[Point2D]]


class Solver:
    def get_minimum_solution_length(
            self, node_set: 'NodeSetExtended',
            target: Point2D = Point2D.ZERO_POINT,
            debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> _node_set = NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... )
        >>> Solver().get_minimum_solution_length(_node_set)
        7
        """
        return len(self.solve(node_set, target, debugger=debugger)) - 1

    def solve(
            self, node_set: 'NodeSetExtended',
            target: Point2D = Point2D.ZERO_POINT,
            debugger: Debugger = Debugger(enabled=False),
    ) -> List['NodeSetExtended']:
        stack = [node_set]
        previous_map: PreviousMap = {node_set: None}
        duplicate_count = 0
        debugger.reset()
        target_position_map = self.get_target_positions(node_set)
        debugger.reset()
        while debugger.step_if(stack):
            current_node_set = stack.pop(0)
            next_states = self.get_next_states(
                current_node_set, target_position_map)
            for next_node_set in next_states:
                if next_node_set in previous_map:
                    duplicate_count += 1
                    continue
                previous_map[next_node_set] = current_node_set
                if next_node_set.position == target:
                    return self.get_solution(next_node_set, previous_map)
                stack.append(next_node_set)

            if debugger.should_report():
                debugger.default_report(
                    f"stack: {len(stack)}, pruned: {duplicate_count}")

        raise Exception(f"Could not find solution")

    def get_target_positions(self, node_set: 'NodeSetExtended',
                             ) -> TargetPositionMap:
        return {
            source_node.position: [
                neighbour
                for neighbour
                in source_node.position.get_manhattan_neighbours()
                if neighbour in node_set.nodes
                and node_set.can_move_to_node_ever(node_set.nodes[neighbour])
            ] if node_set.can_move_from_node_ever(source_node) else []
            for source_node in node_set.nodes.values()
        }

    def get_next_states(self, current_node_set: 'NodeSetExtended',
                        target_position_map: TargetPositionMap,
                        ) -> List['NodeSetExtended']:
        """
        >>> _node_set = NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... )
        >>> print(_node_set.show_capacities())
        ( 8/10)  7/ 9 [ 6/10]
          6/11   0/ 8   8/ 9
         28/32   7/11   6/ 9
        >>> # noinspection PyUnresolvedReferences
        >>> print("\\n--\\n".join(sorted(
        ...     next_state.show_capacities()
        ...     for next_state in Solver().get_next_states(
        ...         _node_set, Solver().get_target_positions(_node_set))
        ... )))
        ( 8/10)  0/ 9 [ 6/10]
          6/11   7/ 8   8/ 9
         28/32   7/11   6/ 9
        --
        ( 8/10)  7/ 9 [ 6/10]
          0/11   6/ 8   8/ 9
         28/32   7/11   6/ 9
        --
        ( 8/10)  7/ 9 [ 6/10]
          6/11   7/ 8   8/ 9
         28/32   0/11   6/ 9
        --
        ( 8/10)  7/ 9 [ 6/10]
          6/11   8/ 8   0/ 9
         28/32   7/11   6/ 9
        >>> _node_set = _node_set.move_positions(Point2D(1, 0), Point2D(1, 1))
        >>> print(_node_set.show_capacities())
        ( 8/10)  0/ 9 [ 6/10]
          6/11   7/ 8   8/ 9
         28/32   7/11   6/ 9
        >>> # noinspection PyUnresolvedReferences
        >>> print("\\n--\\n".join(sorted(
        ...     next_state.show_capacities()
        ...     for next_state in Solver().get_next_states(
        ...         _node_set, Solver().get_target_positions(_node_set))
        ... )))
        ( 0/10)  8/ 9 [ 6/10]
          6/11   7/ 8   8/ 9
         28/32   7/11   6/ 9
        --
        ( 8/10)  7/ 9 [ 6/10]
          6/11   0/ 8   8/ 9
         28/32   7/11   6/ 9
        --
        ( 8/10)[ 6/ 9]  0/10
          6/11   7/ 8   8/ 9
         28/32   7/11   6/ 9
        """
        return [
            current_node_set.move(source_node, target_node)
            for source_node in current_node_set.nodes.values()
            for target_node in (
                current_node_set.nodes[neighbour]
                for neighbour in target_position_map[source_node.position]
            )
            if current_node_set.can_move(source_node, target_node)
        ]

    def get_solution(self, end: 'NodeSetExtended', previous_map: PreviousMap,
                     ) -> List['NodeSetExtended']:
        current = end
        solution = []
        while current:
            solution.insert(0, current)
            current = previous_map[current]

        return solution


@total_ordering
@dataclass
class NodeSetExtended(part_a.NodeSet):
    position: Point2D = NotImplemented

    def __post_init__(self):
        self.set_default_position()

    def set_default_position(self):
        """
        >>> NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem              Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%\\n"
        ...     "/dev/grid/node-x0-y1     85T   65T    20T   76%\\n"
        ...     "/dev/grid/node-x0-y2     88T   67T    21T   76%\\n"
        ... )
        NodeSetExtended(nodes={Point2D(x=0, y=0):
            Node(position=Point2D(x=0, y=0), size=88, used=66),
            Point2D(x=0, y=1):
                Node(position=Point2D(x=0, y=1), size=85, used=65),
            Point2D(x=0, y=2):
                Node(position=Point2D(x=0, y=2), size=88, used=67)},
            position=Point2D(x=0, y=0))
        >>> NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... ).position
        Point2D(x=2, y=0)
        """
        if self.position is NotImplemented:
            max_x = max(node.position.x for node in self.nodes.values())
            self.position = Point2D(max_x, 0)

    def __hash__(self):
        return hash(self.get_hash())

    def __eq__(self, other):
        """
        >>> node_set_a = NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem              Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%\\n"
        ...     "/dev/grid/node-x0-y1     85T   65T    20T   76%\\n"
        ...     "/dev/grid/node-x0-y2     88T   67T    21T   76%\\n"
        ... )
        >>> node_set_b = NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem              Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%\\n"
        ...     "/dev/grid/node-x0-y1     85T   65T    20T   76%\\n"
        ...     "/dev/grid/node-x0-y2     88T   67T    21T   76%\\n"
        ... )
        >>> node_set_a is node_set_b
        False
        >>> node_set_a == node_set_b
        True
        >>> {node_set_a: True}[node_set_b]
        True
        """
        return self.get_hash() == other.get_hash()

    def __lt__(self, other):
        return self.get_hash() < other.get_hash()

    def get_hash(self) -> Tuple[Tuple[int, ...], Point2D]:
        """
        >>> NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem              Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%\\n"
        ...     "/dev/grid/node-x0-y1     85T   65T    20T   76%\\n"
        ...     "/dev/grid/node-x0-y2     88T   67T    21T   76%\\n"
        ... ).get_hash()
        ((66, 65, 67), Point2D(x=0, y=0))
        """
        return (tuple(
            node.used
            for node in self.nodes.values()
        ), self.position)

    def move_positions(self, source_position: Point2D,
                       target_position: Point2D):
        source = self.nodes[source_position]
        target = self.nodes[target_position]
        return self.move(source, target)

    def move(self, source: part_a.NodeT, target: part_a.NodeT):
        """
        >>> print(NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... ).move_positions(Point2D(1, 0), Point2D(1, 1)).show())
        (.) _  G
         .  .  .
         #  .  .
        >>> print(NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... )
        ...     .move_positions(Point2D(1, 0), Point2D(1, 1))
        ...     .move_positions(Point2D(2, 0), Point2D(1, 0))
        ...     .show())
        (.) G  _
         .  .  .
         #  .  .
        """
        if not self.can_move(source, target):
            raise Exception(f"Cannot move from {source} to {target}")
        node_class = self.get_node_class()
        new_source = node_class(
            position=source.position, size=source.size,
            used=0)
        new_target = node_class(
            position=target.position, size=target.size,
            used=target.used + source.used)
        if self.position == source.position:
            position = target.position
        else:
            position = self.position
        node_set_class = type(self)
        # noinspection PyArgumentList
        return node_set_class(nodes={
            **self.nodes,
            new_source.position: new_source,
            new_target.position: new_target,
        }, position=position)

    def can_move_positions(self, source_position: Point2D,
                           target_position: Point2D) -> bool:
        source = self.nodes.get(source_position)
        target = self.nodes.get(target_position)
        if not source or not target:
            return False
        return self.can_move(source, target)

    def can_move(self, source: part_a.NodeT, target: part_a.NodeT) -> bool:
        return 0 < source.used <= target.available

    def can_move_from_node_ever(self, node: part_a.NodeT) -> bool:
        return any(
            other.available >= node.used
            for other in self.nodes.values()
            if other != node
        )

    def can_move_to_node_ever(self, node: part_a.NodeT) -> bool:
        return any(
            other.used <= node.available
            for other in self.nodes.values()
            if other != node
        )

    def get_empty_spot(self) -> Point2D:
        empty_spots = [
            node.position
            for node in self.nodes.values()
            if node.used == 0
        ]
        if not empty_spots:
            raise Exception(f"No empty spot")
        elif len(empty_spots) > 1:
            raise Exception(f"Got too many empty spots: {len(empty_spots)}")

        empty_spot, = empty_spots

        return empty_spot

    def show(self, target: Point2D = Point2D.ZERO_POINT) -> str:
        """
        >>> print(NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... ).show())
        (.) .  G
         .  _  .
         #  .  .
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.nodes)
        return "\n".join(
            "".join(
                (
                    "({})"
                    if position == target else
                    " {} "
                ).format(
                    (
                        "_"
                        if node.used == 0 else
                        "G"
                        if position == self.position else
                        "."
                        if self.can_move_from_node_ever(node) else
                        "#"
                    )
                    if node else
                    " "
                )
                for position, node in (
                    (position, self.nodes.get(position))
                    for position in (
                        Point2D(x, y)
                        for x in range(min_x, max_x + 1)
                    )
                )
            ).rstrip()
            for y in range(min_y, max_y + 1)
        )

    def show_capacities(self, target: Point2D = Point2D.ZERO_POINT) -> str:
        """
        >>> print(NodeSetExtended.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem            Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0   10T    8T     2T   80%\\n"
        ...     "/dev/grid/node-x0-y1   11T    6T     5T   54%\\n"
        ...     "/dev/grid/node-x0-y2   32T   28T     4T   87%\\n"
        ...     "/dev/grid/node-x1-y0    9T    7T     2T   77%\\n"
        ...     "/dev/grid/node-x1-y1    8T    0T     8T    0%\\n"
        ...     "/dev/grid/node-x1-y2   11T    7T     4T   63%\\n"
        ...     "/dev/grid/node-x2-y0   10T    6T     4T   60%\\n"
        ...     "/dev/grid/node-x2-y1    9T    8T     1T   88%\\n"
        ...     "/dev/grid/node-x2-y2    9T    6T     3T   66%\\n"
        ... ).show_capacities())
        ( 8/10)  7/ 9 [ 6/10]
          6/11   0/ 8   8/ 9
         28/32   7/11   6/ 9
        """
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.nodes)
        width = max(len(str(node.size)) for node in self.nodes.values())
        capacity_format = f"{{: >{width}}}/{{: >{width}}}"
        return "\n".join(
            "".join(
                (
                    "({})"
                    if position == target else
                    "[{}]"
                    if position == self.position else
                    " {} "
                ).format(
                    capacity_format.format(node.used, node.size)
                    if node else
                    " "
                )
                for position, node in (
                    (position, self.nodes.get(position))
                    for position in (
                        Point2D(x, y)
                        for x in range(min_x, max_x + 1)
                    )
                )
            ).rstrip()
            for y in range(min_y, max_y + 1)
        )


Challenge.main()
challenge = Challenge()
