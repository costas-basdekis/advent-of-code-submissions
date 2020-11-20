#!/usr/bin/env python3
import re
import string
from dataclasses import dataclass

import utils


class Challenge(utils.BaseChallenge):
    DEFAULT_GROUP = string.ascii_lowercase[:16]

    def solve(self, _input, debug=False):
        """
        >>> Challenge.DEFAULT_GROUP
        'abc...p'
        >>> Challenge().default_solve()
        'cknmidebghlajpfo'
        """
        return Program.from_program_text(_input)\
            .apply(self.DEFAULT_GROUP)


class Program:
    @classmethod
    def from_program_text(cls, program_text):
        """
        >>> Program.from_program_text('s1,x3/4,pe/b').moves
        [Spin(count=1), Exchange(position_a=3, position_b=4),
            Partner(partner_a='e', partner_b='b')]
        """
        move_texts = program_text.strip().split(',')
        return cls(list(map(Move.from_move_text, move_texts)))

    def __init__(self, moves):
        self.moves = moves

    def apply(self, group):
        """
        >>> Program.from_program_text('s1,x3/4,pe/b').apply('abcde')
        'baedc'
        """
        for move in self.moves:
            group = move.apply(group)

        return group


class Move:
    name = NotImplemented

    move_classes = {}

    @classmethod
    def register(cls, move_class, override=False):
        name = move_class.name
        if name is NotImplemented:
            raise Exception(f"{move_class.__name__} did not set a 'name'")
        if name in cls.move_classes and not override:
            raise Exception(
                f"{move_class.__name__} tried to override '{name}' which was "
                f"registered by {cls.move_classes[name].__name__}")
        cls.move_classes[name] = move_class

        return move_class

    @classmethod
    def from_move_text(cls, move_text):
        """
        >>> Move.from_move_text('s1')
        Spin(count=1)
        >>> Move.from_move_text('x3/4')
        Exchange(position_a=3, position_b=4)
        >>> Move.from_move_text('pe/b')
        Partner(partner_a='e', partner_b='b')
        """
        for move_class in cls.move_classes.values():
            move = move_class.try_parse(move_text)
            if move:
                break
        else:
            raise Exception(f"Could not parse '{move_text}'")

        return move

    @classmethod
    def try_parse(cls, move_text):
        raise NotImplementedError()

    def apply(self, group):
        raise NotImplementedError()


@Move.register
@dataclass
class Spin(Move):
    name = 'spin'

    count: int

    re_spin = re.compile(r"^s(\d+)$")

    @classmethod
    def try_parse(cls, move_text):
        """
        >>> Spin.try_parse('s1')
        Spin(count=1)
        >>> Spin.try_parse('x3/4')
        >>> Spin.try_parse('pe/b')
        """
        match = cls.re_spin.match(move_text)
        if not match:
            return None
        count_str, = match.groups()
        return cls(int(count_str))

    def apply(self, group):
        """
        >>> Spin(1).apply('abcde')
        'eabcd'
        """
        return group[-self.count:] + group[:-self.count]


@Move.register
@dataclass
class Exchange(Move):
    name = 'exchange'

    position_a: int
    position_b: int

    re_exchange = re.compile(r"^x(\d+)/(\d+)$")

    @classmethod
    def try_parse(cls, move_text):
        """
        >>> Exchange.try_parse('x3/4')
        Exchange(position_a=3, position_b=4)
        >>> Exchange.try_parse('x4/3')
        Exchange(position_a=3, position_b=4)
        >>> Exchange.try_parse('s1')
        >>> Exchange.try_parse('pe/b')
        """
        match = cls.re_exchange.match(move_text)
        if not match:
            return None
        position_a_str, position_b_str = match.groups()
        position_a = int(position_a_str)
        position_b = int(position_b_str)
        if position_a > position_b:
            position_a, position_b = position_b, position_a
        return cls(position_a, position_b)

    def apply(self, group):
        """
        >>> Exchange(3, 4).apply('eabcd')
        'eabdc'
        """
        return (
            group[:self.position_a]
            + group[self.position_b]
            + group[self.position_a + 1:self.position_b]
            + group[self.position_a]
            + group[self.position_b + 1:]
        )


@Move.register
@dataclass
class Partner(Move):
    name = 'partner'

    partner_a: str
    partner_b: str

    re_partner = re.compile(r"^p(\w)/(\w)$")

    @classmethod
    def try_parse(cls, move_text):
        """
        >>> Partner.try_parse('pe/b')
        Partner(partner_a='e', partner_b='b')
        >>> Partner.try_parse('s1')
        >>> Partner.try_parse('x3/4')
        """
        match = cls.re_partner.match(move_text)
        if not match:
            return None
        partner_a, partner_b = match.groups()
        return cls(partner_a, partner_b)

    def apply(self, group):
        """
        >>> Partner('e', 'b').apply('eabdc')
        'baedc'
        """
        position_a = group.index(self.partner_a)
        position_b = group.index(self.partner_b)
        if position_a > position_b:
            position_a, position_b = position_b, position_a

        return (
            group[:position_a]
            + group[position_b]
            + group[position_a + 1:position_b]
            + group[position_a]
            + group[position_b + 1:]
        )


challenge = Challenge()
challenge.main()
