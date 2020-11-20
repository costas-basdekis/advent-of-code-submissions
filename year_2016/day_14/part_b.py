#!/usr/bin/env python3
from dataclasses import dataclass

from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        19968
        """
        return KeyGeneratorExtended(_input.strip())\
            .get_nth_key_index(debug=debug)


@dataclass
class KeyGeneratorExtended(part_a.KeyGenerator):
    """
    >>> KeyGeneratorExtended("abc").get_nth_key_index()
    22859
    """
    extra_hash_iterations: int = 2016

    def get_hash(self, index: int) -> str:
        """
        >>> KeyGeneratorExtended("abc").get_hash(0)
        'a107ff634856bb300138cac6568c0f24'
        """
        _hash = super().get_hash(index)
        for _ in range(self.extra_hash_iterations):
            _hash = self.hash_text(_hash)

        return _hash


Challenge.main()
challenge = Challenge()
