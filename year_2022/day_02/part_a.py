#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import ClassVar, Dict, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        13924
        """
        return RpsInstructionSet\
            .from_encoded_instructions_text(_input)\
            .get_points()


class Rps(Enum):
    Rock = "rock"
    Paper = "paper"
    Scissors = "scissors"

    @classmethod
    def from_plain(cls, plain: str) -> "Rps":
        return PlainRps.parse(plain)

    @classmethod
    def from_encoded(cls, encoded: str, decoder: "RpsDecoder") -> "Rps":
        return decoder[encoded]

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"


class PlainRps(Enum):
    A = "A"
    B = "B"
    C = "C"

    parsing_map: Dict[str, Rps]

    @classmethod
    def parse(cls, plain: str) -> Rps:
        return cls.parsing_map[plain]


PlainRps.parsing_map = {
    PlainRps.A.value: Rps.Rock,
    PlainRps.B.value: Rps.Paper,
    PlainRps.C.value: Rps.Scissors,
}


class EncodedRps(Enum):
    X = "X"
    Y = "Y"
    Z = "Z"


RpsDecoder = Dict[str, Rps]

DefaultRpsDecoder: RpsDecoder = {
    EncodedRps.X.value: Rps.Rock,
    EncodedRps.Y.value: Rps.Paper,
    EncodedRps.Z.value: Rps.Scissors,
}


class Result(Enum):
    Win = "win"
    Draw = "draw"
    Loss = "loss"

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"

    result_map: Dict[Tuple[Rps, Rps], "Result"]


Result.result_map = {
    (Rps.Rock, Rps.Rock): Result.Draw,
    (Rps.Rock, Rps.Paper): Result.Loss,
    (Rps.Rock, Rps.Scissors): Result.Win,
    (Rps.Paper, Rps.Rock): Result.Win,
    (Rps.Paper, Rps.Paper): Result.Draw,
    (Rps.Paper, Rps.Scissors): Result.Loss,
    (Rps.Scissors, Rps.Rock): Result.Loss,
    (Rps.Scissors, Rps.Paper): Result.Win,
    (Rps.Scissors, Rps.Scissors): Result.Draw,
}


@dataclass
class RpsInstructionSet:
    instructions: ["RpsInstruction"]
    decoder: RpsDecoder = field(default_factory=lambda: DefaultRpsDecoder)

    # noinspection PyDefaultArgument
    @classmethod
    def from_encoded_instructions_text(
        cls, instructions_text: str, decoder: RpsDecoder = DefaultRpsDecoder,
    ) -> "RpsInstructionSet":
        """
        >>> RpsInstructionSet.from_encoded_instructions_text("A Y\\nB X\\nC Z")
        RpsInstructionSet(instructions=[RpsInstruction(opponent=Rps.Rock, you=Rps.Paper), ...], decoder={...})
        """
        return cls(
            instructions=[
                RpsInstruction.from_encoded_instruction_text(line, decoder)
                for line in instructions_text.strip().splitlines()
            ],
        )

    def get_points(self) -> int:
        """
        >>> RpsInstructionSet\\
        ...     .from_encoded_instructions_text("A Y\\nB X\\nC Z").get_points()
        15
        """
        return sum(
            instruction.get_points()
            for instruction in self.instructions
        )


@dataclass
class RpsInstruction:
    opponent: Rps
    you: Rps

    re_instruction = re.compile(r"^([ABC]) ([XYZ])$")

    # noinspection PyDefaultArgument
    @classmethod
    def from_encoded_instruction_text(
        cls, instruction_text: str, decoder: RpsDecoder = DefaultRpsDecoder,
    ) -> "RpsInstruction":
        """
        >>> RpsInstruction.from_encoded_instruction_text("A Y")
        RpsInstruction(opponent=Rps.Rock, you=Rps.Paper)
        """
        opponent_str, encoded_you_str = \
            cls.re_instruction.match(instruction_text).groups()
        return cls(
            opponent=Rps.from_plain(opponent_str),
            you=Rps.from_encoded(encoded_you_str, decoder),
        )

    choice_points: ClassVar[Dict[Rps, int]] = {
        Rps.Rock: 1,
        Rps.Paper: 2,
        Rps.Scissors: 3,
    }

    result_points: ClassVar[Dict[Result, int]] = {
        Result.Win: 6,
        Result.Draw: 3,
        Result.Loss: 0,
    }

    def get_result(self) -> Result:
        """
        >>> RpsInstruction(you=Rps.Rock, opponent=Rps.Paper).get_result()
        Result.Loss
        """
        return Result.result_map[(self.you, self.opponent)]

    def get_points(self) -> int:
        """
        >>> RpsInstruction.from_encoded_instruction_text("A Y").get_points()
        8
        >>> RpsInstruction.from_encoded_instruction_text("B X").get_points()
        1
        >>> RpsInstruction.from_encoded_instruction_text("C Z").get_points()
        6
        """
        return (
            self.choice_points[self.you]
            + self.result_points[self.get_result()]
        )


Challenge.main()
challenge = Challenge()
