#!/usr/bin/env python3
import json

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        2074
        """
        return LiteralSetExtended.from_literals_text(_input)\
            .encode()\
            .get_total_net_length()


class LiteralSetExtended(part_a.LiteralSet['LiteralExtended']):
    def encode(self) -> 'LiteralSetExtended':
        """
        >>> LiteralSetExtended.from_literals_text(
        ...     '""\\n'
        ...     '"abc"\\n'
        ...     '"aaa\\\\"aaa"\\n'
        ...     '"\\\\x27"\\n'
        ... ).encode().get_total_net_length()
        19
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls([
            literal.encode()
            for literal in self.literals
        ])


class LiteralExtended(part_a.Literal):
    def encode(self) -> 'LiteralExtended':
        cls = type(self)
        # noinspection PyArgumentList
        return cls(json.dumps(self.code), self.code)


Challenge.main()
challenge = Challenge()
