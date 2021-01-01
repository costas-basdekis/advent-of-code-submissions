#!/usr/bin/env python3
import utils

from year_2019.day_15.part_a import get_minimum_distances, play_game


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        368
        """
        game = play_game(_input)
        minimum_distances = get_minimum_distances(game, game["oxygen_location"])
        return max(minimum_distances.values())


challenge = Challenge()
challenge.main()
