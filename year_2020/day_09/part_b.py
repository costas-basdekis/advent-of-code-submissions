#!/usr/bin/env python3
import utils

from year_2020.day_09 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        104800569
        """
        encrypted = DecoderExtended.read_encrypted_text(_input)
        return DecoderExtended(25).find_weakness(encrypted)


class DecoderExtended(part_a.Decoder):
    def find_weakness(self, encrypted):
        """
        >>> encrypted_a = (
        ...     35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182,
        ...     127, 219, 299, 277, 309, 576)
        >>> DecoderExtended(5).find_weakness(encrypted_a)
        62
        """
        number, _range = self.find_weakness_range(encrypted)
        if number is None:
            return None

        return min(_range) + max(_range)

    def find_weakness_range(self, encrypted):
        """
        >>> encrypted_a = (
        ...     35, 20, 15, 25, 47, 40, 62, 55, 65, 95, 102, 117, 150, 182,
        ...     127, 219, 299, 277, 309, 576)
        >>> DecoderExtended(5).find_weakness_range(encrypted_a)
        (127, (15, 25, 47, 40))
        """
        number = self.get_first_number_that_is_not_a_sum(encrypted)
        position = encrypted.index(number)
        for start in range(0, position):
            total = encrypted[start]
            if total == number:
                return number, encrypted[start:start + 1]
            if total > number:
                continue
            for end in range(start + 1, position):
                total += encrypted[end]
                if total == number:
                    return number, encrypted[start:end + 1]
                if total > number:
                    break

        return None, None


Challenge.main()
challenge = Challenge()
