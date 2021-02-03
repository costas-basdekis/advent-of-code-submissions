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
        is_boost_enough = self.get_is_boost_enough(group_set, benefactor)

        min_boost = 0
        if is_boost_enough(min_boost, debug=debug):
            return min_boost

        return utils.helper.find_smallest_required_value(
            min_boost, is_boost_enough,
            debug=debug)

    def get_is_boost_enough(self, group_set, benefactor):
        def is_boost_enough(boost, debug=False):
            boosted = group_set.boost(boost, benefactor)
            boosted.step_many(debug=debug)
            winning_side = boosted.get_winning_side()
            return winning_side == benefactor

        return is_boost_enough


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


Challenge.main()
challenge = Challenge()
