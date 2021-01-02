#!/usr/bin/env python3
import dataclasses

import utils
from year_2018.day_24 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2344
        """
        group_set = GroupSetExtended.from_groups_text(_input)
        smallest_required_boost = BoostSolver().find_smallest_required_boost(
            group_set, 'Immune System', debug=debug)
        boosted = group_set.boost(smallest_required_boost, 'Immune System')
        boosted.step_many(debug=debug)
        return boosted.get_unit_count()


class BoostSolver:
    def find_smallest_required_boost(self, group_set, benefactor, debug=False):
        min_boost = 0
        if self.is_boost_enough(group_set, benefactor, min_boost, debug=debug):
            return min_boost
        max_boost = self.get_big_enough_boost(
            group_set, benefactor, debug=debug)
        if debug:
            print(f"Boost must be between {min_boost} and {max_boost}")

        while max_boost > min_boost + 1:
            mid_boost = (max_boost + min_boost) // 2
            if self.is_boost_enough(
                    group_set, benefactor, mid_boost, debug=debug):
                max_boost = mid_boost
                if debug:
                    print(
                    f"Boost {mid_boost} is too much: checking between "
                    f"{min_boost} and {max_boost}")
            else:
                min_boost = mid_boost
                if debug:
                    print(
                    f"Boost {mid_boost} is not enough: checking between "
                    f"{min_boost} and {max_boost}")

        return max_boost

    def get_big_enough_boost(self, group_set, benefactor, start=1, debug=False):
        boost = start
        while not self.is_boost_enough(
                group_set, benefactor, boost, debug=debug):
            if debug:
                print(f"Boost {boost} was not enough")
            boost *= 2
        if debug:
            print(f"Boost {boost} was enough")

        return boost

    def is_boost_enough(self, group_set, benefactor, boost, debug=False):
        boosted = group_set.boost(boost, benefactor)
        boosted.step_many(debug=debug)
        winning_side = boosted.get_winning_side()
        return winning_side == benefactor


class GroupSetExtended(part_a.GroupSet):
    def boost(self, boost, benefactor):
        cls = type(self)
        return cls([
            group.boost(boost)
            if group.faction == benefactor else
            group.copy()
            for group in self.groups
        ])

    def get_winning_side(self):
        remaining_factions = {
            group.faction
            for group in self.groups
        }
        if not remaining_factions:
            return None
        if len(remaining_factions) > 1:
            return None

        winning_side, = remaining_factions

        return winning_side


class GroupExtended(part_a.Group):
    def boost(self, boost):
        return dataclasses.replace(self, attack=self.attack + boost)

    def copy(self):
        return dataclasses.replace(self)


GroupSetExtended.group_class = GroupExtended


challenge = Challenge()
challenge.main()
