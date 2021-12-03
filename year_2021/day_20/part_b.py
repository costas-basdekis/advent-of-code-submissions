#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_20.part_a import Image


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        17917
        """
        algorithm, image = Image.from_mapping_and_image_text(_input)
        return image\
            .step_many(algorithm, 50, debugger=debugger)\
            .light_pixel_count


Challenge.main()
challenge = Challenge()
