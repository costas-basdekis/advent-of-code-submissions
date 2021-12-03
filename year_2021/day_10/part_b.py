#!/usr/bin/env python3
from typing import List

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_10.part_a import Entry, EntrySet, EntryT


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        4329504793
        """
        return EntrySetExtended.from_entries_text(_input).completion_score


class EntrySetExtended(EntrySet["EntryExtended"]):
    @property
    def incomplete_entries(self) -> List[EntryT]:
        """
        >>> EntrySetExtended.from_entries_text('''
        ...     [({(<(())[]>[[{[]{<()<>>
        ...     [(()[<>])]({[<{<<[]>>(
        ...     {([(<{}[<>[]}>{[]{[(<()>
        ...     (((({<>}<{<{<>}{[]{[]{}
        ...     [[<[([]))<([[{}[[()]]]
        ...     [{[{({}]{}}([{[{{{}}([]
        ...     {<[[]]>}<{[{[{[]{()[[[]
        ...     [<(<(<(<{}))><([]([]()
        ...     <{([([[(<>()){}]>(<<{{
        ...     <{([{{}}[<[[[<>{}]]]>[]]
        ... ''').incomplete_entries
        [EntryExtended(characters='[({(<(())[]>[[{[]{<()<>>'), ...]
        """
        return [
            entry
            for entry in self.entries
            if entry.is_incomplete
        ]

    @property
    def completion_score(self) -> int:
        """
        >>> EntrySetExtended.from_entries_text('''
        ...     [({(<(())[]>[[{[]{<()<>>
        ...     [(()[<>])]({[<{<<[]>>(
        ...     {([(<{}[<>[]}>{[]{[(<()>
        ...     (((({<>}<{<{<>}{[]{[]{}
        ...     [[<[([]))<([[{}[[()]]]
        ...     [{[{({}]{}}([{[{{{}}([]
        ...     {<[[]]>}<{[{[{[]{()[[[]
        ...     [<(<(<(<{}))><([]([]()
        ...     <{([([[(<>()){}]>(<<{{
        ...     <{([{{}}[<[[[<>{}]]]>[]]
        ... ''').completion_score
        288957
        """
        sorted_completion_scores = sorted(
            entry.completion_score
            for entry in self.incomplete_entries
        )
        if len(sorted_completion_scores) % 2 != 1:
            raise Exception(
                f"Expected and odd number of incomplete lines, but got "
                f"{len(sorted_completion_scores)}"
            )

        return sorted_completion_scores[len(sorted_completion_scores) // 2]


class EntryExtended(Entry):
    COMPLETION_SCORE_MAP = {
        ")": 1,
        "]": 2,
        "}": 3,
        ">": 4,
    }

    @property
    def is_incomplete(self) -> bool:
        """
        >>> EntryExtended("[({(<(())[]>[[{[]{<()<>>").is_incomplete
        True
        >>> EntryExtended("{([(<{}[<>[]}>{[]{[(<()>").is_incomplete
        False
        """
        stack, wrong_character, _ = self.analyse()
        return bool(stack) and not wrong_character

    @property
    def completion_score(self) -> int:
        """
        >>> EntryExtended("[({(<(())[]>[[{[]{<()<>>").completion_score
        288957
        """
        completion = self.completion
        score = 0
        for character in completion:
            score *= 5
            score += self.COMPLETION_SCORE_MAP[character]
        return score

    @property
    def completion(self) -> str:
        """
        >>> EntryExtended("[({(<(())[]>[[{[]{<()<>>").completion
        '}}]])})]'
        """
        stack, wrong_character, _ = self.analyse()
        if wrong_character is not None:
            raise Exception(f"Entry is corrupted")
        if not stack:
            raise Exception(f"Entry is not incomplete")
        return "".join(
            self.PAIR_MAP   [character]
            for character in reversed(stack)
        )


Challenge.main()
challenge = Challenge()
