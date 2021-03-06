#!/usr/bin/env python3
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        842
        """
        return BoardingPasses.from_passes_text(_input).get_highest_seat_id()


class BoardingPass(namedtuple("BoardingPass", ("name",))):
    @classmethod
    def from_pass_text(cls, pass_text):
        """
        >>> BoardingPass.from_pass_text("FBFBBFFRLR")
        BoardingPass(name='FBFBBFFRLR')
        """
        return cls(pass_text.strip())

    def get_seat_id(self):
        """
        >>> BoardingPass("FBFBBFFRLR").get_seat_id()
        357
        >>> BoardingPass("BFFFBBFRRR").get_seat_id()
        567
        >>> BoardingPass("FFFBBBFRRR").get_seat_id()
        119
        >>> BoardingPass("BBFFBBFRLL").get_seat_id()
        820
        """
        binary_id_str = self.name\
            .replace("F", "0")\
            .replace("B", "1")\
            .replace("L", "0")\
            .replace("R", "1")
        return int(binary_id_str, base=2)


class BoardingPasses:
    boarding_pass_class = BoardingPass

    @classmethod
    def from_passes_text(cls, passes_text):
        """
        >>> BoardingPasses.from_passes_text(
        ...     "FBFBBFFRLR\\n"
        ...     "BFFFBBFRRR\\n"
        ...     "FFFBBBFRRR\\n"
        ...     "BBFFBBFRLL\\n"
        ... ).passes
        [BoardingPass(name='FBFBBFFRLR'), BoardingPass(name='BFFFBBFRRR'), BoardingPass(name='FFFBBBFRRR'), BoardingPass(name='BBFFBBFRLL')]
        """
        lines = passes_text.splitlines()
        non_empty_lines = filter(None, lines)
        return cls(list(map(
            cls.boarding_pass_class.from_pass_text, non_empty_lines)))

    def __init__(self, passes):
        self.passes = passes

    def get_highest_seat_id(self):
        """
        >>> BoardingPasses([
        ...     BoardingPass('FBFBBFFRLR'), BoardingPass('BFFFBBFRRR'),
        ...     BoardingPass('FFFBBBFRRR'), BoardingPass('BBFFBBFRLL')])\\
        ...     .get_highest_seat_id()
        820
        """
        return max(map(self.boarding_pass_class.get_seat_id, self.passes))


Challenge.main()
challenge = Challenge()
