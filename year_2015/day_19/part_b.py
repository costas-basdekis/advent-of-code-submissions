#!/usr/bin/env python3
from collections import Iterable
from typing import Optional, Callable, Tuple

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        200
        """
        machine, target = MachineExtended\
            .from_substitutions_text_and_start(_input)
        return machine.get_min_step_count_to_target(
            "e", target, debugger=debugger)


class MachineExtended(part_a.Machine):
    def reverse(self):
        """
        >>> MachineExtended({'H': ['HO', 'OH'], 'O': ['HH']}).reverse()
        MachineExtended(substitutions={'HH': ['O'], 'HO': ['H'], 'OH': ['H']})
        >>> MachineExtended({'H': ['HO', 'OH'], 'O': ['HH', 'HO']}).reverse()
        MachineExtended(substitutions={'HH': ['O'],
            'HO': ['H', 'O'], 'OH': ['H']})
        >>> MachineExtended({'H': ['OH']}).reverse()
        MachineExtended(substitutions={'OH': ['H']})
        """
        reverse_substitutions_items = [
            (result, match)
            for match, results in self.substitutions.items()
            for result in results
        ]
        return self.from_substitution_items(reverse_substitutions_items)

    def get_min_step_count_to_target(
            self, start: str, target: str,
            debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> MachineExtended.from_substitutions_text(
        ...     "e => H\\n"
        ...     "e => O\\n"
        ...     "H => HO\\n"
        ...     "H => OH\\n"
        ...     "O => HH\\n"
        ... ).get_min_step_count_to_target("e", "HOH")
        3
        >>> MachineExtended.from_substitutions_text(
        ...     "e => H\\n"
        ...     "e => O\\n"
        ...     "H => HO\\n"
        ...     "H => OH\\n"
        ...     "O => HH\\n"
        ... ).get_min_step_count_to_target("e", "HOHOHO")
        6
        """
        def min_length_report_format(_debugger, message):
            return f"min length: {min_length}, {message}"
        min_length = None
        with debugger.adding_extra_report_format(min_length_report_format):
            for chain in self.get_all_possible_chains_to_target(
                    start, target, debugger=debugger):
                chain_length = len(chain) - 1
                if min_length is None or chain_length < min_length:
                    min_length = chain_length

        return min_length

    def get_all_possible_chains_to_target(
            self, start: str, target: str, allow_reverse: bool = True,
            debugger: Debugger = Debugger(enabled=False),
    ) -> Iterable[Tuple[str, ...]]:
        """
        >>> list(MachineExtended().get_all_possible_chains_to_target(
        ...     "a", "b", allow_reverse=False))
        []
        >>> list(MachineExtended({'H': ['O']})
        ...      .get_all_possible_chains_to_target(
        ...         "HH", "OO", allow_reverse=False))
        [('HH', 'OH', 'OO'), ('HH', 'HO', 'OO')]
        >>> list(MachineExtended({'H': ['OH']})
        ...      .get_all_possible_chains_to_target(
        ...         "HH", "OHOH", allow_reverse=False))
        [('HH', 'OHH', 'OHOH'), ('HH', 'HOH', 'OHOH')]
        >>> list(MachineExtended({'H': ['O'], 'O': ['H']})
        ...      .get_all_possible_chains_to_target(
        ...         "HH", "OH", allow_reverse=False))
        [('HH', 'OH'), ('HH', 'HO', 'OO', 'OH')]
        >>> list(MachineExtended({'OH': ['H']})
        ...      .get_all_possible_chains_to_target(
        ...         "OHOH", "HH", allow_reverse=False))
        [('OHOH', 'HOH', 'HH'), ('OHOH', 'OHH', 'HH')]
        >>> list(MachineExtended().get_all_possible_chains_to_target("a", "b"))
        []
        >>> list(MachineExtended({'H': ['O']})
        ...      .get_all_possible_chains_to_target("HH", "OO"))
        [('HH', 'OH', 'OO'), ('HH', 'HO', 'OO')]
        >>> list(MachineExtended({'H': ['OH']})
        ...      .get_all_possible_chains_to_target("HH", "OHOH"))
        [('OHOH', 'HOH', 'HH'), ('OHOH', 'OHH', 'HH')]
        >>> list(MachineExtended({'H': ['O'], 'O': ['H']})
        ...      .get_all_possible_chains_to_target("HH", "OH"))
        [('HH', 'OH'), ('HH', 'HO', 'OO', 'OH')]
        """
        if len(target) < len(start):
            if self.are_substitutions_not_decreasing():
                raise Exception(
                    f"Cannot go from length {len(start)} to length "
                    f"{len(target)}, as substitutions don't decrease")
        elif len(target) > len(start):
            if self.are_substitutions_not_increasing():
                raise Exception(
                    f"Cannot go from length {len(start)} to length "
                    f"{len(target)}, as substitutions don't increase")
        if allow_reverse:
            if len(target) > len(start):
                yield from self.reverse().get_all_possible_chains_to_target(
                    start=target, target=start, debugger=debugger)
                return
        prune = self.get_prune(target)

        for chain in debugger.stepping(
                self.get_all_possible_chains(start, prune, debugger=debugger)):
            if chain[-1] == target:
                yield chain

    def get_prune(self, target: str) -> Callable[[str], bool]:
        if self.are_substitutions_not_decreasing():
            return self.get_prune_remove_decreasing(target)
        elif self.are_substitutions_not_increasing():
            return self.get_prune_remove_increasing(target)
        else:
            raise Exception(
                f"Substitutions are neither not-decreasing nor not-increasing")

    def get_prune_remove_decreasing(self, target: str) -> Callable[[str], bool]:
        max_length = len(target)

        def prune_remove_decreasing(step: str) -> bool:
            return len(step) <= max_length

        return prune_remove_decreasing

    def get_prune_remove_increasing(self, target: str) -> Callable[[str], bool]:
        min_length = len(target)

        def prune_remove_increasing(step: str) -> bool:
            return len(step) >= min_length

        return prune_remove_increasing

    def are_substitutions_not_decreasing(self) -> bool:
        """
        >>> MachineExtended({}).are_substitutions_not_decreasing()
        True
        >>> MachineExtended({'H': ['O']}).are_substitutions_not_decreasing()
        True
        >>> MachineExtended({
        ...     'H': ['O', 'OH']}).are_substitutions_not_decreasing()
        True
        >>> MachineExtended({
        ...     'H': ['O', 'OH', '']}).are_substitutions_not_decreasing()
        False
        """
        return all(
            len(match) <= len(result)
            for match, results in self.substitutions.items()
            for result in results
        )

    def are_substitutions_not_increasing(self) -> bool:
        """
        >>> MachineExtended({}).are_substitutions_not_increasing()
        True
        >>> MachineExtended({'H': ['O']}).are_substitutions_not_increasing()
        True
        >>> MachineExtended({
        ...     'H': ['O', '']}).are_substitutions_not_increasing()
        True
        >>> MachineExtended({
        ...     'H': ['O', 'OH', '']}).are_substitutions_not_increasing()
        False
        """
        return all(
            len(match) >= len(result)
            for match, results in self.substitutions.items()
            for result in results
        )

    def get_all_possible_chains(
            self, start: str, prune: Optional[Callable[[str], bool]] = None,
            debugger: Debugger = Debugger(enabled=False),
    ) -> Iterable[Tuple[str, ...]]:
        """
        >>> list(MachineExtended().get_all_possible_chains(""))
        []
        >>> list(MachineExtended({'H': ['O']}).get_all_possible_chains("HH"))
        [('HH', 'OH'), ('HH', 'HO'), ('HH', 'OH', 'OO'), ('HH', 'HO', 'OO')]
        >>> list(MachineExtended({'H': ['O']}).get_all_possible_chains(
        ...     "HH", lambda step: step != 'HO'))
        [('HH', 'OH'), ('HH', 'OH', 'OO')]
        >>> list(MachineExtended({'H': ['OH']}).get_all_possible_chains(
        ...     "HH", lambda step: len(step) <= 4))
        [('HH', 'OHH'), ('HH', 'HOH'), ('HH', 'OHH', 'OOHH'),
            ('HH', 'OHH', 'OHOH'), ('HH', 'HOH', 'OHOH'), ('HH', 'HOH', 'HOOH')]
        >>> list(MachineExtended({'H': ['O'], 'O': ['H']})
        ...      .get_all_possible_chains("HH"))
        [('HH', 'OH'), ('HH', 'HO'), ('HH', 'OH', 'OO'), ('HH', 'HO', 'OO'),
            ('HH', 'OH', 'OO', 'HO'), ('HH', 'HO', 'OO', 'OH')]
        """
        stack = [(start, ())]
        debugger.reset()
        while stack:
            current, chain = stack.pop()
            next_chain = chain + (current,)
            for next_step in self.get_all_possible_next_steps(current):
                if next_step in next_chain:
                    continue
                if prune and not prune(next_step):
                    continue
                yield next_chain + (next_step,)
                stack.append((next_step, next_chain))
            if debugger.should_report():
                debugger.default_report(
                    f"stack size: {len(stack)}, "
                    f"end length: {len(next_chain[-1])}, "
                    f"chain length: {len(next_chain)}")


Challenge.main()
challenge = Challenge()
