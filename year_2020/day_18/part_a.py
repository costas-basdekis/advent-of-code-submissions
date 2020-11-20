#!/usr/bin/env python3
import functools
import re
import string

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        4940631886147
        """
        expressions = ExpressionSet.from_expressions_text(_input).expressions
        return sum(map(int, expressions))


class ExpressionSet:
    @classmethod
    def from_expressions_text(cls, expressions_text):
        return cls(list(map(
            Expression.from_expression_text, expressions_text.splitlines())))

    def __init__(self, expressions):
        self.expressions = expressions


class Expression:
    re_expression = re.compile(r'^(\d+|\*|\+|\(|\)|\s+)+$')
    re_number = re.compile(r"\d+")

    @classmethod
    def from_expression_text(cls, expression_text):
        """
        >>> str(Expression.from_expression_text("1 + (2 * 3) + (4 * (5 + 6))"))
        '(1 + (2 * 3)) + (4 * (5 + 6))'
        >>> int(Expression.from_expression_text("1 + (2 * 3) + (4 * (5 + 6))"))
        51
        >>> int(Expression.from_expression_text("1 + 2 * 3 + 4 * 5 + 6"))
        71
        >>> int(Expression.from_expression_text("2 * 3 + (4 * 5)"))
        26
        >>> int(Expression.from_expression_text("5 + (8 * 3 + 9 + 3 * 4 * 3)"))
        437
        >>> int(Expression.from_expression_text(
        ...     "5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))"))
        12240
        >>> int(Expression.from_expression_text(
        ...     "((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2"))
        13632
        """
        if not cls.re_expression.match(expression_text):
            raise Exception(f"Invalid expression {expression_text}")
        intercepted = cls.re_number.sub(cls.replace_number, expression_text)
        intercepted = intercepted.replace("*", "+ '*' +")

        return eval(intercepted)

    @classmethod
    def replace_number(cls, match):
        return f"Number({match.group()})"

    def __add__(self, other):
        if other == '*':
            return ConvertToMul(self)
        return Add((self, other))

    def __mul__(self, other):
        return Mul((self, other))

    def __int__(self):
        raise NotImplementedError()


class ConvertToMul:
    def __init__(self, expression):
        self.expression = expression

    def __add__(self, other):
        if not isinstance(other, Expression):
            raise Exception("Expected expression")
        return self.expression * other


class Number(Expression, int):
    def __str__(self):
        return super().__str__()

    def __int__(self):
        return super(Expression, self).__int__()


class Add(Expression, tuple):
    def __str__(self):
        return " + ".join(
            str(item)
            if isinstance(item, Number) else
            f"({str(item)})"
            for item in self
        )

    def __int__(self):
        return sum(map(int, self))


class Mul(Expression, tuple):
    def __str__(self):
        return " * ".join(
            str(item)
            if isinstance(item, Number) else
            f"({str(item)})"
            for item in self
        )

    def __int__(self):
        return functools.reduce(int.__mul__, map(int, self))


class ExpressionEx:
    re_expression = re.compile(r'\d+|\*|\+|\(|\)')

    @classmethod
    def from_expression_text(cls, expression_text):
        """"""
        """
        >>> ExpressionEx.from_expression_text("2 * 3 + (4 * 5)")
        Add(Mul(2, 3), Mul(4, 5))
        """
        parts = ['0', '+'] + cls.re_expression.findall(expression_text)
        parts = [
            int(part)
            if set(part) == set(string.digits) else
            part
            for part in parts
        ]
        groups = cls.group_parts_by_operations(parts)
        return cls.expression_from_groups(groups)

    @classmethod
    def expression_from_groups(cls, groups):
        if not groups:
            raise Exception("No groups given")
        raise Exception("")

    @classmethod
    def group_parts_by_operations(cls, parts):
        """
        >>> ExpressionEx.group_parts_by_operations(['(', 2, '*', '(', 3, ')', ')'])
        [([(2, '*'), ([(3, None)], None)], None)]
        >>> ExpressionEx.group_parts_by_operations([2, '*', '(', 3, ')'])
        [(2, '*'), ([(3, None)], None)]
        >>> ExpressionEx.group_parts_by_operations([2, '*', 3, '+', 4, '*', 5])
        [(2, '*'), (3, '+'), (4, '*'), (5, None)]
        >>> ExpressionEx.group_parts_by_operations([2, '*', 3, '+', '(', 4, '*', 5, ')'])
        [(2, '*'), (3, '+'), ([(4, '*'), (5, None)], None)]
        """
        pairs = []
        remaining_parts = parts
        while remaining_parts:
            node, operation, rest = cls.get_node_and_operation(remaining_parts)
            if remaining_parts == rest:
                raise Exception(f"No progress: {pairs} and {rest}")
            if operation is None and rest:
                raise Exception(
                    f"Got no operation but with more items: "
                    f"{pairs}, {(node, operation)} and {rest}")
            if operation is not None and not rest:
                raise Exception(
                    f"Expected more items: "
                    f"{pairs}, {(node, operation)} and {rest}")
            pairs.append((node, operation))
            remaining_parts = rest

        return pairs

    @classmethod
    def get_node_and_operation(cls, parts):
        """
        >>> ExpressionEx.get_node_and_operation(['*', 3])
        Traceback (most recent call last):
        ...
        Exception: Expected number or node but found *
        >>> ExpressionEx.get_node_and_operation([2, '*', 3])
        (2, '*', [3])
        >>> ExpressionEx.get_node_and_operation(['(', 2, '*', 3, ')'])
        ([(2, '*'), (3, None)], None, [])
        >>> ExpressionEx.get_node_and_operation(['(', 2, '*', 3])
        Traceback (most recent call last):
        ...
        Exception: Unbalanced parenthesis...
        >>> ExpressionEx.get_node_and_operation(['(', 2, '*', '(', 3, ')', ')'])
        ([(2, '*'), ([(3, None)], None)], None, [])
        >>> ExpressionEx.get_node_and_operation(['(', 2, '*', '(', 3])
        Traceback (most recent call last):
        ...
        Exception: Unbalanced parenthesis...
        """
        if not parts:
            raise Exception("No parts left")
        if isinstance(parts[0], int):
            if len(parts) == 1:
                return parts[0], None, []
            if parts[1] not in ('+', '*'):
                raise Exception(
                    f"Expected an operation after {parts[0]} but found "
                    f"{parts[1]}")
            return parts[0], parts[1], parts[2:]
        if parts[0] in ('+', '*'):
            raise Exception(f"Expected number or node but found {parts[0]}")
        if parts[0] == ')':
            raise Exception(
                f"Expected number or node but found end of parenthesis")
        if parts[0] != '(':
            raise Exception(
                f"Expected start of parenthesis, but found {parts[0]}")
        parenthesis_count = 1
        remaining_parts = list(parts)
        contents = [remaining_parts.pop(0)]
        while parenthesis_count > 0:
            if not remaining_parts:
                raise Exception(
                    f"Unbalanced parenthesis: expected {parenthesis_count} "
                    f"more closing parentheses: {parts}")
            part = remaining_parts.pop(0)
            if part == '(':
                parenthesis_count += 1
            elif part == ')':
                parenthesis_count -= 1
            contents.append(part)

        contents_group = cls.group_parts_by_operations(contents[1:-1])

        if not remaining_parts:
            return contents_group, None, []

        if remaining_parts[0] not in ('+', '*'):
            raise Exception(
                f"Expected an operation after {contents} but found "
                f"{remaining_parts[0]}")

        return contents_group, remaining_parts[0], remaining_parts[1:]


challenge = Challenge()
challenge.main()
