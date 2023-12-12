#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, List, Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_09 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        6427437134372
        """
        return DiskFileCompacter.from_disk_text(_input).compact_all_files().to_disk().get_checksum()


@dataclass
class DiskFileCompacter:
    file_starts_by_id: Dict[int, int]
    file_sizes_by_id: Dict[int, int]
    gap_starts_by_size: Dict[int, List[int]]

    @classmethod
    def from_disk_text(cls, text: str) -> "DiskFileCompacter":
        return cls.from_disk(part_a.Disk.from_text(text))
    
    @classmethod
    def from_disk(cls, disk: part_a.Disk) -> "DiskFileCompacter":
        """
        >>> print(DiskFileCompacter.from_disk_text("2333133121414131402"))
        00...111...2...333.44.5555.6666.777.888899
        """
        file_starts_by_id = {}
        file_sizes_by_id = {}
        gap_starts_by_size = {}
        position = 0
        for file in disk.files:
            file_start = min(file.positions)
            file_end = max(file.positions)
            file_size = file_end - file_start + 1
            if file_start > position:
                gap_size = file_start - position
                gap_starts_by_size.setdefault(gap_size, []).append(position)
            file_starts_by_id[file.file_id] = file_start
            file_sizes_by_id[file.file_id] = file_size
            position = file_end + 1
        return cls(
            file_starts_by_id=file_starts_by_id,
            file_sizes_by_id=file_sizes_by_id,
            gap_starts_by_size=gap_starts_by_size,
        )

    def __str__(self):
        return str(self.to_disk())

    def compact_all_files(self) -> "DiskFileCompacter":
        """
        >>> print(DiskFileCompacter.from_disk_text("2333133121414131402").compact_all_files())
        00992111777.44.333....5555.6666.....8888
        >>> DiskFileCompacter.from_disk_text("2333133121414131402").compact_all_files().to_disk().get_checksum()
        2858
        """
        for file_id in sorted(self.file_starts_by_id, reverse=True):
            self.compact_file(file_id)
        return self

    def compact_file(self, file_id: int) -> "DiskFileCompacter":
        """
        >>> print(DiskFileCompacter.from_disk_text("2333133121414131402").compact_file(9))
        0099.111...2...333.44.5555.6666.777.8888
        """
        file_size = self.file_sizes_by_id[file_id]
        file_start = self.file_starts_by_id[file_id]
        new_start_and_gap_size = min((
            (gap_start, gap_size)
            for gap_size in range(file_size, 10)
            for gap_start in self.gap_starts_by_size.get(gap_size, [])
            if gap_start < file_start
        ), default=None)
        if new_start_and_gap_size is None:
            return self
        new_start, gap_size = new_start_and_gap_size
        self.file_starts_by_id[file_id] = new_start
        self.gap_starts_by_size[gap_size].remove(new_start)
        if gap_size > file_size:
            new_gap_size = gap_size - file_size
            self.gap_starts_by_size.setdefault(new_gap_size, []).append(new_start + file_size)
        return self

    def to_disk(self) -> part_a.Disk:
        file_ids = sorted(self.file_starts_by_id)
        return part_a.Disk(files=[
            part_a.File.from_range(file_id, self.file_starts_by_id[file_id], self.file_sizes_by_id[file_id])
            for file_id in file_ids
        ])


Challenge.main()
challenge = Challenge()
