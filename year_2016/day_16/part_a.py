#!/usr/bin/env python3
from aox.challenge import Debugger

from utils import BaseChallenge
from aox.utils import in_groups


class Challenge(BaseChallenge):
    def solve(self, _input, debugger):
        """
        >>> Challenge().default_solve()
        '10011010010010010'
        """
        return DataGenerator().get_disk_checksum(
            272, _input.strip(), debugger=debugger)


class DataGenerator:
    def get_disk_checksum(self, size: int, initial: str, debugger: Debugger,
                          ) -> str:
        """
        >>> DataGenerator().get_disk_checksum(20, "10000")
        '01100'
        """
        debugger.report_if("Getting disk checksum")
        disk = self.fill_disk(size, initial, debugger=debugger.sub_debugger())
        return self.get_checksum(disk, debugger=debugger.sub_debugger())

    def fill_disk(self, size: int, initial: str, debugger: Debugger) -> str:
        """
        >>> DataGenerator().fill_disk(20, "10000")
        '10000011110010000111'
        """
        disk = initial
        while len(disk) < size:
            disk = self.increase_data(disk)
            if debugger.should_report():
                debugger.report(
                    f"Filling, step: {debugger.step_count}, time: "
                    f"{debugger.pretty_duration_since_start}, size: "
                    f"{len(disk)}/{size}")

        disk = disk[:size]
        return disk

    def get_checksum(self, data: str, debugger: Debugger) -> str:
        """
        >>> DataGenerator().get_checksum("110010110100")
        '100'
        >>> DataGenerator().get_checksum("110101")
        '100'
        >>> DataGenerator().get_checksum("100")
        '100'
        >>> DataGenerator().get_checksum("10000011110010000111")
        '01100'
        """
        reduced = data
        while True:
            new_reduced = self.reduce_data(reduced)
            if new_reduced == reduced:
                break
            reduced = new_reduced

            if debugger.should_report():
                debugger.report(
                    f"Check summing, step: {debugger.step_count}, time: "
                    f"{debugger.pretty_duration_since_start}, size: "
                    f"{len(reduced)}/{len(data)}")

        return reduced

    REDUCE_DATA_MAP = {
        "00": "1",
        "01": "0",
        "10": "0",
        "11": "1",
    }

    def reduce_data(self, data: str) -> str:
        """
        >>> DataGenerator().reduce_data("110010110100")
        '110101'
        >>> DataGenerator().reduce_data("110101")
        '100'
        >>> DataGenerator().reduce_data("100")
        '100'
        """
        if len(data) % 2 == 1:
            return data

        return "".join(map(
            self.REDUCE_DATA_MAP.get, map("".join, in_groups(data, 2))))

    INVERT_DATA_MAP = {
        "1": "0",
        "0": "1",
    }

    def increase_data(self, data: str) -> str:
        """
        >>> DataGenerator().increase_data("1")
        '100'
        >>> DataGenerator().increase_data("0")
        '001'
        >>> DataGenerator().increase_data("11111")
        '11111000000'
        >>> DataGenerator().increase_data("111100001010")
        '1111000010100101011110000'
        """
        reversed_inverted = "".join(map(
            self.INVERT_DATA_MAP.get, reversed(data)))
        return f"{data}0{reversed_inverted}"


Challenge.main()
challenge = Challenge()
