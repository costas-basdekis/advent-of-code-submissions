#!/usr/bin/env python3
import functools
import re
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        29759
        """

        return Solver.from_text(_input).get_ticket_error_scanning_rate()


class Solver:
    rule_set_class = NotImplemented
    ticket_class = NotImplemented
    ticket_set_class = NotImplemented

    @classmethod
    def from_text(cls, text):
        """
        >>> Solver.from_text(
        ...     "class: 1-3 or 5-7\\n"
        ...     "row: 6-11 or 33-44\\n"
        ...     "seat: 13-40 or 45-50\\n"
        ...     "\\n"
        ...     "your ticket:\\n"
        ...     "7,1,14\\n"
        ...     "\\n"
        ...     "nearby tickets:\\n"
        ...     "7,3,47\\n"
        ...     "40,4,50\\n"
        ...     "55,2,20\\n"
        ...     "38,6,12\\n"
        ... )
        Solver(RuleSet([Rule(name='class', values={1, ..., 7}),
            Rule(name='row', values={6, ..., 44}),
            Rule(name='seat', values={13, ..., 50})]),
            Ticket((7, 1, 14)),
            TicketSet([Ticket((7, 3, 47)), ..., Ticket((38, 6, 12))]))
        """
        rules_text, your_ticket_section, nearby_tickets_section = \
            text.strip().split("\n\n")
        rule_set = cls.rule_set_class.from_rules_text(rules_text)

        your_ticket, your_ticket_text = your_ticket_section.splitlines()
        if your_ticket != "your ticket:":
            raise Exception(f"Expected 'your ticket:' but got {your_ticket}")
        your_ticket = cls.ticket_class.from_ticket_text(your_ticket_text)

        nearby_tickets, nearby_tickets_text = \
            nearby_tickets_section.split("\n", 1)
        if nearby_tickets != "nearby tickets:":
            raise Exception(
                f"Expected 'nearby tickets:' but got {nearby_tickets}")
        ticket_set = cls.ticket_set_class\
            .from_tickets_text(nearby_tickets_text)

        return cls(rule_set, your_ticket, ticket_set)

    def __init__(self, rule_set, your_ticket, ticket_set):
        self.rule_set = rule_set
        self.your_ticket = your_ticket
        self.ticket_set = ticket_set

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"{self.rule_set}, {self.your_ticket}, {self.ticket_set})"
        )

    def get_ticket_error_scanning_rate(self):
        """
        >>> Solver.from_text(
        ...     "class: 1-3 or 5-7\\n"
        ...     "row: 6-11 or 33-44\\n"
        ...     "seat: 13-40 or 45-50\\n"
        ...     "\\n"
        ...     "your ticket:\\n"
        ...     "7,1,14\\n"
        ...     "\\n"
        ...     "nearby tickets:\\n"
        ...     "7,3,47\\n"
        ...     "40,4,50\\n"
        ...     "55,2,20\\n"
        ...     "38,6,12\\n"
        ... ).get_ticket_error_scanning_rate()
        71
        """
        invalid_values = self.ticket_set.get_invalid_ticket_values(
            self.rule_set.valid_values)
        return sum(invalid_values)

    def get_invalid_tickets_via_invalid_values_only(self):
        """
        >>> Solver.from_text(
        ...     "class: 1-3 or 5-7\\n"
        ...     "row: 6-11 or 33-44\\n"
        ...     "seat: 13-40 or 45-50\\n"
        ...     "\\n"
        ...     "your ticket:\\n"
        ...     "7,1,14\\n"
        ...     "\\n"
        ...     "nearby tickets:\\n"
        ...     "7,3,47\\n"
        ...     "40,4,50\\n"
        ...     "55,2,20\\n"
        ...     "38,6,12\\n"
        ... ).get_invalid_tickets_via_invalid_values_only()
        [Ticket((40, 4, 50)), Ticket((55, 2, 20)), Ticket((38, 6, 12))]
        """
        return self.ticket_set.get_invalid_tickets_via_invalid_values_only(
            self.rule_set.valid_values)


class RuleSet:
    rule_class = NotImplemented

    @classmethod
    def from_rules_text(cls, rules_text):
        """
        >>> RuleSet.from_rules_text(
        ...     "departure location: 31-538 or 546-960\\n"
        ...     "departure station: 39-660 or 673-960\\n"
        ... )
        RuleSet([Rule(name='departure location', values={31, ..., 960}),
        Rule(name='departure station', values={39, ..., 960})])
        """
        non_empty_lines = filter(None, rules_text.splitlines())
        return cls(list(map(cls.rule_class.from_rule_text, non_empty_lines)))

    def __init__(self, rules):
        self.rules = rules
        self.valid_values = self.get_valid_values(self.rules)

    def __repr__(self):
        return f"{type(self).__name__}({self.rules})"

    def get_valid_values(self, rules):
        """
        >>> RuleSet([]).get_valid_values([])
        set()
        >>> RuleSet([]).get_valid_values([
        ...     Rule(name="a", values={1, 2, 3}),
        ... ])
        {1, 2, 3}
        >>> RuleSet([]).get_valid_values([
        ...     Rule(name="a", values={1, 2, 3}),
        ...     Rule(name="b", values={7, 8, 9}),
        ... ])
        {1, 2, 3, 7, 8, 9}
        >>> RuleSet([]).get_valid_values([
        ...     Rule(name="a", values={1, 2, 3}),
        ...     Rule(name="b", values={7, 8, 9}),
        ...     Rule(name="c", values={2, 7, 10}),
        ... ])
        {1, 2, 3, 7, 8, 9, 10}
        """
        return functools.reduce(set.__or__, (
            rule.values
            for rule in rules
        ), set())


Solver.rule_set_class = RuleSet


class Rule(namedtuple("Rule", ("name", "values"))):
    re_rule = re.compile(r"^([^:]+): (\d+)-(\d+) or (\d+)-(\d+)$")

    @classmethod
    def from_rule_text(cls, rule_text):
        """
        >>> Rule.from_rule_text(
        ...     "departure location: 31-538 or 546-960") # doctest: +NORMALIZE_WHITESPACE
        Rule(name='departure location', values={31, ..., 960})
        """
        name, min_a_str, max_a_str, min_b_str, max_b_str = \
            cls.re_rule.match(rule_text).groups()
        min_a, max_a = int(min_a_str), int(max_a_str)
        min_b, max_b = int(min_b_str), int(max_b_str)

        return cls(name, (
            set(range(min_a, max_a + 1))
            | set(range(min_b, max_b + 1))
        ))


RuleSet.rule_class = Rule


class TicketSet:
    ticket_class = NotImplemented

    @classmethod
    def from_tickets_text(cls, tickets_text):
        """
        >>> TicketSet.from_tickets_text(
        ...     "390,125,294,296,621,356,716,135,845,790,433,348,710,927,863,"
        ...     "136,834,139,115,323\\n"
        ...     "819,227,432,784,840,691,760,608,352,759,85,712,578,575,901,"
        ...     "151,440,494,283,274\\n"
        ... )
        TicketSet([Ticket((390, 125, 294, 296, 621, 356, 716, 135, 845, 790,
        433, 348, 710, 927, 863, 136, 834, 139, 115, 323)),
        Ticket((819, 227, 432, 784, 840, 691, 760, 608, 352, 759, 85, 712,
        578, 575, 901, 151, 440, 494, 283, 274))])
        """
        non_empty_lines = filter(None, tickets_text.splitlines())
        return cls(list(map(
            cls.ticket_class.from_ticket_text, non_empty_lines)))

    def __init__(self, tickets):
        self.tickets = tickets

    def __repr__(self):
        return f"{type(self).__name__}({self.tickets})"

    def get_invalid_ticket_values(self, valid_values):
        """
        >>> TicketSet([]).get_invalid_ticket_values(set())
        ()
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ... ]).get_invalid_ticket_values(set())
        (3, 7, 10)
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ... ]).get_invalid_ticket_values({1, 3, 7})
        (10,)
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ... ]).get_invalid_ticket_values({1, 3, 7, 10})
        ()
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ...     Ticket((3, 7, 25)),
        ... ]).get_invalid_ticket_values({1, 3, 7, 10})
        (25,)
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ...     Ticket((3, 7, 25)),
        ... ]).get_invalid_ticket_values({1, 7, 10})
        (3, 3, 25)
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ...     Ticket((3, 7, 25)),
        ... ]).get_invalid_ticket_values({1, 3, 7, 10, 25})
        ()
        """
        return tuple(
            value
            for ticket in self.tickets
            for value in ticket.get_invalid_values(valid_values)
        )

    def get_invalid_tickets_via_invalid_values_only(self, valid_values):
        """
        >>> TicketSet([]).get_invalid_tickets_via_invalid_values_only(set())
        []
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ... ]).get_invalid_tickets_via_invalid_values_only(set())
        [Ticket((3, 7, 10))]
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ... ]).get_invalid_tickets_via_invalid_values_only({1, 3, 7})
        [Ticket((3, 7, 10))]
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ... ]).get_invalid_tickets_via_invalid_values_only({1, 3, 7, 10})
        []
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ...     Ticket((3, 7, 25)),
        ... ]).get_invalid_tickets_via_invalid_values_only({1, 3, 7, 10})
        [Ticket((3, 7, 25))]
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ...     Ticket((3, 7, 25)),
        ... ]).get_invalid_tickets_via_invalid_values_only({1, 7, 10})
        [Ticket((3, 7, 10)), Ticket((3, 7, 25))]
        >>> TicketSet([
        ...     Ticket((3, 7, 10)),
        ...     Ticket((3, 7, 25)),
        ... ]).get_invalid_tickets_via_invalid_values_only({1, 3, 7, 10, 25})
        []
        """
        return [
            ticket
            for ticket in self.tickets
            if ticket.is_invalid_via_invalid_values_only(valid_values)
        ]


Solver.ticket_set_class = TicketSet


class Ticket:
    @classmethod
    def from_ticket_text(cls, ticket_text):
        """
        >>> Ticket.from_ticket_text(
        ...     "390,125,294,296,621,356,716,135,845,790,433,348,710,927,863,"
        ...     "136,834,139,115,323") # doctest: +NORMALIZE_WHITESPACE
        Ticket((390, 125, 294, 296, 621, 356, 716, 135, 845, 790, 433, 348,
        710, 927, 863, 136, 834, 139, 115, 323))
        """
        return cls(tuple(map(int, ticket_text.strip().split(","))))

    def __init__(self, values):
        self.values = values

    def __repr__(self):
        return f"{type(self).__name__}({self.values})"

    def get_invalid_values(self, valid_values):
        """
        >>> Ticket((1, 6, 10)).get_invalid_values(set())
        (1, 6, 10)
        >>> Ticket((1, 6, 10)).get_invalid_values(set(range(20)))
        ()
        >>> Ticket((1, 6, 10, 21)).get_invalid_values(set(range(20)))
        (21,)
        """
        return tuple(sorted(set(self.values) - valid_values))

    def is_invalid_via_invalid_values_only(self, valid_values):
        """
        >>> Ticket((1, 6, 10)).is_invalid_via_invalid_values_only(set())
        True
        >>> Ticket((1, 6, 10)).is_invalid_via_invalid_values_only(
        ...     set(range(20)))
        False
        >>> Ticket((1, 6, 10, 21)).is_invalid_via_invalid_values_only(
        ...     set(range(20)))
        True
        """
        return bool(self.get_invalid_values(valid_values))


Solver.ticket_class = Ticket
TicketSet.ticket_class = Ticket


challenge = Challenge()
challenge.main()
