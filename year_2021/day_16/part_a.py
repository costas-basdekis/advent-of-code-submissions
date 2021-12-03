#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Generic, Iterable, List, Type, Union, TypeVar, cast, Optional

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        938
        """
        return BitStream.parse_hex_stream(_input).get_version_sum()


PacketT = TypeVar("PacketT", bound="Packet")


@dataclass
class BitStream(Generic[PacketT]):
    bits: List[int]
    position: int

    CHAR_MAP = {
        "0": [0, 0, 0, 0],
        "1": [0, 0, 0, 1],
        "2": [0, 0, 1, 0],
        "3": [0, 0, 1, 1],
        "4": [0, 1, 0, 0],
        "5": [0, 1, 0, 1],
        "6": [0, 1, 1, 0],
        "7": [0, 1, 1, 1],
        "8": [1, 0, 0, 0],
        "9": [1, 0, 0, 1],
        "A": [1, 0, 1, 0],
        "B": [1, 0, 1, 1],
        "C": [1, 1, 0, 0],
        "D": [1, 1, 0, 1],
        "E": [1, 1, 1, 0],
        "F": [1, 1, 1, 1],
    }

    @classmethod
    def get_packet_class(cls) -> Type[PacketT]:
        return cast(Type[PacketT], get_type_argument_class(cls, PacketT))

    @classmethod
    def parse_hex_stream(cls, hex_stream: str) -> PacketT:
        return cls.from_hex_stream(hex_stream).parse()

    @classmethod
    def from_hex_stream(cls, hex_stream: str) -> "BitStream":
        """
        >>> BitStream.from_hex_stream("D2FE28")
        BitStream(bits=[1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0,
            1, 0, 1, 0, 0, 0], position=0)
        """
        return cls(
            bits=sum((
                cls.CHAR_MAP[character]
                for character in hex_stream.strip()
            ), []),
            position=0,
        )

    def parse(self) -> PacketT:
        packet_class = self.get_packet_class()
        return packet_class.parse(self, completely=True)

    def __len__(self) -> int:
        return max(0, len(self.bits) - self.position)

    def __bool__(self):
        return len(self) > 0

    def parse_int(self, length: int) -> int:
        """
        >>> BitStream([1, 1, 0], 0).parse_int(3)
        6
        >>> BitStream([1, 1, 0], 0).parse_int(2)
        3
        >>> BitStream([1, 1, 0], 0).parse_int(1)
        1
        """
        return self.parse_bits_as_int(self.consume(length))

    def parse_bool(self) -> bool:
        return bool(self.parse_int(1))

    def parse_stream(self, length: int) -> "BitStream":
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            bits=self.consume(length),
            position=0,
        )

    def parse_padding(self, max_length: Optional[int] = None) -> None:
        if not self:
            return

        if max_length is None:
            max_length = len(self)
        if max_length > len(self):
            raise Exception(
                f"Expected a padding of at most {max_length}, but there are "
                f"{len(self)} bits remaining"
            )
        padding = self.parse_int(max_length)
        if padding:
            raise Exception(f"Expected padding to be 0, but it was {padding}")

    @classmethod
    def parse_bits_as_int(cls, bits: List[int]) -> int:
        return int("".join(map(str, bits)), base=2)

    def consume(self, length: int) -> List[int]:
        """
        >>> stream = BitStream([1, 1, 0], 0)
        >>> stream.consume(3)
        [1, 1, 0]
        >>> stream
        BitStream(bits=[1, 1, 0], position=3)
        >>> stream.consume(1)
        Traceback (most recent call last):
        ...
        IndexError: Bit stream index out of of range
        """
        bits = self.peek(length)
        self.position += len(bits)

        return bits

    def peek(self, length: int) -> List[int]:
        """
        >>> stream = BitStream([1, 1, 0], 0)
        >>> stream.peek(3)
        [1, 1, 0]
        >>> stream
        BitStream(bits=[1, 1, 0], position=0)
        >>> stream.peek(3)
        [1, 1, 0]
        >>> stream
        BitStream(bits=[1, 1, 0], position=0)
        >>> stream.consume(3)
        [1, 1, 0]
        >>> stream
        BitStream(bits=[1, 1, 0], position=3)
        >>> stream.peek(1)
        Traceback (most recent call last):
        ...
        IndexError: Bit stream index out of of range
        """
        new_position = self.position + length
        if new_position > len(self.bits):
            raise IndexError(f"Bit stream index out of of range")

        return self.bits[self.position:new_position]


LiteralT = TypeVar("LiteralT", bound="Literal")
OperatorT = TypeVar("OperatorT", bound="Operator")


@dataclass
class Packet(Generic[LiteralT, OperatorT]):
    version: int
    type_id: int

    @classmethod
    def get_literal_class(cls) -> Type[LiteralT]:
        return cast(Type[LiteralT], get_type_argument_class(cls, LiteralT))

    @classmethod
    def get_operator_class(cls) -> Type[OperatorT]:
        return cast(Type[OperatorT], get_type_argument_class(cls, OperatorT))

    @classmethod
    def parse(cls, bit_stream: BitStream, completely: bool = False) -> "Packet":
        """
        >>> Packet.parse(BitStream.from_hex_stream("D2FE28"))
        Literal(version=6, type_id=4, value=2021)
        >>> Packet.parse(BitStream.from_hex_stream("38006F45291200"))
        Operator(version=1, type_id=6,
            packets=[Literal(version=6, type_id=4, value=10),
            Literal(version=2, type_id=4, value=20)])
        >>> Packet.parse(BitStream.from_hex_stream("EE00D40C823060"))
        Operator(version=7, type_id=3,
            packets=[Literal(version=2, type_id=4, value=1),
            Literal(version=4, type_id=4, value=2),
            Literal(version=1, type_id=4, value=3)])
        """
        version = cls.parse_version(bit_stream)
        type_id = cls.parse_type_id(bit_stream)
        if type_id == 4:
            literal_class = cls.get_literal_class()
            packet = literal_class.parse_literal(version, type_id, bit_stream)
        else:
            operator_class = cls.get_operator_class()
            packet = operator_class.parse_operator(version, type_id, bit_stream)

        if completely:
            bit_stream.parse_padding()
            if bit_stream:
                raise Exception(
                    f"Expected to completely parsing to finish the stream, but "
                    f"there were {len(bit_stream)} bits left"
                )

        return packet

    @classmethod
    def parse_version(cls, bit_stream: BitStream) -> int:
        return bit_stream.parse_int(3)

    @classmethod
    def parse_type_id(cls, bit_stream: BitStream) -> int:
        return bit_stream.parse_int(3)

    def get_version_sum(self) -> int:
        raise NotImplementedError()


@dataclass
class Literal(Packet):
    value: int

    @classmethod
    def parse_literal(
        cls, version: int, type_id: int, bit_stream: BitStream,
    ) -> "Literal":
        bits = sum(cls.parse_bits_group(bit_stream), [])
        value = bit_stream.parse_bits_as_int(bits)
        return cls(
            version=version,
            type_id=type_id,
            value=value,
        )

    @classmethod
    def parse_bits_group(cls, bit_stream: BitStream) -> Iterable[List[int]]:
        should_continue = True
        while should_continue:
            should_continue, *bits_group = bit_stream.consume(5)
            yield bits_group

    def get_version_sum(self) -> int:
        return self.version


@dataclass
class Operator(Packet):
    packets: List[Packet]

    @classmethod
    def parse_operator(
        cls, version: int, type_id: int, bit_stream: BitStream,
    ) -> "Operator":
        parse_packets_by_count = bit_stream.parse_bool()
        if parse_packets_by_count:
            packet_count = bit_stream.parse_int(11)
            packets = [
                cls.parse(bit_stream)
                for _ in range(packet_count)
            ]
        else:
            sub_stream_length = bit_stream.parse_int(15)
            sub_stream = bit_stream.parse_stream(sub_stream_length)
            packets = []
            while sub_stream:
                packets.append(cls.parse(sub_stream))

        return cls(
            version=version,
            type_id=type_id,
            packets=packets,
        )

    def get_version_sum(self) -> int:
        """
        >>> BitStream.parse_hex_stream("8A004A801A8002F478")\\
        ...     .get_version_sum()
        16
        >>> BitStream.parse_hex_stream("620080001611562C8802118E34")\\
        ...     .get_version_sum()
        12
        >>> BitStream.parse_hex_stream("C0015000016115A2E0802F182340")\\
        ...     .get_version_sum()
        23
        >>> BitStream.parse_hex_stream("A0016C880162017C3686B18A3D4780")\\
        ...     .get_version_sum()
        31
        """
        return self.version + sum(
            packet.get_version_sum()
            for packet in self.packets
        )


Challenge.main()
challenge = Challenge()
