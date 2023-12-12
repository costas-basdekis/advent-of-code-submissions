#!/usr/bin/env python3
import string
from dataclasses import dataclass, field
from functools import cached_property
from itertools import product
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, make_and_show_string_table, Direction, sign


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        224326
        """
        return KeypadChain.get_codes_min_total_complexity_from_text(_input)


@dataclass
class KeypadChain:
    keypads: List["Keypad"] = field(default_factory=list)

    @classmethod
    def parse_codes(cls, text: str) -> List[str]:
        return list(map(str.strip, text.strip().splitlines()))

    @classmethod
    def get_codes_min_total_complexity_from_text(cls, text: str, small_count: int = 2) -> int:
        """
        >>> KeypadChain.get_codes_min_total_complexity_from_text('''
        ...     029A
        ...     980A
        ...     179A
        ...     456A
        ...     379A
        ... ''')
        126384
        """
        return cls.default(small_count).get_codes_min_total_complexity(cls.parse_codes(text))

    @classmethod
    def default(cls, small_count: int = 2) -> "KeypadChain":
        return cls().add_large(1).add_small(small_count)

    def add_small(self, count: int = 1) -> "KeypadChain":
        return self.add(*(Keypad.small() for _ in range(count)))

    def add_large(self, count: int = 1) -> "KeypadChain":
        return self.add(*(Keypad.large() for _ in range(count)))

    def add(self, *keypads: "Keypad") -> "KeypadChain":
        self.keypads.extend(keypads)
        return self

    def press(self, keypresses: str) -> str:
        """
        >>> KeypadChain.default().press('<vA<AA>>^AvAA<^A>Av<<A>>^AvA^A<vA>^Av<<A>^A>AAvA^Av<<A>A>^AAAvA<^A>A')
        '029A'
        >>> KeypadChain.default().press("<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A")
        '179A'
        """
        result = keypresses
        for keypad in reversed(self.keypads):
            result = keypad.press(result)
        return result

    def get_keypresses(self, buttons: str) -> str:
        """
        >>> KeypadChain.default().get_keypresses("029A")
        '<vA<AA>>^AvAA<^A>Av<<A>>^AvA^A<vA>^Av<<A>^A>AAvA^Av<<A>A>^AAAvA<^A>A'
        >>> KeypadChain.default().get_keypresses("179A")
        'v<<A>>^A<vA<A>>^AAvAA<^A>Av<<A>>^AAvA^A<vA>^AA<A>Av<<A>A>^AAAvA<^A>A'
        >>> KeypadChain.default().press(KeypadChain.default().get_keypresses("179A"))
        '179A'
        """
        keypad_buttons = buttons
        for keypad in self.keypads:
            keypad_buttons = keypad.get_keypresses(keypad_buttons)
        return keypad_buttons

    def get_shortest_keypresses(self, buttons: str) -> str:
        """
        >>> len(KeypadChain.default().get_shortest_keypresses("029A"))
        68
        >>> KeypadChain.default().press(KeypadChain.default().get_shortest_keypresses("029A"))
        '029A'
        """
        return min(self.get_possible_keypresses(buttons), key=len)

    def get_possible_keypresses(self, buttons: str) -> Iterable[str]:
        """
        >>> min(map(len, KeypadChain.default().get_possible_keypresses("029A")))
        68
        >>> {KeypadChain.default().press(_keypresses) for _keypresses in KeypadChain.default().get_possible_keypresses("029A")}
        {'029A'}
        """
        keypresses_list = [buttons]
        for keypad in self.keypads:
            keypresses_list = [
                next_keypresses
                for keypresses in keypresses_list
                for next_keypresses in keypad.get_possible_keypresses(keypresses)
            ]
        yield from keypresses_list

    def get_codes_min_total_complexity(self, codes: List[str]) -> int:
        """
        >>> KeypadChain.default().get_codes_min_total_complexity(["029A", "980A", "179A", "456A", "379A"])
        126384
        """
        return sum(
            self.get_shortest_code_complexity(code)
            for code in codes
        )

    def get_codes_total_complexity(self, codes: List[str]) -> int:
        """
        >>> KeypadChain.default().get_codes_total_complexity(["029A", "980A", "179A", "456A", "379A"])
        126384
        """
        return sum(
            self.get_code_complexity(code)
            for code in codes
        )

    def get_shortest_code_complexity(self, buttons: str) -> int:
        """
        >>> KeypadChain.default().get_shortest_code_complexity("029A")
        1972
        >>> KeypadChain.default().get_shortest_code_complexity("980A")
        58800
        >>> KeypadChain.default().get_shortest_code_complexity("179A")
        12172
        >>> KeypadChain.default().get_shortest_code_complexity("456A")
        29184
        >>> KeypadChain.default().get_shortest_code_complexity("379A")
        24256
        """
        return self.get_code_complexity(buttons)

    def get_code_complexity(self, buttons: str, keypresses: Optional[str] = None) -> int:
        """
        >>> KeypadChain.default().get_code_complexity("029A")
        1972
        >>> KeypadChain.default().get_code_complexity("980A")
        58800
        >>> KeypadChain.default().get_code_complexity("179A")
        12172
        >>> KeypadChain.default().get_code_complexity("179A", keypresses="<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A")
        12172
        >>> KeypadChain.default().get_code_complexity("456A")
        29184
        >>> KeypadChain.default().get_code_complexity("379A")
        24256
        """
        if keypresses is None:
            keypresses = self.get_shortest_keypresses(buttons)
        length = len(keypresses)
        numeric_part = int("".join(char for char in buttons if char in string.digits))
        return length * numeric_part


@dataclass
class Keypad:
    buttons: Dict[Point2D, str]

    @classmethod
    def small(cls) -> "Keypad":
        """
        >>> print(Keypad.small())
         ^A
        <v>
        """
        return cls.from_rows([[None, "^", "A"], ["<", "v", ">"]])

    @classmethod
    def large(cls) -> "Keypad":
        """
        >>> print(Keypad.large())
        789
        456
        123
         0A
        """
        return cls.from_rows([["7", "8", "9"], ["4", "5", "6"], ["1", "2", "3"], [None, "0", "A"]])

    @classmethod
    def from_rows(cls, rows: List[List[Optional[str]]]) -> "Keypad":
        return cls(buttons={
            Point2D(x, y): char
            for y, row in enumerate(rows)
            for x, char in enumerate(row)
            if char is not None
        })

    def __str__(self) -> str:
        return make_and_show_string_table(self.buttons, get_value=self.show_point)

    def show_point(self, point: Point2D) -> Any:
        return self.buttons.get(point, "")

    @cached_property
    def positions(self) -> Dict[str, Point2D]:
        return {
            button: position
            for position, button in self.buttons.items()
        }

    def press(self, keypresses: str) -> str:
        """
        >>> Keypad.large().press('<A^A>^^AvvvA')
        '029A'
        >>> Keypad.small().press('v<<A>>^A<A>AvA<^AA>A<vAAA>^A')
        '<A^A>^^AvvvA'
        >>> Keypad.small().press('<vA<AA>>^AvAA<^A>A<<vA>>^AvA^A<vA>^A<<vA>^A>AAvA^A<<vA>A>^AAAvA<^A>A')
        Traceback (most recent call last):
        ...
        Exception: There is not button at Point2D(x=0, y=0) (20th keypress)
        >>> Keypad.small().press('<vA<AA>>^AvAA<^A>Av<<A>>^AvA^A<vA>^Av<<A>^A>AAvA^Av<<A>A>^AAAvA<^A>A')
        'v<<A>>^A<A>AvA<^AA>A<vAAA>^A'
        """
        position = self.positions["A"]
        result = ""
        for index, keypress in enumerate(keypresses):
            if keypress == "A":
                result += self.buttons[position]
                continue
            direction = Direction.parse(keypress)
            position = position.offset(direction.offset)
            if position not in self.buttons:
                raise Exception(f"There is not button at {position} ({index + 1}th keypress)")
        return result

    def get_keypresses(self, buttons: str) -> str:
        """
        >>> Keypad.large().get_keypresses("029A")
        '<A^A>^^AvvvA'
        >>> Keypad.small().get_keypresses("<A^A>^^AvvvA")
        'v<<A>>^A<A>AvA<^AA>A<vAAA>^A'
        >>> Keypad.small().get_keypresses("v<<A>>^A<A>AvA<^AA>A<vAAA>^A")
        '<vA<AA>>^AvAA<^A>Av<<A>>^AvA^A<vA>^Av<<A>^A>AAvA^Av<<A>A>^AAAvA<^A>A'
        """
        for keypresses in self.get_possible_keypresses(buttons):
            return keypresses
        raise Exception(f"Could not find keypresses for {buttons}")

    def get_shortest_keypresses(self, buttons: str) -> str:
        """
        >>> len(Keypad.large().get_keypresses("029A"))
        12
        """
        return min(self.get_keypresses(buttons), key=len)

    def get_possible_keypresses(self, buttons: str) -> Iterable[str]:
        """
        >>> list(Keypad.large().get_possible_keypresses("029A"))
        ['<A^A>^^AvvvA', '<A^A^^>AvvvA']
        >>> {Keypad.large().press(keypresses) for keypresses in Keypad.large().get_possible_keypresses("029A")}
        {'029A'}
        """
        for paths in self.get_possible_keypress_paths_list("A", buttons):
            yield "".join(
                "".join(
                    str(direction)
                    for direction in path
                ) + "A"
                for path in paths
            )

    def get_keypress_paths(self, start: str, buttons: str) -> Iterable[List[Direction]]:
        """
        >>> list(Keypad.large().get_keypress_paths("A", "029A"))
        [[Direction.Left], [Direction.Up], [Direction.Right, Direction.Up, Direction.Up], [Direction.Down, Direction.Down, Direction.Down]]
        """
        for keypress_paths in self.get_possible_keypress_paths_list(start, buttons):
            return keypress_paths
        raise Exception(f"Could not find keypresses path for {start} and {buttons}")

    def get_possible_keypress_paths_list(self, start: str, buttons: str) -> Iterable[List[List[Direction]]]:
        """
        >>> list(Keypad.large().get_possible_keypress_paths_list("A", "029A"))
        [[[Direction.Left], [Direction.Up], [Direction.Right, Direction.Up, Direction.Up], [Direction.Down, Direction.Down, Direction.Down]], ...]
        """
        start_position = self.positions[start]
        targets = [self.positions[button] for button in buttons]
        point_paths_list = filter(None, [
            list(self.get_possible_point_paths(source, target))
            for source, target in zip([start_position] + targets, targets)
        ])
        for point_paths_combination in product(*point_paths_list):
            yield list(point_paths_combination)

    def get_point_path(self, source: Point2D, target: Point2D) -> List[Direction]:
        for path in self.get_possible_point_paths(source, target):
            return path
        raise Exception(f"No path from {source} to {target}")

    def get_possible_point_keypresses(self, source_button: str, target_button: str) -> List[str]:
        source = self.positions[source_button]
        target = self.positions[target_button]
        directions_and_counts_lists = self.get_directions_and_counts_list(source, target)
        paths = []
        for directions_and_counts in directions_and_counts_lists:
            path = "".join(map(str, (
                str(direction) * count
                for direction, count in directions_and_counts
            ))) + "A"
            paths.append(path)
        return paths

    def get_possible_point_paths(self, source: Point2D, target: Point2D) -> Iterable[List[Direction]]:
        directions_and_counts_lists = self.get_directions_and_counts_list(source, target)
        for directions_and_counts in directions_and_counts_lists:
            path = [
                direction
                for direction, count in directions_and_counts
                for _ in range(count)
            ]
            position = source
            for direction in path:
                position = position.offset(direction.offset)
                if position not in self.buttons:
                    raise Exception(f"Path {path} is not possible")

            yield path

    def get_directions_and_counts_list(self, source: Point2D, target: Point2D) -> List[List[Tuple[Direction, int]]]:
        if source == target:
            return [[]]
        diff = target.difference(source)
        horizontal_directions_and_counts: List[Tuple[Direction, int]]
        if diff.x != 0:
            horizontal_directions_and_counts = [
                (Direction.from_offset(Point2D(sign(diff.x), 0)), abs(diff.x)),
            ]
        else:
            horizontal_directions_and_counts = []
        vertical_directions_and_counts: List[Tuple[Direction, int]]
        if diff.y != 0:
            vertical_directions_and_counts = [
                (Direction.from_offset(Point2D(0, sign(diff.y))), abs(diff.y)),
            ]
        else:
            vertical_directions_and_counts = []
        if horizontal_directions_and_counts and source.offset(horizontal_directions_and_counts[0][0].offset, factor=horizontal_directions_and_counts[0][1]) in self.buttons:
            horizontal_first_directions_and_counts_lists = [horizontal_directions_and_counts + vertical_directions_and_counts]
        else:
            horizontal_first_directions_and_counts_lists = []
        if vertical_directions_and_counts and source.offset(vertical_directions_and_counts[0][0].offset, factor=vertical_directions_and_counts[0][1]) in self.buttons:
            vertical_first_directions_and_counts_lists = [vertical_directions_and_counts + horizontal_directions_and_counts]
        else:
            vertical_first_directions_and_counts_lists = []
        directions_and_counts_lists = horizontal_first_directions_and_counts_lists + vertical_first_directions_and_counts_lists
        if not directions_and_counts_lists:
            raise Exception(f"No possible paths between {source} and {target}")
        return directions_and_counts_lists


Challenge.main()
challenge = Challenge()
