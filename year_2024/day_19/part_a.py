#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        283
        """
        return Onsen.from_text(_input).get_possible_pattern_count()


@dataclass
class Onsen:
    source_patterns: Set[str]
    target_patterns: List[str]

    @classmethod
    def from_text(cls, text: str) -> "Onsen":
        """
        >>> Onsen.from_text('''
        ...     r, wr, b, g, bwu, rb, gb, br
        ...
        ...     brwrr
        ...     bggr
        ...     gbbr
        ...     rrbgbr
        ...     ubwu
        ...     bwurrg
        ...     brgr
        ...     bbrgwb
        ... ''')
        Onsen(source_patterns={...'bwu'...}, target_patterns=['brwrr', ..., 'bbrgwb'])
        """
        source_str, target_str = text.strip().split("\n\n")
        source_patterns = set(source_str.strip().split(", "))
        target_patterns = list(map(str.strip, target_str.strip().splitlines()))
        return cls(source_patterns=source_patterns, target_patterns=target_patterns)

    def get_possible_pattern_count(self) -> int:
        """
        >>> Onsen.from_text('''
        ...     r, wr, b, g, bwu, rb, gb, br
        ...
        ...     brwrr
        ...     bggr
        ...     gbbr
        ...     rrbgbr
        ...     ubwu
        ...     bwurrg
        ...     brgr
        ...     bbrgwb
        ... ''').get_possible_pattern_count()
        6
        """
        return sum(1 for _ in self.get_possible_patterns())

    def get_possible_patterns(self) -> Iterable[str]:
        """
        >>> list(Onsen.from_text('''
        ...     r, wr, b, g, bwu, rb, gb, br
        ...
        ...     brwrr
        ...     bggr
        ...     gbbr
        ...     rrbgbr
        ...     ubwu
        ...     bwurrg
        ...     brgr
        ...     bbrgwb
        ... ''').get_possible_patterns())
        ['brwrr', 'bggr', 'gbbr', 'rrbgbr', 'bwurrg', 'brgr']
        """
        cache: Dict[str, bool] = {}
        for pattern in self.target_patterns:
            if self.is_pattern_possible(pattern, cache):
                yield pattern

    def is_pattern_possible(self, target: str, cache: Optional[Dict[str, bool]] = None) -> bool:
        if target in self.source_patterns:
            return True
        if cache and target in cache:
            return cache[target]
        queue = [(target, [target])]
        seen = {target}
        found_path = None
        while queue:
            pattern, path = queue.pop(0)
            any_sub_pattern_possible = False
            for source in self.source_patterns:
                if not pattern.startswith(source):
                    if cache:
                        cache[pattern] = False
                    continue
                next_pattern = pattern[len(source):]
                if cache and next_pattern in cache:
                    if cache[next_pattern]:
                        found_path = path + [next_pattern]
                        break
                    continue
                if next_pattern in self.source_patterns:
                    found_path = path + [next_pattern]
                    break
                if next_pattern in seen:
                    continue
                seen.add(next_pattern)
                queue.append((next_pattern, path + [next_pattern]))
                any_sub_pattern_possible = True
            if cache and not any_sub_pattern_possible:
                cache[pattern] = False
            if found_path:
                break
        if cache and found_path:
            for pattern in found_path:
                cache[pattern] = True
        return bool(found_path)


Challenge.main()
challenge = Challenge()
