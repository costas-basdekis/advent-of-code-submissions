#!/usr/bin/env python3
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        37262
        """
        return Node.from_nodes_text(_input).metadata_sum()


class Node(namedtuple("Node", ("children", "metadata"))):
    @classmethod
    def from_nodes_text(cls, nodes_text):
        """
        >>> Node.from_nodes_text("2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2")
        Node(children=(Node(children=(), metadata=(10, 11, 12)), Node(children=(Node(children=(), metadata=(99,)),), metadata=(2,))), metadata=(1, 1, 2))
        """
        value_strs = nodes_text.strip().split(" ")
        values = tuple(map(int, value_strs))
        root, _ = cls.from_values(values, is_root=True)

        return root

    @classmethod
    def from_values(cls, values, is_root=False):
        """
        >>> Node.from_values(
        ...     [2, 3, 0, 3, 10, 11, 12, 1, 1, 0, 1, 99, 2, 1, 1, 2], True)[0]
        Node(children=(Node(children=(), metadata=(10, 11, 12)), Node(children=(Node(children=(), metadata=(99,)),), metadata=(2,))), metadata=(1, 1, 2))
        >>> Node.from_values(
        ...     [2, 3, 0, 3, 10, 11, 12, 1, 1, 0, 1, 99, 2, 1, 1, 2, 3], True)[0]
        Traceback (most recent call last):
        ...
        Exception: There were 1 extra values
        """
        values = tuple(values)
        (child_count, metadata_count), remaining = values[:2], values[2:]
        nodes = ()
        for _ in range(child_count):
            node, remaining = cls.from_values(remaining)
            nodes += (node,)
        metadata, remaining = \
            remaining[:metadata_count], remaining[metadata_count:]
        if len(metadata) < metadata_count:
            raise Exception(
                f"Expected {metadata_count} metadata, but got {len(metadata)}")
        if is_root and remaining:
            raise Exception(f"There were {len(remaining)} extra values")

        return cls(nodes, metadata), remaining

    def metadata_sum(self):
        """
        >>> Node.from_nodes_text("2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2")\\
        ...     .metadata_sum()
        138
        """
        return sum(self.metadata) + sum(
            child.metadata_sum()
            for child in self.children
        )


challenge = Challenge()
challenge.main()
