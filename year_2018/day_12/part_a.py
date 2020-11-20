#!/usr/bin/env python3
import doctest
import itertools
import re
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    3221
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    pot_state, rule_set = PotRuleSet.read_state_and_rule_set(_input)

    return rule_set\
        .advance_state_many_times(pot_state, 20)\
        .get_pot_sum()


class PotRuleSet:
    re_state = re.compile(r"^initial state: ([.#]+)$")

    @classmethod
    def read_state_and_rule_set(cls, state_and_rule_set_text):
        parts = state_and_rule_set_text.strip().split('\n\n')
        if len(parts) != 2:
            raise Exception(f"Expected 2 parts but got {len(parts)}")
        state_text, rules_text = parts

        state_match = cls.re_state.match(state_text)
        if not state_match:
            raise Exception(f"First line was not state: '{state_text}'")

        pot_state_text, = state_match.groups()
        pot_state = PotState.from_pot_state_text(pot_state_text)

        rule_set = cls.from_pot_rules_text(rules_text)

        return pot_state, rule_set

    @classmethod
    def from_pot_rules_text(cls, pot_rules_text, allow_missing=False):
        """
        >>> list(map(tuple, PotRuleSet.from_pot_rules_text((
        ...     "...## => #\\n"
        ...     "..#.. => #\\n"
        ...     ".#... => #\\n"
        ... ), True).pot_rules))
        [((False, False, False, True, True), True), ((False, False, True, False, False), True), ((False, True, False, False, False), True)]
        """
        rules = list(map(
            PotRule.from_pot_rule_text,
            filter(None, pot_rules_text.splitlines())))

        return cls(rules, allow_missing)

    def __init__(self, pot_rules, allow_missing=False):
        """
        >>> PotRuleSet([PotRule((False,) * 5, False)], True)\\
        ...     .neighbour_length
        5
        >>> PotRuleSet([PotRule((False,) * 5, False)], True)\\
        ...     .max_neighbour_distance
        2
        """
        self.pot_rules = pot_rules
        self.by_neighbour_pots = self\
            .get_by_neighbour_pots(pot_rules, allow_missing)
        self.neighbour_length = len(self.pot_rules[0].neighbour_pots)
        self.max_neighbour_distance = (self.neighbour_length - 1) // 2

    def get_by_neighbour_pots(self, pot_rules, allow_missing):
        """
        >>> PotRuleSet([PotRule((True,), True)], True).by_neighbour_pots
        {(True,): True, (False,): False}
        >>> PotRuleSet([PotRule((True,), True)], False).by_neighbour_pots
        Traceback (most recent call last):
        ...
        Exception: Did not allow missing rules, but only 1 out of 2 were given
        >>> PotRuleSet([
        ...     PotRule((True,), True), PotRule((False,), False)
        ... ], False).by_neighbour_pots
        {(True,): True, (False,): False}
        >>> PotRuleSet([
        ...     PotRule((True,), True), PotRule((True,), False)
        ... ], False).by_neighbour_pots
        Traceback (most recent call last):
        ...
        Exception: Multiple rules had the same input: (True,)
        >>> PotRuleSet([
        ...     PotRule((True,), True), PotRule((False, False), False)
        ... ], False).by_neighbour_pots
        Traceback (most recent call last):
        ...
        Exception: Expected all rules to have the same length, but got [1, 2]
        """
        lengths = {len(rule.neighbour_pots) for rule in pot_rules}
        if len(lengths) != 1:
            raise Exception(
                f"Expected all rules to have the same length, but got "
                f"{sorted(lengths)}")
        length, = lengths
        by_neighbour_pots = {}
        for rule in pot_rules:
            if rule.neighbour_pots in by_neighbour_pots:
                raise Exception(
                    f"Multiple rules had the same input: "
                    f"{rule.neighbour_pots}")
            by_neighbour_pots[rule.neighbour_pots] = rule.result
        if len(by_neighbour_pots) < 2 ** length:
            if not allow_missing:
                raise Exception(
                    f"Did not allow missing rules, but only "
                    f"{len(by_neighbour_pots)} out of {2 ** length} were "
                    f"given")
            for neighbour_pots \
                    in itertools.product((False, True), repeat=length):
                if neighbour_pots not in by_neighbour_pots:
                    by_neighbour_pots[neighbour_pots] = False

        if by_neighbour_pots[(False,) * length]:
            raise Exception(
                "Expected empty rule to return empty, but it did not")

        return by_neighbour_pots

    def advance_state_many_times(self, pot_state, count):
        """
        >>> pot_rule_set_a = PotRuleSet.from_pot_rules_text((
        ...     "...## => #\\n"
        ...     "..#.. => #\\n"
        ...     ".#... => #\\n"
        ...     ".#.#. => #\\n"
        ...     ".#.## => #\\n"
        ...     ".##.. => #\\n"
        ...     ".#### => #\\n"
        ...     "#.#.# => #\\n"
        ...     "#.### => #\\n"
        ...     "##.#. => #\\n"
        ...     "##.## => #\\n"
        ...     "###.. => #\\n"
        ...     "###.# => #\\n"
        ...     "####. => #\\n"
        ... ), True)
        >>> print("!", pot_rule_set_a.advance_state_many_times(
        ...     PotState.from_pot_state_text("#"), 1)\\
        ...     .show())
        ! ##
        >>> print("!", pot_rule_set_a.advance_state_many_times(
        ...     PotState.from_pot_state_text("#..#.#..##......###...###"), 1)\\
        ...     .show(range(-3, 36)))
        ! ...#...#....#.....#..#..#..#...........
        >>> print("!", pot_rule_set_a.advance_state_many_times(
        ...     PotState.from_pot_state_text("#..#.#..##......###...###"), 20)\\
        ...     .show(range(-3, 36)))
        ! .#....##....#####...#######....#.#..##.
        """
        for _ in range(count):
            pot_state = self.advance_state(pot_state)

        return pot_state

    def advance_state(self, pot_state):
        """
        >>> pot_rule_set_a = PotRuleSet.from_pot_rules_text((
        ...     "...## => #\\n"
        ...     "..#.. => #\\n"
        ...     ".#... => #\\n"
        ...     ".#.#. => #\\n"
        ...     ".#.## => #\\n"
        ...     ".##.. => #\\n"
        ...     ".#### => #\\n"
        ...     "#.#.# => #\\n"
        ...     "#.### => #\\n"
        ...     "##.#. => #\\n"
        ...     "##.## => #\\n"
        ...     "###.. => #\\n"
        ...     "###.# => #\\n"
        ...     "####. => #\\n"
        ... ), True)
        >>> print("!", pot_rule_set_a.advance_state(
        ...     PotState.from_pot_state_text("#"))\\
        ...     .show())
        ! ##
        >>> print("!", pot_rule_set_a.advance_state(
        ...     PotState.from_pot_state_text("#..#"))\\
        ...     .show())
        ! #..##
        >>> print("!", pot_rule_set_a.advance_state(
        ...     PotState.from_pot_state_text("#..#.#"))\\
        ...     .show())
        ! #...#.#
        >>> print("!", pot_rule_set_a.advance_state(
        ...     PotState.from_pot_state_text("#..#.#..##......###...###"))\\
        ...     .show())
        ! #...#....#.....#..#..#..#
        >>> PotState.from_pot_state_text("#..#.#..##......###...###")\\
        ...     .get_indexes_range()
        (0, 24)
        >>> pot_rule_set_a.advance_state(
        ...     PotState.from_pot_state_text("#..#.#..##......###...###"))\\
        ...     .get_indexes_range()
        (0, 24)
        >>> print("!", pot_rule_set_a.advance_state(
        ...     PotState.from_pot_state_text("#..#.#..##......###...###"))\\
        ...     .show(range(-3, 36)))
        ! ...#...#....#.....#..#..#..#...........
        """
        min_index, max_index = pot_state.get_indexes_range()
        min_update_index = min_index - self.max_neighbour_distance
        max_update_index = max_index + self.max_neighbour_distance
        return PotState.from_pot_state_tuple(tuple(
            self.get_next_pot_at_position(pot_state, position)
            for position in range(min_update_index, max_update_index + 1)
        ), min_update_index)

    def get_next_pot_at_position(self, pot_state, position):
        """
        >>> PotRuleSet(
        ...     [PotRule((False, False, True, False, False), True)], True)\\
        ...     .get_next_pot_at_position(PotState.from_pot_state_text("#"), 0)
        True
        >>> PotRuleSet(
        ...     [PotRule((False, False, True, False, False), True)], True)\\
        ...     .get_next_pot_at_position(PotState.from_pot_state_text("#"), -3)
        False
        """
        pots_around = self.get_pots_around(pot_state, position)
        return self.by_neighbour_pots[pots_around]

    def get_pots_around(self, pot_state, position):
        """
        >>> PotRuleSet(
        ...     [PotRule((False, False, True, False, False), True)], True)\\
        ...     .get_pots_around(PotState.from_pot_state_text("#"), 0)
        (False, False, True, False, False)
        >>> PotRuleSet(
        ...     [PotRule((False, False, True, False, False), True)], True)\\
        ...     .get_pots_around(PotState.from_pot_state_text("#"), -3)
        (False, False, False, False, False)
        """
        return tuple(
            index in pot_state.active_pot_indexes
            for index in range(
                position - self.max_neighbour_distance,
                position + self.max_neighbour_distance + 1,
            )
        )


