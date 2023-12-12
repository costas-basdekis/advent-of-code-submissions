#!/usr/bin/env python3
import itertools
from functools import reduce
from itertools import count
from math import gcd
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge, product
from year_2023.day_20 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        247702167614647
        """
        network = NetworkExtended.from_text(_input)
        sub_network_ranges = [
            ("pj", "qb"),
            ("xz", "mp"),
            ("ns", "qt"),
            ("sg", "ng"),
        ]
        low_message_index_list = []
        for start, end in sub_network_ranges:
            sub_network = network.cut_part(start, end)
            sub_network.press_button().process_queue()
            # print("\n".join(map(str, sub_network.processed_messages)))
            # print(sub_network)
            prefix_count, cycle_length, _, _ = sub_network.find_cycle_numbers(10000)
            if cycle_length == 0:
                debugger.report(f"No cycles found for '{start}'->'{end}'")
                continue
            # debugger.report()(numbers)
            high_message_count = 0
            low_message_count = 0
            low_message_indexes = []
            sub_network.restart()
            for click_index in range(prefix_count + cycle_length):
                sub_network.clear_processed_messages().press_button().process_queue()
                high_message_count += sum(
                    1
                    for message in sub_network.processed_messages
                    if message.target == end and message.state == part_a.State.High
                )
                low_message_count_for_click = sum(
                    1
                    for message in sub_network.processed_messages
                    if message.target == end and message.state == part_a.State.Low
                )
                low_message_count += low_message_count_for_click
                if low_message_count_for_click:
                    low_message_indexes.append(click_index + 1)
            low_message_index_list.append(low_message_indexes)
            debugger.report(f"Messages to '{end}' after {prefix_count + cycle_length} clicks: {low_message_count} low (at {low_message_indexes}) and {high_message_count} high")
        low_message_indexes_combinations = itertools.product(*low_message_index_list)
        min_click_count = min(
            product(low_message_indexes_combination) // reduce(gcd, low_message_indexes_combination)
            for low_message_indexes_combination in low_message_indexes_combinations
        )
        debugger.report(f"Min click count: {min_click_count}")
        return min_click_count


class NetworkExtended(part_a.Network):
    def get_click_count_until_message_to(self, target: str, state: part_a.State, debugger: Debugger = Debugger(enabled=False)) -> int:
        message = f"Looking for -{state.value}-> {target}"
        for click_count in debugger.stepping(count(1)):
            self.clear_processed_messages().press_button().process_queue()
            if any(message.target == target and message.state == state for message in self.processed_messages):
                return click_count
            debugger.default_report_if(message)
        raise Exception(f"Could not find message -{state.value}-> {target}")

    def cut_part(self, start: str, end: str) -> "NetworkExtended":
        names = {start}
        queue = [start]
        while queue:
            name = queue.pop(0)
            module_template = self.modules_by_name[name].template
            new_names = set(module_template.output_names) - names - {end}
            names.update(new_names)
            queue.extend(new_names)
        return NetworkExtended.from_network_template(part_a.NetworkTemplate.from_module_templates([
            part_a.CopierModuleTemplate(module_name="broadcaster", input_names=[], output_names=[start])
        ] + [
            module_template.set_input_names([])
            for name in names
            for module_template in [self.modules_by_name[name].template]
        ] + [
            self.modules_by_name[end].template.set_input_names([]).set_output_names([])
        ]))


Challenge.main()
challenge = Challenge()
