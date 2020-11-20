#!/usr/bin/env python3
from dataclasses import dataclass
from itertools import count

from aox.challenge import Debugger
from utils import BaseChallenge, get_md5_hex_hash


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        254575
        """
        return Hasher(_input.strip())\
            .get_lowest_index_with_zeros(debugger=debugger)


@dataclass
class Hasher:
    secret_key: str

    def get_lowest_index_with_zeros(
            self, start: int = 1, zero_count: int = 5,
            debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> Hasher("abcdef").get_lowest_index_with_zeros()
        609043
        >>> Hasher("pqrstuv").get_lowest_index_with_zeros()
        1048970
        """
        prefix = '0' * zero_count
        debugger.reset()
        for index in debugger.stepping(count(start)):
            if self.does_index_give_hash_prefix(index, prefix):
                return index
            debugger.default_report_if(index)

    def does_index_give_hash_prefix(self, index: int,
                                    prefix: str = "0" * 5) -> bool:
        """
        >>> Hasher("abcdef").does_index_give_hash_prefix(1)
        False
        >>> Hasher("abcdef").does_index_give_hash_prefix(609043)
        True
        >>> Hasher("pqrstuv").does_index_give_hash_prefix(1)
        False
        >>> Hasher("pqrstuv").does_index_give_hash_prefix(1048970)
        True
        """
        return self.get_index_hash(index)[:len(prefix)] == prefix

    def get_index_hash(self, index: int) -> str:
        """
        >>> Hasher("abcdef").get_index_hash(609043)
        '000001dbbfa...'
        >>> Hasher("pqrstuv").get_index_hash(1048970)
        '000006136ef...'
        """
        return get_md5_hex_hash(f"{self.secret_key}{index}")


Challenge.main()
challenge = Challenge()
