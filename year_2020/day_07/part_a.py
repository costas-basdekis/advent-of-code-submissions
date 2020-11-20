#!/usr/bin/env python3
import doctest
import re
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    238
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return BagRuleSet.from_bag_rule_set_text(_input)\
        .get_colour_count_eventually_containing_colour("shiny gold")


class BagRuleSet:
    @classmethod
    def from_bag_rule_set_text(cls, bag_rule_set_text):
        """
        >>> BagRuleSet.from_bag_rule_set_text(
        ...     "light red bags contain 1 bright white bag, 2 muted yellow bags.\\n"
        ...     "dark orange bags contain 3 bright white bags, 4 muted yellow bags.\\n"
        ...     "bright white bags contain 1 shiny gold bag.\\n"
        ...     "muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.\\n"
        ...     "shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.\\n"
        ...     "dark olive bags contain 3 faded blue bags, 4 dotted black bags.\\n"
        ...     "vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.\\n"
        ...     "faded blue bags contain no other bags.\\n"
        ...     "dotted black bags contain no other bags.\\n"
        ... ).bag_rules
        [BagRule(colour='light red', contents=(BagQuantity(colour='bright white', count=1), BagQuantity(colour='muted yellow', count=2))), \
BagRule(colour='dark orange', contents=(BagQuantity(colour='bright white', count=3), BagQuantity(colour='muted yellow', count=4))), \
BagRule(colour='bright white', contents=(BagQuantity(colour='shiny gold', count=1),)), \
BagRule(colour='muted yellow', contents=(BagQuantity(colour='shiny gold', count=2), BagQuantity(colour='faded blue', count=9))), \
BagRule(colour='shiny gold', contents=(BagQuantity(colour='dark olive', count=1), BagQuantity(colour='vibrant plum', count=2))), \
BagRule(colour='dark olive', contents=(BagQuantity(colour='faded blue', count=3), BagQuantity(colour='dotted black', count=4))), \
BagRule(colour='vibrant plum', contents=(BagQuantity(colour='faded blue', count=5), BagQuantity(colour='dotted black', count=6))), \
BagRule(colour='faded blue', contents=()), \
BagRule(colour='dotted black', contents=())]
        """
        non_empty_lines = filter(None, bag_rule_set_text.splitlines())
        return cls(list(map(BagRule.from_bag_rule_text, non_empty_lines)))

    def __init__(self, bag_rules):
        self.bag_rules = bag_rules

    def get_colour_count_eventually_containing_colour(self, target):
        """
        >>> BagRuleSet.from_bag_rule_set_text(
        ...     "light red bags contain 1 bright white bag, 2 muted yellow bags.\\n"
        ...     "dark orange bags contain 3 bright white bags, 4 muted yellow bags.\\n"
        ...     "bright white bags contain 1 shiny gold bag.\\n"
        ...     "muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.\\n"
        ...     "shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.\\n"
        ...     "dark olive bags contain 3 faded blue bags, 4 dotted black bags.\\n"
        ...     "vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.\\n"
        ...     "faded blue bags contain no other bags.\\n"
        ...     "dotted black bags contain no other bags.\\n"
        ... ).get_colour_count_eventually_containing_colour("shiny gold")
        4
        """
        return len(self.get_colours_eventually_containing_colour(target))

    def get_colours_eventually_containing_colour(self, target):
        """
        >>> BagRuleSet.from_bag_rule_set_text(
        ...     "light red bags contain 1 bright white bag, 2 muted yellow bags.\\n"
        ...     "dark orange bags contain 3 bright white bags, 4 muted yellow bags.\\n"
        ...     "bright white bags contain 1 shiny gold bag.\\n"
        ...     "muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.\\n"
        ...     "shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.\\n"
        ...     "dark olive bags contain 3 faded blue bags, 4 dotted black bags.\\n"
        ...     "vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.\\n"
        ...     "faded blue bags contain no other bags.\\n"
        ...     "dotted black bags contain no other bags.\\n"
        ... ).get_colours_eventually_containing_colour("shiny gold")
        ['bright white', 'dark orange', 'light red', 'muted yellow']
        """
        eventual_contents = self.get_eventual_contents()
        return sorted(
            colour
            for colour, contents in eventual_contents.items()
            if target in contents
        )

    def get_eventual_contents(self):
        """
        >>> sorted(tuple((colour, tuple(sorted(contents))) for colour, contents in BagRuleSet.from_bag_rule_set_text(
        ...     "light red bags contain 1 bright white bag, 2 muted yellow bags.\\n"
        ...     "dark orange bags contain 3 bright white bags, 4 muted yellow bags.\\n"
        ...     "bright white bags contain 1 shiny gold bag.\\n"
        ...     "muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.\\n"
        ...     "shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.\\n"
        ...     "dark olive bags contain 3 faded blue bags, 4 dotted black bags.\\n"
        ...     "vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.\\n"
        ...     "faded blue bags contain no other bags.\\n"
        ...     "dotted black bags contain no other bags.\\n"
        ... ).get_eventual_contents().items()))
        [('bright white', ('dark olive', 'dotted black', 'faded blue', \
'shiny gold', 'vibrant plum')), ('dark olive', ('dotted black', 'faded blue'\
)), ('dark orange', ('bright white', 'dark olive', 'dotted black', \
'faded blue', 'muted yellow', 'shiny gold', 'vibrant plum')), \
('dotted black', ()), ('faded blue', ()), ('light red', ('bright white', \
'dark olive', 'dotted black', 'faded blue', 'muted yellow', 'shiny gold', \
'vibrant plum')), ('muted yellow', ('dark olive', 'dotted black', \
'faded blue', 'shiny gold', 'vibrant plum')), ('shiny gold', ('dark olive', \
'dotted black', 'faded blue', 'vibrant plum')), ('vibrant plum', \
('dotted black', 'faded blue'))]
        """
        eventual_contents = {
            rule.colour: {quantity.colour for quantity in rule.contents}
            for rule in self.bag_rules
        }
        terminated_colours = set()
        recently_terminated_colours = {
            rule.colour
            for rule in self.bag_rules
            if not rule.contents
        }
        # print("RTC", recently_terminated_colours)

        while recently_terminated_colours:
            for terminated_colour in recently_terminated_colours:
                terminated_contents = eventual_contents[terminated_colour]
                for colour, contents in eventual_contents.items():
                    if terminated_colour in contents:
                        # print("Add", terminated_contents, "to", colour)
                        contents.update(terminated_contents)
            terminated_colours |= recently_terminated_colours
            # print("T", terminated_colours)
            recently_terminated_colours = {
                colour
                for colour, contents in eventual_contents.items()
                if not contents - terminated_colours
            } - terminated_colours
            # print("ECR", {
            #     colour: contents - terminated_colours
            #     for colour, contents in eventual_contents.items()
            #     if colour not in terminated_colours
            # })
            # print("RTC", recently_terminated_colours)

        not_terminated_colours = set(eventual_contents) - terminated_colours
        if not_terminated_colours:
            raise Exception(
                "There are not-terminated colours, but not any recently "
                "terminated ones")

        return eventual_contents


