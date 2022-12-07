#!/usr/bin/env python3
from abc import ABC

import itertools
from dataclasses import dataclass, field
import re
from typing import Dict, Iterable, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1583951
        """
        root = Parser().parse_output(_input)
        debugger.report(root.get_tree())
        return root.get_total_size_for_directories_with_max_total_size()


class Parser:
    re_cd = re.compile(r"^\$ cd (/|\.\.|\w+)$")
    re_ls = re.compile(r"^\$ ls$")

    def parse_output(self, output: str) -> "Directory":
        """
        >>> _root = Parser().parse_output(
        ...     "$ cd /\\n"
        ...     "$ ls\\n"
        ...     "dir a\\n"
        ...     "14848514 b.txt\\n"
        ...     "8504156 c.dat\\n"
        ...     "dir d\\n"
        ...     "$ cd a\\n"
        ...     "$ ls\\n"
        ...     "dir e\\n"
        ...     "29116 f\\n"
        ...     "2557 g\\n"
        ...     "62596 h.lst\\n"
        ...     "$ cd e\\n"
        ...     "$ ls\\n"
        ...     "584 i\\n"
        ...     "$ cd ..\\n"
        ...     "$ cd ..\\n"
        ...     "$ cd d\\n"
        ...     "$ ls\\n"
        ...     "4060174 j\\n"
        ...     "8033020 d.log\\n"
        ...     "5626152 d.ext\\n"
        ...     "7214296 k"
        ... )
        >>> print(_root.get_tree())
        - / (dir)
          - a (dir)
            - e (dir)
              - i (file, size=584)
            - f (file, size=29116)
            - g (file, size=2557)
            - h.lst (file, size=62596)
          - b.txt (file, size=14848514)
          - c.dat (file, size=8504156)
          - d (dir)
            - d.ext (file, size=5626152)
            - d.log (file, size=8033020)
            - j (file, size=4060174)
            - k (file, size=7214296)
        >>> print("\\n".join(
        ...     f"{_directory.path}: {_directory.get_total_size()}"
        ...     for _directory in _root.directories(
        ...         _sorted=True, recursive=True, include_self=True,
        ...     )
        ... ))
        /: 48381165
        /a/: 94853
        /d/: 24933642
        /a/e/: 584
        >>> print("\\n".join(
        ...     f"{_directory.path}: {_directory.get_total_size()}"
        ...     for _directory
        ...     in _root.get_directories_that_can_free_enough_space()
        ... ))
        /: 48381165
        /d/: 24933642
        >>> _root.get_total_size_for_directories_with_max_total_size()
        95437
        >>> _root.get_smallest_directory_that_can_free_enough_space().path
        '/d/'
        """
        lines = output.strip().splitlines()
        root: Directory = Directory(name="/", parent=None)
        current_directory: Optional[Directory] = None
        listing_directory = False
        for line in lines:
            if match := self.re_cd.match(line):
                if listing_directory:
                    listing_directory = False
                name, = match.groups()
                if name == "/":
                    current_directory = root
                elif name == "..":
                    if not current_directory:
                        raise Exception(
                            f"Not in any directory currently, can't move to "
                            f"parent one"
                        )
                    elif not current_directory.parent:
                        raise Exception(
                            f"Already at root, can't move to parent"
                        )
                    current_directory = current_directory.parent
                else:
                    if name not in current_directory.sub_directories:
                        raise Exception(
                            f"Could not find sub-directory {name} of "
                            f"{current_directory.path}: available ones are "
                            f"{sorted(current_directory.sub_directories)}"
                        )
                    current_directory = current_directory\
                        .sub_directories[name]
            elif self.re_ls.match(line):
                listing_directory = True
            elif File.re_file.match(line):
                if not listing_directory:
                    raise Exception(
                        f"Got a file listing ('{line}') while not in a listing "
                        f"command output"
                    )
                File.from_file_text(line, current_directory)
            elif Directory.re_directory.match(line):
                if not listing_directory:
                    raise Exception(
                        f"Got a directory listing ('{line}') while not in a "
                        f"listing command output"
                    )
                Directory.from_directory_text(line, current_directory)
            else:
                raise Exception(f"Unknown output: '{line}'")

        return root


@dataclass
class Item(ABC):
    name: str
    parent: Optional["Directory"]

    @property
    def path(self) -> str:
        raise NotImplementedError()

    @property
    def root(self) -> "Directory":
        parent = self
        while parent.parent:
            parent = parent.parent
        if not isinstance(parent, Directory):
            raise Exception(f"Item is an orphan")

        return parent

    def get_tree(self, level: int = 0) -> str:
        raise NotImplementedError()

    def get_total_size(self) -> int:
        raise NotImplementedError()


@dataclass
class File(Item):
    size: int

    re_file = re.compile(r"^(\d+) (.*)$")

    @classmethod
    def from_file_text(cls, file_text: str, parent: "Directory") -> "File":
        """
        >>> File.from_file_text("149291 cgc.vzv", Directory.make_root())
        File(name='cgc.vzv', parent=Directory(...), size=149291)
        """
        size_str, name = cls.re_file.match(file_text).groups()
        _file = cls(name=name, size=int(size_str), parent=parent)
        parent.add(_file)
        return _file

    @property
    def path(self) -> str:
        """
        >>> File.from_file_text("149291 cgc.vzv", Directory.make_root()).path
        '/cgc.vzv'
        """
        return f"{self.parent.path}{self.name}"

    def get_tree(self, level: int = 0) -> str:
        return f"{level * 2 * ' '}- {self.name} (file, size={self.size})"

    def get_total_size(self) -> int:
        return self.size


@dataclass
class Directory(Item):
    contents: Dict[str, "File"] = field(default_factory=dict)
    sub_directories: Dict[str, "Directory"] = field(default_factory=dict)

    re_directory = re.compile(r"^dir (.*)$")

    @classmethod
    def make_root(cls) -> "Directory":
        return cls(name="", parent=None)

    @classmethod
    def from_directory_text(
        cls, directory_text: str, parent: "Directory",
    ) -> "Directory":
        """
        >>> Directory.from_directory_text("dir cmcrzdt", Directory.make_root())
        Directory(name='cmcrzdt', parent=Directory(...), contents={},
            sub_directories={})
        """
        name, = cls.re_directory.match(directory_text).groups()
        directory = cls(name=name, parent=parent)
        parent.add(directory)
        return directory

    @property
    def path(self) -> str:
        """
        >>> Directory.make_root().path
        '/'
        >>> Directory\\
        ...     .from_directory_text("dir cmcrzdt", Directory.make_root())\\
        ...     .path
        '/cmcrzdt/'
        """
        if not self.parent:
            return "/"
        return f"{self.parent.path}{self.name}/"

    def __getitem__(self, item_name: str) -> "Item":
        item = self.get(item_name)
        if not item:
            raise KeyError(item_name)
        return item

    def get(
        self, item_name: str, default: "Item" = None,
    ) -> Optional["Item"]:
        return (
            self.contents.get(item_name)
            or self.sub_directories.get(item_name)
            or default
        )

    def items(
        self, _sorted: bool = False, recursive: bool = False,
    ) -> Iterable[Item]:
        items = itertools.chain(
            self.contents.values(),
            self.sub_directories.values(),
        )
        if recursive:
            items = (
                sub_item
                for item in items
                for sub_item in (
                    itertools.chain([item], item.items(recursive=recursive))
                    if isinstance(item, Directory) else
                    [item]
                )
            )
        if _sorted:
            items = sorted(items, key=lambda item: item.name)
        return items

    def directories(
        self, _sorted: bool = False, recursive: bool = False,
        include_self: bool = False,
    ) -> Iterable["Directory"]:
        items = self.items(_sorted=_sorted, recursive=recursive)
        if include_self:
            items = itertools.chain([self], items)
        return (
            item
            for item in items
            if isinstance(item, Directory)
        )

    def add(self, item: "Item") -> "Directory":
        item_name = item.name
        existing: Optional["Item"] = self.get(item_name)
        if existing == item:
            return self
        if existing:
            raise Exception(
                f"Tried to add an item named '{item_name}' to "
                f"{self.parent}, but one existed already"
            )
        if isinstance(item, File):
            self.contents[item_name] = item
        elif isinstance(item, Directory):
            self.sub_directories[item.name] = item
        else:
            raise Exception(f"Unknown item type {type(item_name).__name__}")

        return self

    def get_tree(self, level: int = 0) -> str:
        return "{}\n{}".format(
            f"{level * 2 * ' '}- {self.name if self.parent else '/'} (dir)",
            "\n".join(
                item.get_tree(level=level + 1)
                for item in self.items(_sorted=True)
            )
        )

    def get_total_size(self) -> int:
        return sum(
            item.get_total_size()
            for item in self.items()
        )

    def get_total_size_for_directories_with_max_total_size(
        self, max_size: int = 100000,
    ) -> int:
        return sum(
            directory.get_total_size()
            for directory in self.get_directories_with_max_total_size(max_size)
        )

    def get_directories_with_max_total_size(
        self, max_size: int = 100000, include_self: bool = False,
    ) -> Iterable["Directory"]:
        return (
            directory
            for directory in self.directories(
                _sorted=True, recursive=True, include_self=include_self,
            )
            if directory.get_total_size() <= max_size
        )

    def get_directories_with_min_total_size(
        self, min_size: int = 100000, include_self: bool = False,
    ) -> Iterable["Directory"]:
        return (
            directory
            for directory in self.directories(
                _sorted=True, recursive=True, include_self=include_self,
            )
            if directory.get_total_size() >= min_size
        )

    def get_smallest_directory_that_can_free_enough_space(
        self, total_space: int = 40000000,
    ) -> "Directory":
        directories = self\
            .get_directories_that_can_free_enough_space(total_space)
        return min(
            directories,
            key=lambda directory: directory.get_total_size(),
        )

    def get_directories_that_can_free_enough_space(
        self, total_space: int = 40000000,
    ) -> Iterable["Directory"]:
        root = self.root
        total_size = root.get_total_size()
        min_total_size = total_size - total_space
        return self.get_directories_with_min_total_size(
            min_total_size, include_self=True,
        )


Challenge.main()
challenge = Challenge()
