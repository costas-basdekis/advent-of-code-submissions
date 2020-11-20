#!/usr/bin/env python3
import re
from typing import Optional, Tuple

from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        99145
        """
        return Decompressor().get_decompressed_length(_input)


class Decompressor:
    re_marker = re.compile(r"^\((\d+)x(\d+)\)")

    def get_decompressed_length(self, text: str) -> int:
        """
        >>> Decompressor().get_decompressed_length("    ADVENT   ")
        6
        >>> Decompressor().get_decompressed_length("ADVENT")
        6
        >>> Decompressor().get_decompressed_length("A(1x5)BC")
        7
        >>> Decompressor().get_decompressed_length("(3x3)XYZ")
        9
        >>> Decompressor().get_decompressed_length("A(2x2)BCD(2x2)EFG")
        11
        >>> Decompressor().get_decompressed_length("(6x1)(1x3)A")
        6
        >>> Decompressor().get_decompressed_length("X(8x2)(3x3)ABCY")
        18
        """
        return len(self.decompress(text))

    def decompress(self, text: str) -> str:
        """
        >>> Decompressor().decompress("    ADVENT   ")
        'ADVENT'
        >>> Decompressor().decompress("ADVENT")
        'ADVENT'
        >>> Decompressor().decompress("A(1x5)BC")
        'ABBBBBC'
        >>> Decompressor().decompress("(3x3)XYZ")
        'XYZXYZXYZ'
        >>> Decompressor().decompress("A(2x2)BCD(2x2)EFG")
        'ABCBCDEFEFG'
        >>> Decompressor().decompress("(6x1)(1x3)A")
        '(1x3)A'
        >>> Decompressor().decompress("X(8x2)(3x3)ABCY")
        'X(3x3)ABC(3x3)ABCY'
        """
        text = text.strip()
        position = 0
        result = ""
        while position < len(text):
            marker = self.get_marker(text[position:])
            if not marker:
                result += text[position]
                position += 1
                continue
            repeat_length, repeat_count, marker_length = marker
            position += marker_length
            repeat_string = text[position:position + repeat_length]
            position += repeat_length
            result += repeat_string * repeat_count

        return result

    def get_marker(self, text: str) -> Optional[Tuple[int, int, int]]:
        """
        >>> Decompressor().get_marker("A(1x5)BC")
        >>> Decompressor().get_marker("(1x5)BC")
        (1, 5, 5)
        """
        match = self.re_marker.match(text)
        if not match:
            return None
        repeat_length_str, repeat_count_str = match.groups()
        repeat_length = int(repeat_length_str)
        repeat_count = int(repeat_count_str)

        return repeat_length, repeat_count, len(match.group())


Challenge.main()
challenge = Challenge()
