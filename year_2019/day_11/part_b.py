#!/usr/bin/env python3
import utils

from year_2019.day_11.part_a import paint_panels
import year_2019.day_09.part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> print("\\n".join(filter(None, (
        ...     line.strip()
        ...     for line in Challenge().default_solve().splitlines()
        ... ))))
        #  #   ##  ##  #      ## #### #### #  #
        #  #    # #  # #       #    # #    #  #
        ####    # #  # #       #   #  ###  ####
        #  #    # #### #       #  #   #    #  #
        #  # #  # #  # #    #  # #    #    #  #
        #  #  ##  #  # ####  ##  #### #    #  #
        """
        paint_map = paint_panels(_input, {(0, 0): 1})

        return f"\n{show_paint_map(paint_map)}"


def show_paint_map(paint_map):
    xs = [point[0] for point in paint_map]
    min_x = min(xs)
    max_x = max(xs)
    ys = [point[1] for point in paint_map]
    min_y = min(ys)
    max_y = max(ys)

    return "\n".join(
        "".join(
            '#' if paint_map.get((x, y), 0) == 1 else ' '
            for x in range(min_x, max_x + 1)
        )
        for y in range(min_y, max_y + 1)
    )


Challenge.main()
challenge = Challenge()
