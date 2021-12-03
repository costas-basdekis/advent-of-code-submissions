#!/usr/bin/env python3
from dataclasses import dataclass
from functools import reduce

from itertools import combinations
from typing import List, Iterable, Tuple, ClassVar, Type, cast

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        11846773891
        """
        return PackageSet\
            .from_packages_text(_input)\
            .first_group_quantum_entanglement


@dataclass
class PackageSet:
    packages: List[int]
    group_count: ClassVar[int] = 3

    @classmethod
    def of_group_count(cls, group_count: int) -> Type["PackageSet"]:
        return cast(Type[PackageSet], type(
            f"PackageSetOf{group_count}",
            (cls,),
            {"group_count": group_count},
        ))

    @classmethod
    def from_packages_text(cls, packages_text: str) -> "PackageSet":
        """
        >>> PackageSet.from_packages_text('''
        ...     1
        ...     2
        ...     3
        ...     4
        ...     5
        ...     7
        ...     8
        ...     9
        ...     10
        ...     11
        ... ''')
        PackageSet(packages=[1, 2, 3, 4, 5, 7, 8, 9, 10, 11])
        """
        return cls(
            packages=list(map(
                int, filter(None, map(str.strip, packages_text.splitlines()))
            )),
        )

    @property
    def group_sum(self) -> int:
        """
        >>> PackageSet([1, 2, 3, 4, 5, 7, 8, 9, 10, 11]).group_sum
        20
        """
        total_sum = sum(self.packages)
        if total_sum % self.group_count != 0:
            raise Exception(
                f"Expected total sum to be divisible by {self.group_count}, "
                f"but it wasn't: {total_sum}"
            )

        return total_sum // self.group_count

    @property
    def first_group_quantum_entanglement(self) -> int:
        """
        >>> PackageSet(
        ...     [1, 2, 3, 4, 5, 7, 8, 9, 10, 11],
        ... ).first_group_quantum_entanglement
        99
        """
        return self.get_group_quantum_entanglement(self.first_group)

    def get_group_quantum_entanglement(self, group: Tuple[int, ...]) -> int:
        """
        >>> PackageSet([]).get_group_quantum_entanglement((9, 11))
        99
        """
        return reduce(int.__mul__, group)

    @property
    def first_group(self) -> Tuple[int, ...]:
        """
        >>> PackageSet(
        ...     [1, 2, 3, 4, 5, 7, 8, 9, 10, 11],
        ... ).first_group
        (9, 11)
        """
        first_group_candidates = list(self.first_group_candidates)
        if not first_group_candidates:
            raise Exception("No group candidates found")

        first_group = min(
            first_group_candidates,
            key=self.get_group_quantum_entanglement,
        )
        return first_group

    @property
    def first_group_candidates(self) -> Iterable[Tuple[int, ...]]:
        """
        >>> sorted(PackageSet(
        ...     [1, 2, 3, 4, 5, 7, 8, 9, 10, 11],
        ... ).first_group_candidates)
        [(9, 11)]
        """
        group_sum = self.group_sum
        found_length = False
        for length in range(1, len(self.packages) - 2):
            for group in combinations(self.packages, length):
                if sum(group) != group_sum:
                    continue
                yield group
                found_length = True
            if found_length:
                break


Challenge.main()
challenge = Challenge()
