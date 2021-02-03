#!/usr/bin/env python3
import utils

from year_2019.day_21.part_a import SpringScript, run_spring_robot


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1139206699
        """
        return run_spring_robot(get_extended_script(), _input, running=True)


def get_extended_script():
    """
    >>> script = get_extended_script()
    >>> script.simulate("#####.###########", True)
    >>> script.simulate("#####.##.##..####", True)
    >>> script.simulate("#####.#.#...#####", True)
    """

    return SpringScript()\
        .not_('A', 'J')\
        .not_('C', 'T')\
        .or_('T', 'J')\
        .not_('B', 'T')\
        .or_('T', 'J')\
        .and_('D', 'J')\
        .set_('E', 'T')\
        .or_('H', 'T')\
        .and_('T', 'J')


Challenge.main()
challenge = Challenge()
