#!/usr/bin/env python3
import re
from itertools import groupby
from typing import Set, Union

import click
import pyperclip

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2023.day_22 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        96356
        """
        return BrickStackExtended.from_text(_input).drop_bricks().get_disintegrating_sum()

    def play(self):
        stack = BrickStackExtended.from_text(self.input).drop_bricks()
        # print(stack.get_2d_representation(0, 2))
        # print(stack.get_2d_representation(1, 2))
        counts_list = [
            len(stack.get_recursive_disintegrating_bricks(brick))
            for brick, brick_dependencies in stack.brick_disintegration_dependencies.items()
            if brick_dependencies
        ]
        counts_by_count = {
            count: len(list(items))
            for count, items in groupby(sorted(counts_list))
        }
        # print(counts_by_count)
        # print(sum(counts_list))
        re_brick = re.compile(r"^b(\d+)$")
        re_level = re.compile(r"^l(\d+)$")
        re_graph_all = re.compile(r"^ga$")
        re_graph_one = re.compile(r"^g(\d+)$")
        def c(text: any) -> str:
            return click.style(str(text), fg="red")
        while True:
            user_input = click.prompt(
                f"Enter a brick number [0-{len(stack.bricks) - 1}] with {c('bX')}, "
                f"visualise a level [{stack.boundaries[0].z}-{stack.boundaries[1].z}] with {c('lX')}, "
                f"generate the Graphviz graph for all bricks with {c('ga')}, "
                f"or generate the Graphviz graph for one brick with {c('gX')}"
            )
            if matches := re_brick.match(user_input):
                brick_index_str, = matches.groups()
                brick_index = int(brick_index_str)
                brick = stack.bricks[brick_index]
                disintegrating_bricks = stack.get_recursive_disintegrating_bricks(brick)
                print(
                    f"Brick #{brick_index} {brick}\n"
                    f" * Depends on {', '.join(map(str, (stack.bricks.index(dependency) for dependency in stack.brick_dependencies[brick])))}\n"
                    f" * Is depended on by {', '.join(map(str, (stack.bricks.index(dependency) for dependency in stack.brick_reverse_dependencies[brick])))}\n"
                    f" * Recursive disintegrating count is {len(disintegrating_bricks)}: {', '.join(sorted(map(str, map(stack.bricks.index, disintegrating_bricks))))}"
                )
            elif matches := re_level.match(user_input):
                z_str, = matches.groups()
                z = int(z_str)
                print(stack.get_2d_slice_representation(0, 1, z))
            elif re_graph_all.match(user_input):
                graph_text = "\n".join(filter(None, [
                    f"b{stack.bricks.index(brick)} -> b{stack.bricks.index(dependency)};"
                    for brick in stack.bricks
                    for dependency in stack.brick_dependencies[brick]
                ] + [
                    f"b{stack.bricks.index(brick)}[label=\"b{stack.bricks.index(brick)}\\n{count}\",style=filled,fillcolor=green];"
                    if count > 0 else
                    ""
                    for brick in stack.bricks
                    for count in [len(stack.get_recursive_disintegrating_bricks(brick))]
                ]))
                pyperclip.copy(graph_text)
                print(f"Copied {len(graph_text)} characters to clipboard")
            elif match := re_graph_one.match(user_input):
                chosen_brick_index_str, = match.groups()
                chosen_brick_index = int(chosen_brick_index_str)
                chosen_brick = stack.bricks[chosen_brick_index]
                disintegrating_bricks = stack.get_recursive_disintegrating_bricks(chosen_brick)
                graph_text = "\n".join(filter(None, [
                    f"b{stack.bricks.index(brick)} -> b{stack.bricks.index(dependency)};"
                    for brick in stack.bricks
                    for dependency in stack.brick_dependencies[brick]
                ] + [
                    f"b{stack.bricks.index(brick)}[label=\"b{stack.bricks.index(brick)}\\n{len(disintegrating_bricks)}\",style=filled,fillcolor=green];"
                    if brick == chosen_brick else
                    f"b{stack.bricks.index(brick)}[style=filled,fillcolor=blue];"
                    if brick in disintegrating_bricks else
                    ""
                    for brick in stack.bricks
                ]))
                pyperclip.copy(graph_text)
                print(f"Copied {len(graph_text)} characters to clipboard")
            else:
                print(f"Could not parse '{user_input}'")


class BrickStackExtended(part_a.BrickStack):
    def get_disintegrating_sum(self) -> int:
        """
        >>> _stack = BrickStackExtended.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''').drop_bricks()
        >>> _stack.get_disintegrating_sum()
        7
        """
        disintegrating_dependencies = self.brick_disintegration_dependencies
        return sum(
            len(self.get_recursive_disintegrating_bricks(brick))
            for brick, brick_dependencies in disintegrating_dependencies.items()
            if brick_dependencies
        )

    def get_recursive_disintegrating_bricks(self, start: part_a.Brick) -> Set[part_a.Brick]:
        """
        >>> def _check(s: BrickStackExtended, bi: int):
        ...     bs = s.get_recursive_disintegrating_bricks(s.bricks[bi])
        ...     print(', '.join(sorted(s.brick_names[s.bricks.index(d)] for d in bs)))
        >>> _stack = BrickStackExtended.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''').drop_bricks()
        >>> _check(_stack, 0)
        B, C, D, E, F, G
        >>> _check(_stack, 5)
        G
        """
        dependencies = self.brick_dependencies
        reverse_dependencies = self.brick_reverse_dependencies
        queue = list(reverse_dependencies[start])
        removed = {start}
        while queue:
            brick = queue.pop(0)
            remaining_dependencies = dependencies[brick] - removed
            if remaining_dependencies:
                continue
            removed.add(brick)
            next_bricks = reverse_dependencies[brick] - removed
            queue.extend(next_bricks)
        removed.remove(start)
        return removed

    def get_tips(self) -> Set[part_a.Brick]:
        """
        >>> _stack = BrickStackExtended.from_text('''
        ...     1,0,1~1,2,1
        ...     0,0,2~2,0,2
        ...     0,2,3~2,2,3
        ...     0,0,4~0,2,4
        ...     2,0,5~2,2,5
        ...     0,1,6~2,1,6
        ...     1,1,8~1,1,9
        ... ''').drop_bricks()
        >>> sorted(map(_stack.bricks.index, _stack.get_tips()))
        [6]
        """
        reverse_dependencies = self.brick_reverse_dependencies
        return {
            brick
            for brick, dependencies in reverse_dependencies.items()
            if not dependencies
        }

    def get_2d_slice_representation(self, first_axis_index: int, second_axis_index: int, third_axis_value: int) -> str:
        third_axis_index, = {0, 1, 2} - {first_axis_index, second_axis_index}
        bricks = [
            brick
            for brick in self.bricks
            if brick.start[third_axis_index] <= third_axis_value <= brick.end[third_axis_index]
        ]
        return "{}\n{}".format(
            f"{self.axis_names[third_axis_index]}={third_axis_value}",
            self.get_2d_representation(first_axis_index, second_axis_index, bricks=bricks),
        )


Challenge.main()
challenge = Challenge()
