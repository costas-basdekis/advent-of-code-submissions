#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Generic, Type, List

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        1342
        """
        return LiteralSet.from_literals_text(_input).get_total_net_length()


LiteralT = TV['Literal']


@dataclass
class LiteralSet(Generic[LiteralT]):
    literals: List[LiteralT]

    @classmethod
    def get_literal_class(cls) -> Type[LiteralT]:
        return get_type_argument_class(cls, LiteralT)

    @classmethod
    def from_literals_text(cls, literals_text: str):
        """
        >>> LiteralSet.from_literals_text(
        ...     '""\\n'
        ...     '"abc"\\n'
        ...     '"aaa\\\\"aaa"\\n'
        ...     '"\\\\x27"\\n'
        ... )
        LiteralSet(literals=[Literal(code='""', string=''),
            Literal(code='"abc"', string='abc'),
            Literal(code='"aaa\\\\"aaa"', string='aaa"aaa'),
            Literal(code='"\\\\x27"', string="'")])
        """
        literal_class = cls.get_literal_class()
        return cls(list(map(
            literal_class.from_literal_text, literals_text.splitlines())))

    def get_total_net_length(self) -> int:
        """
        >>> LiteralSet.from_literals_text(
        ...     '""\\n'
        ...     '"abc"\\n'
        ...     '"aaa\\\\"aaa"\\n'
        ...     '"\\\\x27"\\n'
        ... ).get_total_net_length()
        12
        """
        return sum(
            literal.get_net_length()
            for literal in self.literals
        )


@dataclass
class Literal:
    code: str
    string: str

    @classmethod
    def from_literal_text(cls, literal_text: str):
        """
        >>> Literal.from_literal_text(r'""')
        Literal(code='""', string='')
        >>> Literal.from_literal_text(r'"abc"')
        Literal(code='"abc"', string='abc')
        >>> Literal.from_literal_text(r'"aaa\\"aaa"')
        Literal(code='"aaa\\\\"aaa"', string='aaa"aaa')
        >>> Literal.from_literal_text(r'"\\x27"')
        Literal(code='"\\\\x27"', string="'")
        """
        return cls(literal_text, eval(literal_text))

    def get_net_length(self) -> int:
        return self.get_code_length() - self.get_string_length()

    def get_code_length(self) -> int:
        """
        >>> Literal.from_literal_text(r'""').get_code_length()
        2
        >>> Literal.from_literal_text(r'"abc"').get_code_length()
        5
        >>> Literal.from_literal_text(r'"aaa\\"aaa"').get_code_length()
        10
        >>> Literal.from_literal_text(r'"\\x27"').get_code_length()
        6
        """
        return len(self.code)

    def get_string_length(self) -> int:
        """
        >>> Literal.from_literal_text(r'""').get_string_length()
        0
        >>> Literal.from_literal_text(r'"abc"').get_string_length()
        3
        >>> Literal.from_literal_text(r'"aaa\\"aaa"').get_string_length()
        7
        >>> Literal.from_literal_text(r'"\\x27"').get_string_length()
        1
        """
        return len(self.string)


Challenge.main()
challenge = Challenge()
