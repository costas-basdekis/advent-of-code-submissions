#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        47136
        """
        return Spreadsheet.from_text(_input).get_checksum()


class Spreadsheet:
    @classmethod
    def from_text(cls, text):
        """
        >>> Spreadsheet.from_text((
        ...     "5 1 9 5\\n"
        ...     "7 5 3\\n"
        ...     "2 4 6 8\\n"
        ... ).replace(' ', '\\t')).cells
        ((5, 1, 9, 5), (7, 5, 3), (2, 4, 6, 8))
        """
        return cls(tuple(
            tuple(map(int, line.strip().split('\t')))
            for line in text.strip().splitlines()
        ))

    def __init__(self, cells):
        self.cells = cells

    def get_checksum(self):
        """
        >>> Spreadsheet.from_text((
        ...     "5 1 9 5\\n"
        ...     "7 5 3\\n"
        ...     "2 4 6 8\\n"
        ... ).replace(' ', '\\t')).get_checksum()
        18
        """
        return sum(map(self.get_line_checksum, self.cells))

    def get_line_checksum(self, line):
        """
        >>> Spreadsheet(()).get_line_checksum((1, 5, -3, 10, 2))
        13
        """
        min_value = min(line)
        max_value = max(line)

        return max_value - min_value


Challenge.main()
challenge = Challenge()