class BagRule(namedtuple("BagRule", ("colour", "contents"))):
    re_bag_rule = re.compile(r"^(.*) bags contain ([^.]*).$")
    content_split = ", "
    no_other_bags = "no other bags"

    @classmethod
    def from_bag_rule_text(cls, bag_rule_text):
        """
        >>> BagRule.from_bag_rule_text(
        ...     "dark orange bags contain 3 bright white bags, 4 muted yellow "
        ...     "bags.")
        BagRule(colour='dark orange', contents=(BagQuantity(colour='bright white', count=3), BagQuantity(colour='muted yellow', count=4)))
        >>> BagRule.from_bag_rule_text(
        ...     "bright white bags contain 1 shiny gold bag.")
        BagRule(colour='bright white', contents=(BagQuantity(colour='shiny gold', count=1),))
        >>> BagRule.from_bag_rule_text(
        ...     "posh brown bags contain 5 dim coral bags, 1 plaid blue bag, "
        ...     "2 faded bronze bags, 2 light black bags.")
        BagRule(colour='posh brown', contents=(BagQuantity(colour='dim coral', count=5), BagQuantity(colour='plaid blue', count=1), BagQuantity(colour='faded bronze', count=2), BagQuantity(colour='light black', count=2)))
        >>> BagRule.from_bag_rule_text(
        ...     "faded blue bags contain no other bags.")
        BagRule(colour='faded blue', contents=())
        """
        match = cls.re_bag_rule.match(bag_rule_text)
        if not match:
            raise Exception(f"Could not parse '{bag_rule_text}'")
        colour, quantities_str = match.groups()
        quantity_strs = quantities_str.split(", ")
        quantity_strs = list(filter(None, quantity_strs))
        if quantity_strs == [cls.no_other_bags]:
            quantity_strs = []
        return cls(colour, tuple(map(
            BagQuantity.from_quantity_text, quantity_strs)))


class BagQuantity(namedtuple("BagQuantity", ("colour", "count"))):
    re_quantity = re.compile(r"^(\d+) (.+) bags?$")

    @classmethod
    def from_quantity_text(cls, quantity_text):
        """
        >>> BagQuantity.from_quantity_text("1 bright white bag")
        BagQuantity(colour='bright white', count=1)
        >>> BagQuantity.from_quantity_text("3 bright white bags")
        BagQuantity(colour='bright white', count=3)
        """
        match = cls.re_quantity.match(quantity_text)
        if not match:
            raise Exception(f"Could not parse quantity '{quantity_text}'")
        count_str, colour = match.groups()

        return cls(colour, int(count_str))


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
