#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Iterable, Set

from aox.challenge import Debugger
from utils import BaseChallenge, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        518
        """
        machine, start = Machine.from_substitutions_text_and_start(_input)
        return machine.get_all_possible_distinct_next_step_count(start)


@dataclass
class Machine:
    substitutions: Dict[str, List[str]] = field(default_factory=dict)

    re_substitution = re.compile(r"^(\w+) => (\w+)$")

    @classmethod
    def from_substitutions_text_and_start(
            cls, substitutions_and_start_text: str):
        """
        >>> Machine.from_substitutions_text_and_start(
        ...     "H => HO\\n"
        ...     "H => OH\\n"
        ...     "O => HH\\n"
        ...     "\\n"
        ...     "HOH\\n"
        ... )
        (Machine(substitutions={'H': ['HO', 'OH'], 'O': ['HH']}), 'HOH')
        """
        substitutions_text, start = \
            cls.split_substitutions_and_start_text(substitutions_and_start_text)
        return cls.from_substitutions_text(substitutions_text), start

    @classmethod
    def split_substitutions_and_start_text(
            cls, substitutions_and_start_text: str) -> Tuple[str, str]:
        """
        >>> Machine.split_substitutions_and_start_text(
        ...     "H => HO\\nH => OH\\nO => HH\\n\\nHOH\\n")
        ('H => HO\\nH => OH\\nO => HH', 'HOH')
        """
        substitutions_text, start = substitutions_and_start_text\
            .strip().split('\n\n')
        return substitutions_text, start

    @classmethod
    def from_substitutions_text(cls, substitutions_text: str):
        """
        >>> Machine.from_substitutions_text(
        ...     "H => HO\\n"
        ...     "H => OH\\n"
        ...     "O => HH\\n"
        ... )
        Machine(substitutions={'H': ['HO', 'OH'], 'O': ['HH']})
        """
        substitutions = map(
            cls.parse_substitution, substitutions_text.splitlines())
        return cls(helper.group_by(
            substitutions, key=lambda pair: pair[0],
            value=lambda pair: pair[1]))

    @classmethod
    def parse_substitution(cls, substitution_text: str) -> Tuple[str, str]:
        match = cls.re_substitution.match(substitution_text)
        if not match:
            raise Exception(
                f"Could not parse substitution {repr(substitution_text)}")
        start, result = match.groups()

        return start, result

    def get_all_possible_distinct_next_step_count(self, start: str) -> int:
        """
        >>> Machine({'H': ['HO', 'OH'], 'O': ['HH']})\\
        ...     .get_all_possible_distinct_next_step_count('HOH')
        4
        >>> Machine({'H': ['HO', 'OH'], 'O': ['HH']})\\
        ...     .get_all_possible_distinct_next_step_count('HOHOHO')
        7
        """
        return len(self.get_all_possible_distinct_next_steps(start))

    def get_all_possible_distinct_next_steps(self, start: str) -> Set[str]:
        """
        >>> sorted(Machine({'H': ['HO', 'OH'], 'O': ['HH']})
        ...      .get_all_possible_distinct_next_steps('HOH'))
        ['HHHH', 'HOHO', 'HOOH', 'OHOH']
        """
        return set(self.get_all_possible_next_steps(start))

    def get_all_possible_next_steps(self, start: str) -> Iterable[str]:
        """
        >>> list(Machine({'H': ['HO', 'OH'], 'O': ['HH']})
        ...      .get_all_possible_next_steps('HOH'))
        ['HOOH', 'HOHO', 'OHOH', 'HOOH', 'HHHH']
        """
        for match, results in self.substitutions.items():
            for result in results:
                yield from self.get_next_steps_for_replacement(
                    start, match, result)

    def get_next_steps_for_replacement(self, start: str, match: str,
                                       result: str) -> Iterable[str]:
        """
        >>> list(Machine().get_next_steps_for_replacement('HOH', 'H', 'HO'))
        ['HOOH', 'HOHO']
        """
        prefix = ""
        remaining = start
        while len(remaining) >= len(match):
            parts = remaining.split(match, 1)
            if len(parts) < 2:
                return
            extra_prefix, suffix = parts
            yield f"{prefix}{extra_prefix}{result}{suffix}"
            prefix = f"{prefix}{extra_prefix}{match[:1]}"
            remaining = start[len(prefix):]


Challenge.main()
challenge = Challenge()
