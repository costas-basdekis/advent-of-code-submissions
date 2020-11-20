#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        14134
        """
        connection_set = part_a.ConnectionSet.from_connections_text(_input)
        harness = connection_set.apply()
        if debugger:
            print(harness.show())
        new_harness = part_a.Harness({'b': harness['a']})
        write_to_b, = [
            connection
            for connection in connection_set.connections
            if connection.destination == part_a.Wire('b')
        ]
        connection_set.connections.remove(write_to_b)
        connection_set.apply(new_harness)
        return new_harness['a']


Challenge.main()
challenge = Challenge()
