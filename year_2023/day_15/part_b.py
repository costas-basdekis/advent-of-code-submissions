#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser
from year_2023.day_15 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        246762
        """
        return BoxSet.from_instructions_text(_input).get_focusing_power()


@dataclass
class BoxSet:
    boxes: Dict[int, "Box"]

    @classmethod
    def empty(cls) -> "BoxSet":
        """
        >>> print(BoxSet.empty())
        """
        return cls(boxes={box_id: Box.empty() for box_id in range(256)})

    @classmethod
    def from_instructions_text(cls, text: str) -> "BoxSet":
        return cls.empty().apply_instructions(InstructionSet.from_text(text))

    def __str__(self) -> str:
        return "\n".join(
            f"Box {box_id}: {box}"
            for box_id, box in self.boxes.items()
            if box.lenses
        )

    def __getitem__(self, item: int) -> "Box":
        return self.boxes[item]

    def apply_instructions(self, instruction_set: "InstructionSet") -> "BoxSet":
        instruction_set.apply_to(self)
        return self

    def get_focusing_power(self) -> int:
        """
        >>> BoxSet.empty().apply_instructions(InstructionSet.from_text(
        ...     'rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7')).get_focusing_power()
        145
        """
        return sum(
            box.get_focusing_power(box_id)
            for box_id, box in self.boxes.items()
        )


@dataclass
class Box:
    lenses: List["Lens"]

    @classmethod
    def empty(cls) -> "Box":
        return cls(lenses=[])

    def __str__(self) -> str:
        return " ".join(map(str, self.lenses))

    def add_lens(self, lens: "Lens") -> "Box":
        """
        >>> print(Box.empty().add_lens(Lens('rn', 1)))
        [rn 1]
        >>> print(Box.empty().add_lens(Lens('rn', 1)).add_lens(Lens('rn', 2)))
        [rn 2]
        >>> print(Box.empty().add_lens(Lens('rn', 1)).add_lens(Lens('qp', 2)))
        [rn 1] [qp 2]
        >>> print(Box.empty().add_lens(Lens('rn', 1)).add_lens(Lens('qp', 2)).add_lens(Lens('rn', 3)))
        [rn 3] [qp 2]
        """
        existing_lens_index = self.get_existing_lens_index(lens.label)
        if existing_lens_index is None:
            self.lenses.append(lens)
            return self
        self.lenses[existing_lens_index] = lens
        return self

    def remove_lens(self, label: str) -> "Box":
        """
        >>> print(Box.empty().remove_lens('rn'))
        >>> print(Box.empty().add_lens(Lens('rn', 1)))
        [rn 1]
        >>> print(Box.empty().add_lens(Lens('rn', 1)).remove_lens('rn'))
        >>> print(Box.empty().add_lens(Lens('rn', 1)).add_lens(Lens('rn', 2)))
        [rn 2]
        >>> print(Box.empty().add_lens(Lens('rn', 1)).add_lens(Lens('qp', 2)).remove_lens('rn'))
        [qp 2]
        >>> print(Box.empty().add_lens(Lens('rn', 1)).add_lens(Lens('qp', 2)).remove_lens('qp'))
        [rn 1]
        """
        existing_lens_index = self.get_existing_lens_index(label)
        if existing_lens_index is None:
            return self
        self.lenses.remove(self.lenses[existing_lens_index])
        return self

    def get_existing_lens_index(self, label: str) -> Optional[int]:
        existing_lenses_indexes = [
            index
            for index, existing in enumerate(self.lenses)
            if existing.label == label
        ]
        if not existing_lenses_indexes:
            return None
        if len(existing_lenses_indexes) > 1:
            raise Exception(f"Box has too many lenses with label {label}: {self}")
        existing_lens_index, = existing_lenses_indexes
        return existing_lens_index

    def get_focusing_power(self, box_id: int) -> int:
        """
        >>> Box.empty().get_focusing_power(0)
        0
        >>> Box([Lens('rn', 1), Lens('cm', 2)]).get_focusing_power(0)
        5
        >>> Box([Lens('ot', 7), Lens('ab', 5), Lens('pc', 6)]).get_focusing_power(3)
        140
        """
        return (box_id + 1) * sum(
            (lens_index + 1) * lens.level
            for lens_index, lens in enumerate(self.lenses)
        )


@dataclass
class Lens:
    label: str
    level: int

    def __str__(self) -> str:
        return f"[{self.label} {self.level}]"


@dataclass
class InstructionSet:
    instructions: List["Instruction"]

    @classmethod
    def from_text(cls, text: str) -> "InstructionSet":
        """
        >>> InstructionSet.from_text('rn=1,cm-,qp=3')
        InstructionSet(instructions=[AddInstruction(box_id=0, label='rn', level=1),
            RemoveInstruction(box_id=0, label='cm'), AddInstruction(box_id=1, label='qp', level=3)])
        """
        return cls(instructions=list(map(Instruction.parse, text.strip().split(","))))

    def apply_to(self, box_set: BoxSet) -> "InstructionSet":
        """
        >>> print(BoxSet.empty().apply_instructions(InstructionSet.from_text(
        ...     'rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7')))
        Box 0: [rn 1] [cm 2]
        Box 3: [ot 7] [ab 5] [pc 6]
        """
        for instruction in self.instructions:
            instruction.apply_to(box_set)
        return self


@dataclass
class Instruction(PolymorphicParser, ABC, root=True):
    """
    >>> Instruction.parse("rn=1")
    AddInstruction(box_id=0, label='rn', level=1)
    >>> Instruction.parse("cm-")
    RemoveInstruction(box_id=0, label='cm')
    """
    box_id: int
    label: str

    def apply_to(self, box_set: BoxSet) -> BoxSet:
        raise NotImplementedError()


@Instruction.register
@dataclass
class AddInstruction(Instruction):
    name = "add"

    level: int

    @classmethod
    def try_parse(cls, text: str) -> Optional["AddInstruction"]:
        """
        >>> AddInstruction.try_parse("rn=1")
        AddInstruction(box_id=0, label='rn', level=1)
        >>> AddInstruction.try_parse("cm-")
        """
        if "=" not in text:
            return None
        label, level_str = text.strip().split("=")
        return cls(box_id=part_a.Hasher(label).hash(), label=label, level=int(level_str))

    def apply_to(self, box_set: BoxSet) -> BoxSet:
        box_set[self.box_id].add_lens(Lens(self.label, self.level))
        return box_set


@Instruction.register
@dataclass
class RemoveInstruction(Instruction):
    name = "remove"

    @classmethod
    def try_parse(cls, text: str) -> Optional["RemoveInstruction"]:
        """
        >>> RemoveInstruction.try_parse("rn=1")
        >>> RemoveInstruction.try_parse("cm-")
        RemoveInstruction(box_id=0, label='cm')
        """
        if "-" not in text:
            return None
        label, rest = text.strip().split("-")
        return cls(box_id=part_a.Hasher(label).hash(), label=label)

    def apply_to(self, box_set: BoxSet) -> BoxSet:
        box_set[self.box_id].remove_lens(self.label)


Challenge.main()
challenge = Challenge()