class PotRule(namedtuple("PotRule", ("neighbour_pots", "result"))):
    re_pot_rule = re.compile(r"([.#]+) => ([.#])")

    @classmethod
    def from_pot_rule_text(cls, pot_rule_text):
        """
        >>> PotRule.from_pot_rule_text("...## => #")
        PotRule(neighbour_pots=(False, False, False, True, True), result=True)
        >>> PotRule.from_pot_rule_text("..... => .")
        PotRule(neighbour_pots=(False, False, False, False, False), result=False)
        """
        neighbour_pots_str, result_str = \
            cls.re_pot_rule.match(pot_rule_text).groups()
        if len(neighbour_pots_str) % 2 != 1:
            raise Exception(
                f"Expected odd length for neighbours, but got "
                f"{len(neighbour_pots_str)}: '{neighbour_pots_str}'")
        neighbour_pots = tuple(map("#".__eq__, neighbour_pots_str))
        result = result_str == "#"

        return cls(neighbour_pots, result)


class PotState(namedtuple("PotState", ("active_pot_indexes",))):
    @classmethod
    def from_pot_state_text(cls, pot_state_text, start_index=0):
        """
        >>> PotState.from_pot_state_text("#..#.#..##......###...###")
        PotState(active_pot_indexes=(0, 3, 5, 8, 9, 16, 17, 18, 22, 23, 24))
        """
        return cls.from_pot_state_tuple(tuple(
            pot == "#"
            for pot in pot_state_text.strip()
        ), start_index=start_index)

    @classmethod
    def from_pot_state_tuple(cls, pot_state, start_index=0):
        """
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False, True, False, False, True,
        ...     True, False, False, False, False, False, False, True, True,
        ...     True, False, False, False, True, True, True))
        PotState(active_pot_indexes=(0, 3, 5, 8, 9, 16, 17, 18, 22, 23, 24))
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False, True, False, False, True,
        ...     True, False, False, False, False, False, False, True, True,
        ...     True, False, False, False, True, True, True), 3)
        PotState(active_pot_indexes=(3, 6, 8, 11, 12, 19, 20, 21, 25, 26, 27))
        """
        return cls(tuple(
            index
            for index, pot in enumerate(pot_state, start=start_index)
            if pot
        ))

    SHOW_MAP = {
        False: ".",
        True: "#",
    }

    def to_tuple(self, start, length):
        """
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False)).to_tuple(0, 5)
        (True, False, False, True, False)
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False), 3).to_tuple(0, 5)
        (False, False, False, True, False)
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False)).to_tuple(-3, 5)
        (False, False, False, True, False)
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False), -3).to_tuple(0, 5)
        (True, False, False, False, False)
        >>> PotState.from_pot_state_tuple((
        ...     True, False, False, True, False)).to_tuple(3, 5)
        (True, False, False, False, False)
        """
        return tuple(
            index in self.active_pot_indexes
            for index in range(start, start + length)
        )

    def show(self, _range=None):
        """
        >>> print("!", PotState.from_pot_state_text(
        ...     "#..#.#..##......###...###").show(range(-3, 36)))
        ! ...#..#.#..##......###...###...........
        >>> print("!", PotState.from_pot_state_text(
        ...     "#..#.#..##......###...###").show())
        ! #..#.#..##......###...###
        """
        if _range is None:
            min_index, max_index = self.get_indexes_range()
            _range = range(min_index, max_index + 1)
        return "".join(
            self.SHOW_MAP[index in self.active_pot_indexes]
            for index in _range
        )

    def get_indexes_range(self):
        min_index = min(self.active_pot_indexes)
        max_index = max(self.active_pot_indexes)
        return min_index, max_index

    def get_pot_sum(self):
        """
        >>> PotState.from_pot_state_text(
        ...     ".#....##....#####...#######....#.#..##.", -3).get_pot_sum()
        325
        """
        return sum(self.active_pot_indexes)


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
