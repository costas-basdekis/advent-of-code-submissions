#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from itertools import combinations
from typing import Generic, Type, Dict, List, Iterable, Tuple

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1034
        """
        return NodeSet.from_nodes_text(_input).get_viable_pair_count()


NodeT = TV['Node']


@dataclass
class NodeSet(Generic[NodeT]):
    nodes: Dict[Point2D, NodeT] = field(default_factory=dict)

    @classmethod
    def get_node_class(cls) -> Type[NodeT]:
        return get_type_argument_class(cls, NodeT)

    re_command = re.compile(r"^root@[^#]+# df -h$")
    re_header = re.compile(r"^Filesystem\s*Size\s*Used\s*Avail\s*Use%$")

    @classmethod
    def from_nodes_text(cls, nodes_text: str):
        """
        >>> NodeSet.from_nodes_text(
        ...     "root@ebhq-gridcenter# df -h\\n"
        ...     "Filesystem              Size  Used  Avail  Use%\\n"
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%\\n"
        ...     "/dev/grid/node-x0-y1     85T   65T    20T   76%\\n"
        ...     "/dev/grid/node-x0-y2     88T   67T    21T   76%\\n"
        ... )
        NodeSet(nodes={Point2D(x=0, y=0):
            Node(position=Point2D(x=0, y=0), size=88, used=66),
            Point2D(x=0, y=1):
                Node(position=Point2D(x=0, y=1), size=85, used=65),
            Point2D(x=0, y=2):
                Node(position=Point2D(x=0, y=2), size=88, used=67)})
        """
        command_str, header_str, *node_strs = nodes_text.splitlines()
        if not cls.re_command.match(command_str):
            raise Exception(
                f"Expected command input as first line but got '{command_str}'")
        if not cls.re_header.match(header_str):
            raise Exception(
                f"Expected header as first line but got '{header_str}'")
        node_class = cls.get_node_class()
        return cls.from_nodes(list(map(node_class.from_node_text, node_strs)))

    @classmethod
    def from_nodes(cls, nodes: List[NodeT]):
        """
        >>> NodeSet.from_nodes([
        ...     Node(position=Point2D(x=0, y=0), size=88, used=66),
        ...     Node(position=Point2D(x=0, y=1), size=85, used=65),
        ...     Node(position=Point2D(x=0, y=2), size=88, used=67),
        ... ])
        NodeSet(nodes={Point2D(x=0, y=0):
            Node(position=Point2D(x=0, y=0), size=88, used=66),
            Point2D(x=0, y=1):
                Node(position=Point2D(x=0, y=1), size=85, used=65),
            Point2D(x=0, y=2):
                Node(position=Point2D(x=0, y=2), size=88, used=67)})
        """
        return cls({
            node.position: node
            for node in nodes
        })

    def get_viable_pair_count(self) -> int:
        return helper.iterable_length(self.get_viable_pairs())

    def get_viable_pairs(self) -> Iterable[Tuple[NodeT, NodeT]]:
        return (
            pair
            for pair in combinations(sorted(self.nodes.values()), 2)
            if self.is_node_pair_viable(*pair)
        )

    def is_node_pair_viable(self, lhs: NodeT, rhs: NodeT,
                            recurse: bool = True) -> bool:
        """
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 66), Node(Point2D(0, 0), 88, 66))
        False
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 22), Node(Point2D(0, 0), 88, 22))
        False
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 22), Node(Point2D(1, 1), 88, 22))
        True
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 22), Node(Point2D(1, 1), 88, 66))
        True
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 22), Node(Point2D(1, 1), 10, 2))
        True
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 0), Node(Point2D(1, 1), 10, 2))
        True
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 88, 22), Node(Point2D(1, 1), 10, 0))
        False
        >>> NodeSet().is_node_pair_viable(
        ...     Node(Point2D(0, 0), 10, 0), Node(Point2D(1, 1), 88, 22))
        False
        """
        if lhs == rhs:
            return False
        if lhs.used == 0:
            if not recurse:
                return False
            return self.is_node_pair_viable(rhs, lhs, recurse=False)
        if lhs.used > rhs.available:
            if not recurse:
                return False
            return self.is_node_pair_viable(rhs, lhs, recurse=False)
        return True


@dataclass(eq=True, frozen=True, order=True)
class Node:
    position: Point2D
    size: int
    used: int

    re_node = re.compile(
        r"^/dev/grid/node-x(\d+)-y(\d+)\s*(\d+)T\s*(\d+)T\s*\d+T\s*\d+%$")

    @classmethod
    def from_node_text(cls, node_text: str):
        """
        >>> Node.from_node_text(
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%")
        Node(position=Point2D(x=0, y=0), size=88, used=66)
        """
        x_str, y_str, size_str, used_str = cls.re_node.match(node_text).groups()
        return cls(
            Point2D(int(x_str), int(y_str)), int(size_str), int(used_str))

    @property
    def available(self) -> int:
        """
        >>> Node.from_node_text(
        ...     "/dev/grid/node-x0-y0     88T   66T    22T   75%").available
        22
        """
        return self.size - self.used


Challenge.main()
challenge = Challenge()
