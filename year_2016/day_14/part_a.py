#!/usr/bin/env python3
import re
from collections import Iterable
from dataclasses import dataclass
from itertools import count
from typing import Optional

from aox.utils import Timer

from utils import BaseChallenge, get_windows, get_md5_hex_hash


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        15035
        """
        return KeyGenerator(_input.strip()).get_nth_key_index(debug=debug)


@dataclass
class KeyGenerator:
    salt: str

    re_triple = re.compile(r".*?(.)\1{2}")
    re_quintuple = re.compile(r".*(.)\1{4}")

    def get_nth_key_index(self, _count: int = 64, start: int = 0,
                          window_size: int = 1000, debug: bool = False,
                          ) -> Optional[int]:
        """
        >>> KeyGenerator("abc").get_nth_key_index()
        22728
        """
        if _count < 1:
            return None
        keys = self.get_keys(_count, start, window_size, debug)
        for key_count, index, _ in keys:
            if key_count == _count:
                return index

        return None

    def get_keys(self, _count: Optional[int] = 64, start: int = 0,
                 window_size: int = 1000, debug: bool = False) -> Iterable[int]:
        windows = get_windows(self.get_all_hashes(start), window_size + 1)
        key_count = 0
        if debug:
            timer = Timer()
        for index, window in enumerate(windows):
            _hash, next_hashes = window[0], window[1:]
            if self.is_hash_a_key(_hash, next_hashes):
                key_count += 1
                yield key_count, index, _hash
                if _count is not None and key_count >= _count:
                    break

            if debug:
                if index % 1000 == 0:
                    print(
                        f"Count: {index}, time: "
                        f"{timer.get_pretty_current_duration()}, key count: "
                        f"{key_count}/{_count}")

    def get_all_hashes(self, start: int = 0) -> Iterable[str]:
        return map(self.get_hash, count(start))

    def is_hash_a_key(self, _hash: str, next_hashes: Iterable[str]) -> bool:
        """
        >>> KeyGenerator("").is_hash_a_key("abcdefgh", [])
        False
        >>> KeyGenerator("").is_hash_a_key("abcdeeefgh", [])
        False
        >>> KeyGenerator("").is_hash_a_key("abcdeeefgh", ["eeaaaaaeebbbbbee"])
        False
        >>> KeyGenerator("").is_hash_a_key(
        ...     "abcdeeefgh", ["eeaaaaaeeeeebbbbbee"])
        True
        >>> KeyGenerator("").is_hash_a_key(
        ...     "abcdeeefaaagh", ["eeaaaaaeebbbbbee"])
        False
        >>> KeyGenerator("").is_hash_a_key(
        ...     "abcdeeefaaagh", ["eeaaaaaeebbbbbee", "eeaaaaaeeeeebbbbbee"])
        True
        """
        first_triple_character_match = self.re_triple.match(_hash)
        if not first_triple_character_match:
            return False
        character, = first_triple_character_match.groups()
        quintuple = character * 5
        return any(
            quintuple in next_hash
            for next_hash in next_hashes
        )

    def is_hash_triple(self, _hash: str) -> bool:
        """
        >>> KeyGenerator("").is_hash_triple("abceeedfg")
        True
        >>> KeyGenerator("").is_hash_triple("abceee")
        True
        >>> KeyGenerator("").is_hash_triple("eeedfg")
        True
        >>> KeyGenerator("").is_hash_triple("abeecdeefg")
        False
        """
        return bool(self.re_triple.match(_hash))

    def is_hash_quintuple(self, _hash: str) -> bool:
        """
        >>> KeyGenerator("").is_hash_quintuple("abceeedfg")
        False
        >>> KeyGenerator("").is_hash_quintuple("abceee")
        False
        >>> KeyGenerator("").is_hash_quintuple("eeedfg")
        False
        >>> KeyGenerator("").is_hash_quintuple("abeecdeefg")
        False
        >>> KeyGenerator("").is_hash_quintuple("abceeeeedfg")
        True
        >>> KeyGenerator("").is_hash_quintuple("abceeeee")
        True
        >>> KeyGenerator("").is_hash_quintuple("eeeeedfg")
        True
        >>> KeyGenerator("").is_hash_quintuple("abeeeecdeeeefg")
        False
        """
        return bool(self.re_quintuple.match(_hash))

    def get_hash(self, index: int) -> str:
        """
        >>> KeyGenerator("abc").get_hash(18)
        '...cc38887a5...'
        >>> KeyGenerator("abc").get_hash(39)
        '...eee...'
        >>> KeyGenerator("abc").get_hash(816)
        '...eeeee...'
        """
        return get_md5_hex_hash(f"{self.salt}{index}")


Challenge.main()
challenge = Challenge()
