#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Union, Set

import pyperclip

from aox.challenge import Debugger
from utils import BaseIcpcChallenge, PrimeGenerator


class Challenge(BaseIcpcChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        'second'
        """
        winner_values = []
        node_counts = list(map(int, map(str.strip, _input.strip().splitlines()[1:])))
        debugger.default_report(f"Checking {len(node_counts)} graphs")
        for index, node_count in debugger.stepping(enumerate(node_counts, start=1)):
            debugger.default_report(f"Checking graph with {node_count} nodes")
            with debugger.adding_extra_report_format(lambda _, message: f"M{node_count}: {message}"):
                winner = Graph.from_count(node_count).find_winner(by_removing_tails=True, debugger=debugger)
            if winner:
                winner_values.append(winner.value)
            else:
                winner_values.append(None)
            if debugger.should_report():
                debugger.default_report_if(f"Checked {index}/{len(node_counts)}")
        return "\n".join(
            f"first {winner_value}"
            if winner_value is not None else
            "second"
            for winner_value in winner_values
        )

    def does_solution_match_output(self, result: str, output: str) -> bool:
        return "\n".join(line.split(" ")[0] for line in result.splitlines()) == "\n".join(line.split(" ")[0] for line in output.splitlines())

    def play(self):
        # graph = Graph.from_count(17)
        # GraphClassifier.from_graph(graph).check_is_winner(graph.nodes[10])
        self.classify()

    def classify(self):
        graph_text = ""
        for m in range(1, 18):
            graph = Graph.from_count(m).classify(evens_only=False, by_removing_tails=True)
            graph_text += "\n" + "\n".join([
                f"m{m}n{node.value}{' -- ' if next_nodes else ''}{','.join(f'm{m}n{next_node.value}' for next_node in next_nodes)};"
                for node in graph.nodes
                for next_nodes in [[next_node for next_node in node.next_nodes if next_node.value > node.value]]
            ] + [
                f"m{m}n{node.value}[style=filled,fillcolor={'green' if node.winning else 'red'}];"
                if node.value % 2 == 0 else
                f"m{m}n{node.value}[style=radial,fillcolor=\"white:{'green' if node.winning else 'red'}\"];"
                for node in graph.nodes
                if node.winning is not None
            ])
        pyperclip.copy(graph_text)
        print(f"Copied {len(graph_text)} characters to clipboard, paste into https://dreampuf.github.io/GraphvizOnline/")


@dataclass
class Graph:
    nodes: List["Node"]

    @classmethod
    def from_count(cls, node_count: int) -> "Graph":
        nodes_by_value = {
            value: Node(value=value)
            for value in range(1, node_count + 1)
        }
        generator = PrimeGenerator()
        for value in range(1, node_count + 1):
            node = nodes_by_value[value]
            for prime in generator:
                next_value = value // prime
                if next_value < 1:
                    break
                if next_value * prime != value:
                    continue
                next_node = nodes_by_value[next_value]
                node.next_nodes.append(next_node)
                next_node.next_nodes.append(node)
        return cls(nodes=list(nodes_by_value.values()))

    def find_winner(self, by_removing_tails: bool = False, debugger: Debugger = Debugger(enabled=False)) -> Optional["Node"]:
        return GraphClassifier.from_graph(self).find_winner(by_removing_tails=by_removing_tails, debugger=debugger)

    def classify(self, evens_only: bool = True, by_removing_tails: bool = False) -> "Graph":
        GraphClassifier.from_graph(self).classify(evens_only=evens_only, by_removing_tails=by_removing_tails)
        return self


@dataclass
class GraphClassifier:
    nodes: List["Node"]

    @classmethod
    def from_graph(cls, graph: Graph) -> "GraphClassifier":
        return cls(nodes=graph.nodes)

    def classify(self, evens_only: bool = False, by_removing_tails: bool = False) -> None:
        for winner in self.iterate_winners(evens_only=evens_only, by_removing_tails=by_removing_tails):
            winner.winning = True
        for node in self.nodes:
            if (not evens_only or (node.value % 2 == 0)) and node.winning is None:
                node.winning = False

    def find_winner(self, by_removing_tails: bool = False, debugger: Debugger = Debugger(enabled=False)) -> Optional["Node"]:
        for winner in self.iterate_winners(by_removing_tails=by_removing_tails, debugger=debugger):
            return winner
        return None

    def find_all_winners(self) -> None:
        for _ in self.iterate_winners():
            pass

    def iterate_winners(self, evens_only: bool = True, by_removing_tails: bool = False, debugger: Debugger = Debugger(enabled=False)) -> Iterable["Node"]:
        if by_removing_tails:
            check_is_winner = self.check_is_winner_by_removing_tails
        else:
            check_is_winner = self.check_is_winner
        for index, start in debugger.stepping(enumerate(reversed(self.nodes), start=1)):
            with debugger.adding_extra_report_format(lambda _, message: f"N{start.value}: {message}"):
                if (not evens_only or (start.value % 2 == 0)) and check_is_winner(start, debugger=debugger):
                    yield start
            if debugger.should_report():
                debugger.default_report_if(f"Checked {start.value}, {index}/{len(self.nodes) // 2}")

    def check_is_winner(self, start: "Node", debugger: Debugger = Debugger(enabled=False)) -> bool:
        stack = [(start, 0)]
        seen = {start}
        while debugger.step_if(stack):
            node, start_index = stack[-1]
            for next_node_index in range(start_index, len(node.next_nodes)):
                next_node = node.next_nodes[next_node_index]
                if next_node in seen:
                    continue
                stack[-1] = (node, next_node_index + 1)
                stack.append((next_node, 0))
                seen.add(next_node)
                # print(f"Added {[x.value for x, _ in stack]}")
                break
            else:
                # print(f"Removing {[x.value for x, _ in stack]}")
                seen.remove(stack.pop()[0])
                if not stack:
                    # print(f"Is winner")
                    return True
                else:
                    # print(f"Removing {[x.value for x, _ in stack]}")
                    seen.remove(stack.pop()[0])
            if debugger.should_report():
                completed_percentage = 0
                for node, index in reversed(stack):
                    completed_percentage = (completed_percentage + index) / len(node.next_nodes)
                debugger.default_report_if(f"Stack height is {len(stack)}, completed {round(completed_percentage, 4)}%")
        return False

    def check_is_winner_by_removing_tails(self, start: "Node", debugger: Debugger = Debugger(enabled=False)) -> bool:
        seen = {start} | self.get_discarded_from_seen(start, set())
        stack = [(start, 0, seen)]
        # print(f"Start with {start.value} and {sorted(x.value for x in seen)}")
        while debugger.step_if(stack):
            node, start_index, seen = stack[-1]
            for next_node_index in range(start_index, len(node.next_nodes)):
                next_node = node.next_nodes[next_node_index]
                # print(f"Check {node.value} -> {next_node.value} ({next_node_index}/{len(node.next_nodes) - 1})")
                if next_node in seen:
                    continue
                stack[-1] = (node, next_node_index + 1, seen)
                next_seen = seen | {next_node} | self.get_discarded_from_seen(next_node, seen)
                stack.append((next_node, 0, next_seen))
                # print(f"Move to {next_node.value} ({[x.value for x, _, _ in stack]}) and {sorted(x.value for x in next_seen)}")
                # print(f"Added {[x.value for x, _ in stack]}")
                break
            else:
                # print(f"Removing {[x.value for x, _ in stack]}")
                # print(f"Popping from {[x.value for x, _, _ in stack]} and {sorted(x.value for x in seen)}")
                _, _, seen = stack.pop()
                if not stack:
                    # print(f"Is winner")
                    return True
                else:
                    # print(f"Removing {[x.value for x, _ in stack]}")
                    # print(f"Popping from {[x.value for x, _, _ in stack]} and {sorted(x.value for x in seen)}")
                    _, _, seen = stack.pop()
            if debugger.should_report():
                completed_percentage = 0
                for node, index, _ in reversed(stack):
                    completed_percentage = (completed_percentage + index) / len(node.next_nodes)
                debugger.default_report_if(f"Stack height is {len(stack)}, completed {round(completed_percentage, 4)}%")
        return False

    def get_discarded_from_seen(self, leaf: "Node", seen: Set["Node"]) -> Set["Node"]:
        leaves = [
            node
            for node in self.nodes
            for next_nodes in [set(node.next_nodes) - seen]
            if len(next_nodes) == 1
        ]
        # print(f"Leaves of {sorted(x.value for x in seen)}: {sorted(x.value for x in leaves)}")
        tails = [
            self.get_tail(leaf, seen)
            for leaf in leaves
        ]
        return {
            node
            for tail in tails
            if (leaf not in tail) and not (seen & tail)
            for node in tail
        }

    def get_tail(self, leaf: "Node", seen: Set["Node"]) -> Set["Node"]:
        tail = set()
        tail_seen = set(seen)
        node = leaf
        next_nodes = set(node.next_nodes) - tail_seen
        while len(next_nodes) <= 1:
            tail.add(node)
            tail_seen.add(node)
            if not next_nodes:
                break
            node, = next_nodes
            next_nodes = set(node.next_nodes) - tail_seen
        if len(tail) % 2 == 1:
            tail.add(node)
        # print(f"Tail of {leaf.value} and {sorted(x.value for x in seen)}: {sorted(x.value for x in tail)}")
        return tail


@dataclass
class Node:
    value: int
    next_nodes: List["Node"] = field(default_factory=list)
    winning: Optional[bool] = None

    def __hash__(self) -> int:
        return hash(self.value)


Challenge.main()
challenge = Challenge()
