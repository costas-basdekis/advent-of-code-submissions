#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, List, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        '122-12==0-01=00-0=02'
        """
        return FuelMachine.from_snafu_list(_input).get_total_fuel_in_snafu()


@dataclass
class FuelMachine:
    snafu_list: List[str]

    @classmethod
    def from_snafu_list(cls, snafu_list: str) -> "FuelMachine":
        """
        >>> print(FuelMachine.from_snafu_list('''
        ... 1=-0-2
        ... 12111
        ... 2=0=
        ... 21
        ... 2=01
        ... 111
        ... 20012
        ... 112
        ... 1=-1=
        ... 1-12
        ... 12
        ... 1=
        ... 122
        ... '''))
        1=-0-2
        12111
        2=0=
        21
        2=01
        111
        20012
        112
        1=-1=
        1-12
        12
        1=
        122
        """
        return FuelMachine(list(map(str.strip, snafu_list.strip().splitlines())))

    def __str__(self) -> str:
        return "\n".join(self.snafu_list)

    def get_total_fuel_in_snafu(self) -> str:
        """
        >>> FuelMachine.from_snafu_list('''
        ... 1=-0-2
        ... 12111
        ... 2=0=
        ... 21
        ... 2=01
        ... 111
        ... 20012
        ... 112
        ... 1=-1=
        ... 1-12
        ... 12
        ... 1=
        ... 122
        ... ''').get_total_fuel_in_snafu()
        '2=-1=0'
        """
        return SnafuCodec.to_snafu(self.get_total_fuel())

    def get_total_fuel(self) -> int:
        """
        >>> FuelMachine.from_snafu_list('''
        ... 1=-0-2
        ... 12111
        ... 2=0=
        ... 21
        ... 2=01
        ... 111
        ... 20012
        ... 112
        ... 1=-1=
        ... 1-12
        ... 12
        ... 1=
        ... 122
        ... ''').get_total_fuel()
        4890
        """
        return sum(map(SnafuCodec.from_snafu, self.snafu_list))


class SnafuCodec:
    SNAFU_MAP: Dict[str, int] = {
        "=": -2,
        "-": -1,
        "0": 0,
        "1": 1,
        "2": 2,
    }
    SNAFU_REVERSE_MAP: Dict[int, str] = {
        number: snafu
        for snafu, number in SNAFU_MAP.items()
    }

    @classmethod
    def from_snafu(cls, snafu: str) -> int:
        """
        >>> list(map(SnafuCodec.from_snafu, ["1", "2", "1=", "1-", "10", "11", "12", "2=", "2-", "20", "21", "22"]))
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        >>> list(map(SnafuCodec.from_snafu, ["1=0", "1-0", "1=11-2", "1-0---0", "1121-1110-1=0"]))
        [15, 20, 2022, 12345, 314159265]
        """
        number = 0
        for char in snafu.strip():
            number *= 5
            number += cls.SNAFU_MAP[char]
        return number

    @classmethod
    def to_snafu(cls, number: int) -> str:
        """
        >>> list(map(SnafuCodec.to_snafu, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
        ['1', '2', '1=', '1-', '10', '11', '12', '2=', '2-', '20', '21', '22']
        >>> list(map(SnafuCodec.to_snafu, [15, 20, 2022, 12345, 314159265]))
        ['1=0', '1-0', '1=11-2', '1-0---0', '1121-1110-1=0']
        """
        if not number:
            return "0"
        snafu = ""
        while number > 0:
            remainder = number % 5
            number = number // 5
            if remainder > 2:
                remainder -= 5
                number += 1
            snafu = cls.SNAFU_REVERSE_MAP[remainder] + snafu
        return snafu


Challenge.main()
challenge = Challenge()
