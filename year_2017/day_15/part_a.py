#!/usr/bin/env python3
import itertools
import re
from dataclasses import dataclass

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        638
        """
        return GeneratorPair.from_generators_text(_input).get_pair_match_count()


class GeneratorPair:
    generator_class = NotImplemented

    FACTORS = {
        'A': 16807,
        'B': 48271,
    }

    @classmethod
    def from_generators_text(cls, generators_text):
        """
        >>> GeneratorPair.from_generators_text(
        ...     "Generator A starts with 65\\n"
        ...     "Generator B starts with 8921\\n"
        ... ).generators
        {'A': Generator(name='A', value=65, factor=16807),
            'B': Generator(name='B', value=8921, factor=48271)}
        """
        return cls({
            generator.name: generator
            for generator in (
                cls.generator_class.from_generator_text(line, cls.FACTORS)
                for line in generators_text.strip().splitlines()
            )
        })

    def __init__(self, generators):
        self.generators = generators

    def get_pair_match_count(self, count=40 * 1000 * 1000):
        """
        >>> GeneratorPair.from_generators_text(
        ...     "Generator A starts with 65\\n"
        ...     "Generator B starts with 8921\\n"
        ... ).get_pair_match_count(5)
        1
        >>> GeneratorPair.from_generators_text(
        ...     "Generator A starts with 65\\n"
        ...     "Generator B starts with 8921\\n"
        ... ).get_pair_match_count()
        588
        """
        return sum(
            1
            for pair in self.get_pairs(count)
            if self.does_pair_match(pair)
        )

    MATCH_BITS = 16
    MATCH_MODULO = 2 ** MATCH_BITS - 1

    def does_pair_match(self, pair):
        """
        >>> GeneratorPair({}).does_pair_match((1092455, 430625591))
        False
        >>> GeneratorPair({}).does_pair_match((1181022009, 1233683848))
        False
        >>> GeneratorPair({}).does_pair_match((245556042, 1431495498))
        True
        >>> GeneratorPair({}).does_pair_match((1744312007, 137874439))
        False
        >>> GeneratorPair({}).does_pair_match((1352636452, 285222916))
        False
        """
        value_a, value_b = pair
        return (value_a & self.MATCH_MODULO) == (value_b & self.MATCH_MODULO)

    def get_pairs(self, count=None):
        """
        >>> list(GeneratorPair.from_generators_text(
        ...     "Generator A starts with 65\\n"
        ...     "Generator B starts with 8921\\n"
        ... ).get_pairs(5))
        [(1092455, 430625591), (1181022009, 1233683848),
            (245556042, 1431495498), (1744312007, 137874439),
            (1352636452, 285222916)]
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)

        generator_a = self.generators['A']
        generator_b = self.generators['B']
        for _ in steps:
            value_a = generator_a.step()
            value_b = generator_b.step()
            yield value_a, value_b


@dataclass
class Generator:
    name: str
    value: int
    factor: int

    re_generator = re.compile(r'^Generator ([AB]) starts with (\d+)$')

    @classmethod
    def from_generator_text(cls, generator_text, factors):
        """
        >>> Generator.from_generator_text(
        ...     'Generator A starts with 65', {'A': 1})
        Generator(name='A', value=65, factor=1)
        """
        name, value = cls.parse_generator(generator_text)
        factor = factors[name]

        return cls(name, value, factor)

    @classmethod
    def parse_generator(cls, generator_text):
        name, value_str = cls.re_generator.match(generator_text).groups()
        value = int(value_str)

        return name, value

    MODULO = 2147483647

    def step(self):
        """
        >>> generator_a = Generator('A', 65, 16807)
        >>> [generator_a.step() for _ in range(5)]
        [1092455, 1181022009, 245556042, 1744312007, 1352636452]
        >>> generator_b = Generator('A', 8921, 48271)
        >>> [generator_b.step() for _ in range(5)]
        [430625591, 1233683848, 1431495498, 137874439, 285222916]
        """
        self.value = (self.value * self.factor) % self.MODULO

        return self.value


GeneratorPair.generator_class = Generator


challenge = Challenge()
challenge.main()
