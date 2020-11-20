#!/usr/bin/env python3
import doctest

from utils import get_current_directory
from year_2020.day_16 import part_a


def solve(_input=None):
    """
    >>> solve()
    1307550234719
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    return SolverExtended.from_text(_input).get_ticket_checksum()


class SolverExtended(part_a.Solver):
    def get_ticket_checksum(self):
        """
        >>> SolverExtended.from_text(
        ...     "class: 0-1 or 4-19\\n"
        ...     "row: 0-5 or 8-19\\n"
        ...     "seat: 0-13 or 16-19\\n"
        ...     "\\n"
        ...     "your ticket:\\n"
        ...     "11,12,13\\n"
        ...     "\\n"
        ...     "nearby tickets:\\n"
        ...     "3,9,18\\n"
        ...     "15,1,5\\n"
        ...     "5,14,9\\n"
        ... ).get_ticket_checksum()
        1
        """

        rule_field_mapping = self.solve_field_mapping()

        departure_product = 1
        for rule, field in rule_field_mapping.items():
            if rule.name.startswith('departure'):
                departure_product *= self.your_ticket.values[field]

        return departure_product

    def solve_field_mapping(self, allow_partial=False):
        """
        >>> [name for _, name in sorted((field, rule.name) for rule, field in SolverExtended.from_text(
        ...     "class: 0-1 or 4-19\\n"
        ...     "row: 0-5 or 8-19\\n"
        ...     "seat: 0-13 or 16-19\\n"
        ...     "\\n"
        ...     "your ticket:\\n"
        ...     "11,12,13\\n"
        ...     "\\n"
        ...     "nearby tickets:\\n"
        ...     "3,9,18\\n"
        ...     "15,1,5\\n"
        ...     "5,14,9\\n"
        ... ).solve_field_mapping().items())]
        ['row', 'class', 'seat']
        """
        return self.rule_set.solve_field_mapping(
            self.ticket_set.get_values_per_field(
                self.rule_set.valid_values), allow_partial)


class RuleSetExtended(part_a.RuleSet):
    def solve_field_mapping(self, values_per_field, allow_partial=False):
        fields_per_rule = {
            rule: rule.get_possible_fields(values_per_field)
            for rule in self.rules
        }
        return self.solve_fields_per_rule(fields_per_rule, allow_partial)

    def solve_fields_per_rule(self, fields_per_rule, allow_partial=False):
        remaining_fields_per_rule = dict(fields_per_rule)
        rule_field_mapping = {}
        while remaining_fields_per_rule:
            single_field_rules = [
                rule
                for rule, fields in remaining_fields_per_rule.items()
                if len(fields) == 1
            ]
            if not single_field_rules:
                break
            solved_rule = single_field_rules[0]
            solved_field, = remaining_fields_per_rule.pop(solved_rule)
            rule_field_mapping[solved_rule] = solved_field
            for fields in remaining_fields_per_rule.values():
                fields -= {solved_field}

        if remaining_fields_per_rule:
            if not allow_partial:
                raise Exception(
                    f"There are {len(remaining_fields_per_rule)} "
                    f"unresolved rules remaining, but none of them are "
                    f"about 1 field")

        return rule_field_mapping


SolverExtended.rule_set_class = RuleSetExtended


class RuleExtended(part_a.Rule):
    def __hash__(self):
        return id(self)

    def get_possible_fields(self, values_per_field):
        """
        >>> RuleExtended("row", {1, 2, 3}).get_possible_fields(
        ...     [{1, 2}, {2, 3}])
        {0, 1}
        >>> RuleExtended("row", {1, 2, 3}).get_possible_fields(
        ...     [{1, 2}, {2, 3}, {3, 4}])
        {0, 1}
        >>> RuleExtended("row", {1, 2, 3}).get_possible_fields(
        ...     [{1, 2}, {2, 3}, {3, 4}, set()])
        {0, 1, 3}
        """
        return {
            index
            for index, values in enumerate(values_per_field)
            if not values - self.values
        }


RuleSetExtended.rule_class = RuleExtended


class TicketSetExtended(part_a.TicketSet):
    def get_values_per_field(self, valid_values):
        """
        >>> TicketSetExtended([
        ...     part_a.Ticket((1, 2, 3))
        ... ]).get_values_per_field(set())
        (set(), set(), set())
        >>> TicketSetExtended([
        ...     part_a.Ticket((1, 2, 3))
        ... ]).get_values_per_field({1, 2})
        (set(), set(), set())
        >>> TicketSetExtended([
        ...     part_a.Ticket((1, 2, 3))
        ... ]).get_values_per_field(set(range(5)))
        ({1}, {2}, {3})
        >>> tuple(map(tuple, map(sorted, TicketSetExtended([
        ...     part_a.Ticket((1, 2, 3)),
        ...     part_a.Ticket((1, 3, 7)),
        ...     part_a.Ticket((5, 2, 8)),
        ... ]).get_values_per_field(set(range(5))))))
        ((1,), (2,), (3,))
        >>> tuple(map(tuple, map(sorted, TicketSetExtended([
        ...     part_a.Ticket((1, 2, 3)),
        ...     part_a.Ticket((1, 3, 7)),
        ...     part_a.Ticket((5, 2, 8)),
        ... ]).get_values_per_field(set(range(8))))))
        ((1,), (2, 3), (3, 7))
        >>> tuple(map(tuple, map(sorted, TicketSetExtended([
        ...     part_a.Ticket((1, 2, 3)),
        ...     part_a.Ticket((1, 3, 7)),
        ...     part_a.Ticket((5, 2, 8)),
        ... ]).get_values_per_field(set(range(10))))))
        ((1, 5), (2, 3), (3, 7, 8))
        """
        if not self.tickets:
            raise Exception("Empty ticket set")
        a_ticket = self.tickets[0]
        return tuple(
            {
                ticket.values[position]
                for ticket in self.tickets
                if not ticket.is_invalid_via_invalid_values_only(valid_values)
            }
            for position in range(len(a_ticket.values))
        )


SolverExtended.ticket_set_class = TicketSetExtended


if __name__ == '__main__':
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE
    if doctest.testmod(part_a, optionflags=optionflags).failed \
            | doctest.testmod(optionflags=optionflags).failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
