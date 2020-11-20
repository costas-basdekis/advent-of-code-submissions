#!/usr/bin/env python3
import utils
from year_2017.day_22 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2511702
        """
        return GridExtended.from_grid_text(_input)\
            .step_many(10000000)\
            .infection_count


class GridExtended(part_a.Grid):
    """
    >>> print(GridExtended.from_grid_text(
    ...     '..#\\n#..\\n...').step_many(7).show(4, 4, False))
    . . . . . . . . .
    . . . . . . . . .
    . . . . . . . . .
    . . W W . # . . .
    .[.]# . W . . . .
    . . . . . . . . .
    . . . . . . . . .
    . . . . . . . . .
    . . . . . . . . .
    >>> GridExtended.from_grid_text(
    ...     '..#\\n#..\\n...').step_many(100).infection_count
    26
    >>> GridExtended.from_grid_text(
    ...     '..#\\n#..\\n...').step_many(10000000).infection_count
    2511944
    """
    STATE_WEAKENED = 'weakened'
    STATE_FLAGGED = 'flagged'
    STATES = part_a.Grid.STATES + [STATE_WEAKENED, STATE_FLAGGED]

    PARSE_MAP = {
        **part_a.Grid.PARSE_MAP,
        'W': STATE_WEAKENED,
        'F': STATE_FLAGGED,
    }

    SHOW_MAP = {
        content: state
        for state, content in PARSE_MAP.items()
    }

    def get_new_direction_for_state(self, state):
        if state == self.STATE_WEAKENED:
            return self.direction
        elif state == self.STATE_FLAGGED:
            return self.rotate_direction_left(
                self.rotate_direction_left(self.direction))
        else:
            return super().get_new_direction_for_state(state)

    def get_new_state_for_state(self, state):
        if state == self.STATE_CLEAN:
            return self.STATE_WEAKENED
        elif state == self.STATE_WEAKENED:
            return self.STATE_INFECTED
        elif state == self.STATE_INFECTED:
            return self.STATE_FLAGGED
        elif state == self.STATE_FLAGGED:
            return self.STATE_CLEAN
        else:
            raise Exception(f"Unknown state '{state}'")


challenge = Challenge()
challenge.main()
