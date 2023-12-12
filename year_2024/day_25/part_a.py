#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import Iterable, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2835
        """
        return Facility.from_text(_input).get_matching_pair_count()


@dataclass
class Facility:
    keys: List["Key"]
    locks: List["Lock"]

    @classmethod
    def from_text(cls, text: str) -> "Facility":
        """
        >>> _facility = Facility.from_text(EXAMPLE_TEXT)
        >>> len(_facility.keys), len(_facility.locks)
        (3, 2)
        """
        blocks = text.strip().split("\n\n")
        keys = []
        locks = []
        for block in blocks:
            key = Key.maybe_from_text(block)
            if key:
                keys.append(key)
                continue
            lock = Lock.maybe_from_text(block)
            if not lock:
                raise Exception(f"Could not parse block:\n{block}")
            locks.append(lock)
        return cls(keys=keys, locks=locks)

    def get_matching_pair_count(self, max_size: int = 7) -> int:
        """
        >>> Facility.from_text(EXAMPLE_TEXT).get_matching_pair_count()
        3
        """
        return sum(
            1
            for _ in self.get_matching_pairs(max_size=max_size)
        )

    def get_matching_pairs(self, max_size: int = 7) -> Iterable[Tuple["Key", "Lock"]]:
        for key in self.keys:
            for lock in self.locks:
                if lock.fits(key, max_size=max_size):
                    yield key, lock


@dataclass
class Key:
    pins: List[int]

    re_key = re.compile(r"^\.+(#+)$")

    @classmethod
    def maybe_from_text(cls, text: str) -> Optional["Key"]:
        """
        >>> Key.maybe_from_text('''
        ...     #####
        ...     .####
        ...     .####
        ...     .####
        ...     .#.#.
        ...     .#...
        ...     .....
        ... ''')
        >>> Key.maybe_from_text('''
        ...     .....
        ...     #....
        ...     #....
        ...     #...#
        ...     #.#.#
        ...     #.###
        ...     #####
        ... ''')
        Key(pins=[6, 1, 3, 2, 4])
        """
        pins = cls.parse_pins(text, cls.re_key)
        if not pins:
            return None
        return cls(pins=pins)

    @classmethod
    def parse_pins(cls, text: str, regex: re.Pattern) -> Optional[List[int]]:
        stripped = list(map(str.strip, text.strip().splitlines()))
        columns = list(map(''.join, zip(*stripped)))
        matches = list(map(regex.match, columns))
        if not all(matches):
            return None
        return [len(pin_str) for match in matches for pin_str, in [match.groups()]]


@dataclass
class Lock:
    pins: List[int]

    re_lock = re.compile(r"^(#+)\.+$")

    @classmethod
    def maybe_from_text(cls, text: str) -> Optional["Lock"]:
        """
        >>> Lock.maybe_from_text('''
        ...     #####
        ...     .####
        ...     .####
        ...     .####
        ...     .#.#.
        ...     .#...
        ...     .....
        ... ''')
        Lock(pins=[1, 6, 4, 5, 4])
        >>> Lock.maybe_from_text('''
        ...     .....
        ...     #....
        ...     #....
        ...     #...#
        ...     #.#.#
        ...     #.###
        ...     #####
        ... ''')
        """
        pins = Key.parse_pins(text, cls.re_lock)
        if not pins:
            return None
        return cls(pins=pins)

    def fits(self, key: Key, max_size: int = 7) -> bool:
        if len(self.pins) != len(key.pins):
            return False
        return all(
            lock_pin + key_pin <= max_size
            for lock_pin, key_pin in zip(self.pins, key.pins)
        )


EXAMPLE_TEXT = """
    #####
    .####
    .####
    .####
    .#.#.
    .#...
    .....

    #####
    ##.##
    .#.##
    ...##
    ...#.
    ...#.
    .....

    .....
    #....
    #....
    #...#
    #.#.#
    #.###
    #####

    .....
    .....
    #.#..
    ###..
    ###.#
    ###.#
    #####

    .....
    .....
    .....
    #....
    #.#..
    #.#.#
    #####
"""



Challenge.main()
challenge = Challenge()
