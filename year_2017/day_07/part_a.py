#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'airlri'
        """
        return Node.from_nodes_text(_input).name


@dataclass
class Node:
    name: str
    weight: int
    children: List['Node']
    parent: Optional['Node']

    re_node = re.compile(r'^(\w+) \((\d+)\)(?: -> (\w+(?:, \w+)*))?$')

    @classmethod
    def from_nodes_text(cls, nodes_text):
        """
        >>> Node.from_nodes_text(
        ...     "pbga (66)\\n"
        ...     "xhth (57)\\n"
        ...     "ebii (61)\\n"
        ...     "havc (66)\\n"
        ...     "ktlj (57)\\n"
        ...     "fwft (72) -> ktlj, cntj, xhth\\n"
        ...     "qoyq (66)\\n"
        ...     "padx (45) -> pbga, havc, qoyq\\n"
        ...     "tknk (41) -> ugml, padx, fwft\\n"
        ...     "jptl (61)\\n"
        ...     "ugml (68) -> gyxo, ebii, jptl\\n"
        ...     "gyxo (61)\\n"
        ...     "cntj (57)\\n"
        ... )
        Node(name='tknk', weight=41, children=['ugml', 'padx', 'fwft'],
            parent=None)
        """
        nodes_info_by_name = cls.parse_infos(nodes_text)
        if not nodes_info_by_name:
            return None
        nodes_by_name: Dict[str, Node] = {
            name: cls(name, weight, [], None)
            for name, weight, _ in nodes_info_by_name.values()
        }
        for node in nodes_by_name.values():
            node.children = [
                nodes_by_name[sub_node_name]
                for sub_node_name in nodes_info_by_name[node.name][2]
            ]
            for child in node.children:
                if child.parent:
                    raise Exception(
                        f"Node '{child.name}' had multiple parents: "
                        f"'{child.parent.name}' and '{node.name}'")
                child.parent = node

        a_node = next(iter(nodes_by_name.values()))
        a_root = a_node.find_root()
        descendants = a_root.get_descendants()
        if descendants != set(nodes_by_name.values()):
            extra_descendants = descendants - set(nodes_by_name.values())
            if extra_descendants:
                raise Exception(f"Got more descendants than nodes")
            else:
                raise Exception(f"Graph is a forest, not a tree")

        return a_root

    @classmethod
    def parse_infos(cls, nodes_text):
        nodes_info_by_name = {}
        for line in map(str.strip, nodes_text.strip().splitlines()):
            name, weight, children_names = cls.parse_node(line)
            if name in nodes_info_by_name:
                raise Exception(f"Got duplicate node {name}")
            nodes_info_by_name[name] = (name, weight, children_names)

        cls.check_referenced_nodes(nodes_info_by_name)

        return nodes_info_by_name

    @classmethod
    def check_referenced_nodes(cls, nodes_info_by_name):
        referenced_children_names = sum((
            children_names
            for _, _, children_names in nodes_info_by_name.values()
        ), [])
        if len(referenced_children_names) \
                != len(set(referenced_children_names)):
            raise Exception(f"Some nodes were referenced more than once")
        unknown_referenced_children_names = \
            set(referenced_children_names) - set(nodes_info_by_name)
        if unknown_referenced_children_names:
            raise Exception(
                f"Got {len(unknown_referenced_children_names)} unknown node "
                f"names: "
                f"{', '.join(sorted(unknown_referenced_children_names))}")

    @classmethod
    def parse_node(cls, node_text):
        """
        >>> Node.parse_node('vpryah (310) -> iedlpkf, epeain')
        ('vpryah', 310, ['iedlpkf', 'epeain'])
        >>> Node.parse_node('vpryah (310) -> iedlpkf')
        ('vpryah', 310, ['iedlpkf'])
        >>> Node.parse_node('vpryah (310)')
        ('vpryah', 310, [])
        """
        name, weight_str, children_names_str = \
            cls.re_node.match(node_text).groups()
        weight = int(weight_str)
        if children_names_str:
            children_names = children_names_str.split(', ')
        else:
            children_names = []
        if len(children_names) != len(set(children_names)):
            raise Exception(f"Parsed duplicate sub-nodes in '{node_text}'")

        return name, weight, children_names

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"name={repr(self.name)}, "
            f"weight={repr(self.weight)}, "
            f"children={repr([child.name for child in self.children])}, "
            f"parent={repr(self.parent.name if self.parent else None)}"
            f")"
        )

    def __hash__(self):
        return hash(self.name)

    def find_root(self):
        root = self
        while root.parent:
            root = root.parent

        return root

    def get_descendants(self):
        descendants = {self}
        stack = [self]
        while stack:
            node = stack.pop(0)
            new_descendants = set(node.children) - descendants
            stack.extend(new_descendants)
            descendants.update(new_descendants)

        return descendants


Challenge.main()
challenge = Challenge()
