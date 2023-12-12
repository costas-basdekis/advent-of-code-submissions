#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Generic, List, Type, Union

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, TV


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        515210
        """
        return HasherSet.from_text(_input).hash()


HasherT = TV["Hasher"]


@dataclass
class HasherSet(Generic[HasherT]):
    hashers: List["Hasher"]

    @classmethod
    def get_hasher_class(cls) -> Type[HasherT]:
        return get_type_argument_class(cls, HasherT)

    @classmethod
    def from_text(cls, text: str) -> "HasherSet":
        """
        >>> print(HasherSet.from_text('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7'))
        rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7
        >>> len(HasherSet.from_text('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7').hashers)
        11
        """
        hasher_class = cls.get_hasher_class()
        return cls(hashers=list(map(hasher_class, text.strip().split(","))))

    def __str__(self) -> str:
        return ",".join(map(str, self.hashers))

    def hash(self) -> int:
        """
        >>> HasherSet.from_text('rn=1,cm-,qp=3,cm=2,qp-,pc=4,ot=9,ab=5,pc-,pc=6,ot=7').hash()
        1320
        """
        return sum(
            hasher.hash()
            for hasher in self.hashers
        )


@dataclass
class Hasher:
    text: str

    def __str__(self) -> str:
        """
        >>> print(Hasher("HASH"))
        HASH
        """
        return self.text

    def hash(self) -> int:
        """
        >>> Hasher("HASH").hash()
        52
        """
        value = 0
        for char in self.text:
            value += ord(char)
            value *= 17
            value %= 256
        return value


Challenge.main()
challenge = Challenge()
