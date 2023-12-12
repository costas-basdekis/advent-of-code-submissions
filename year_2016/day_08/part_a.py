#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from typing import Optional, Type, Dict, Tuple, Generic, List

from utils import BaseChallenge, Cls, Self
from utils.typing_utils import TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        119
        """
        return InstructionSet.result_from_instructions_text(_input)\
            .get_lit_count()


@dataclass
class Screen:
    width: int = 50
    height: int = 6
    contents: Dict[Tuple[int, int], bool] = field(default_factory=dict)

    def __post_init__(self):
        self.adjust_contents()

    def adjust_contents(self):
        """
        >>> Screen(2, 2).contents
        {(0, 0): False, (1, 0): False, (0, 1): False, (1, 1): False}
        >>> # noinspection PyUnresolvedReferences
        >>> Screen(2, 2, {
        ...     (x, y): True for x in range(5) for y in range(1)}).contents
        {(0, 0): True, (1, 0): True, (0, 1): False, (1, 1): False}
        """
        self.contents = {
            (x, y): self.contents.get((x, y), False)
            for y in range(self.height)
            for x in range(self.width)
        }

    def __getitem__(self, item: Tuple[int, int]) -> bool:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> screen = Screen(2, 2, {
        ...     (x, y): True for x in range(5) for y in range(1)})
        >>> screen[(0, 0)]
        True
        >>> screen[(1, 1)]
        False
        >>> screen[(2, 2)]
        Traceback (most recent call last):
        ...
        KeyError: (2, 2)
        """
        return self.contents[item]

    def __setitem__(self, key: Tuple[int, int], value: bool):
        """
        >>> # noinspection PyUnresolvedReferences
        >>> screen = Screen(2, 2, {
        ...     (x, y): True for x in range(5) for y in range(1)})
        >>> screen[(0, 0)] = True
        >>> screen[(0, 0)]
        True
        >>> screen[(1, 1)] = False
        >>> screen[(1, 1)]
        False
        >>> screen[(2, 2)]
        Traceback (most recent call last):
        ...
        KeyError: (2, 2)
        """
        if key not in self.contents:
            raise KeyError(key)

        self.contents[key] = value

    def get_lit_count(self) -> int:
        """
        >>> InstructionSet.from_instructions_text(
        ...     'rect 3x2\\n'
        ...     'rotate column x=1 by 1\\n'
        ...     'rotate row y=0 by 4\\n'
        ...     'rotate column x=1 by 1\\n'
        ... ).apply(Screen(7, 3)).get_lit_count()
        6
        """
        return sum(
            1
            for x in range(self.width)
            for y in range(self.height)
            if self[(x, y)]
        )

    SHOW_MAP = {
        False: '.',
        True: '#',
    }

    def show(self) -> str:
        """
        >>> print("!" + Screen(2, 2).show())
        !..
        ..
        >>> # noinspection PyUnresolvedReferences
        >>> print("!" + Screen(2, 2, {
        ...     (x, y): True for x in range(5) for y in range(1)}).show())
        !##
        ..
        """
        return "\n".join(
            "".join(
                self.SHOW_MAP[self[(x, y)]]
                for x in range(self.width)
            )
            for y in range(self.height)
        )


InstructionT = TV['Instruction']
ScreenT = TV['Screen']


@dataclass
class InstructionSet(Generic[InstructionT, ScreenT]):
    instructions: List[InstructionT]

    @classmethod
    def get_instruction_class(cls) -> Type[InstructionT]:
        return get_type_argument_class(cls, InstructionT)

    @classmethod
    def get_screen_class(cls) -> Type[ScreenT]:
        return get_type_argument_class(cls, ScreenT)

    @classmethod
    def result_from_instructions_text(cls, instructions_text: str) -> ScreenT:
        instruction_set = cls.from_instructions_text(instructions_text)
        return instruction_set.get_variable()

    @classmethod
    def from_instructions_text(
            cls: Cls['InstructionSet'], instructions_text: str,
    ) -> Self['InstructionSet']:
        """
        >>> InstructionSet.from_instructions_text(
        ...     'rect 3x2\\n'
        ...     'rotate column x=1 by 1\\n'
        ...     'rotate row y=0 by 4\\n'
        ... )
        InstructionSet(instructions=[RectInstruction(width=3, height=2),
            RotateColumnInstruction(column=1, offset=1),
            RotateRowInstruction(row=0, offset=4)])
        """
        instruction_class = cls.get_instruction_class()
        return cls(list(map(
            instruction_class.parse, instructions_text.splitlines())))

    def get_result(self) -> ScreenT:
        return self.apply(self.get_screen_class()())

    def apply(self, screen: ScreenT) -> ScreenT:
        """
        >>> print("!" + InstructionSet([]).apply(Screen(3, 3)).show())
        !...
        ...
        ...
        >>> print("!" + InstructionSet.from_instructions_text(
        ...     'rect 3x2\\n'
        ...     'rotate column x=1 by 1\\n'
        ...     'rotate row y=0 by 4\\n'
        ... ).apply(Screen(7, 3)).show())
        !....#.#
        ###....
        .#.....
        >>> print("!" + InstructionSet.from_instructions_text(
        ...     'rect 3x2\\n'
        ...     'rotate column x=1 by 1\\n'
        ...     'rotate row y=0 by 4\\n'
        ...     'rotate column x=1 by 1\\n'
        ... ).apply(Screen(7, 3)).show())
        !.#..#.#
        #.#....
        .#.....
        """
        for instruction in self.instructions:
            instruction.apply(screen)

        return screen


