#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Iterable, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1723
        """
        return Stream.from_stream_text(_input).get_packet_start_offset()


@dataclass
class Stream:
    characters: str

    @classmethod
    def from_stream_text(
        cls: Cls["Stream"], stream_text: str,
    ) -> Self["Stream"]:
        """
        >>> Stream.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")
        Stream(characters='mjqjpqmgbljsphdztnvjfqwrcgsmlb')
        """
        return cls(characters=stream_text.strip())

    def get_packet_start_offset(self) -> int:
        """
        >>> Stream.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")\\
        ...     .get_packet_start_offset()
        7
        >>> Stream.from_stream_text("bvwbjplbgvbhsrlpgdmjqwftvncz")\\
        ...     .get_packet_start_offset()
        5
        >>> Stream.from_stream_text("nppdvjthqldpwncqszvftbrmjlhg")\\
        ...     .get_packet_start_offset()
        6
        >>> Stream.from_stream_text("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg")\\
        ...     .get_packet_start_offset()
        10
        >>> Stream.from_stream_text("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw")\\
        ...     .get_packet_start_offset()
        11
        """
        return self.get_start_offset(4)

    def get_start_offset(self, size) -> int:
        for start_index, packet in self.iterate_packets(size=size):
            if self.is_start_of_packet_marker(packet, size=size):
                return start_index + size

        raise Exception("Could not find start offset")

    def iterate_packets(self, size: int = 4) -> Iterable[Tuple[int, str]]:
        """
        >>> list(Stream.from_stream_text("mjqjpqmgbljsphdztnvjfqwrcgsmlb")
        ...      .iterate_packets())
        [(0, 'mjqj'), (1, 'jqjp'), (2, 'qjpq'), (3, 'jpqm'), ...]
        """
        for start_index in range(0, len(self.characters) - size + 1):
            packet = self.characters[start_index:start_index + size]
            yield start_index, packet

    def is_start_of_packet_marker(self, packet: str, size: int = 4) -> bool:
        """
        >>> Stream("").is_start_of_packet_marker("mjq")
        False
        >>> Stream("").is_start_of_packet_marker("mjqj")
        False
        >>> Stream("").is_start_of_packet_marker("jpqm")
        True
        """
        return len(packet) == size and len(set(packet)) == size


Challenge.main()
challenge = Challenge()
