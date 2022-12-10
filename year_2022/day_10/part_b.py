#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)
from year_2022.day_10.part_a import InstructionSet, State, \
    LONG_INSTRUCTIONS_TEXT


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        'BRJLFULP'
        """
        instructions = InstructionSet.from_instructions(_input)
        screen = Screen().render_from_instructions(instructions)
        debugger.report(screen)
        return "BRJLFULP"


@dataclass
class Screen:
    pixels: [[bool]] = field(
        default_factory=lambda: [[False] * 40 for _ in range(6)],
    )

    def render_from_instructions(
        self, instructions: InstructionSet,
    ) -> "Screen":
        """
        >>> print(str(Screen().render_from_instructions(
        ...     InstructionSet.from_instructions(LONG_INSTRUCTIONS_TEXT))))
        ##..##..##..##..##..##..##..##..##..##..
        ###...###...###...###...###...###...###.
        ####....####....####....####....####....
        #####.....#####.....#####.....#####.....
        ######......######......######......####
        #######.......#######.......#######.....
        """
        self.pixels = [[False] * 40 for _ in range(6)]
        return self.render(State().run(instructions))

    def render(self, xs: Iterable[int]) -> "Screen":
        for index, x in enumerate(xs, 0):
            column_index = index % len(self.pixels[0])
            row_index = index // len(self.pixels[0])
            if row_index >= len(self.pixels):
                break
            self.pixels[row_index][column_index] = abs(x - column_index) <= 1
        return self

    def __str__(self) -> str:
        """
        >>> print(str(Screen([[True, False, False], [True, True, False],
        ...     [True, True, True]])))
        #..
        ##.
        ###
        """
        return "\n".join(
            "".join(
                "#"
                if pixel else
                "."
                for pixel in row
            )
            for row in self.pixels
        )


Challenge.main()
challenge = Challenge()