class Instruction:
    name: str = NotImplemented

    instruction_classes: Dict[str, Type['Instruction']] = {}

    @classmethod
    def register(cls, instruction_class: Type['Instruction'],
                 override: bool = False) -> Type['Instruction']:
        name = instruction_class.name
        class_name = instruction_class.__name__
        if name is NotImplemented:
            raise Exception(
                f"Tried to register {class_name}, but it hadn't set the name")
        if not override:
            existing_instruction_class = cls.instruction_classes.get(name)
            if existing_instruction_class:
                raise Exception(
                    f"Tried to register {class_name} under {name}, but "
                    f"{existing_instruction_class.__name__} was already "
                    f"registered")
        cls.instruction_classes[name] = instruction_class
        return instruction_class

    @classmethod
    def parse(cls: Cls['Instruction'], text: str) -> Self['Instruction']:
        """
        >>> Instruction.parse('rect 3x2')
        RectInstruction(width=3, height=2)
        >>> Instruction.parse('rotate column x=1 by 1')
        RotateColumnInstruction(column=1, offset=1)
        >>> Instruction.parse('rotate row y=0 by 4')
        RotateRowInstruction(row=0, offset=4)
        """
        for instruction_class in cls.instruction_classes.values():
            instruction = instruction_class.try_parse(text)
            if instruction:
                return instruction

        raise Exception(f"Could not parse '{text}'")

    @classmethod
    def try_parse(cls: Cls['Instruction'], text: str
                  ) -> Optional[Self['Instruction']]:
        raise NotImplementedError()

    def apply(self, screen: Screen) -> Screen:
        raise NotImplementedError()


@Instruction.register
@dataclass
class RectInstruction(Instruction):
    name = "rect"

    width: int
    height: int

    re_rect = re.compile(r'^rect (\d+)x(\d+)$')

    @classmethod
    def try_parse(cls: Cls['RectInstruction'], text: str
                  ) -> Optional['RectInstruction']:
        """
        >>> RectInstruction.try_parse('rect 3x2')
        RectInstruction(width=3, height=2)
        >>> RectInstruction.try_parse('rotate column x=1 by 1')
        >>> RectInstruction.try_parse('rotate row y=0 by 4')
        """
        match = cls.re_rect.match(text)
        if not match:
            return None

        width_str, height_str = match.groups()
        return cls(int(width_str), int(height_str))

    def apply(self, screen: Screen) -> Screen:
        """
        >>> print(RectInstruction(width=3, height=2).apply(Screen(4, 4)).show())
        ###.
        ###.
        ....
        ....
        """
        for x in range(self.width):
            for y in range(self.height):
                screen[(x, y)] = True

        return screen


@Instruction.register
@dataclass
class RotateColumnInstruction(Instruction):
    name = "rotate-column"

    column: int
    offset: int

    re_rotate_column = re.compile(r'^rotate column x=(\d+) by (\d+)$')

    @classmethod
    def try_parse(cls: Cls['RotateColumnInstruction'], text: str
                  ) -> Optional['RotateColumnInstruction']:
        """
        >>> RotateColumnInstruction.try_parse('rect 3x2')
        >>> RotateColumnInstruction.try_parse('rotate column x=1 by 1')
        RotateColumnInstruction(column=1, offset=1)
        >>> RotateColumnInstruction.try_parse('rotate row y=0 by 4')
        """
        match = cls.re_rotate_column.match(text)
        if not match:
            return None

        column_str, offset_str = match.groups()
        return cls(int(column_str), int(offset_str))

    def apply(self, screen: Screen) -> Screen:
        """
        >>> _screen = Screen(7, 3)
        >>> _ = RectInstruction(width=3, height=2).apply(_screen)
        >>> print(RotateColumnInstruction(
        ...     column=1, offset=1).apply(_screen).show())
        #.#....
        ###....
        .#.....
        """
        x = self.column
        column = [
            screen[(x, y)]
            for y in range(screen.height)
        ]
        for y in range(screen.height):
            screen[(x, y)] = column[(y - self.offset) % screen.height]

        return screen


@Instruction.register
@dataclass
class RotateRowInstruction(Instruction):
    name = "rotate-row"

    row: int
    offset: int

    re_rotate_row = re.compile(r'^rotate row y=(\d+) by (\d+)$')

    @classmethod
    def try_parse(cls: Cls['RotateRowInstruction'], text: str
                  ) -> Optional['RotateRowInstruction']:
        """
        >>> RotateRowInstruction.try_parse('rect 3x2')
        >>> RotateRowInstruction.try_parse('rotate column x=1 by 1')
        >>> RotateRowInstruction.try_parse('rotate row y=0 by 4')
        RotateRowInstruction(row=0, offset=4)
        """
        match = cls.re_rotate_row.match(text)
        if not match:
            return None

        row_str, offset_str = match.groups()
        return cls(int(row_str), int(offset_str))

    def apply(self, screen: Screen) -> Screen:
        """
        >>> _screen = Screen(7, 3)
        >>> _ = RectInstruction(width=3, height=2).apply(_screen)
        >>> _ = RotateColumnInstruction(column=1, offset=1).apply(_screen)
        >>> print("!" + RotateRowInstruction(
        ...     row=0, offset=4).apply(_screen).show())
        !....#.#
        ###....
        .#.....
        """
        y = self.row
        row = [
            screen[(x, y)]
            for x in range(screen.width)
        ]
        for x in range(screen.width):
            screen[(x, y)] = row[(x - self.offset) % screen.width]

        return screen


Challenge.main()
challenge = Challenge()
