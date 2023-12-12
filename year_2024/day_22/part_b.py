#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_22 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1612
        """
        return MonkeySequenceSet.from_text(_input).get_best_pattern_sum(4, 2000)


@dataclass
class MonkeySequenceSet:
    sequences: List["MonkeySequenceExtended"]

    @classmethod
    def from_text(cls, text: str) -> "MonkeySequenceSet":
        """
        >>> len(MonkeySequenceSet.from_text('''
        ...     1
        ...     2
        ...     3
        ...     2024
        ... ''').sequences)
        4
        """
        return cls(sequences=list(map(MonkeySequenceExtended, MonkeySequenceExtended.parse_secrets(text))))

    def get_best_pattern_sum(self, pattern_length: int, max_count: int) -> int:
        """
        >>> MonkeySequenceSet.from_text('''
        ...     1
        ...     2
        ...     3
        ...     2024
        ... ''').get_best_pattern_sum(4, 2000)
        23
        """
        best_sum, _ = self.find_best_patterns(pattern_length, max_count)
        return best_sum

    def find_best_pattern(self, pattern_length: int, max_count: int) -> Tuple[int, ...]:
        """
        >>> MonkeySequenceSet.from_text('''
        ...     1
        ...     2
        ...     3
        ...     2024
        ... ''').find_best_pattern(4, 2000)
        (-2, 1, -1, 3)
        """
        _, best_patterns = self.find_best_patterns(pattern_length, max_count)
        if len(best_patterns) != 1:
            raise Exception(f"Expected 1 best pattern, got {len(best_patterns)}")
        best_pattern, = best_patterns
        return best_pattern

    def find_best_patterns(self, pattern_length: int, max_count: int) -> Tuple[int, Set[Tuple[int, ...]]]:
        """
        >>> MonkeySequenceSet.from_text('''
        ...     1
        ...     2
        ...     3
        ...     2024
        ... ''').find_best_patterns(4, 2000)
        (23, {(-2, 1, -1, 3)})
        """
        number_per_pattern_maps = [
            sequence.get_number_per_pattern(pattern_length, max_count)
            for sequence in self.sequences
        ]
        patterns = {
            pattern
            for number_per_pattern in number_per_pattern_maps
            for pattern in number_per_pattern
        }
        sum_per_pattern = {
            pattern: sum(
                number_per_pattern.get(pattern, 0)
                for number_per_pattern in number_per_pattern_maps
            )
            for pattern in patterns
        }
        max_sum = max(sum_per_pattern.values())
        return max_sum, {
            pattern
            for pattern, pattern_sum in sum_per_pattern.items()
            if pattern_sum == max_sum
        }


class MonkeySequenceExtended(part_a.MonkeySequence):
    def get_number_per_pattern(self, pattern_length: int, max_count: int) -> Dict[Tuple[int, ...], int]:
        pattern = ()
        digits_and_differences = iter(self.get_digits_and_differences(max_count))
        number_per_pattern: Dict[Tuple[int, ...], int] = {}
        for difference, digit in digits_and_differences:
            pattern = (pattern + (difference,))[-pattern_length:]
            if len(pattern) == pattern_length and pattern not in number_per_pattern:
                number_per_pattern[pattern] = digit
        return number_per_pattern

    def find_number_after_pattern(self, pattern: List[int], max_count: int) -> Optional[int]:
        """
        >>> MonkeySequenceExtended(123).find_number_after_pattern([-1, -1, 0, 2], 2000)
        6
        >>> MonkeySequenceExtended(1).find_number_after_pattern([-2, 1, -1, 3], 2000)
        7
        """
        last_n_numbers = []
        digits_and_differences = iter(self.get_digits_and_differences(max_count))
        for difference, digit in digits_and_differences:
            last_n_numbers.append(difference)
            if len(last_n_numbers) > len(pattern):
                last_n_numbers.pop(0)
            if last_n_numbers == pattern:
                return digit
        return None

    def get_digits_differences(self, count: int) -> Iterable[int]:
        """
        >>> list(MonkeySequenceExtended(123).get_digits_differences(10))
        [-3, 6, -1, -1, 0, 2, -2, 0, -2]
        """
        for difference, _ in self.get_digits_and_differences(count):
            yield difference

    def get_digits_and_differences(self, count: int) -> Iterable[Tuple[int, int]]:
        """
        >>> list(MonkeySequenceExtended(123).get_digits_and_differences(10))
        [(-3, 0), (6, 6), (-1, 5), (-1, 4), (0, 4), (2, 6), (-2, 4), (0, 4), (-2, 2)]
        """
        digits = iter(self.get_digits_sequence(count))
        previous_secret = next(digits)
        for secret in digits:
            yield secret - previous_secret, secret
            previous_secret = secret

    def get_digits_sequence(self, count: int) -> Iterable[int]:
        """
        >>> list(MonkeySequenceExtended(123).get_digits_sequence(10))
        [3, 0, 6, 5, 4, 4, 6, 4, 4, 2]
        """
        yield self.secret % 10
        for secret in self.get_next_many(count -1 ):
            yield secret % 10


Challenge.main()
challenge = Challenge()
