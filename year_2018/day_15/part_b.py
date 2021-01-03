#!/usr/bin/env python3
import copy
import itertools

import utils
from year_2018.day_15 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        53576
        """
        return CaveExtended.from_cave_text(_input)\
            .get_outcome_for_smallest_sufficient_elf_attack()


class CaveExtended(part_a.Cave):
    def get_outcome_for_smallest_sufficient_elf_attack(self, debug=False):
        """
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... ).get_outcome_for_smallest_sufficient_elf_attack()
        4988
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#E..EG#\\n"
        ...     "#.#G.E#\\n"
        ...     "#E.##E#\\n"
        ...     "#G..#.#\\n"
        ...     "#..E#.#\\n"
        ...     "#######\\n"
        ... ).get_outcome_for_smallest_sufficient_elf_attack()
        31284
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#E.G#.#\\n"
        ...     "#.#G..#\\n"
        ...     "#G.#.G#\\n"
        ...     "#G..#.#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).get_outcome_for_smallest_sufficient_elf_attack()
        3478
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.E...#\\n"
        ...     "#.#..G#\\n"
        ...     "#.###.#\\n"
        ...     "#E#G#G#\\n"
        ...     "#...#G#\\n"
        ...     "#######\\n"
        ... ).get_outcome_for_smallest_sufficient_elf_attack()
        6474
        >>> CaveExtended.from_cave_text(
        ...     "#########\\n"
        ...     "#G......#\\n"
        ...     "#.E.#...#\\n"
        ...     "#..##..G#\\n"
        ...     "#...##..#\\n"
        ...     "#...#...#\\n"
        ...     "#.G...G.#\\n"
        ...     "#.....G.#\\n"
        ...     "#########\\n"
        ... ).get_outcome_for_smallest_sufficient_elf_attack()
        1140
        """
        smallest_sufficient_elf_attack =\
            self.find_smallest_sufficient_elf_attack(debug=debug)
        return self.duplicate()\
            .update_elf_attack(smallest_sufficient_elf_attack)\
            .tick_many()\
            .get_outcome()

    def find_smallest_sufficient_elf_attack(self, debug=False):
        """
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... ).find_smallest_sufficient_elf_attack()
        15
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#E..EG#\\n"
        ...     "#.#G.E#\\n"
        ...     "#E.##E#\\n"
        ...     "#G..#.#\\n"
        ...     "#..E#.#\\n"
        ...     "#######\\n"
        ... ).find_smallest_sufficient_elf_attack()
        4
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#E.G#.#\\n"
        ...     "#.#G..#\\n"
        ...     "#G.#.G#\\n"
        ...     "#G..#.#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).find_smallest_sufficient_elf_attack()
        15
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.E...#\\n"
        ...     "#.#..G#\\n"
        ...     "#.###.#\\n"
        ...     "#E#G#G#\\n"
        ...     "#...#G#\\n"
        ...     "#######\\n"
        ... ).find_smallest_sufficient_elf_attack()
        12
        >>> CaveExtended.from_cave_text(
        ...     "#########\\n"
        ...     "#G......#\\n"
        ...     "#.E.#...#\\n"
        ...     "#..##..G#\\n"
        ...     "#...##..#\\n"
        ...     "#...#...#\\n"
        ...     "#.G...G.#\\n"
        ...     "#.....G.#\\n"
        ...     "#########\\n"
        ... ).find_smallest_sufficient_elf_attack()
        34
        """
        return utils.helper.find_smallest_required_value(
            3, self.is_elf_attack_sufficient, debug=debug)

    def is_elf_attack_sufficient(self, elf_attack, debug=False):
        """
        >>> cave = CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... )
        >>> cave.is_elf_attack_sufficient(14)
        False
        >>> cave.is_elf_attack_sufficient(3)
        False
        >>> cave.is_elf_attack_sufficient(15)
        True
        """
        dead_elf_count = self.duplicate()\
            .update_elf_attack(elf_attack)\
            .tick_many()\
            .get_dead_elf_count()

        if debug:
            print(f"With elf attack {elf_attack} {dead_elf_count} elves died")

        return dead_elf_count == 0

    def duplicate(self):
        """
        >>> cave = CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... )
        >>> duplicated = cave.duplicate()
        >>> print(cave.tick_many().show())
        #######
        #G....#
        #.G...#
        #.#.#G#
        #...#.#
        #....G#
        #######
        >>> print(duplicated.show())
        #######
        #.G...#
        #...EG#
        #.#.#G#
        #..G#E#
        #.....#
        #######
        >>> cave = CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... )
        >>> duplicated = cave.duplicate()
        >>> print(duplicated.tick_many().show())
        #######
        #G....#
        #.G...#
        #.#.#G#
        #...#.#
        #....G#
        #######
        >>> print(cave.show())
        #######
        #.G...#
        #...EG#
        #.#.#G#
        #..G#E#
        #.....#
        #######
        """
        cls = type(self)
        cave_with_attack = cls(
            self.spaces, copy.deepcopy(self.units), step_count=self.step_count)

        return cave_with_attack

    def update_elf_attack(self, elf_attack):
        """
        >>> cave = CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... )
        >>> {
        ...     _type: sorted(set(unit.attack for unit in units))
        ...     for _type, units
        ...     in itertools.groupby(sorted(
        ...         cave.units, key=lambda unit: type(unit).__name__),
        ...         key=lambda unit: type(unit).__name__)
        ... }
        {'Elf': [3], 'Goblin': [3]}
        >>> cave.update_elf_attack(5)
        C...
        >>> {
        ...     _type: sorted(set(unit.attack for unit in units))
        ...     for _type, units
        ...     in itertools.groupby(sorted(
        ...         cave.units, key=lambda unit: type(unit).__name__),
        ...         key=lambda unit: type(unit).__name__)
        ... }
        {'Elf': [5], 'Goblin': [3]}
        """
        for unit in self.units:
            if not isinstance(unit, part_a.Elf):
                continue
            unit.attack = elf_attack

        return self

    def get_dead_elf_count(self):
        """
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_dead_elf_count()
        2
        >>> CaveExtended.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... , elf_attack=15).tick_many().get_dead_elf_count()
        0
        """
        return sum(
            1
            for unit in self.units_at_start
            if isinstance(unit, part_a.Elf)
            and unit.is_dead()
        )


challenge = Challenge()
challenge.main()
