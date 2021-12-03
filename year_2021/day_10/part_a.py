#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import List, Generic, Type, Tuple, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        358737
        """
        return EntrySet.from_entries_text(_input).syntax_error_score


EntryT = TV["Entry"]


@dataclass
class EntrySet(Generic[EntryT]):
    entries: List[EntryT]

    @classmethod
    def get_entry_class(cls) -> Type[EntryT]:
        return get_type_argument_class(cls, EntryT)

    @classmethod
    def from_entries_text(cls, entries_text: str) -> "EntrySet":
        """
        >>> EntrySet.from_entries_text('''
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
        ... ''')
        EntrySet(entries=[Entry(characters='[({(<(())[]>[[{[]{<()<>>'), ...])
        """
        entry_class = cls.get_entry_class()
        return cls(
            entries=list(map(
                entry_class.from_entry_text,
                entries_text.strip().splitlines(),
            )),
        )

    @property
    def syntax_error_score(self) -> int:
        """
        >>> EntrySet.from_entries_text('''
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
        ... ''').syntax_error_score
        26397
        """
        return sum((
            entry.syntax_error_score
            for entry in self.corrupted_entries
        ), 0)

    @property
    def corrupted_entries(self) -> List[EntryT]:
        """
        >>> EntrySet.from_entries_text('''
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
        ... ''').corrupted_entries
        [Entry(characters='{([(<{}[<>[]}>{[]{[(<()>'), ...]
        """
        return [
            entry
            for entry in self.entries
            if entry.is_corrupted
        ]


@dataclass
class Entry:
    characters: str

    re_entry = re.compile(r"^\s*[\[\](){}<>]+\s*$")

    PAIR_MAP = {
        '[': ']',
        '{': '}',
        '(': ')',
        '<': '>',
    }
    REVERSE_PAIR_MAP = {
        closing: opening
        for opening, closing in PAIR_MAP.items()
    }
    SYNTAX_ERROR_SCORES = {
        ")": 3,
        "]": 57,
        "}": 1197,
        ">": 25137,
    }

    @classmethod
    def from_entry_text(cls, entry_text: str) -> "Entry":
        """
        >>> Entry.from_entry_text("  {([(<{}[<>[]}>{[]{[(<()>  ")
        Entry(characters='{([(<{}[<>[]}>{[]{[(<()>')
        """
        if not cls.re_entry.match(entry_text):
            raise Exception(f"Could not parse entry '{entry_text}'")
        return cls(characters=entry_text.strip())

    @property
    def syntax_error_score(self) -> int:
        """
        >>> Entry("{([(<{}[<>[]}>{[]{[(<()>").syntax_error_score
        1197
        """
        _, wrong_character, _ = self.analyse()
        if wrong_character is None:
            raise Exception(f"Entry is not corrupted")

        return self.SYNTAX_ERROR_SCORES[wrong_character]

    @property
    def is_corrupted(self) -> bool:
        """
        >>> Entry("[({(<(())[]>[[{[]{<()<>>").is_corrupted
        False
        >>> Entry("{([(<{}[<>[]}>{[]{[(<()>").is_corrupted
        True
        """
        _, wrong_character, _ = self.analyse()
        return wrong_character is not None

    def analyse(self) -> Tuple[str, Optional[str], Optional[str]]:
        """
        >>> Entry("[({(<(())[]>[[{[]{<()<>>").analyse()
        ('[({([[{{', None, None)
        >>> Entry("{([(<{}[<>[]}>{[]{[(<()>").analyse()
        ('{([(<[', '}', '}>{[]{[(<()>')
        """
        stack = []
        for index, character in enumerate(self.characters):
            if character in self.PAIR_MAP:
                stack.append(character)
            else:
                if not stack or stack[-1] != self.REVERSE_PAIR_MAP[character]:
                    return "".join(stack), character, self.characters[index:]
                stack.pop()

        return "".join(stack), None, None


Challenge.main()
challenge = Challenge()
