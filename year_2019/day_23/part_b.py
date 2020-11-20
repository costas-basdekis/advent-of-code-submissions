#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2019.day_23.part_a import run_network


def solve(_input=None):
    """
    >>> solve()
    10650
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return run_network(_input, create_manage_output_twice_to_0())


def create_manage_output_twice_to_0():
    previous = {
        0: None,
        'senders': set(),
        'found': False,
    }

    def manage_output_twice_to_0(from_address, output, queues):
        if previous['found']:
            raise Exception("Found yet continuing")
        if not output:
            queue_255 = queues[255]
            idle = not any(queues[address] for address in range(50))
            if idle and queue_255:
                x, y = queue_255.pop()
                queue_255.clear()
                # print("Sent", (x, y))
                return manage_output_twice_to_0(255, (0, x, y), queues)
            elif idle:
                pass
                # print("Idle, but no 255 message")
            return False, None
        # print(from_address, output)
        while output:
            (to_address, x, y), output = output[:3], output[3:]
            if to_address == 0:
                if from_address not in previous['senders']:
                    previous['senders'].add(from_address)
                    # print("Senders", previous['senders'])
                # print(y, y == previous[0], previous[0])
                # print("Compare 0", previous[0], y)
                if y == previous[0]:
                    previous['found'] = True
                    return True, y
                previous[0] = y
            queues[to_address].append((x, y))

        return False, None

    return manage_output_twice_to_0


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
