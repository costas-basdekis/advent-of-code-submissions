#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from typing import List, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        22887907
        """
        firewall = Firewall.from_ranges_text(_input)
        if debugger.should_report():
            debugger.report(f"Total range: {firewall.total_range}")
            for _range in firewall.blocked_ranges:
                debugger.report(f"  {_range}")
        return firewall.get_lowest_non_blocked_value()


@dataclass
class Firewall:
    blocked_ranges: List[range] = field(default_factory=list)
    total_range: range = range(4294967295 + 1)

    re_range = re.compile(r"^(\d+)-(\d+)$")

    @classmethod
    def from_ranges_text(cls, ranges_text: str,
                         total_range: range = total_range):
        """
        >>> Firewall.from_ranges_text((
        ...     "5-8\\n"
        ...     "0-2\\n"
        ...     "4-7\\n"
        ... ), range(10))
        Firewall(blocked_ranges=[range(0, 3), range(4, 9)],
            total_range=range(0, 10))
        """
        ranges = map(cls.parse_range, ranges_text.splitlines())
        return cls([], total_range).block_ranges(ranges)

    @classmethod
    def parse_range(cls, range_text: str) -> range:
        """
        >>> Firewall.parse_range('5-8')
        range(5, 9)
        >>> list(Firewall.parse_range('5-8'))
        [5, 6, 7, 8]
        >>> Firewall.parse_range('1562116064-1563502746')
        range(1562116064, 1563502747)
        """
        start_str, end_str = cls.re_range.match(range_text).groups()
        start, end = int(start_str), int(end_str)
        if start > end:
            raise Exception(f"Got inverse range '{range_text}'")
        elif start == end:
            raise Exception(f"Got empty range '{range_text}'")

        return range(start, end + 1)

    def get_lowest_non_blocked_value(self) -> int:
        """
        >>> Firewall.from_ranges_text((
        ...     "5-8\\n"
        ...     "0-2\\n"
        ...     "4-7\\n"
        ... ), range(10)).get_lowest_non_blocked_value()
        3
        """
        if not self.blocked_ranges:
            return self.total_range.start
        first_range = self.blocked_ranges[0]
        if self.total_range.start < first_range.start:
            return self.total_range.start
        if first_range.stop >= self.total_range.stop:
            raise Exception(f"No values are allowed")
        return first_range.stop

    def block_ranges(self, new_ranges: Iterable[range]):
        for new_range in new_ranges:
            self.block_range(new_range)

        return self

    def block_range(self, new_range: range):
        """
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))
        Firewall(blocked_ranges=[range(3, 5), range(10, 15)], total_range=...)
        >>> Firewall().block_range(range(10, 15)).block_range(range(3, 5))
        Firewall(blocked_ranges=[range(3, 5), range(10, 15)], total_range=...)
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))\\
        ...     .block_range(range(6, 9))
        Firewall(blocked_ranges=[range(3, 5), range(6, 9), range(10, 15)],
            total_range=...)
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))\\
        ...     .block_range(range(4, 11))
        Firewall(blocked_ranges=[range(3, 15)], total_range=...)
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))\\
        ...     .block_range(range(11, 13))
        Firewall(blocked_ranges=[range(3, 5), range(10, 15)], total_range=...)
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))\\
        ...     .block_range(range(9, 16))
        Firewall(blocked_ranges=[range(3, 5), range(9, 16)], total_range=...)
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))\\
        ...     .block_range(range(5, 16))
        Firewall(blocked_ranges=[range(3, 16)], total_range=...)
        >>> Firewall().block_range(range(3, 5)).block_range(range(10, 15))\\
        ...     .block_range(range(5, 10))
        Firewall(blocked_ranges=[range(3, 15)], total_range=...)
        """
        overlapping_ranges = [
            _range
            for _range in self.blocked_ranges
            if self.do_ranges_overlap_or_touch(new_range, _range)
        ]
        if not overlapping_ranges:
            self.blocked_ranges = self.sort_ranges(
                self.blocked_ranges + [new_range])
            return self

        ranges_to_merge = overlapping_ranges + [new_range]
        min_start = min(
            _range.start
            for _range in ranges_to_merge
        )
        max_stop = max(
            _range.stop
            for _range in ranges_to_merge
        )
        new_range = range(min_start, max_stop)
        self.blocked_ranges = self.sort_ranges(
            set(self.blocked_ranges)
            - set(ranges_to_merge)
            | {new_range}
        )

        return self

    def sort_ranges(self, ranges: Iterable[range]):
        """
        >>> Firewall().sort_ranges([])
        []
        >>> Firewall().sort_ranges([range(5), range(3), range(2)])
        [range(0, 2), range(0, 3), range(0, 5)]
        >>> Firewall().sort_ranges([range(5), range(3, 7), range(-4, 10)])
        [range(-4, 10), range(0, 5), range(3, 7)]
        """
        return sorted(ranges, key=lambda _range: (_range.position, _range.stop))

    def do_ranges_overlap_or_touch(self, lhs: range, rhs: range):
        """
        >>> Firewall().do_ranges_overlap_or_touch(range(5), range(7, 10))
        False
        >>> Firewall().do_ranges_overlap_or_touch(range(5), range(5, 10))
        True
        >>> Firewall().do_ranges_overlap_or_touch(range(5), range(4, 10))
        True
        >>> Firewall().do_ranges_overlap_or_touch(range(5), range(2))
        True
        >>> Firewall().do_ranges_overlap_or_touch(range(7, 10), range(5))
        False
        >>> Firewall().do_ranges_overlap_or_touch(range(5, 10), range(5))
        True
        >>> Firewall().do_ranges_overlap_or_touch(range(4, 10), range(5))
        True
        >>> Firewall().do_ranges_overlap_or_touch(range(2), range(5))
        True
        """
        if not (lhs.step == rhs.step == 1):
            raise Exception(
                f"Can only compare ranges with step 1, not {lhs} and {rhs}")
        return (
            lhs.stop >= rhs.start
            and rhs.stop >= lhs.start
        )


Challenge.main()
challenge = Challenge()
