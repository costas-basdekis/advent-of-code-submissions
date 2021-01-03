#!/usr/bin/env python3
from collections import defaultdict

import utils

from year_2019.day_15.part_a import run_interactive_program
import year_2019.day_09.part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        15969
        """
        return run_network(_input, manage_output_first_to_255)


def run_network(_input, manage_output_func):
    computers = [
        run_interactive_program(_input, endless=True)
        for _ in range(50)
    ]

    queues = defaultdict(list)

    for address, computer in enumerate(computers):
        _, first_output = computer.send(None)
        manage_output_func(address, first_output, queues)
        _, second_output = computer.send(address)
        manage_output_func(address, second_output, queues)

    finished, result = False, None
    while not finished:
        for address, computer in enumerate(computers):
            queue = queues[address]
            if queue:
                next_input = queue.pop(0)
            else:
                next_input = -1
            _, computer_output = computer.send(next_input)
            finished, result = manage_output_func(
                address, computer_output, queues)
            if finished:
                break

    if result is None:
        raise Exception("Got empty result")

    return result


def manage_output_first_to_255(from_address, output, queues):
    if not output:
        return False, None
    # print(from_address, output)
    while output:
        (to_address, x, y), output = output[:3], output[3:]
        if to_address == 255:
            return True, y
        queues[to_address].append((x, y))

    return False, None


challenge = Challenge()
challenge.main()
