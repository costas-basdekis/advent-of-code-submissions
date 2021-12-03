#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Dict, Union, Generic

from aox.challenge import Debugger
from utils import BaseChallenge, helper, iterable_length, min_and_max, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3259
        """
        polymer_text, process_text = _input.split("\n\n")
        polymer = Polymer.from_polymer_text(polymer_text)
        process = Process.from_rules_text(process_text)

        return process.apply_many(polymer, count=10).score


PolymerT = TV["Polymer"]


@dataclass
class Process(Generic[PolymerT]):
    rules: Dict[str, str]

    re_rule = re.compile(r"^\s*(\w{2})\s*->\s*(\w)\s*$")

    @classmethod
    def from_rules_text(cls, rules_text: str) -> "Process":
        """
        >>> Process.from_rules_text('''
        ...     CH -> B
        ...     HH -> N
        ...     CB -> H
        ...     NH -> C
        ...     HB -> C
        ...     HC -> B
        ...     HN -> C
        ...     NN -> C
        ...     BH -> H
        ...     NC -> B
        ...     NB -> B
        ...     BN -> B
        ...     BB -> N
        ...     BC -> B
        ...     CC -> N
        ...     CN -> C
        ... ''')
        Process(rules={'CH': 'B', 'HH': 'N', ...})
        """
        lines = filter(None, map(str.strip, rules_text.splitlines()))
        return cls(
            rules={
                matched: inserted
                for line in lines
                for matched, inserted in [cls.re_rule.match(line).groups()]
            },
        )

    def apply_many(self, polymer: PolymerT, count: int) -> PolymerT:
        """
        >>> Process.from_rules_text('''
        ...     CH -> B
        ...     HH -> N
        ...     CB -> H
        ...     NH -> C
        ...     HB -> C
        ...     HC -> B
        ...     HN -> C
        ...     NN -> C
        ...     BH -> H
        ...     NC -> B
        ...     NB -> B
        ...     BN -> B
        ...     BB -> N
        ...     BC -> B
        ...     CC -> N
        ...     CN -> C
        ... ''').apply_many(Polymer("NNCB"), 4)
        Polymer(template='NBBNBNBBCCNBCNCCNBBNBBNBBBNBBNBBCBHCBHHNHCBBCBHCB')
        """
        result = polymer
        for _ in range(count):
            result = self.apply(result)

        return result

    def apply(self, polymer: PolymerT) -> PolymerT:
        """
        >>> Process.from_rules_text('''
        ...     CH -> B
        ...     HH -> N
        ...     CB -> H
        ...     NH -> C
        ...     HB -> C
        ...     HC -> B
        ...     HN -> C
        ...     NN -> C
        ...     BH -> H
        ...     NC -> B
        ...     NB -> B
        ...     BN -> B
        ...     BB -> N
        ...     BC -> B
        ...     CC -> N
        ...     CN -> C
        ... ''').apply(Polymer("NNCB"))
        Polymer(template='NCNBCHB')
        """
        result = polymer.template[0]
        for start in range(len(polymer.template) - 1):
            matched = polymer.template[start:start + 2]
            inserted = self.rules.get(matched, "")
            result += inserted + matched[1]

        polymer_class = type(polymer)
        # noinspection PyArgumentList
        return polymer_class(template=result)


@dataclass
class Polymer:
    template: str

    @classmethod
    def from_polymer_text(cls, polymer_text: str) -> "Polymer":
        """
        >>> Polymer.from_polymer_text("NNCB")
        Polymer(template='NNCB')
        """
        return cls(template=polymer_text.strip())

    @property
    def score(self) -> int:
        """
        >>> Process.from_rules_text('''
        ...     CH -> B
        ...     HH -> N
        ...     CB -> H
        ...     NH -> C
        ...     HB -> C
        ...     HC -> B
        ...     HN -> C
        ...     NN -> C
        ...     BH -> H
        ...     NC -> B
        ...     NB -> B
        ...     BN -> B
        ...     BB -> N
        ...     BC -> B
        ...     CC -> N
        ...     CN -> C
        ... ''').apply_many(Polymer("NNCB"), 10).score
        1588
        """
        counts = helper.group_by(
            self.template, values_container=iterable_length,
        )
        min_count, max_count = min_and_max(counts.values())

        return max_count - min_count


Challenge.main()
challenge = Challenge()
