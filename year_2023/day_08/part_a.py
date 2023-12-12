#!/usr/bin/env python3
from dataclasses import dataclass
import re
from enum import Enum
from typing import cast, Dict, Generic, List, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        19241
        """
        return Network.from_network_text(_input).get_step_count("AAA", "ZZZ")


NodeT = TV["Node"]


@dataclass
class Network(Generic[NodeT]):
    directions: List["Direction"]
    nodes: Dict[str, NodeT]

    @classmethod
    def get_node_class(cls) -> Type[NodeT]:
        return cast(Type[NodeT], get_type_argument_class(cls, NodeT))

    @classmethod
    def from_network_text(cls, network_text: str) -> "Network":
        """
        >>> Network.from_network_text('''
        ...     RL
        ...
        ...     AAA = (BBB, CCC)
        ...     BBB = (DDD, EEE)
        ...     CCC = (ZZZ, GGG)
        ...     DDD = (DDD, DDD)
        ...     EEE = (EEE, EEE)
        ...     GGG = (GGG, GGG)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        Network(directions=[Direction.Right, Direction.Left],
            nodes={'AAA': Node(name='AAA', left='BBB', right='CCC',
            network=...), ...})
        """
        directions_str, nodes_str = network_text.strip().split("\n\n")
        node_class = cls.get_node_class()
        network = cls(Direction.from_directions_text(directions_str), {})
        network.nodes.update({
            node.name: node
            for node_text in nodes_str.splitlines()
            for node in [node_class.from_node_text(node_text, network)]
        })
        return network

    def __getitem__(self, item: str) -> NodeT:
        return self.nodes[item]

    def get_step_count(
        self, start: Union[str, NodeT], target: Union[str, NodeT],
    ) -> int:
        if isinstance(start, str):
            start = self[start]
        return start.get_step_count(target)


class Direction(Enum):
    Left = "L"
    Right = "R"

    @classmethod
    def from_directions_text(cls, directions_text: str) -> List["Direction"]:
        """
        >>> Direction.from_directions_text("LR")
        [Direction.Left, Direction.Right]
        """
        direction_map = {"L": cls.Left, "R": cls.Right}
        return list(map(direction_map.__getitem__, directions_text.strip()))

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


@dataclass
class Node:
    name: str
    left: str
    right: str
    network: Network

    re_node = re.compile(r"([A-Z]+) = \(([A-Z]+), ([A-Z]+)\)")

    @classmethod
    def from_node_text(cls, node_text: str, network: Network) -> "Node":
        """
        >>> Node.from_node_text("AAA = (BBB, CCC)", Network([], {}))
        Node(name='AAA', left='BBB', right='CCC', network=...)
        """
        match = cls.re_node.match(node_text.strip())
        if not match:
            raise Exception(f"Could not parse node '{node_text}'")
        name, left, right = match.groups()
        return cls(name, left, right, network)

    @property
    def left_node(self) -> "Node":
        """
        >>> network = Network.from_network_text('''
        ...     RL
        ...
        ...     AAA = (BBB, CCC)
        ...     BBB = (DDD, EEE)
        ...     CCC = (ZZZ, GGG)
        ...     DDD = (DDD, DDD)
        ...     EEE = (EEE, EEE)
        ...     GGG = (GGG, GGG)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        >>> network["AAA"].left_node
        Node(name='BBB', ...)
        """
        return self.network[self.left]

    @property
    def right_node(self) -> "Node":
        """
        >>> network = Network.from_network_text('''
        ...     RL
        ...
        ...     AAA = (BBB, CCC)
        ...     BBB = (DDD, EEE)
        ...     CCC = (ZZZ, GGG)
        ...     DDD = (DDD, DDD)
        ...     EEE = (EEE, EEE)
        ...     GGG = (GGG, GGG)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        >>> network["AAA"].right_node
        Node(name='CCC', ...)
        """
        return self.network[self.right]

    def __getitem__(self, item: Direction) -> "Node":
        """
        >>> network = Network.from_network_text('''
        ...     RL
        ...
        ...     AAA = (BBB, CCC)
        ...     BBB = (DDD, EEE)
        ...     CCC = (ZZZ, GGG)
        ...     DDD = (DDD, DDD)
        ...     EEE = (EEE, EEE)
        ...     GGG = (GGG, GGG)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        >>> network["AAA"][Direction.Left]
        Node(name='BBB', ...)
        """
        if not isinstance(item, Direction):
            raise Exception(
                f"Expected a Direction but got {type(item).__name__}"
            )
        if item == Direction.Left:
            return self.left_node
        else:
            return self.right_node

    def get_step_count(self, target: Union[str, "Node"]) -> int:
        """
        >>> network = Network.from_network_text('''
        ...     LLR
        ...
        ...     AAA = (BBB, BBB)
        ...     BBB = (AAA, ZZZ)
        ...     ZZZ = (ZZZ, ZZZ)
        ... ''')
        >>> network["AAA"].get_step_count(network["AAA"])
        0
        >>> network["AAA"].get_step_count("ZZZ")
        6
        """
        if isinstance(target, str):
            target = self.network[target]
        current = self
        count = 0
        next_direction_index = 0
        directions = self.network.directions
        direction_count = len(directions)
        while current != target:
            next_direction = directions[next_direction_index]
            current = current[next_direction]
            count += 1
            next_direction_index = (next_direction_index + 1) % direction_count
        return count


Challenge.main()
challenge = Challenge()
