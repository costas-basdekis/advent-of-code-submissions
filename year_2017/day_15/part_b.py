#!/usr/bin/env python3
from dataclasses import dataclass

import utils
from year_2017.day_15 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        343
        """
        return GeneratorPairExtended.from_generators_text(_input)\
            .get_pair_match_count(5 * 1000 * 1000)


class GeneratorPairExtended(part_a.GeneratorPair):
    """
    >>> GeneratorPairExtended.from_generators_text(
    ...     "Generator A starts with 65\\n"
    ...     "Generator B starts with 8921\\n"
    ... ).get_pair_match_count(1055)
    0
    >>> GeneratorPairExtended.from_generators_text(
    ...     "Generator A starts with 65\\n"
    ...     "Generator B starts with 8921\\n"
    ... ).get_pair_match_count(1056)
    1
    >>> GeneratorPairExtended.from_generators_text(
    ...     "Generator A starts with 65\\n"
    ...     "Generator B starts with 8921\\n"
    ... ).get_pair_match_count(5 * 1000 * 1000)
    309
    """
    SKIP_MODULOS = {
        'A': 4,
        'B': 8,
    }

    @classmethod
    def from_generators_text(cls, generators_text):
        """
        >>> GeneratorPairExtended.from_generators_text(
        ...     "Generator A starts with 65\\n"
        ...     "Generator B starts with 8921\\n"
        ... ).generators
        {'A': GeneratorExtended(name='A', value=65, factor=16807,
            skip_modulo=4),
            'B': GeneratorExtended(name='B', value=8921, factor=48271,
                skip_modulo=8)}
        """
        return cls({
            generator.name: generator
            for generator in (
                cls.generator_class.from_generator_text_extended(
                    line, cls.FACTORS, cls.SKIP_MODULOS)
                for line in generators_text.strip().splitlines()
            )
        })


@dataclass
class GeneratorExtended(part_a.Generator):
    skip_modulo: int

    @classmethod
    def from_generator_text_extended(cls, generator_text, factors,
                                     skip_modulos):
        """
        >>> GeneratorExtended.from_generator_text_extended(
        ...     'Generator A starts with 65', {'A': 1}, {'A': 4})
        GeneratorExtended(name='A', value=65, factor=1, skip_modulo=4)
        """
        name, value = cls.parse_generator(generator_text)
        factor = factors[name]
        skip_modulo = skip_modulos[name]

        return cls(name, value, factor, skip_modulo)

    def step(self):
        """
        >>> generator_a = GeneratorExtended('A', 65, 16807, 4)
        >>> [generator_a.step() for _ in range(5)]
        [1352636452, 1992081072, 530830436, 1980017072, 740335192]
        >>> generator_b = GeneratorExtended('b', 8921, 48271, 8)
        >>> [generator_b.step() for _ in range(5)]
        [1233683848, 862516352, 1159784568, 1616057672, 412269392]
        """
        while super().step() % self.skip_modulo != 0:
            pass

        return self.value


GeneratorPairExtended.generator_class = GeneratorExtended


Challenge.main()
challenge = Challenge()
