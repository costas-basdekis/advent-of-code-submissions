#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
from typing import cast, ClassVar, Dict, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_21 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3769668716709
        """
        original_root = ExtendedMonkey.from_monkeys_text(_input)
        if debugger:
            root = ExtendedMonkey.from_monkeys_text(part_a.LONG_INPUT)
            debugger.report(root.represent())
            root = root.simplify()
            debugger.report(root.represent())
            root = root.reverse_step()
            debugger.report(root.represent())
            root = root.reverse_step()
            debugger.report(root.represent())
            root = root.reverse_step()
            debugger.report(root.represent())
            root = root.reverse_step()
            debugger.report(root.represent())
            solution = root.get_solution()
            debugger.report(solution)
            debugger.report(original_root.replace(solution).represent())
            debugger.report(
                original_root.replace(solution).simplify().represent())
            debugger.report(original_root.check_solution(solution))
        return original_root.solve()


class ExtendedMonkey(ABC):
    @classmethod
    def from_monkeys_text(cls, monkeys_text: str) -> "EqualityExtendedMonkey":
        return cls.from_monkeys(
            part_a.MonkeySet.from_monkeys_text(monkeys_text),
        )

    @classmethod
    def from_monkeys(
        cls, monkeys: part_a.MonkeySet,
    ) -> "EqualityExtendedMonkey":
        root = monkeys.monkeys_by_id["root"]
        monkey = cls.build(root, monkeys)
        if not isinstance(monkey, EqualityExtendedMonkey):
            raise Exception(
                f"Expected an equality monkey, but got: {monkey.represent()}"
            )
        return monkey

    @classmethod
    def build(
        cls, monkey: part_a.Monkey, monkeys: part_a.MonkeySet,
    ) -> "ExtendedMonkey":
        if isinstance(monkey, part_a.ConstantMonkey):
            if monkey.id == "humn":
                return UnknownExtendedMonkey()
            else:
                return ConstantExtendedMonkey(
                    value=cast(part_a.ConstantMonkey, monkey).value,
                )
        else:
            root_monkey = cast(part_a.OperationMonkey, monkey)
            left = cls.build(
                monkeys.monkeys_by_id[root_monkey.left_reference],
                monkeys,
            )
            right = cls.build(
                monkeys.monkeys_by_id[root_monkey.right_reference],
                monkeys,
            )
            if monkey.id == "root":
                return EqualityExtendedMonkey(
                    left=left,
                    right=right,
                )
            else:
                return OperationExtendedMonkey(
                    left=left,
                    right=right,
                    operator=root_monkey.operator,
                )

    def simplify(self) -> "ExtendedMonkey":
        raise NotImplementedError()

    def represent(self) -> str:
        raise NotImplementedError()

    def replace(self, solution: int) -> "ExtendedMonkey":
        raise NotImplementedError()


@dataclass
class ConstantExtendedMonkey(ExtendedMonkey):
    value: int

    def simplify(self) -> "ExtendedMonkey":
        return self

    def represent(self) -> str:
        return str(self.value)

    def replace(self, solution: int) -> "ExtendedMonkey":
        return self


class UnknownExtendedMonkey(ExtendedMonkey):
    def simplify(self) -> "ExtendedMonkey":
        return self

    def represent(self) -> str:
        return "?"

    def replace(self, solution: int) -> "ExtendedMonkey":
        return ConstantExtendedMonkey(
            value=solution,
        )


@dataclass
class OperationExtendedMonkey(ExtendedMonkey):
    left: ExtendedMonkey
    right: ExtendedMonkey
    operator: part_a.Operator

    operator_by_name: ClassVar[Dict[str, part_a.Operator]] = \
        part_a.OperationMonkey.operator_by_name
    name_by_operand: ClassVar[Dict[part_a.Operator, str]] = {
        operator: name
        for name, operator in operator_by_name.items()
    }

    def simplify(self) -> "ExtendedMonkey":
        left = self.left.simplify()
        right = self.right.simplify()
        if isinstance(left, ConstantExtendedMonkey) \
                and isinstance(right, ConstantExtendedMonkey):
            return ConstantExtendedMonkey(
                value=self.operator(left.value, right.value),
            )
        return OperationExtendedMonkey(
            left=left,
            right=right,
            operator=self.operator,
        )

    def represent(self) -> str:
        return (
            f"({self.left.represent()} "
            f"{self.name_by_operand[self.operator]} "
            f"{self.right.represent()})"
        )

    def replace(self, solution: int) -> "ExtendedMonkey":
        return OperationExtendedMonkey(
            left=self.left.replace(solution),
            right=self.right.replace(solution),
            operator=self.operator,
        )


@dataclass
class EqualityExtendedMonkey(ExtendedMonkey):
    left: ExtendedMonkey
    right: ExtendedMonkey

    def simplify(self) -> "EqualityExtendedMonkey":
        return EqualityExtendedMonkey(
            left=self.left.simplify(),
            right=self.right.simplify(),
        )

    def represent(self) -> str:
        return (
            f"{self.left.represent()} "
            f"?= "
            f"{self.right.represent()}"
        )

    def replace(self, solution: int) -> "EqualityExtendedMonkey":
        return EqualityExtendedMonkey(
            left=self.left.replace(solution),
            right=self.right.replace(solution),
        )

    def check_solution(self, solution: int) -> bool:
        left = self.left.replace(solution).simplify()
        right = self.right.replace(solution).simplify()
        if not isinstance(left, ConstantExtendedMonkey):
            return False
        if not isinstance(right, ConstantExtendedMonkey):
            return False
        return left.value == right.value

    def solve(self) -> int:
        """
        >>> ExtendedMonkey.from_monkeys_text(part_a.LONG_INPUT).solve()
        301
        """
        solution = self.reverse().get_solution()
        if not self.check_solution(solution):
            raise Exception(f"Could not verify solution {solution}")
        return solution

    def get_solution(self) -> int:
        if isinstance(self.left, ConstantExtendedMonkey):
            if not isinstance(self.right, UnknownExtendedMonkey):
                raise Exception(
                    f"Monkey is not fully reversed: {self.represent()}"
                )
            return cast(ConstantExtendedMonkey, self.left).value
        elif isinstance(self.right, ConstantExtendedMonkey):
            if not isinstance(self.left, UnknownExtendedMonkey):
                raise Exception(
                    f"Monkey is not fully reversed: {self.represent()}"
                )
            return cast(ConstantExtendedMonkey, self.right).value
        else:
            raise Exception(
                f"Monkey is not fully reversed: {self.represent()}"
            )

    def reverse(self) -> "EqualityExtendedMonkey":
        monkey = self.simplify()
        while True:
            try:
                next_monkey = monkey.reverse_step()
            except Exception as e:
                raise Exception(
                    f"Could not reverse step of {monkey.represent()}"
                ) from e
            if next_monkey == monkey:
                break
            monkey = next_monkey
        return monkey

    def reverse_step(self) -> "EqualityExtendedMonkey":
        if isinstance(self.left, UnknownExtendedMonkey) \
                or isinstance(self.right, UnknownExtendedMonkey):
            return self
        if isinstance(self.left, ConstantExtendedMonkey):
            left_constant = cast(ConstantExtendedMonkey, self.left)
            if not isinstance(self.right, OperationExtendedMonkey):
                raise Exception(
                    f"Unsupported operands: "
                    f"{type(self.left)} and {type(self.right)}"
                )
            right_operation = cast(OperationExtendedMonkey, self.right)
            reverse = False
        elif isinstance(self.right, ConstantExtendedMonkey):
            left_constant = cast(ConstantExtendedMonkey, self.right)
            if not isinstance(self.left, OperationExtendedMonkey):
                raise Exception(
                    f"Unsupported operands: "
                    f"{type(self.left)} and {type(self.right)}"
                )
            right_operation = cast(OperationExtendedMonkey, self.left)
            reverse = True
        else:
            raise Exception(
                f"Unsupported operands: "
                f"{type(self.left)} and {type(self.right)}"
            )
        _reversed = self.reverse_operands(left_constant, right_operation)
        if reverse:
            _reversed = EqualityExtendedMonkey(
                left=_reversed.right,
                right=_reversed.left,
            )
        return _reversed

    def reverse_operands(
        self, left_constant: ConstantExtendedMonkey,
        right_operation: OperationExtendedMonkey,
    ) -> "EqualityExtendedMonkey":
        if right_operation.operator \
                == OperationExtendedMonkey.operator_by_name["+"]:
            return self.reverse_addition(left_constant, right_operation)
        elif right_operation.operator \
                == OperationExtendedMonkey.operator_by_name["-"]:
            return self.reverse_subtraction(left_constant, right_operation)
        elif right_operation.operator \
                == OperationExtendedMonkey.operator_by_name["*"]:
            return self.reverse_multiplication(left_constant, right_operation)
        elif right_operation.operator \
                == OperationExtendedMonkey.operator_by_name["/"]:
            return self.reverse_division(left_constant, right_operation)
        else:
            raise Exception(f"Unknown operator: {right_operation.operator}")

    def reverse_addition(
        self, left_constant: ConstantExtendedMonkey,
        right_operation: OperationExtendedMonkey,
    ) -> "EqualityExtendedMonkey":
        if isinstance(right_operation.left, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.left)
            if not isinstance(
                    right_operation.right,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.right
        elif isinstance(right_operation.right, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.right)
            if not isinstance(
                    right_operation.left,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.left
        else:
            raise Exception(
                f"Unsupported nested operands: "
                f"{type(right_operation.left)} "
                f"and {type(right_operation.right)}"
            )
        return EqualityExtendedMonkey(
            left=ConstantExtendedMonkey(
                value=(
                    left_constant.value - nested_constant.value
                ),
            ),
            right=nested_other,
        )

    def reverse_subtraction(
        self, left_constant: ConstantExtendedMonkey,
        right_operation: OperationExtendedMonkey,
    ) -> "EqualityExtendedMonkey":
        if isinstance(right_operation.left, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.left)
            if not isinstance(
                    right_operation.right,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.right
            return EqualityExtendedMonkey(
                left=nested_other,
                right=ConstantExtendedMonkey(
                    value=(
                        nested_constant.value - left_constant.value
                    ),
                ),
            )
        elif isinstance(right_operation.right, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.right)
            if not isinstance(
                    right_operation.left,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.left
            return EqualityExtendedMonkey(
                left=ConstantExtendedMonkey(
                    value=(
                        left_constant.value + nested_constant.value
                    ),
                ),
                right=nested_other,
            )
        else:
            raise Exception(
                f"Unsupported nested operands: "
                f"{type(right_operation.left)} "
                f"and {type(right_operation.right)}"
            )

    def reverse_multiplication(
        self, left_constant: ConstantExtendedMonkey,
        right_operation: OperationExtendedMonkey,
    ) -> "EqualityExtendedMonkey":
        if isinstance(right_operation.left, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.left)
            if not isinstance(
                    right_operation.right,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.right
        elif isinstance(right_operation.right, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.right)
            if not isinstance(
                    right_operation.left,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.left
        else:
            raise Exception(
                f"Unsupported nested operands: "
                f"{type(right_operation.left)} "
                f"and {type(right_operation.right)}"
            )
        return EqualityExtendedMonkey(
            left=ConstantExtendedMonkey(
                value=(
                    left_constant.value // nested_constant.value
                ),
            ),
            right=nested_other,
        )

    def reverse_division(
        self, left_constant: ConstantExtendedMonkey,
        right_operation: OperationExtendedMonkey,
    ) -> "EqualityExtendedMonkey":
        if isinstance(right_operation.left, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.left)
            if not isinstance(
                    right_operation.right,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.right
            return EqualityExtendedMonkey(
                left=nested_other,
                right=ConstantExtendedMonkey(
                    value=(
                        left_constant.value // nested_constant.value
                    ),
                ),
            )
        elif isinstance(right_operation.right, ConstantExtendedMonkey):
            nested_constant = \
                cast(ConstantExtendedMonkey, right_operation.right)
            if not isinstance(
                    right_operation.left,
                    (OperationExtendedMonkey, UnknownExtendedMonkey)):
                raise Exception(
                    f"Unsupported nested operands: "
                    f"{type(right_operation.left)} "
                    f"and {type(right_operation.right)}"
                )
            nested_other = right_operation.left
            return EqualityExtendedMonkey(
                left=ConstantExtendedMonkey(
                    value=(
                        nested_constant.value * left_constant.value
                    ),
                ),
                right=nested_other,
            )
        else:
            raise Exception(
                f"Unsupported nested operands: "
                f"{type(right_operation.left)} "
                f"and {type(right_operation.right)}"
            )


Challenge.main()
challenge = Challenge()
