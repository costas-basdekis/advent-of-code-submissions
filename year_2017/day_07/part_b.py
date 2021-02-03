#!/usr/bin/env python3
import itertools
from typing import Optional, List

import click

import utils
from year_2017.day_07 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1206
        """
        root = NodeExtended.from_nodes_text(_input)
        _, expected_weight = root \
            .find_unbalanced_child_and_expected_weight(debug=debug)

        return expected_weight

    def play(self):
        root = NodeExtended.from_nodes_text(self.input)
        descendants = root.get_descendants()
        max_name_length = max(len(node.name) for node in descendants)
        node = root
        level = 0
        child_format = f"  {{: >2}}: {{: <{max_name_length}}} {{: <10}} {{}}"
        while True:
            click.echo(
                f"Node {click.style(node.name, fg='green')} at level "
                f"{click.style(str(level), fg='blue')} with "
                f"{click.style(str(len(node.children)), fg='yellow')} children")
            for index, child in enumerate(node.children, 1):
                click.echo(
                    child_format.format(
                        index, child.name, child.weight,
                        child.get_total_weight(),
                    ))
            child_choices = list(map(str, range(1, len(node.children) + 1)))
            command = click.prompt(
                "'q' to quit, 'r' for root, 'u' to go up a level, or the "
                "number of the node", show_choices=False, type=click.Choice(
                    ['q', 'r', 'u'] + child_choices))
            if command == 'q':
                break
            elif command == 'r':
                node = root
                level = 0
            elif command == 'u':
                if node.parent:
                    node = node.parent
                    level -= 1
            else:
                child_index = int(command) - 1
                node = node.children[child_index]
                level += 1


class NodeExtended(part_a.Node):
    children: List['NodeExtended']
    parent: Optional['NodeExtended']

    def __lt__(self, other):
        return self.name < other.name

    def find_unbalanced_child_and_expected_weight(self, debug=False):
        """
        >>> NodeExtended.from_nodes_text(
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
        ... ).find_unbalanced_child_and_expected_weight()
        (NodeExtended(name='ugml', ...), 60)
        """
        unbalanced_child_and_expected_weight = next(filter(None, (
            child.find_unbalanced_child_and_expected_weight(debug=debug)
            for child in self.children
        )), None)
        if unbalanced_child_and_expected_weight:
            return unbalanced_child_and_expected_weight

        return self.get_unbalanced_child_and_expected_weight(debug=debug)

    def get_unbalanced_child_and_expected_weight(self, debug=False):
        total_weight_by_child = {
            child: child.get_total_weight()
            for child in self.children
        }
        count_by_total_weights = {
            total_weight: utils.helper.iterable_length(items)
            for total_weight, items
            in itertools.groupby(sorted(total_weight_by_child.values()))
        }
        if len(count_by_total_weights) <= 1:
            if debug:
                print(
                    f"All children of {self.name} have the same weights: "
                    f"{sorted(total_weight_by_child.values())}, "
                    f"{count_by_total_weights}")
            return None

        if len(count_by_total_weights) > 2:
            raise Exception(
                f"Got too many different total weights in {self}: "
                f"{sorted(count_by_total_weights)}")

        min_count = min(count_by_total_weights.values())
        if min_count != 1:
            raise Exception(
                f"Got too many children with same different total weight in "
                f"{self}: {min_count}")

        max_count = max(count_by_total_weights.values())
        if max_count == 1:
            raise Exception(
                f"Got multiple total weights with 1 child in {self}")

        different_total_weight = min(
            count_by_total_weights,
            key=lambda total_weight: count_by_total_weights[total_weight])
        expected_total_weight = max(
            count_by_total_weights,
            key=lambda total_weight: count_by_total_weights[total_weight])
        total_weight_difference = expected_total_weight - different_total_weight

        different_child, = [
            child
            for child, total_weight in total_weight_by_child.items()
            if total_weight == different_total_weight
        ]
        expected_weight = different_child.weight + total_weight_difference
        if debug:
            print(
                f"Child {different_child.name} of {self.name} should have had "
                f"weight of {expected_weight}, "
                f"{sorted(total_weight_by_child.values())}")

        return different_child, expected_weight

    def get_total_weight(self):
        return self.weight + sum(
            child.get_total_weight()
            for child in self.children
        )

    def show(self, indent='*'):
        return "{}{}{}{}".format(
            indent,
            self.name,
            '\n' if self.children else '',
            '\n'.join(
                child.show(indent=f'  {indent}')
                for child in self.children
            ),
        )


Challenge.main()
challenge = Challenge()
