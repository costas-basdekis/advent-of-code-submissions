#!/usr/bin/env python3
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_19 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        615388132411142
        """
        return OnsenExtended.from_text(_input).get_all_pattern_arrangement_count(debugger=debugger)

class OnsenExtended(part_a.Onsen):
    def get_all_pattern_arrangement_count(self, cache: Optional["PatternCache"] = None, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> OnsenExtended.from_text('''
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
        ... ''').get_all_pattern_arrangement_count()
        16
        """
        if cache is None:
            cache = PatternCache.from_source_patterns(self.source_patterns)
        return sum(
            self.get_pattern_arrangement_count(pattern, cache=cache, debugger=debugger)
            for pattern in self.target_patterns
        )

    def get_pattern_arrangement_count(self, target: str, cache: Optional["PatternCache"] = None, debugger: Debugger = Debugger(enabled=False)) -> int:
        if cache is None:
            cache = PatternCache.from_source_patterns(self.source_patterns)
        if target in cache:
            return cache[target]
        self.fill_cache(target, cache, debugger=debugger)
        self.backtrack(target, cache, debugger=debugger)
        return cache[target]

    def backtrack(self, target: str, cache: "PatternCache", debugger: Debugger = Debugger(enabled=False)):
        stack = [target]
        while debugger.step_if(stack):
            pattern = stack[-1]
            if debugger.should_report():
                debugger.default_report_if(f"Backtracking for '{pattern}', stack({len(stack)}) is '{stack[0]}' -> '{stack[-1]}'")
            if pattern in cache:
                stack.pop()
                continue
            missing_dependencies = [
                dependency
                for dependency in cache.dependencies[pattern]
                if dependency not in cache
            ]
            if missing_dependencies:
                stack.extend(missing_dependencies)
                continue
            cache[pattern] = sum(
                cache[dependency]
                for dependency in cache.dependencies[pattern]
            )
            stack.pop()

    def fill_cache(self, target: str, cache: "PatternCache", debugger: Debugger = Debugger(enabled=False)):
        queue = [(target, [])]
        seen = {target}
        while debugger.step_if(queue):
            pattern, path = queue.pop(0)
            for source in self.source_patterns:
                if not pattern.startswith(source):
                    continue
                next_pattern = pattern[len(source):]
                if not next_pattern:
                    cache.add_dependency(pattern, f"-{source}")
                    continue
                cache.add_dependency(pattern, next_pattern)
                if next_pattern in seen:
                    continue
                seen.add(next_pattern)
                next_path = path + [source]
                queue.append((next_pattern, next_path))
            if debugger.should_report():
                debugger.default_report_if(f"Checking for '{target}', queue {len(queue)}, last pattern is '{pattern}'")


@dataclass
class PatternCache:
    cache: Dict[str, int] = field(default_factory=dict)
    dependencies: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    reverse_dependencies: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))

    @classmethod
    def from_source_patterns(cls, source_patterns: Iterable[str]) -> "PatternCache":
        return cls(cache={
            f"-{source}": 1
            for source in source_patterns
        })

    def __getitem__(self, item: str) -> int:
        return self.cache[item]

    def __setitem__(self, key: str, value: int) -> None:
        self.cache[key] = value

    def __contains__(self, item: str) -> bool:
        return item in self.cache

    def add_dependency(self, parent: str, child: str) -> None:
        self.dependencies[parent].add(child)
        self.reverse_dependencies[child].add(parent)


Challenge.main()
challenge = Challenge()
