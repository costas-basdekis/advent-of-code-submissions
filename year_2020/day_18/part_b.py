#!/usr/bin/env python3
from abc import ABC

import utils
from year_2020.day_18 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        283582817678281
        """
        return int(ExpressionSet2.from_expressions_text(_input))


class ExpressionSet2(part_a.ExpressionSet):
    pass


class Expression2(part_a.Expression, ABC):
    """
    >>> int(Expression2.from_expression_text("1 + 2 * 3 + 4 * 5 + 6"))
    231
    >>> int(Expression2.from_expression_text(
    ...     "1 + (2 * 3) + (4 * (5 + 6))"))
    51
    >>> int(Expression2.from_expression_text(
    ...     "2 * 3 + (4 * 5)"))
    46
    >>> int(Expression2.from_expression_text(
    ...     "5 + (8 * 3 + 9 + 3 * 4 * 3)"))
    1445
    >>> int(Expression2.from_expression_text(
    ...     "5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))"))
    669060
    >>> int(Expression2.from_expression_text(
    ...     "((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2"))
    23340
    """

    @classmethod
    def intercept_text(cls, expression_text):
        intercepted = cls.re_number.sub(cls.replace_number, expression_text)
        intercepted = intercepted.replace('+', '?')
        intercepted = intercepted.replace('*', '+')
        intercepted = intercepted.replace('?', '*')
        return intercepted

    def __add__(self, other):
        return self.mul_class((self, other))

    def __mul__(self, other):
        return self.add_class((self, other))


ExpressionSet2.expression_class = Expression2


class Number2(Expression2, part_a.Number):
    pass


Expression2.number_class = Number2


class Add2(Expression2, part_a.Add):
    pass


Expression2.add_class = Add2


class Mul2(Expression2, part_a.Mul):
    pass


Expression2.mul_class = Mul2


challenge = Challenge()
challenge.main()
