#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass
from typing import Optional, Generic, Type, List

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        'bdfhgeca'
        """
        return OperationSet.from_operations_text(_input).apply('abcdefgh')


OperationT = TV['Operation']


@dataclass
class OperationSet(Generic[OperationT]):
    operations: List[OperationT]

    @classmethod
    def get_operation_class(cls) -> Type[OperationT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, OperationT)

    @classmethod
    def from_operations_text(cls, operations_text: str):
        """
        >>> OperationSet.from_operations_text(
        ...     "swap position 4 with position 0\\n"
        ...     "swap letter d with letter b\\n"
        ...     "reverse positions 0 through 4\\n"
        ...     "rotate left 1 step\\n"
        ...     "move position 1 to position 4\\n"
        ...     "move position 3 to position 0\\n"
        ...     "rotate based on position of letter b\\n"
        ...     "rotate based on position of letter d\\n"
        ... )
        OperationSet(operations=[SwapPositions(position_a=0, position_b=4),
            SwapLetters(letter_a='b', letter_b='d'),
            ReversePositions(start=0, end=4),
            Rotate(steps=-1),
            MovePosition(source=1, target=4),
            MovePosition(source=3, target=0),
            RotateBasedOnLetter(letter='b'),
            RotateBasedOnLetter(letter='d')])
        """
        operation_class = cls.get_operation_class()
        return cls(list(map(
            operation_class.parse, operations_text.splitlines())))

    def apply(self, text: str) -> str:
        """
        >>> OperationSet.from_operations_text(
        ...     "swap position 4 with position 0\\n"
        ...     "swap letter d with letter b\\n"
        ...     "reverse positions 0 through 4\\n"
        ...     "rotate left 1 step\\n"
        ...     "move position 1 to position 4\\n"
        ...     "move position 3 to position 0\\n"
        ...     "rotate based on position of letter b\\n"
        ...     "rotate based on position of letter d\\n"
        ... ).apply("abcde")
        'decab'
        """
        result = text
        for operation in self.operations:
            new_result = operation.apply(result)
            if len(new_result) != len(text):
                raise Exception(
                    f"Operation {operation} converted {result} into different "
                    f"length {new_result}")
            if set(new_result) != set(text):
                raise Exception(
                    f"Operation {operation} converted {result} into different "
                    f"letters {new_result}")
            result = new_result

        return result


class Operation(PolymorphicParser, ABC, root=True):
    """
    >>> Operation.parse("swap position 0 with position 4")
    SwapPositions(position_a=0, position_b=4)
    >>> Operation.parse("swap position 4 with position 0")
    SwapPositions(position_a=0, position_b=4)
    >>> Operation.parse("swap letter b with letter d")
    SwapLetters(letter_a='b', letter_b='d')
    >>> Operation.parse("swap letter d with letter b")
    SwapLetters(letter_a='b', letter_b='d')
    >>> Operation.parse("rotate left 1 step")
    Rotate(steps=-1)
    >>> Operation.parse("rotate right 1 step")
    Rotate(steps=1)
    >>> Operation.parse("rotate based on position of letter b")
    RotateBasedOnLetter(letter='b')
    >>> Operation.parse("reverse positions 0 through 4")
    ReversePositions(start=0, end=4)
    >>> Operation.parse("move position 1 to position 4")
    MovePosition(source=1, target=4)
    """

    def apply(self, text: str) -> str:
        raise NotImplementedError()


@Operation.register
@dataclass
class SwapPositions(Operation):
    name = "swap-positions"

    position_a: int
    position_b: int

    re_swap_positions = re.compile(r"^swap position (\d+) with position (\d+)")

    @classmethod
    def try_parse(cls, text: str) -> Optional['SwapPositions']:
        """
        >>> SwapPositions.try_parse("swap position 0 with position 4")
        SwapPositions(position_a=0, position_b=4)
        >>> SwapPositions.try_parse("swap position 4 with position 0")
        SwapPositions(position_a=0, position_b=4)
        """
        match = cls.re_swap_positions.match(text)
        if not match:
            return None
        position_a_str, position_b_str = match.groups()
        position_a, position_b = int(position_a_str), int(position_b_str)
        position_a, position_b = sorted([position_a, position_b])

        return cls(position_a, position_b)

    def apply(self, text: str) -> str:
        """
        >>> SwapPositions(0, 4).apply("abcde")
        'ebcda'
        """
        return (
            f"{text[:self.position_a]}"
            f"{text[self.position_b]}"
            f"{text[self.position_a + 1:self.position_b]}"
            f"{text[self.position_a]}"
            f"{text[self.position_b + 1:]}"
        )


@Operation.register
@dataclass
class SwapLetters(Operation):
    name = "swap-letters"

    letter_a: str
    letter_b: str

    re_swap_letters = re.compile(r"^swap letter (\w) with letter (\w)")

    @classmethod
    def try_parse(cls, text: str) -> Optional['SwapLetters']:
        """
        >>> SwapLetters.try_parse("swap letter b with letter d")
        SwapLetters(letter_a='b', letter_b='d')
        >>> SwapLetters.try_parse("swap letter d with letter b")
        SwapLetters(letter_a='b', letter_b='d')
        """
        match = cls.re_swap_letters.match(text)
        if not match:
            return None
        letter_a, letter_b = match.groups()
        letter_a, letter_b = sorted([letter_a, letter_b])

        return cls(letter_a, letter_b)

    def apply(self, text: str) -> str:
        """
        >>> SwapLetters("b", "d").apply("ebcda")
        'edcba'
        """
        position_a = text.index(self.letter_a)
        position_b = text.index(self.letter_b)
        position_a, position_b = sorted([position_a, position_b])
        return (
            f"{text[:position_a]}"
            f"{text[position_b]}"
            f"{text[position_a + 1:position_b]}"
            f"{text[position_a]}"
            f"{text[position_b + 1:]}"
        )


@Operation.register
@dataclass
class Rotate(Operation):
    name = "rotate"

    steps: int

    re_rotate = re.compile(r"^rotate (left|right) (\d+) steps?")

    DIRECTION_MULTIPLIERS = {
        'left': -1,
        'right': 1,
    }

    @classmethod
    def try_parse(cls, text: str) -> Optional['Rotate']:
        """
        >>> Rotate.try_parse("rotate left 1 step")
        Rotate(steps=-1)
        >>> Rotate.try_parse("rotate right 1 step")
        Rotate(steps=1)
        """
        match = cls.re_rotate.match(text)
        if not match:
            return None
        direction, step_count_str = match.groups()
        multiplier = cls.DIRECTION_MULTIPLIERS[direction]
        step_count = int(step_count_str)

        return cls(step_count * multiplier)

    def apply(self, text: str) -> str:
        """
        >>> Rotate(-1).apply("abcde")
        'bcdea'
        """
        if self.steps < 0:
            steps = len(text) + self.steps
        else:
            steps = self.steps
        steps %= len(text)
        return f"{text[-steps:]}{text[:-steps]}"


@Operation.register
@dataclass
class RotateBasedOnLetter(Operation):
    name = "rotate-based-on-letter"

    letter: str

    re_rotate_based_on_letter = re.compile(
        r"^rotate based on position of letter (\w)")

    @classmethod
    def try_parse(cls, text: str) -> Optional['RotateBasedOnLetter']:
        """
        >>> RotateBasedOnLetter.try_parse(
        ...     "rotate based on position of letter b")
        RotateBasedOnLetter(letter='b')
        """
        match = cls.re_rotate_based_on_letter.match(text)
        if not match:
            return None
        letter, = match.groups()

        return cls(letter)

    def apply(self, text: str) -> str:
        """
        >>> RotateBasedOnLetter("b").apply("abdec")
        'ecabd'
        >>> RotateBasedOnLetter("d").apply("ecabd")
        'decab'
        """
        position = text.index(self.letter)
        return Rotate(position + 1 + (1 if position >= 4 else 0)).apply(text)


@Operation.register
@dataclass
class ReversePositions(Operation):
    name = "reverse-positions"

    start: int
    end: int

    re_reverse_positions = re.compile(r"^reverse positions (\d+) through (\d+)")

    @classmethod
    def try_parse(cls, text: str) -> Optional['ReversePositions']:
        """
        >>> ReversePositions.try_parse("reverse positions 0 through 4")
        ReversePositions(start=0, end=4)
        """
        match = cls.re_reverse_positions.match(text)
        if not match:
            return None
        start_str, end_str = match.groups()

        return cls(int(start_str), int(end_str))

    def apply(self, text: str) -> str:
        """
        >>> ReversePositions(0, 4).apply("edcba")
        'abcde'
        """
        return (
            f"{text[:self.start]}"
            f"{text[self.start:self.end + 1][::-1]}"
            f"{text[self.end + 1:]}"
        )


@Operation.register
@dataclass
class MovePosition(Operation):
    name = "move-position"

    source: int
    target: int

    re_move_position = re.compile(r"^move position (\d+) to position (\d+)")

    @classmethod
    def try_parse(cls, text: str) -> Optional['MovePosition']:
        """
        >>> MovePosition.try_parse("move position 1 to position 4")
        MovePosition(source=1, target=4)
        """
        match = cls.re_move_position.match(text)
        if not match:
            return None
        source_str, target_str = match.groups()

        return cls(int(source_str), int(target_str))

    def apply(self, text: str) -> str:
        """
        >>> MovePosition(1, 4).apply("bcdea")
        'bdeac'
        >>> MovePosition(3, 0).apply("bdeac")
        'abdec'
        """
        letter = text[self.source]
        removed = f"{text[:self.source]}{text[self.source + 1:]}"
        return f"{removed[:self.target]}{letter}{removed[self.target:]}"


Challenge.main()
challenge = Challenge()
