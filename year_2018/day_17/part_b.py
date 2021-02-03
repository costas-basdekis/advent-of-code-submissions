#!/usr/bin/env python3
import utils
from year_2018.day_17 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        22182
        """
        ground = GroundExtended.from_ground_text(_input)
        ground.step_many()
        return ground.get_settled_water_reach()


class GroundExtended(part_a.Ground):
    def get_settled_water_reach(self):
        """
        >>> GroundExtended.from_visual(
        ...     ".....+......\\n"
        ...     ".....|.....#\\n"
        ...     "#..#||||...#\\n"
        ...     "#..#~~#|....\\n"
        ...     "#..#~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#######|....\\n"
        ...     ".......|....\\n"
        ...     "..|||||||||.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#######|.\\n"
        ... , spring_water_points=False).get_settled_water_reach()
        29
        >>> GroundExtended.from_visual(
        ...     ".....+......\\n"
        ...     ".....|......\\n"
        ...     "#..#||||...#\\n"
        ...     "#..#~~#|....\\n"
        ...     "#..#~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#######|....\\n"
        ...     ".......|....\\n"
        ...     "..|||||||||.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#######|.\\n"
        ... , spring_water_points=False).get_settled_water_reach()
        29
        """
        return len(self.settled_water)


Challenge.main()
challenge = Challenge()
