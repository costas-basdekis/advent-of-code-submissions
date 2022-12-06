#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Iterable, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1723
        """
        return Stream.from_stream_text(_input).get_start_offset()


@dataclass
class Stream:
    characters: str

    @classmethod
    def from_stream_text(cls, stream_text: str) -> "Stream":
        """
        >>> Stream.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")
        Stream(characters='mjqjpqmgbljsphdztnvjfqwrcgsmlb')
        """
        return cls(characters=stream_text.strip())

    def get_start_offset(self) -> int:
        """
        >>> Stream.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")\\
        ...     .get_start_offset()
        7
        >>> Stream.from_stream_text("bvwbjplbgvbhsrlpgdmjqwftvncz")\\
        ...     .get_start_offset()
        5
        >>> Stream.from_stream_text("nppdvjthqldpwncqszvftbrmjlhg")\\
        ...     .get_start_offset()
        6
        >>> Stream.from_stream_text("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg")\\
        ...     .get_start_offset()
        10
        >>> Stream.from_stream_text("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw")\\
        ...     .get_start_offset()
        11
        """
        for start_index, packet in self.iterate_packets():
            if self.is_start_of_packet_marker(packet):
                return start_index + 4

        raise Exception("Could not find start offset")

    def iterate_packets(self) -> Iterable[Tuple[int, str]]:
        """
        >>> list(Stream.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")
        ...      .iterate_packets())
        [(0, 'mjqj'), (1, 'jqjp'), (2, 'qjpq'), (3, 'jpqm'), ...]
        """
        for start_index in range(0, len(self.characters) - 4 + 1):
            packet = self.characters[start_index:start_index + 4]
            yield start_index, packet

    def is_start_of_packet_marker(self, packet: str) -> bool:
        """
        >>> Stream("").is_start_of_packet_marker("mjq")
        False
        >>> Stream("").is_start_of_packet_marker("mjqj")
        False
        >>> Stream("").is_start_of_packet_marker("jpqm")
        True
        """
        return len(packet) == 4 and len(set(packet)) == 4


Challenge.main()
challenge = Challenge()
