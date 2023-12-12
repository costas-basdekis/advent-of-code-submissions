#!/usr/bin/env python3
import operator
from dataclasses import dataclass
from itertools import product
from typing import Callable, ClassVar, List, Tuple, Union, Generic, TypeVar, Type

from aox.challenge import Debugger
from utils import BaseChallenge, Cls, get_type_argument_class, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3598800864292
        """
        return Calibration.from_text(_input).get_viable_calibration_result()


EquationT = TypeVar("EquationT", bound="Equation")


@dataclass
class Calibration(Generic[EquationT]):
    equations: List[EquationT]

    @classmethod
    def get_equation_class(cls) -> Type[EquationT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, EquationT)

    @classmethod
    def from_text(cls: Cls["Calibration"], text: str) -> Self["Calibration"]:
        """
        >>> len(Calibration.from_text('''
        ...     190: 10 19
        ...     3267: 81 40 27
        ...     83: 17 5
        ...     156: 15 6
        ...     7290: 6 8 6 15
        ...     161011: 16 10 13
        ...     192: 17 8 14
        ...     21037: 9 7 18 13
        ...     292: 11 6 16 20
        ... ''').equations)
        9
        """
        equation_class = cls.get_equation_class()
        return cls(equations=list(map(equation_class.from_text, text.strip().splitlines())))

    def get_viable_calibration_result(self, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> Calibration.from_text('''
        ...     190: 10 19
        ...     3267: 81 40 27
        ...     83: 17 5
        ...     156: 15 6
        ...     7290: 6 8 6 15
        ...     161011: 16 10 13
        ...     192: 17 8 14
        ...     21037: 9 7 18 13
        ...     292: 11 6 16 20
        ... ''').get_viable_calibration_result()
        3749
        """
        return self.viable_only(debugger=debugger).get_calibration_result()

    def viable_only(self: Self["Calibration"], debugger: Debugger = Debugger(enabled=False)) -> Self["Calibration"]:
        """
        >>> len(Calibration.from_text('''
        ...     190: 10 19
        ...     3267: 81 40 27
        ...     83: 17 5
        ...     156: 15 6
        ...     7290: 6 8 6 15
        ...     161011: 16 10 13
        ...     192: 17 8 14
        ...     21037: 9 7 18 13
        ...     292: 11 6 16 20
        ... ''').viable_only().equations)
        3
        """
        equations = []
        for index, equation in enumerate(debugger.stepping(self.equations)):
            if equation.is_viable():
                equations.append(equation)
            if debugger.should_report():
                debugger.default_report_if(f"Checked {index + 1}/{len(self.equations)}, found {len(equations)}")
        cls = type(self)
        return cls(equations = equations)

    def get_calibration_result(self) -> int:
        """
        >>> Calibration.from_text('''
        ...     190: 10 19
        ...     3267: 81 40 27
        ...     83: 17 5
        ...     156: 15 6
        ...     7290: 6 8 6 15
        ...     161011: 16 10 13
        ...     192: 17 8 14
        ...     21037: 9 7 18 13
        ...     292: 11 6 16 20
        ... ''').viable_only().get_calibration_result()
        3749
        """
        return sum(
            equation.result
            for equation in self.equations
        )


@dataclass
class Equation:
    result: int
    operands: List[int]

    @classmethod
    def from_text(cls, text: str) -> "Equation":
        """
        >>> Equation.from_text("190: 10 19")
        Equation(result=190, operands=[10, 19])
        """
        result_str, operands_str = text.strip().split(": ")
        return cls(result=int(result_str), operands=list(map(int, operands_str.split(" "))))

    operators: ClassVar[List[Callable[[int, int], int]]] = [operator.add, operator.mul]

    def is_viable(self) -> bool:
        """
        >>> Equation.from_text("190: 10 19").is_viable()
        True
        >>> Equation.from_text("292: 11 6 16 20").is_viable()
        True
        """
        return any(
            self.are_operators_viable(operators)
            for operators in product(self.operators, repeat=len(self.operands) - 1)
        )

    def are_operators_viable(self, operators: Tuple[Callable[[int, int], int], ...]) -> bool:
        """
        >>> Equation.from_text("190: 10 19").are_operators_viable((operator.mul,))
        True
        >>> Equation.from_text("190: 10 19").are_operators_viable((operator.add,))
        False
        >>> Equation.from_text("292: 11 6 16 20").are_operators_viable((operator.add, operator.mul, operator.add,))
        True
        """
        if len(operators) != len(self.operands) - 1:
            raise Exception(f"Expected {len(self.operands) - 1} operators, got {len(operators)}")
        total = self.operands[0]
        for _operator, operand in zip(operators, self.operands[1:]):
            total = _operator(total, operand)
            if total > self.result:
                return False
        return total == self.result


Challenge.main()
challenge = Challenge()
