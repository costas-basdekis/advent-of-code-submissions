#!/usr/bin/env python3
from dataclasses import dataclass
from itertools import groupby
from typing import Dict, Generic, List, Optional, Set, Type, Union, TypeVar

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, Self


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        6398608069280
        """
        return DiskCompacter.from_disk_text(_input).compact(debugger=debugger).to_disk().get_checksum()


FileT = TypeVar("FileT", bound="File")


@dataclass
class Disk(Generic[FileT]):
    files: List[FileT]

    @classmethod
    def get_file_class(cls) -> Type[FileT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, FileT)

    @classmethod
    def from_text(cls, text: str) -> "Disk":
        """
        >>> print(Disk.from_text("12345"))
        0..111....22222
        >>> print(Disk.from_text("2333133121414131402"))
        00...111...2...333.44.5555.6666.777.888899
        """
        position = 0
        files = []
        file_class = cls.get_file_class()
        for index, count in enumerate(map(int, text.strip())):
            if index % 2 == 0:
                files.append(file_class.from_range(len(files), position, count))
            position += count
        return cls(files=files)

    def __str__(self) -> str:
        return self.show()

    def show(self, max_position: Optional[int] = None) -> str:
        ids_by_position = {
            position: file.file_id
            for file in self.files
            for position in file.positions
        }
        if max_position is None:
            max_position = max(ids_by_position)
        return "".join(
            f"{file_id}"
            if file_id is not None else
            "."
            for position in range(max_position + 1)
            for file_id in [ids_by_position.get(position)]
        )

    def get_checksum(self) -> int:
        """
        >>> Disk.from_text("2333133121414131402").compact().get_checksum()
        1928
        """
        return sum(
            position * file.file_id
            for file in self.files
            for position in file.positions
        )

    def compact(self: Self["Disk"], debugger: Debugger = Debugger(enabled=False)) -> Self["Disk"]:
        """
        >>> print(Disk.from_text("12345").compact())
        022111222
        >>> print(Disk.from_text("2333133121414131402").compact())
        0099811188827773336446555566
        """
        disk = self
        while debugger.step_if(True):
            next_disk = disk.compact_one(debugger=debugger)
            if next_disk == disk:
                break
            disk = next_disk
        return disk

    def compact_one(self: Self["Disk"], debugger: Debugger = Debugger(enabled=False)) -> Self["Disk"]:
        """
        >>> _disk = Disk.from_text("12345")
        >>> print(_disk.show(max_position=14))
        0..111....22222
        >>> _disk = _disk.compact_one()
        >>> print(_disk.show(max_position=14))
        02.111....2222.
        """
        ids_by_position = {
            position: file.file_id
            for file in self.files
            for position in file.positions
        }
        max_position = max(ids_by_position)
        if debugger.should_report():
            ids_by_position = {
                position: file.file_id
                for file in self.files
                for position in file.positions
            }
            max_position = max(ids_by_position)
            debugger.default_report_if(f"Compacting: {len(ids_by_position)}/{max_position}")
        if len(ids_by_position) == max_position + 1:
            return self
        min_empty_position = min(
            position
            for position in range(max_position + 1)
            if position not in ids_by_position
        )
        max_position_file_id = ids_by_position[max_position]
        max_position_file = self.files[max_position_file_id]
        new_max_position_file = max_position_file.replace(max_position, min_empty_position)
        return self.replace(max_position_file, new_max_position_file)

    def replace(self: Self["Disk"], old_file: "File", new_file: "File") -> Self["Disk"]:
        if old_file not in self.files:
            raise Exception(f"File {old_file.file_id} does not exist")
        if new_file.file_id != old_file.file_id:
            raise Exception(f"Trying to replace #{old_file.file_id} with #{new_file.file_id}")
        files = list(self.files)
        files[old_file.file_id] = new_file
        cls = type(self)
        return cls(files=files)


@dataclass
class DiskCompacter:
    ids_by_position: Dict[int, int]
    max_position: int
    min_empty_position: int

    @classmethod
    def from_disk_text(cls, text: str) -> "DiskCompacter":
        return cls.from_disk(Disk.from_text(text))

    @classmethod
    def from_disk(cls, disk: Disk) -> "DiskCompacter":
        ids_by_position = {
            position: file.file_id
            for file in disk.files
            for position in file.positions
        }
        return cls(ids_by_position=ids_by_position, max_position=max(ids_by_position), min_empty_position=0)

    def __str__(self) -> str:
        return str(self.to_disk())

    def get_min_empty_position(self) -> int:
        for position in range(self.min_empty_position, self.max_position + 2):
            if position not in self.ids_by_position:
                self.min_empty_position = position
                break
        return self.min_empty_position

    def compact(self: Self["DiskCompacter"], debugger: Debugger = Debugger(enabled=False)) -> Self["DiskCompacter"]:
        """
        >>> print(DiskCompacter.from_disk_text("12345").compact())
        022111222
        >>> print(DiskCompacter.from_disk_text("2333133121414131402").compact())
        0099811188827773336446555566
        """
        while debugger.step_if(self.compact_one()):
            if debugger.should_report():
                debugger.default_report_if(f"Compacting: {len(self.ids_by_position)}/{self.max_position}")
        return self

    def compact_one(self) -> bool:
        if len(self.ids_by_position) == self.max_position + 1:
            return False
        min_empty_position = self.get_min_empty_position()
        if min_empty_position > self.max_position:
            return False
        file_id = self.ids_by_position.pop(self.max_position)
        self.ids_by_position[self.min_empty_position] = file_id
        for position in range(self.max_position - 1, self.min_empty_position - 1, -1):
            if position in self.ids_by_position:
                self.max_position = position
                break
        return True

    def to_disk(self) -> Disk:
        by_file_id = lambda position: self.ids_by_position[position]
        positions_by_id = {
            file_id: set(positions)
            for file_id, positions in groupby(sorted(self.ids_by_position, key=by_file_id), key=by_file_id)
        }
        return Disk(files=[
            File(file_id=file_id, positions=positions)
            for file_id, positions in positions_by_id.items()
        ])


@dataclass
class File:
    file_id: int
    positions: Set[int]

    @classmethod
    def from_range(cls, file_id: int, start: int, length: int) -> "File":
        return cls(file_id=file_id, positions=set(range(start, start + length)))

    def replace(self: Self["File"], old_position: int, new_position: int) -> Self["File"]:
        if old_position not in self.positions:
            raise Exception(f"Position {old_position} not in {self}")
        if new_position in self.positions:
            raise Exception(f"Position {new_position} already in {self}")
        cls = type(self)
        positions = self.positions - {old_position} | {new_position}
        # noinspection PyArgumentList
        return cls(file_id=self.file_id, positions=positions)


Challenge.main()
challenge = Challenge()
