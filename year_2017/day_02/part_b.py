#!/usr/bin/env python3
import itertools

import utils
from year_2017.day_02 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        250
        """
        return SpreadsheetExtended.from_text(_input).get_even_checksum()


class SpreadsheetExtended(part_a.Spreadsheet):
    def get_even_checksum(self):
        """
        >>> SpreadsheetExtended.from_text((
        ...     "5 9 2 8\\n"
        ...     "9 4 7 3\\n"
        ...     "3 8 6 5\\n"
        ... ).replace(' ', '\\t')).get_even_checksum()
        9
        """
        return sum(map(self.get_line_even_checksum, self.cells))

    def get_line_even_checksum(self, line):
        """
        >>> SpreadsheetExtended(()).get_line_even_checksum((5, 9, 2, 8))
        4
        """
        non_co_primes = self.get_non_co_primes(line)
        if len(non_co_primes) != 2:
            raise Exception(
                f"Expected exactly 2 non-co-primes but got "
                f"{len(non_co_primes)} in {line}")

        smaller, larger = non_co_primes

        return larger // smaller

    def get_non_co_primes(self, line):
        """
        >>> SpreadsheetExtended(()).get_non_co_primes((5, 9, 2, 8))
        [2, 8]
        >>> SpreadsheetExtended(()).get_non_co_primes((5, 9, 2, 8, 4))
        [2, 4, 8]
        """
        return sorted({
            value
            for smaller, larger in itertools.combinations(sorted(line), 2)
            if larger % smaller == 0
            for value in (smaller, larger)
        })


Challenge.main()
challenge = Challenge()
