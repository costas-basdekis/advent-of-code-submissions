#!/usr/bin/env python3
import utils

from year_2018.day_04.part_a import Observations


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        49944
        """
        sleepiest_profile = Observations.from_lines(_input).attach_guard_ids()\
            .get_sleep_schedule()\
            .get_guards_sleep_profiles()\
            .get_sleepiest_profile_by_strategy_2()
        if not sleepiest_profile:
            raise Exception("No sleepiest profile")

        return sleepiest_profile.get_signature()


Challenge.main()
challenge = Challenge()
