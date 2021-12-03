#!/usr/bin/env python3
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Union

from aox.challenge import Debugger
from utils import BaseChallenge, min_and_max, helper
from year_2021.day_14.part_a import Process


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3459174981021
        """
        polymer_text, process_text = _input.split("\n\n")
        polymer = IndexedPolymer.from_polymer_text(polymer_text)
        process = IndexedProcess.from_rules_text(process_text)

        return process.apply_many(polymer, 40).score


class IndexedProcess(Process["IndexedPolymer"]):
    def apply(self, polymer: "IndexedPolymer") -> "IndexedPolymer":
        """
        >>> dict(IndexedProcess.from_rules_text('''
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
        ... ''').apply_many(IndexedPolymer.from_polymer_text("NNCB"), 1).portion_counts)
        {'NN': 0, 'NC': 1, 'CB': 0, 'CN': 1, 'NB': 1, 'BC': 1, 'CH': 1, 'HB': 1}
        >>> IndexedProcess.from_rules_text('''
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
        ... ''').apply_many(IndexedPolymer.from_polymer_text("NNCB"), 40).score
        2188189693529
        """
        result = deepcopy(polymer)
        for matched, count in polymer.portion_counts.items():
            if count <= 0:
                continue
            if matched in self.rules:
                before, after = matched
                inserted = self.rules[matched]
                result.portion_counts[matched] -= count
                result.portion_counts[f"{before}{inserted}"] += count
                result.portion_counts[f"{inserted}{after}"] += count

        return result


@dataclass
class IndexedPolymer:
    portion_counts: Dict[str, int]
    start: str
    end: str

    @classmethod
    def from_polymer_text(cls, polymer_text: str) -> "IndexedPolymer":
        template = polymer_text.strip()
        portion_counts = defaultdict(int)
        for before, after in zip(template, template[1:]):
            portion_counts[f"{before}{after}"] += 1
        return cls(
            portion_counts=portion_counts,
            start=template[0],
            end=template[-1],
        )

    @property
    def score(self) -> int:
        """
        >>> IndexedProcess.from_rules_text('''
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
        ... ''').apply_many(IndexedPolymer.from_polymer_text("NNCB"), 10).score
        1588
        """
        counts = helper.group_by(
            (
                (letter, count / 2)
                for portion, count in self.portion_counts.items()
                for letter in portion
            ),
            key=lambda letter_and_count: letter_and_count[0],
            value="auto",
            values_container=sum,
        )
        counts[self.start] += 0.5
        counts[self.end] += 0.5
        min_count, max_count = min_and_max(counts.values())

        return int(max_count - min_count)


Challenge.main()
challenge = Challenge()
