#!/usr/bin/env python3
from functools import reduce
from operator import add

import math
from abc import ABC
from dataclasses import dataclass
import re
from typing import (
    Generic, Iterable, List, Optional, Tuple, Type, Union, cast, TypeVar,
)

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, PolymorphicParser


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        4132
        """
        return SnailfishNumberSet.from_numbers_text(_input).magnitude


SnailfishNumberT = TypeVar("SnailfishNumberT", bound="SnailfishNumber")


@dataclass
class SnailfishNumberSet(Generic[SnailfishNumberT]):
    numbers: List[SnailfishNumberT]

    @classmethod
    def get_number_class(cls) -> Type[SnailfishNumberT]:
        return cast(
            Type[SnailfishNumberT],
            get_type_argument_class(cls, SnailfishNumberT),
        )

    @classmethod
    def from_numbers_text(cls, numbers_text: str) -> "SnailfishNumberSet":
        number_class = cls.get_number_class()
        lines = filter(None, map(str.strip, numbers_text.splitlines()))
        return cls(
            numbers=list(map(number_class.from_number_text, lines)),
        )

    @property
    def magnitude(self) -> int:
        """
        >>> SnailfishNumberSet.from_numbers_text('''
        ...     [[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]
        ...     [[[5,[2,8]],4],[5,[[9,9],0]]]
        ...     [6,[[[6,2],[5,6]],[[7,6],[4,7]]]]
        ...     [[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]
        ...     [[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]
        ...     [[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]
        ...     [[[[5,4],[7,7]],8],[[8,3],8]]
        ...     [[9,3],[[9,9],[6,[4,9]]]]
        ...     [[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]
        ...     [[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]
        ... ''').magnitude
        4140
        """
        return self.sum().magnitude

    def sum(self) -> SnailfishNumberT:
        return reduce(add, self.numbers)


class SnailfishNumber(PolymorphicParser, ABC, root=True):
    @classmethod
    def from_number_text(cls, number_text: str) -> "SnailfishNumber":
        """
        >>> SnailfishNumber.from_number_text("[1,2]")
        [1,2]
        >>> SnailfishNumber.from_number_text("[[1,9],[8,5]]")
        [[1,9],[8,5]]
        >>> SnailfishNumber.from_number_text(
        ...     "[[[[1,3],[5,3]],[[1,3],[8,7]]],[[[4,9],[6,9]],[[8,2],[7,3]]]]"
        ... )
        [[[[1,3],[5,3]],[[1,3],[8,7]]],[[[4,9],[6,9]],[[8,2],[7,3]]]]
        """
        number, rest = cls.parse(number_text.strip())
        if rest:
            raise Exception(f"Excess was left after parsing: '{rest}'")

        return number

    @classmethod
    def parse(cls, number_text: str) -> Tuple["SnailfishNumber", str]:
        return super().parse(number_text)

    @classmethod
    def try_parse(
        cls, number_text: str,
    ) -> Optional[Tuple["SnailfishNumber", str]]:
        raise NotImplementedError()

    def __add__(self, other: "SnailfishNumber") -> "SnailfishNumber":
        """
        >>> number = SnailfishNumber.from_number_text("[1,2]")
        >>> (number := number + SnailfishNumber.from_number_text("[[3,4],5]"))
        [[1,2],[[3,4],5]]
        >>> (
        ...     SnailfishNumber.from_number_text("[1,1]")
        ...     + SnailfishNumber.from_number_text("[2,2]")
        ...     + SnailfishNumber.from_number_text("[3,3]")
        ...     + SnailfishNumber.from_number_text("[4,4]")
        ... )
        [[[[1,1],[2,2]],[3,3]],[4,4]]
        >>> (
        ...     SnailfishNumber.from_number_text("[1,1]")
        ...     + SnailfishNumber.from_number_text("[2,2]")
        ...     + SnailfishNumber.from_number_text("[3,3]")
        ...     + SnailfishNumber.from_number_text("[4,4]")
        ...     + SnailfishNumber.from_number_text("[5,5]")
        ... )
        [[[[3,0],[5,3]],[4,4]],[5,5]]
        >>> (
        ...     SnailfishNumber.from_number_text("[1,1]")
        ...     + SnailfishNumber.from_number_text("[2,2]")
        ...     + SnailfishNumber.from_number_text("[3,3]")
        ...     + SnailfishNumber.from_number_text("[4,4]")
        ...     + SnailfishNumber.from_number_text("[5,5]")
        ...     + SnailfishNumber.from_number_text("[6,6]")
        ... )
        [[[[5,0],[7,4]],[5,5]],[6,6]]
        >>> number = SnailfishNumber.from_number_text(
        ...     "[[[0,[4,5]],[0,0]],[[[4,5],[2,6]],[9,5]]]"
        ... )
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[7,[[[3,7],[4,3]],[[6,3],[8,8]]]]"
        ... ))
        [[[[4,0],[5,4]],[[7,7],[6,0]]],[[8,[7,7]],[[7,9],[5,0]]]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[[2,[[0,8],[3,4]]],[[[6,7],1],[7,[1,6]]]]"
        ... ))
        [[[[6,7],[6,7]],[[7,7],[0,7]]],[[[8,7],[7,7]],[[8,8],[8,0]]]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[[[[2,4],7],[6,[0,5]]],[[[6,8],[2,8]],[[2,1],[4,5]]]]"
        ... ))
        [[[[7,0],[7,7]],[[7,7],[7,8]]],[[[7,7],[8,8]],[[7,7],[8,7]]]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[7,[5,[[3,8],[1,4]]]]"
        ... ))
        [[[[7,7],[7,8]],[[9,5],[8,7]]],[[[6,8],[0,8]],[[9,9],[9,0]]]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[[2,[2,2]],[8,[8,1]]]"
        ... ))
        [[[[6,6],[6,6]],[[6,0],[6,7]]],[[[7,7],[8,9]],[8,[8,1]]]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[2,9]"
        ... ))
        [[[[6,6],[7,7]],[[0,7],[7,7]]],[[[5,5],[5,6]],9]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[1,[[[9,3],9],[[9,0],[0,7]]]]"
        ... ))
        [[[[7,8],[6,7]],[[6,8],[0,8]]],[[[7,7],[5,0]],[[5,5],[5,6]]]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[[[5,[7,4]],7],1]"
        ... ))
        [[[[7,7],[7,7]],[[8,7],[8,7]]],[[[7,0],[7,7]],9]]
        >>> (number := number + SnailfishNumber.from_number_text(
        ...     "[[[[4,2],2],6],[8,7]]"
        ... ))
        [[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]
        >>> (
        ...     SnailfishNumber.from_number_text(
        ...         "[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[5,[2,8]],4],[5,[[9,9],0]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[[5,4],[7,7]],8],[[8,3],8]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[9,3],[[9,9],[6,[4,9]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]"
        ...     )
        ... )
        [[[[6,6],[7,6]],[[7,7],[7,0]]],[[[7,7],[7,7]],[[7,8],[9,9]]]]
        """
        # noinspection PyArgumentList
        return type(self)[NestedNumber](left=self, right=other).reduce()

    @property
    def magnitude(self) -> int:
        """
        >>> SnailfishNumber.from_number_text("[9,1]").magnitude
        29
        >>> SnailfishNumber.from_number_text("[1,9]").magnitude
        21
        >>> SnailfishNumber.from_number_text("[[9,1],[1,9]]").magnitude
        129
        >>> SnailfishNumber.from_number_text(
        ...     "[[1,2],[[3,4],5]]"
        ... ).magnitude
        143
        >>> SnailfishNumber.from_number_text(
        ...     "[[[[0,7],4],[[7,8],[6,0]]],[8,1]]"
        ... ).magnitude
        1384
        >>> SnailfishNumber.from_number_text(
        ...     "[[[[1,1],[2,2]],[3,3]],[4,4]]"
        ... ).magnitude
        445
        >>> SnailfishNumber.from_number_text(
        ...     "[[[[3,0],[5,3]],[4,4]],[5,5]]"
        ... ).magnitude
        791
        >>> SnailfishNumber.from_number_text(
        ...     "[[[[5,0],[7,4]],[5,5]],[6,6]]"
        ... ).magnitude
        1137
        >>> SnailfishNumber.from_number_text(
        ...     "[[[[8,7],[7,7]],[[8,6],[7,7]]],[[[0,7],[6,6]],[8,7]]]"
        ... ).magnitude
        3488
        >>> (
        ...     SnailfishNumber.from_number_text(
        ...         "[[[0,[5,8]],[[1,7],[9,6]]],[[4,[1,2]],[[1,4],2]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[5,[2,8]],4],[5,[[9,9],0]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[6,[[[6,2],[5,6]],[[7,6],[4,7]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[6,[0,7]],[0,9]],[4,[9,[9,0]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[7,[6,4]],[3,[1,3]]],[[[5,5],1],9]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[6,[[7,3],[3,2]]],[[[3,8],[5,7]],4]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[[5,4],[7,7]],8],[[8,3],8]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[9,3],[[9,9],[6,[4,9]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[2,[[7,7],7]],[[5,8],[[9,3],[0,2]]]]"
        ...     )
        ...     + SnailfishNumber.from_number_text(
        ...         "[[[[5,2],5],[8,[3,7]]],[[5,[7,5]],[4,4]]]"
        ...     )
        ... ).magnitude
        4140
        """
        raise NotImplementedError()

    def reduce(self) -> "SnailfishNumber":
        """
        >>> SnailfishNumber\\
        ...     .from_number_text("[[[[[4,3],4],4],[7,[[8,4],9]]],[1,1]]")\\
        ...     .reduce()
        [[[[0,7],4],[[7,8],[6,0]]],[8,1]]
        """
        current = None
        next_number = self
        while current is not next_number:
            if current == next_number:
                raise Exception(
                    f"Next is the same as current, but different entity"
                )
            current = next_number
            next_number = next_number.explode_first_nested_pair()
            if next_number is current:
                next_number = next_number.split_first_regular_number()

        return current

    def explode_first_nested_pair(self) -> "SnailfishNumber":
        """
        >>> SnailfishNumber\\
        ...     .from_number_text('[[1,9],[8,5]]')\\
        ...     .explode_first_nested_pair()
        [[1,9],[8,5]]
        >>> SnailfishNumber\\
        ...     .from_number_text('[[[[[9,8],1],2],3],4]')\\
        ...     .explode_first_nested_pair()
        [[[[0,9],2],3],4]
        >>> SnailfishNumber\\
        ...     .from_number_text('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]')\\
        ...     .explode_first_nested_pair()
        [[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]
        >>> SnailfishNumber\\
        ...     .from_number_text('[[3,[2,[8,0]]],[9,[5,[4,[3,2]]]]]')\\
        ...     .explode_first_nested_pair()
        [[3,[2,[8,0]]],[9,[5,[7,0]]]]
        >>> SnailfishNumber\\
        ...     .from_number_text('[[[[0,7],4],[7,[[8,4],9]]],[1,1]]')\\
        ...     .explode_first_nested_pair()
        [[[[0,7],4],[15,[0,13]]],[1,1]]
        """
        first_nested_pair = self.get_first_4_nested_pair()
        if first_nested_pair is None:
            return self

        exploded, _, _ = \
            self.explode_nested_pair(first_nested_pair)
        if exploded is self:
            raise Exception(f"{self} could not explode {first_nested_pair}")

        return exploded

    def explode_nested_pair(
        self, nested_pair: "NestedNumber",
    ) -> Tuple["SnailfishNumber", Optional[int], Optional[int]]:
        raise NotImplementedError()

    def absorb(self, value: int, at_left: bool) -> "SnailfishNumber":
        raise NotImplementedError()

    def get_first_4_nested_pair(self) -> Optional["NestedNumber"]:
        """
        >>> SnailfishNumber\\
        ...     .from_number_text('[[1,9],[8,5]]')\\
        ...     .get_first_4_nested_pair()
        >>> SnailfishNumber\\
        ...     .from_number_text('[[[[[9,8],1],2],3],4]')\\
        ...     .get_first_4_nested_pair()
        [9,8]
        >>> SnailfishNumber\\
        ...     .from_number_text('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]')\\
        ...     .get_first_4_nested_pair()
        [7,3]
        """
        return next(iter(self.get_nested_pairs(4)), None)

    def get_nested_pairs(self, level: int) -> Iterable["NestedNumber"]:
        raise NotImplementedError()

    def split_first_regular_number(self) -> "SnailfishNumber":
        """
        >>> SnailfishNumber\\
        ...     .from_number_text("[[[[0,7],4],[15,[0,13]]],[1,1]]")\\
        ...     .split_first_regular_number()
        [[[[0,7],4],[[7,8],[0,13]]],[1,1]]
        >>> SnailfishNumber\\
        ...     .from_number_text("[[[[0,7],4],[[7,8],[0,13]]],[1,1]]")\\
        ...     .split_first_regular_number()
        [[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]
        >>> SnailfishNumber\\
        ...     .from_number_text("[[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]")\\
        ...     .split_first_regular_number()
        [[[[0,7],4],[[7,8],[0,[6,7]]]],[1,1]]
        """
        first_regular_number = \
            self.get_first_regular_number_greater_equal_than_10()
        if first_regular_number is None:
            return self

        split = self.split_regular_number(first_regular_number)
        if split is self:
            raise Exception(f"{self} could not split {first_regular_number}")

        return split

    def split_regular_number(
        self, number: "RegularNumber",
    ) -> "SnailfishNumber":
        raise NotImplementedError()

    def get_first_regular_number_greater_equal_than_10(
        self,
    ) -> Optional["RegularNumber"]:
        """
        >>> SnailfishNumber\\
        ...     .from_number_text('[[1,9],[8,5]]')\\
        ...     .get_first_regular_number_greater_equal_than_10()
        >>> SnailfishNumber\\
        ...     .from_number_text('[[1,10],[8,5]]')\\
        ...     .get_first_regular_number_greater_equal_than_10()
        10
        >>> SnailfishNumber\\
        ...     .from_number_text('[[[[[19,8],1],2],3],4]')\\
        ...     .get_first_regular_number_greater_equal_than_10()
        19
        >>> SnailfishNumber\\
        ...     .from_number_text('[[3,[2,[1,[7,13]]]],[6,[15,[4,[3,2]]]]]')\\
        ...     .get_first_regular_number_greater_equal_than_10()
        13
        """
        return next((
            number
            for number in self.get_regular_numbers()
            if number.value >= 10
        ), None)

    def get_regular_numbers(self) -> Iterable["RegularNumber"]:
        raise NotImplementedError()

    @property
    def is_regular_pair(self) -> bool:
        raise NotImplementedError()


@SnailfishNumber.register
@dataclass
class NestedNumber(SnailfishNumber):
    name = "snailfish"

    left: SnailfishNumber
    right: SnailfishNumber

    @classmethod
    def try_parse(
        cls, number_text: str,
    ) -> Optional[Tuple["SnailfishNumber", str]]:
        """
        >>> NestedNumber.try_parse("[1,2]")
        ([1,2], '')
        """
        if number_text[0] != "[":
            return None

        rest = number_text[1:]
        left, rest = cls.root_class.parse(rest)
        if not rest or rest[0] != ",":
            raise Exception(
                f"Could not parse snailfish number from '{number_text}': "
                f"expected ',' in '{rest}'"
            )
        rest = rest[1:]
        right, rest = cls.root_class.parse(rest)
        if not rest or rest[0] != "]":
            raise Exception(
                f"Could not parse snailfish number from '{number_text}': "
                f"expected ']' in '{rest}'"
            )
        rest = rest[1:]

        return cls(left=left, right=right), rest

    def __post_init__(self):
        if not isinstance(self.left, SnailfishNumber):
            raise Exception(
                f"Expected {SnailfishNumber.__name__}, but got "
                f"{type(self.left).__name__} ({self.left})"
            )
        if not isinstance(self.right, SnailfishNumber):
            raise Exception(
                f"Expected {SnailfishNumber.__name__}, but got "
                f"{type(self.right).__name__} ({self.right})"
            )

    def __str__(self) -> str:
        return f"[{self.left},{self.right}]"

    def __repr__(self) -> str:
        return str(self)

    @property
    def magnitude(self) -> int:
        return 3 * self.left.magnitude + 2 * self.right.magnitude

    def explode_nested_pair(
        self, nested_pair: "NestedNumber",
    ) -> Tuple["SnailfishNumber", Optional[int], Optional[int]]:
        """
        >>> number = SnailfishNumber.from_number_text("[0,[[1,2],3]]")
        >>> pair = cast(
        ...     NestedNumber,
        ...     cast(NestedNumber, cast(NestedNumber, number).right).left,
        ... )
        >>> number.explode_nested_pair(pair)
        ([1,[0,5]], None, None)
        """
        cls = type(self)

        if self.left is nested_pair:
            nested_left: RegularNumber = cast(RegularNumber, nested_pair.left)
            nested_right: RegularNumber = cast(RegularNumber, nested_pair.right)
            assert isinstance(nested_left, RegularNumber)
            assert isinstance(nested_right, RegularNumber)
            # noinspection PyArgumentList
            return cls(
                left=type(self)[RegularNumber](value=0),
                right=self.right.absorb(nested_right.value, True),
            ), nested_left.value, None
        elif self.right is nested_pair:
            nested_left: RegularNumber = cast(RegularNumber, nested_pair.left)
            nested_right: RegularNumber = cast(RegularNumber, nested_pair.right)
            assert isinstance(nested_left, RegularNumber)
            assert isinstance(nested_right, RegularNumber)
            # noinspection PyArgumentList
            return cls(
                left=self.left.absorb(nested_left.value, False),
                right=type(self)[RegularNumber](value=0),
            ), None, nested_right.value

        new_left, left_residue, right_residue = \
            self.left.explode_nested_pair(nested_pair)
        if new_left is self.left:
            new_right, left_residue, right_residue = \
                self.right.explode_nested_pair(nested_pair)
            if new_right is self.right:
                return self, None, None
            if left_residue is not None:
                new_left = new_left.absorb(left_residue, False)
                left_residue = None
        else:
            new_right = self.right
            if right_residue is not None:
                new_right = new_right.absorb(right_residue, True)
                right_residue = None

        # noinspection PyArgumentList
        return cls(left=new_left, right=new_right), left_residue, right_residue

    def absorb(self, value: int, at_left: bool) -> "SnailfishNumber":
        cls = type(self)
        if at_left:
            # noinspection PyArgumentList
            return cls(left=self.left.absorb(value, at_left), right=self.right)
        else:
            # noinspection PyArgumentList
            return cls(left=self.left, right=self.right.absorb(value, at_left))

    def get_nested_pairs(self, level: int) -> Iterable["NestedNumber"]:
        """
        >>> list(
        ...     SnailfishNumber
        ...     .from_number_text('[[1,9],[8,5]]')
        ...     .get_nested_pairs(4)
        ... )
        []
        >>> list(
        ...     SnailfishNumber
        ...     .from_number_text('[[[[[9,8],1],2],3],4]')
        ...     .get_nested_pairs(4)
        ... )
        [[9,8]]
        >>> list(
        ...     SnailfishNumber
        ...     .from_number_text('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]')
        ...     .get_nested_pairs(4)
        ... )
        [[7,3], [3,2]]
        """
        if level > 1:
            yield from self.left.get_nested_pairs(level - 1)
            yield from self.right.get_nested_pairs(level - 1)
        elif level == 1:
            for number in (self.left, self.right):
                if number.is_regular_pair:
                    yield number
        else:
            yield from ()

    def split_regular_number(
        self, number: "RegularNumber",
    ) -> "SnailfishNumber":
        """
        >>> _number = SnailfishNumber.from_number_text("[15,3]")
        >>> _number.split_regular_number(
        ...     cast(RegularNumber, SnailfishNumber.from_number_text("16")),
        ... )
        [15,3]
        >>> _number.split_regular_number(
        ...     cast(RegularNumber, cast(NestedNumber, _number).left),
        ... )
        [[7,8],3]
        """
        new_left = self.left.split_regular_number(number)
        if new_left is self.left:
            new_right = self.right.split_regular_number(number)
            if new_right is self.right:
                return self
        else:
            new_right = self.right

        cls = type(self)
        # noinspection PyArgumentList
        return cls(left=new_left, right=new_right)

    def get_regular_numbers(self) -> Iterable["RegularNumber"]:
        """
        >>> list(
        ...     SnailfishNumber
        ...     .from_number_text('[[1,9],[8,5]]')
        ...     .get_regular_numbers()
        ... )
        [1, 9, 8, 5]
        >>> list(
        ...     SnailfishNumber
        ...     .from_number_text('[[[[[9,8],1],2],3],4]')
        ...     .get_regular_numbers()
        ... )
        [9, 8, 1, 2, 3, 4]
        >>> list(
        ...     SnailfishNumber
        ...     .from_number_text('[[3,[2,[1,[7,3]]]],[6,[5,[4,[3,2]]]]]')
        ...     .get_regular_numbers()
        ... )
        [3, 2, 1, 7, 3, 6, 5, 4, 3, 2]
        """
        yield from self.left.get_regular_numbers()
        yield from self.right.get_regular_numbers()

    @property
    def is_regular_pair(self) -> bool:
        return (
            isinstance(self.left, RegularNumber)
            and isinstance(self.right, RegularNumber)
        )


@SnailfishNumber.register
@dataclass
class RegularNumber(SnailfishNumber):
    name = "regular"

    value: int

    re_number = re.compile(r"^(\d+).*")

    @classmethod
    def try_parse(
        cls, number_text: str,
    ) -> Optional[Tuple["SnailfishNumber", str]]:
        """
        >>> RegularNumber.try_parse("1,2]")
        (1, ',2]')
        """
        match = cls.re_number.match(number_text)
        if not match:
            return None

        value_str, = match.groups()
        rest = number_text[len(value_str):]
        return cls(value=int(value_str)), rest

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return str(self)

    @property
    def magnitude(self) -> int:
        return self.value

    def explode_nested_pair(
        self, nested_pair: "NestedNumber",
    ) -> Tuple["SnailfishNumber", Optional[int], Optional[int]]:
        return self, None, None

    def absorb(self, value: int, at_left: bool) -> "SnailfishNumber":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(value=self.value + value)

    def get_nested_pairs(self, level: int) -> Iterable["NestedNumber"]:
        yield from ()

    def split_regular_number(
        self, number: "RegularNumber",
    ) -> "SnailfishNumber":
        """
        >>> _number = SnailfishNumber.from_number_text("15")
        >>> _number.split_regular_number(
        ...     cast(RegularNumber, SnailfishNumber.from_number_text("16")),
        ... )
        15
        >>> _number.split_regular_number(
        ...     cast(RegularNumber, _number),
        ... )
        [7,8]
        """
        if number is not self:
            return self

        nested_number_class: Type[NestedNumber] = \
            cast(Type[NestedNumber], type(self)[NestedNumber])
        cls = type(self)
        # noinspection PyArgumentList
        return nested_number_class(
            left=cls(math.floor(self.value / 2)),
            right=cls(math.ceil(self.value / 2)),
        )

    def get_regular_numbers(self) -> Iterable["RegularNumber"]:
        yield self

    @property
    def is_regular_pair(self) -> bool:
        return False


Challenge.main()
challenge = Challenge()
