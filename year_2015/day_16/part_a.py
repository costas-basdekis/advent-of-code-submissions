#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Optional, List, get_type_hints, Dict, Generic, Type, Tuple, \
    Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        373
        """
        sample = Sample.from_sample_text(
            "children: 3, cats: 7, samoyeds: 2, pomeranians: 3, akitas: 0, "
            "vizslas: 0, goldfish: 5, trees: 3, cars: 2, perfumes: 1")
        return AuntSet.from_aunt_sues_text(_input).get_matching_aunt_id(sample)


SampleT = TV['Sample']


@dataclass
class AuntSet(Generic[SampleT]):
    aunts: List[Tuple[int, SampleT]]

    @classmethod
    def get_sample_class(cls) -> Type[SampleT]:
        return get_type_argument_class(cls, SampleT)

    @classmethod
    def from_aunt_sues_text(cls, aunt_sues_text: str):
        """
        >>> AuntSet.from_aunt_sues_text(
        ...     "Sue 1: cars: 9, akitas: 3, goldfish: 0\\n"
        ...     "Sue 2: akitas: 9, children: 3, samoyeds: 9\\n"
        ... )
        AuntSet(aunts=[(1, Sample(children=None, cats=None, samoyeds=None,
            pomeranians=None, akitas=3, vizslas=None, goldfish=0, trees=None,
            cars=9, perfumes=None)),
            (2, Sample(children=3, cats=None, samoyeds=9,
                pomeranians=None, akitas=9, vizslas=None, goldfish=None,
                trees=None, cars=None, perfumes=None))])
        """
        sample_class = cls.get_sample_class()
        return cls(list(map(
            sample_class.from_aunt_sue_text, aunt_sues_text.splitlines())))

    def get_matching_aunt_id(self, sample: SampleT) -> int:
        aunt_id, = (
            aunt_id
            for aunt_id, aunt_sample in self.aunts
            if sample.is_sample_for(aunt_sample)
        )

        return aunt_id


@dataclass
class Sample:
    children: Optional[int]
    cats: Optional[int]
    samoyeds: Optional[int]
    pomeranians: Optional[int]
    akitas: Optional[int]
    vizslas: Optional[int]
    goldfish: Optional[int]
    trees: Optional[int]
    cars: Optional[int]
    perfumes: Optional[int]

    re_aunt_sue = re.compile(r"^Sue (\d+): (.*)$")
    re_sample_pair = re.compile(r"^(\w+): (\d+)$")

    @classmethod
    def get_field_names(cls) -> List[str]:
        return [
            field_name
            for field_name, annotation in get_type_hints(cls).items()
            if annotation == Optional[int]
        ]

    @classmethod
    def get_default_pairs(cls) -> Dict[str, None]:
        return {
            field_name: None
            for field_name in cls.get_field_names()
        }

    @classmethod
    def from_aunt_sue_text(cls, aunt_sue_text: str):
        """
        >>> Sample.from_aunt_sue_text("Sue 1: cars: 9, akitas: 3, goldfish: 0")
        (1, Sample(children=None, cats=None, samoyeds=None, pomeranians=None,
            akitas=3, vizslas=None, goldfish=0, trees=None, cars=9,
            perfumes=None))
        """
        match = cls.re_aunt_sue.match(aunt_sue_text)
        if not match:
            raise Exception(f"Could not parse {repr(aunt_sue_text)}")
        id_str, sample_text = match.groups()
        return int(id_str), cls.from_sample_text(sample_text)

    @classmethod
    def from_sample_text(cls, sample_text: str):
        """
        >>> Sample.from_sample_text("")
        Sample(children=None, cats=None, samoyeds=None, pomeranians=None,
            akitas=None, vizslas=None, goldfish=None, trees=None, cars=None,
            perfumes=None)
        >>> Sample.from_sample_text("cars: 9, akitas: 3, goldfish: 0")
        Sample(children=None, cats=None, samoyeds=None, pomeranians=None,
            akitas=3, vizslas=None, goldfish=0, trees=None, cars=9,
            perfumes=None)
        """
        matches = [
            (pair_str, cls.re_sample_pair.match(pair_str))
            for pair_str in sample_text.split(", ")
            if pair_str
        ]
        failed_pair_strs = [
            pair_str
            for pair_str, match in matches
            if not match
        ]
        if failed_pair_strs:
            raise Exception(
                f"Could not parse some pairs: "
                f"{', '.join(map(repr, failed_pair_strs))}")
        pairs = {
            key: int(value_str)
            for key, value_str in (
                match.groups()
                for _, match in matches
            )
        }

        return cls(**{**cls.get_default_pairs(), **pairs})

    def is_sample_for(self, other: 'Sample') -> bool:
        """
        >>> Sample.from_sample_text("").is_sample_for(
        ...     Sample.from_sample_text(""))
        True
        >>> Sample.from_sample_text("cars: 9").is_sample_for(
        ...     Sample.from_sample_text("cars: 5, children: 9"))
        False
        >>> Sample.from_sample_text("cars: 9, children: 5").is_sample_for(
        ...     Sample.from_sample_text("cars: 9, children: 9"))
        False
        >>> Sample.from_sample_text("cars: 9").is_sample_for(
        ...     Sample.from_sample_text("children: 9"))
        True
        >>> Sample.from_sample_text("cars: 9").is_sample_for(
        ...     Sample.from_sample_text("cars: 9, children: 9"))
        True
        >>> Sample.from_sample_text("cars: 9").is_sample_for(
        ...     Sample.from_sample_text("cars: 9"))
        True
        >>> Sample.from_sample_text("").is_sample_for(
        ...     Sample.from_sample_text("cars: 9"))
        True
        """
        return self.is_sample_for_with_for_fields(other, self.get_field_names())

    def is_sample_for_with_for_fields(self, other: 'Sample',
                                      field_names: Iterable[str]) -> bool:
        fields = [
            (field_name, getattr(self, field_name), getattr(other, field_name))
            for field_name in field_names
        ]
        return all(
            from_sample is None or from_other is None
            or self.is_value_from_sample_for(
                field_name, from_sample, from_other)
            for field_name, from_sample, from_other in fields
        )

    def is_value_from_sample_for(self, field_name: str,
                                 from_sample: int, from_other: int) -> bool:
        return from_sample == from_other


Challenge.main()
challenge = Challenge()
