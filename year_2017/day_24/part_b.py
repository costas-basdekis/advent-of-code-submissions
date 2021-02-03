#!/usr/bin/env python3
import utils
from year_2017.day_24 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1841
        """
        return GraphExtended.from_graph_text(_input).get_longest_path_distance()


class GraphExtended(part_a.Graph):
    def get_longest_path_distance(self):
        _, longest_path_distance, _ = \
            self.get_distances_and_longest_path_and_distance()
        return longest_path_distance


Challenge.main()
challenge = Challenge()
