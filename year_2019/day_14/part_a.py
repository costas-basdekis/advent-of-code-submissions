#!/usr/bin/env python3
import doctest
import math
import re
from collections import defaultdict

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    143173
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    reactions = parse_reactions(_input)
    return get_ore_requirements(reactions)


def get_ore_requirements(reactions, fuel_count=1):
    """
    >>> get_ore_requirements(parse_reactions(\
        "1 ORE => 5 A\\n"\
        "1 ORE => 5 B\\n"\
        "1 A, 1 B => 1 FUEL"), 15)
    6
    >>> get_ore_requirements(parse_reactions(\
        "10 ORE => 10 A\\n"\
        "1 ORE => 1 B\\n"\
        "7 A, 1 B => 1 C\\n"\
        "7 A, 1 C => 1 D\\n"\
        "7 A, 1 D => 1 E\\n"\
        "7 A, 1 E => 1 FUEL"))
    31
    >>> get_ore_requirements(parse_reactions(\
        "9 ORE => 2 A\\n"\
        "8 ORE => 3 B\\n"\
        "7 ORE => 5 C\\n"\
        "3 A, 4 B => 1 AB\\n"\
        "5 B, 7 C => 1 BC\\n"\
        "4 C, 1 A => 1 CA\\n"\
        "2 AB, 3 BC, 4 CA => 1 FUEL"))
    165
    >>> get_ore_requirements(parse_reactions(\
        "157 ORE => 5 NZVS\\n"\
        "165 ORE => 6 DCFZ\\n"\
        "44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL\\n"\
        "12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ\\n"\
        "179 ORE => 7 PSHF\\n"\
        "177 ORE => 5 HKGWZ\\n"\
        "7 DCFZ, 7 PSHF => 2 XJWVT\\n"\
        "165 ORE => 2 GPVTF\\n"\
        "3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT"))
    13312
    >>> get_ore_requirements(parse_reactions(\
        "2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG\\n"\
        "17 NVRVD, 3 JNWZP => 8 VPVL\\n"\
        "53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL\\n"\
        "22 VJHF, 37 MNCFX => 5 FWMGM\\n"\
        "139 ORE => 4 NVRVD\\n"\
        "144 ORE => 7 JNWZP\\n"\
        "5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC\\n"\
        "5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV\\n"\
        "145 ORE => 6 MNCFX\\n"\
        "1 NVRVD => 8 CXFTF\\n"\
        "1 VJHF, 6 MNCFX => 4 RFSQX\\n"\
        "176 ORE => 6 VJHF"))
    180697
    >>> get_ore_requirements(parse_reactions(\
        "171 ORE => 8 CNZTR\\n"\
        "7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL\\n"\
        "114 ORE => 4 BHXH\\n"\
        "14 VRPVC => 6 BMBT\\n"\
        "6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL\\n"\
        "6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT\\n"\
        "15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW\\n"\
        "13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW\\n"\
        "5 BMBT => 4 WPTQ\\n"\
        "189 ORE => 9 KTJDG\\n"\
        "1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP\\n"\
        "12 VRPVC, 27 CNZTR => 2 XDBXC\\n"\
        "15 KTJDG, 12 BHXH => 5 XCVML\\n"\
        "3 BHXH, 2 VRPVC => 7 MZWV\\n"\
        "121 ORE => 7 VRPVC\\n"\
        "7 XCVML => 6 RJRHP\\n"\
        "5 BHXH, 4 VRPVC => 5 LTCX"))
    2210736
    """
    balance = get_balance(reactions, {'FUEL': fuel_count})

    if 'ORE' not in balance:
        raise Exception("Finished all requirements, but not ORE was required")
    return balance['ORE']


def get_balance(reactions, target):
    balance = defaultdict(lambda: 0, target)
    while True:
        needs = [
            result
            for result, quantity in balance.items()
            if result != 'ORE'
            and quantity > 0
        ]
        if not needs:
            break
        result = needs[0]
        needed_quantity = balance[result]
        reaction_quantity, ingredients = reactions[result]
        reaction_count = math.ceil(needed_quantity / reaction_quantity)
        balance[result] -= reaction_quantity * reaction_count
        for ingredient, quantity in ingredients:
            balance[ingredient] += quantity * reaction_count

    zero_needs = [
        need
        for need, quantity in balance.items()
        if quantity == 0
    ]
    for need in zero_needs:
        del balance[need]

    return balance


def parse_reactions(reactions_text):
    """
    >>> parse_reactions(\
        "10 ORE => 10 A\\n1 ORE => 1 B\\n7 A, 1 B => 1 C\\n7 A, 1 C => 1 D"\
        "\\n7 A, 1 D => 1 E\\n7 A, 1 E => 1 FUEL")
    {'A': (10, [('ORE', 10)]), 'B': (1, [('ORE', 1)]), \
'C': (1, [('A', 7), ('B', 1)]), 'D': (1, [('A', 7), ('C', 1)]), \
'E': (1, [('A', 7), ('D', 1)]), 'FUEL': (1, [('A', 7), ('E', 1)])}
    """
    lines = reactions_text.splitlines()
    non_empty_lines = list(filter(None, map(str.strip, lines)))
    parsed_reactions = list(map(parse_reaction, non_empty_lines))
    results = [result for result, _, _ in parsed_reactions]
    if len(results) != len(set(results)):
        raise Exception("Got multiple reactions that produce the same result")
    reactions = {
        result: (quantity, ingredient)
        for result, quantity, ingredient
        in map(parse_reaction, non_empty_lines)
    }
    fuel_quantity = reactions['FUEL'][0]
    if fuel_quantity != 1:
        raise Exception(
            f"Expected a reaction that produces exactly 1 FUEL but got one "
            f"that produces {fuel_quantity}")

    return reactions


re_parse_participant = re.compile(r"^\s*(\d+)\s+(\w+)s*$")


def parse_reaction(reaction_text):
    """
    >>> parse_reaction("10 ORE => 10 A")
    ('A', 10, [('ORE', 10)])
    >>> parse_reaction("7 A, 1 B => 3 C")
    ('C', 3, [('A', 7), ('B', 1)])
    >>> parse_reaction("12 ABC, 34 DEF => 56 GHI")
    ('GHI', 56, [('ABC', 12), ('DEF', 34)])
    """
    ingredients_text, result_text = \
        map(str.strip, reaction_text.strip().split('=>'))
    ingredients = [
        (ingredient, int(quantity))
        for quantity, ingredient in (
            re_parse_participant.match(ingredient_text.strip()).groups()
            for ingredient_text in ingredients_text.split(',')
        )
    ]
    quantity, result = \
        re_parse_participant.match(result_text.strip()).groups()

    return result, int(quantity), ingredients


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
