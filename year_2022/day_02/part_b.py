#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import ClassVar, Dict, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2022.day_02.part_a import Result, EncodedRps, RpsInstruction, Rps


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        13448
        """
        return ResultInstructionSet\
            .from_encoded_instructions_text(_input)\
            .get_points()


# noinspection PyTypeChecker
ResultDecoder: Dict[str, Result] = {
    EncodedRps.X.value: Result.Loss,
    EncodedRps.Y.value: Result.Draw,
    EncodedRps.Z.value: Result.Win,
}


@dataclass
class ResultInstructionSet:
    instructions: ["ResultInstruction"]

    @classmethod
    def from_encoded_instructions_text(
        cls, instructions_text: str,
    ) -> "ResultInstructionSet":
        """
        >>> ResultInstructionSet.from_encoded_instructions_text("A Y\\nB X\\nC Z")
        ResultInstructionSet(instructions=[ResultInstruction(opponent=Rps.Rock, result=Result.Draw), ...])
        """
        return cls(
            instructions=[
                ResultInstruction.from_encoded_instruction_text(line)
                for line in instructions_text.strip().splitlines()
            ],
        )

    def get_points(self) -> int:
        """
        >>> ResultInstructionSet\\
        ...     .from_encoded_instructions_text("A Y\\nB X\\nC Z").get_points()
        12
        """
        return sum(
            instruction.get_points()
            for instruction in self.instructions
        )


@dataclass
class ResultInstruction:
    opponent: Rps
    result: Result

    re_instruction = re.compile(r"^([ABC]) ([XYZ])$")

    @classmethod
    def from_encoded_instruction_text(
        cls, instruction_text: str,
    ) -> "ResultInstruction":
        """
        >>> ResultInstruction.from_encoded_instruction_text("A Y")
        ResultInstruction(opponent=Rps.Rock, result=Result.Draw)
        """
        opponent_str, result_str, = \
            cls.re_instruction.match(instruction_text).groups()
        return cls(
            opponent=Rps.from_plain(opponent_str),
            result=ResultDecoder[result_str],
        )

    choice_points: ClassVar[Dict[Rps, int]] = RpsInstruction.choice_points
    result_points: ClassVar[Dict[Result, int]] = RpsInstruction.result_points

    you_map: ClassVar[Dict[Tuple[Rps, Result], Rps]] = {
        (_opponent, _result): _you
        for (_you, _opponent), _result in Result.result_map.items()
    }

    def get_you(self) -> Rps:
        """
        >>> ResultInstruction.from_encoded_instruction_text("A Y").get_you()
        Rps.Rock
        >>> ResultInstruction.from_encoded_instruction_text("B X").get_you()
        Rps.Rock
        >>> ResultInstruction.from_encoded_instruction_text("C Z").get_you()
        Rps.Rock
        """
        return self.you_map[(self.opponent, self.result)]

    def get_points(self) -> int:
        """
        >>> ResultInstruction.from_encoded_instruction_text("A Y").get_points()
        4
        >>> ResultInstruction.from_encoded_instruction_text("B X").get_points()
        1
        >>> ResultInstruction.from_encoded_instruction_text("C Z").get_points()
        7
        """
        return (
            self.choice_points[self.get_you()]
            + self.result_points[self.result]
        )


Challenge.main()
challenge = Challenge()
