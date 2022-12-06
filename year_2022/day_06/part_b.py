#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_06 import part_a
from year_2022.day_06.part_a import Stream


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3708
        """
        return StreamExtended\
            .from_stream_text(_input)\
            .get_message_start_offset()


class StreamExtended(Stream):
    def get_message_start_offset(self):
        """
        >>> StreamExtended.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")\\
        ...     .get_message_start_offset()
        19
        >>> StreamExtended.from_stream_text("bvwbjplbgvbhsrlpgdmjqwftvncz")\\
        ...     .get_message_start_offset()
        23
        >>> StreamExtended.from_stream_text("nppdvjthqldpwncqszvftbrmjlhg")\\
        ...     .get_message_start_offset()
        23
        >>> StreamExtended\\
        ...     .from_stream_text("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg")\\
        ...     .get_message_start_offset()
        29
        >>> StreamExtended\\
        ...     .from_stream_text("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw")\\
        ...     .get_message_start_offset()
        26
        """
        return self.get_start_offset(14)


Challenge.main()
challenge = Challenge()
