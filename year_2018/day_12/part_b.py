#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2018.day_12 import part_a


def solve(_input=None):
    """
    >>> solve()
    2600000001872
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    pot_state, rule_set = PotRuleSetExtended.read_state_and_rule_set(_input)

    return rule_set\
        .predict_state_after_generations(pot_state, 50000000000)\
        .get_pot_sum()


class PotRuleSetExtended(part_a.PotRuleSet):
    def predict_state_after_generations(self, pot_state, count, attempts=1000):
        for step in range(attempts):
            previous_pot_state = pot_state
            pot_state = self\
                .advance_state(pot_state)
            if previous_pot_state.show() == pot_state.show():
                break
        else:
            raise Exception("Couldn't find repeating pattern")

        min_index, max_index = pot_state.get_indexes_range()
        target_step = count - 1
        target_min_index = min_index - step + target_step
        target_pot_state = part_a.PotState.from_pot_state_tuple(
            pot_state.to_tuple(min_index, max_index - min_index + 1),
            target_min_index)
        return target_pot_state


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
