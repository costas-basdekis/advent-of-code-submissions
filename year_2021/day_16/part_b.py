#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
from functools import reduce
from typing import cast, ClassVar, Dict, List, Optional, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2021.day_16.part_a import Operator, Literal, Packet, BitStream


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1495959086337
        """
        return BitStreamExtended.get_value_from_hex_stream(_input)


class BitStreamExtended(BitStream["PacketExtended"]):
    @classmethod
    def get_value_from_hex_stream(cls, hex_stream: str) -> int:
        """
        >>> BitStreamExtended.get_value_from_hex_stream("C200B40A82")
        3
        >>> BitStreamExtended.get_value_from_hex_stream("04005AC33890")
        54
        >>> BitStreamExtended.get_value_from_hex_stream("880086C3E88112")
        7
        >>> BitStreamExtended.get_value_from_hex_stream("CE00C43D881120")
        9
        >>> BitStreamExtended.get_value_from_hex_stream("D8005AC2A8F0")
        1
        >>> BitStreamExtended.get_value_from_hex_stream("F600BC2D8F")
        0
        >>> BitStreamExtended.get_value_from_hex_stream("9C005AC2F8F0")
        0
        >>> BitStreamExtended\\
        ...     .get_value_from_hex_stream("9C0141080250320F1802104A08")
        1
        """
        return cls.parse_hex_stream(hex_stream).get_value()


class PacketExtended(Packet["LiteralExtended", "OperatorExtended"], ABC):
    def get_value(self) -> int:
        raise NotImplementedError()


class LiteralExtended(PacketExtended, Literal):
    def get_value(self) -> int:
        return self.value


@dataclass
class OperatorExtended(PacketExtended, Operator):
    def __post_init__(self):
        OperatorType.check_arity_for_operator(self)

    def get_value(self) -> int:
        return OperatorType.apply_for_operator(self)


@dataclass
class OperatorType:
    min_operand_count: Optional[int]
    max_operand_count: Optional[int]

    type_id: ClassVar[int]

    operator_types_by_type_id: ClassVar[Dict[int, "OperatorType"]] = {}

    @classmethod
    def register(cls, type_class: Type["OperatorType"]) -> Type["OperatorType"]:
        cls.operator_types_by_type_id[type_class.type_id] = type_class.make()
        return type_class

    @classmethod
    def make(cls) -> "OperatorType":
        raise NotImplementedError()

    @classmethod
    def check_arity_for_operator(cls, operator: OperatorExtended) -> None:
        return cls.get_for_operator(operator).check_arity(operator)

    @classmethod
    def apply_for_operator(cls, operator: OperatorExtended) -> int:
        return cls.get_for_operator(operator).apply(operator)

    @classmethod
    def get_for_operator(cls, operator: OperatorExtended) -> "OperatorType":
        return cls.operator_types_by_type_id[operator.type_id]

    def check_arity(self, operator: OperatorExtended) -> None:
        min_operand_count = self.min_operand_count
        max_operand_count = self.max_operand_count
        if min_operand_count is None and max_operand_count is None:
            return

        packet_count = len(operator.packets)
        if max_operand_count is None:
            if packet_count < min_operand_count:
                raise Exception(
                    f"Expected operator to have at least {min_operand_count} "
                    f"packets, but it had {packet_count}"
                )
        elif min_operand_count is None:
            if packet_count > max_operand_count:
                raise Exception(
                    f"Expected operator to have at most {max_operand_count} "
                    f"packets, but it had {packet_count}"
                )
        elif min_operand_count == max_operand_count:
            if packet_count != min_operand_count:
                raise Exception(
                    f"Expected operator to have exactly {min_operand_count} "
                    f"packets, but it had {packet_count}"
                )
        else:
            if not (min_operand_count <= packet_count <= max_operand_count):
                raise Exception(
                    f"Expected operator to have between {min_operand_count} "
                    f"and {max_operand_count} packets, but it had "
                    f"{packet_count}"
                )

    def apply(self, operator: OperatorExtended) -> int:
        raise NotImplementedError()


@OperatorType.register
class OperatorSum(OperatorType):
    type_id = 0

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=None,
            max_operand_count=None,
        )

    def apply(self, operator: OperatorExtended) -> int:
        return sum(
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        )


@OperatorType.register
class OperatorProduct(OperatorType):
    type_id = 1

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=None,
            max_operand_count=None,
        )

    def apply(self, operator: OperatorExtended) -> int:
        return reduce(int.__mul__, (
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        ), 1)


@OperatorType.register
class OperatorMin(OperatorType):
    type_id = 2

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=1,
            max_operand_count=None,
        )

    def apply(self, operator: OperatorExtended) -> int:
        return min(
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        )


@OperatorType.register
class OperatorMax(OperatorType):
    type_id = 3

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=1,
            max_operand_count=None,
        )

    def apply(self, operator: OperatorExtended) -> int:
        return max(
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        )


@OperatorType.register
class OperatorGreaterThan(OperatorType):
    type_id = 5

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=2,
            max_operand_count=2,
        )

    def apply(self, operator: OperatorExtended) -> int:
        lhs, rhs = (
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        )
        if lhs > rhs:
            return 1
        else:
            return 0


@OperatorType.register
class OperatorLessThan(OperatorType):
    type_id = 6

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=2,
            max_operand_count=2,
        )

    def apply(self, operator: OperatorExtended) -> int:
        lhs, rhs = (
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        )
        if lhs < rhs:
            return 1
        else:
            return 0


@OperatorType.register
class OperatorEqual(OperatorType):
    type_id = 7

    @classmethod
    def make(cls) -> "OperatorType":
        # noinspection PyArgumentList
        return cls(
            min_operand_count=2,
            max_operand_count=2,
        )

    def apply(self, operator: OperatorExtended) -> int:
        lhs, rhs = (
            packet.get_value()
            for packet in cast(List[PacketExtended], operator.packets)
        )
        if lhs == rhs:
            return 1
        else:
            return 0


Challenge.main()
challenge = Challenge()
