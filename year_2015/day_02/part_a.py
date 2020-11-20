#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Tuple, Generic, Type, List

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1598415
        """
        return PresentSet.from_presents_text(_input)\
            .get_wrapping_paper_requirement()


PresentT = TV['Present']


@dataclass
class PresentSet(Generic[PresentT]):
    presents: List[PresentT]

    @classmethod
    def get_present_class(cls) -> Type[PresentT]:
        return get_type_argument_class(cls, PresentT)

    @classmethod
    def from_presents_text(cls, presents_text: str):
        """
        >>> PresentSet.from_presents_text("2x3x4\\n1x1x10\\n")
        PresentSet(presents=[Present(dimensions=(2, 3, 4)),
            Present(dimensions=(1, 1, 10))])
        """
        present_class = cls.get_present_class()
        return cls(list(map(
            present_class.from_present_text, presents_text.splitlines())))

    def get_wrapping_paper_requirement(self) -> int:
        """
        >>> PresentSet([]).get_wrapping_paper_requirement()
        0
        >>> PresentSet.from_presents_text("2x3x4\\n1x1x10\\n")\\
        ...     .get_wrapping_paper_requirement()
        101
        """
        return sum(
            present.get_wrapping_paper_requirement()
            for present in self.presents
        )


@dataclass
class Present:
    dimensions: Tuple[int, int, int]

    re_present = re.compile(r"^(\d+)x(\d+)x(\d+)$")

    @classmethod
    def from_present_text(cls, present_text: str):
        """
        >>> Present.from_present_text("2x3x4")
        Present(dimensions=(2, 3, 4))
        >>> Present.from_present_text("4x2x3")
        Present(dimensions=(2, 3, 4))
        """
        a_str, b_str, c_str = cls.re_present.match(present_text).groups()
        return cls((int(a_str), int(b_str), int(c_str)))

    def __post_init__(self):
        """
        >>> Present((1, 2, 3))
        Present(dimensions=(1, 2, 3))
        >>> Present((3, 2, 1))
        Present(dimensions=(1, 2, 3))
        """
        # noinspection PyTypeChecker
        self.dimensions = tuple(sorted(self.dimensions))

    def get_wrapping_paper_requirement(self) -> int:
        """
        >>> Present.from_present_text("2x3x4").get_wrapping_paper_requirement()
        58
        >>> Present.from_present_text("1x1x10").get_wrapping_paper_requirement()
        43
        """
        a, b, c = self.dimensions

        return 2 * (a * b + a * c + b * c) + a * b


Challenge.main()
challenge = Challenge()
