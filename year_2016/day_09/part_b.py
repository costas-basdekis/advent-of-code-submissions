#!/usr/bin/env python3
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        10943094568
        """
        return DecompressorExtended().get_decompressed_length(_input)


class DecompressorExtended(part_a.Decompressor):
    def get_decompressed_length(self, text: str) -> int:
        """
        >>> DecompressorExtended().get_decompressed_length("    ADVENT   ")
        6
        >>> DecompressorExtended().get_decompressed_length("ADVENT")
        6
        >>> DecompressorExtended().get_decompressed_length("A(1x5)BC")
        7
        >>> DecompressorExtended().get_decompressed_length("(3x3)XYZ")
        9
        >>> DecompressorExtended().get_decompressed_length("A(2x2)BCD(2x2)EFG")
        11
        >>> DecompressorExtended().get_decompressed_length("(6x1)(1x3)A")
        3
        >>> DecompressorExtended().decompress("X(8x2)(3x3)ABCY")
        'X(3x3)ABC(3x3)ABCY'
        >>> DecompressorExtended().decompress(
        ...     DecompressorExtended().decompress("X(8x2)(3x3)ABCY"))
        'XABCABCABCABCABCABCY'
        >>> len(DecompressorExtended().decompress(
        ...     DecompressorExtended().decompress("X(8x2)(3x3)ABCY")))
        20
        >>> DecompressorExtended().get_decompressed_length("X(8x2)(3x3)ABCY")
        20
        >>> DecompressorExtended().get_decompressed_length(
        ...     "(27x12)(20x12)(13x14)(7x10)(1x12)A")
        241920
        >>> DecompressorExtended().get_decompressed_length(
        ...     "(25x3)(3x3)ABC(2x3)XY(5x2)PQRSTX(18x9)(3x2)TWO(5x7)SEVEN")
        445
        """
        length = 0
        for repeat_string, repeat_count in self.stream_decompress(text):
            if '(' in repeat_string:
                repeat_length = self.get_decompressed_length(repeat_string)
            else:
                repeat_length = len(repeat_string)
            length += repeat_length * repeat_count

        return length


Challenge.main()
challenge = Challenge()
