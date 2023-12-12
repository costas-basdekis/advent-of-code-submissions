#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Iterable, List, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        13584398738
        """
        return MonkeySequence.get_sum_of_nths_from_text(_input, 2000)


@dataclass
class MonkeySequence:
    secret: int

    @classmethod
    def get_sum_of_nths_from_text(cls, text: str, count: int) -> int:
        """
        >>> MonkeySequence.get_sum_of_nths_from_text('''
        ...     1
        ...     10
        ...     100
        ...     2024
        ... ''', 2000)
        37327623
        """
        return cls.get_sum_of_nths(cls.parse_secrets(text), count)

    @classmethod
    def parse_secrets(cls, text: str) -> List[int]:
        """
        >>> MonkeySequence.parse_secrets('''
        ...     1
        ...     10
        ...     100
        ...     2024
        ... ''')
        [1, 10, 100, 2024]
        """
        return list(map(int, map(str.strip, text.strip().splitlines())))

    @classmethod
    def get_sum_of_nths(cls, secrets: List[int], count: int) -> int:
        """
        >>> MonkeySequence.get_sum_of_nths([1, 10, 100, 2024], 2000)
        37327623
        """
        return sum(
            MonkeySequence(secret).get_nth(count)
            for secret in secrets
        )

    def get_nth(self, count: int, secret: Optional[int] = None) -> int:
        """
        >>> MonkeySequence(1).get_nth(2000)
        8685429
        """
        if secret is None:
            secret = self.secret
        for secret in self.get_next_many(count, secret=secret):
            pass
        return secret

    def get_next_many(self, count: int, secret: Optional[int] = None) -> Iterable[int]:
        """
        >>> list(MonkeySequence(123).get_next_many(10))
        [15887950, 16495136, 527345, 704524, 1553684, 12683156, 11100544, 12249484, 7753432, 5908254]
        """
        if secret is None:
            secret = self.secret
        for _ in range(count):
            secret = self.get_next(secret)
            yield secret

    def get_next(self, secret: Optional[int] = None) -> int:
        """
        >>> MonkeySequence(123).get_next()
        15887950
        """
        if secret is None:
            secret = self.secret
        secret = self.mix_and_prune(secret, secret * 64)
        secret = self.mix_and_prune(secret, secret // 32)
        secret = self.mix_and_prune(secret, secret * 2048)
        return secret

    def mix_and_prune(self, secret: int, number: int) -> int:
        secret = self.mix(secret, number)
        secret = self.prune(secret)
        return secret

    def mix(self, secret: int, number: int) -> int:
        """
        >>> MonkeySequence(123).mix(42, 15)
        37
        """
        return secret ^ number

    def prune(self, secret: int) -> int:
        """
        >>> MonkeySequence(123).prune(100000000)
        16113920
        """
        return secret % 16777216


Challenge.main()
challenge = Challenge()
