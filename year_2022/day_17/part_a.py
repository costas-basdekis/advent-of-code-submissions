#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Dict, List, Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, Cls, min_and_max_tuples


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        3114
        """
        return Cave\
            .from_winds_text(_input)\
            .process_many_new_rocks(2022)\
            .locked_top_row


@dataclass
class Cave:
    points: Set[Point2D]
    locked_top_row: int
    width: int
    winds: List["Direction"]
    next_wind_index: int
    next_rock_index: int
    active_rock: Optional["Rock"]

    @classmethod
    def from_winds_text(cls, winds_text: str) -> "Cave":
        """
        >>> print(str(Cave.from_winds_text(
        ...     ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")))
        +-------+
        """
        return cls.from_winds(DirectionSet.from_directions_text(winds_text))

    @classmethod
    def from_winds(cls, winds: "DirectionSet") -> "Cave":
        return cls(
            points=set(),
            locked_top_row=0,
            width=7,
            winds=list(winds.directions),
            next_wind_index=0,
            next_rock_index=0,
            active_rock=None,
        )

    def process_many_new_rocks(self, count: int) -> "Cave":
        """
        >>> cave = Cave\\
        ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")
        >>> print(str(cave.process_many_new_rocks(5)))
        |    ## |
        |    ## |
        |    #  |
        |  # #  |
        |  # #  |
        |#####  |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> print(str(cave.process_many_new_rocks(3)))
        |     # |
        |     # |
        |  #### |
        | ###   |
        |  #    |
        | ####  |
        |    ## |
        |    ## |
        |    #  |
        |  # #  |
        |  # #  |
        |#####  |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> print(str(cave.process_many_new_rocks(1)))
        |    #  |
        |    #  |
        |    ## |
        |    ## |
        |  #### |
        | ###   |
        |  #    |
        | ####  |
        |    ## |
        |    ## |
        |    #  |
        |  # #  |
        |  # #  |
        |#####  |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> print(str(cave.process_many_new_rocks(1)))
        |    #  |
        |    #  |
        |    ## |
        |##  ## |
        |###### |
        | ###   |
        |  #    |
        | ####  |
        |    ## |
        |    ## |
        |    #  |
        |  # #  |
        |  # #  |
        |#####  |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> cave = Cave\\
        ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")
        >>> cave.process_many_new_rocks(2022).locked_top_row
        3068
        """
        for _ in range(count):
            self.process_new_rock()
        return self

    def process_new_rock(self) -> "Cave":
        """
        >>> cave = Cave\\
        ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")
        >>> print(str(cave.process_new_rock()))
        |  #### |
        +-------+
        >>> print(str(cave.process_new_rock()))
        |   #   |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> print(str(cave.process_new_rock()))
        |  #    |
        |  #    |
        |####   |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> print(str(cave.process_new_rock()))
        |    #  |
        |  # #  |
        |  # #  |
        |#####  |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        >>> print(str(cave.process_new_rock()))
        |    ## |
        |    ## |
        |    #  |
        |  # #  |
        |  # #  |
        |#####  |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        """
        if self.active_rock:
            raise Exception(
                f"Cannot process a new rock while there is an active one")
        self.add_rock()
        while self.active_rock:
            self.apply_wind_to_rock()
            self.drop_rock()
        return self

    def drop_rock(self) -> "Cave":
        """
        >>> cave = Cave\\
        ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")\\
        ...     .add_rock()
        >>> cave.locked_top_row
        0
        >>> print(str(cave.drop_rock()))
        |  @@@@ |
        |       |
        |       |
        +-------+
        >>> print(str(cave.drop_rock()))
        |  @@@@ |
        |       |
        +-------+
        >>> print(str(cave.drop_rock()))
        |  @@@@ |
        +-------+
        >>> cave.locked_top_row
        0
        >>> cave.active_rock.top
        0
        >>> print(str(cave.drop_rock()))
        |  #### |
        +-------+
        >>> cave.locked_top_row
        1
        >>> print(str(cave.add_rock(0)))
        |   @   |
        |  @@@  |
        |   @   |
        |  #### |
        +-------+
        >>> print(str(cave.drop_rock()))
        |   #   |
        |  ###  |
        |   #   |
        |  #### |
        +-------+
        """
        if not self.active_rock:
            raise Exception(f"There is no active rock to drop")
        if self.active_rock.bottom <= 0:
            return self.lock_active_rock()
        next_active_rock = self.active_rock.offset(Point2D(0, -1))
        if self.intersects_with(next_active_rock):
            return self.lock_active_rock()
        self.active_rock = next_active_rock
        return self

    def lock_active_rock(self) -> "Cave":
        if not self.active_rock:
            raise Exception(f"There's no active rock to lock")
        self.points.update(self.active_rock.points)
        self.locked_top_row = max(self.locked_top_row, self.active_rock.top + 1)
        self.active_rock = None
        return self

    def apply_wind_to_rock(self) -> "Cave":
        """
        >>> cave = Cave\\
        ...     .from_winds_text(">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")\\
        ...     .add_rock()
        >>> print(str(cave.apply_wind_to_rock()))
        |   @@@@|
        |       |
        |       |
        |       |
        +-------+
        """
        if not self.active_rock:
            raise Exception(f"There is no active rock to apply wind to")
        direction = self.winds[self.next_wind_index % len(self.winds)]
        self.next_wind_index += 1
        if direction == Direction.Left:
            if self.active_rock.left <= 0:
                return self
            next_active_rock = self.active_rock.offset(Point2D(-1, 0))
        else:
            if self.active_rock.right >= self.width - 1:
                return self
            next_active_rock = self.active_rock.offset((Point2D(1, 0)))
        if not self.intersects_with(next_active_rock):
            self.active_rock = next_active_rock
        return self

    def add_rock(self, y_offset: int = 3) -> "Cave":
        """
        >>> print(str(Cave.from_winds_text(
        ...     ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>").add_rock()))
        |  @@@@ |
        |       |
        |       |
        |       |
        +-------+
        """
        if self.active_rock:
            raise Exception(f"Can't add rock when there is an active one")
        self.active_rock = Rock.get(self.next_rock_index)\
            .offset(Point2D(2, self.locked_top_row + y_offset))
        self.next_rock_index += 1
        return self

    def __str__(self) -> str:
        points = self.points
        if self.active_rock:
            points = points | self.active_rock.points
        if points:
            _, (_, max_y) = min_and_max_tuples(points)
        else:
            max_y = -1
        return "{}\n{}".format(
            "\n".join(
                "|{}|".format(
                    "".join(
                        "@"
                        if self.active_rock
                        and point in self.active_rock.points else
                        "#"
                        if point in self.points else
                        " "
                        for x in range(0, self.width)
                        for point in [Point2D(x, y)]
                    )
                )
                for y in range(max_y, -1, -1)
            ),
            f"+{'-' * self.width}+",
        )

    def intersects_with(self, rock: "Rock") -> bool:
        return bool(self.points & rock.points)


@dataclass
class DirectionSet:
    directions: List["Direction"]

    @classmethod
    def from_directions_text(cls, directions_text: str) -> "DirectionSet":
        """
        >>> DirectionSet.from_directions_text(
        ...     ">>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>")
        DirectionSet(directions=[Direction.Right, Direction.Right,
            Direction.Right, Direction.Left, ...])
        """
        return cls(
            directions=list(map(
                Direction.from_direction_text,
                directions_text.strip(),
            )),
        )


class Direction(Enum):
    Left = "left"
    Right = "right"

    parse_map: Dict[str, "Direction"]

    @classmethod
    def from_direction_text(cls, direction_text: str) -> "Direction":
        """
        >>> Direction.from_direction_text("<")
        Direction.Left
        >>> Direction.from_direction_text(">")
        Direction.Right
        """
        return cls.parse_map[direction_text]

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


Direction.parse_map = {
    "<": Direction.Left,
    ">": Direction.Right,
}


@dataclass
class Rock:
    points: Set[Point2D]
    height: int
    left: int
    right: int
    top: int
    bottom: int

    DEFAULT_ROCKS: ClassVar[List["Rock"]]

    @classmethod
    def from_rock_text(cls, rock_text: str) -> "Rock":
        """
        >>> print(str(Rock.from_rock_text("####")))
        ####
        >>> print(str(Rock.from_rock_text(".#.\\n###\\n.#.")))
        .#.
        ###
        .#.
        """
        return cls(
            points={
                Point2D(x, y)
                for y, line in enumerate(rock_text.strip().splitlines())
                for x, char in enumerate(line)
                if char == "#"
            },
            height=-1,
            left=-1,
            right=-1,
            top=-1,
            bottom=-1,
        )

    @classmethod
    def get(cls, item: int) -> "Rock":
        """
        >>> print(str(Rock.get(0)))
        ####
        >>> print(str(Rock.get(1)))
        .#.
        ###
        .#.
        >>> print(str(Rock.get(5)))
        ####
        """
        return cls.DEFAULT_ROCKS[item % len(cls.DEFAULT_ROCKS)]

    def __post_init__(self):
        if self.height == -1:
            (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.points)
            self.height = max_y - min_y + 1
            self.left = min_x
            self.right = max_x
            self.top = max_y
            self.bottom = min_y

    def __str__(self, preserve_origin: bool = False) -> str:
        (min_x, min_y), (max_x, max_y) = min_and_max_tuples(self.points)
        if preserve_origin:
            min_x, min_y = 0, 0
        return "\n".join(
            "".join(
                "#"
                if point in self.points else
                "."
                for x in range(min_x, max_x + 1)
                for point in [Point2D(x, y)]
            )
            for y in range(max_y, min_y - 1, -1)
        )

    def offset(self, offset: Point2D) -> "Rock":
        """
        >>> print(Rock.get(0).offset(
        ...     Point2D(1, 1)).__str__(preserve_origin=True))
        .####
        .....
        """
        cls: Cls["Rock"] = type(self)
        # noinspection PyArgumentList
        return cls(
            points={
                point.offset(offset)
                for point in self.points
            },
            height=self.height,
            left=self.left + offset.x,
            right=self.right + offset.x,
            top=self.top + offset.y,
            bottom=self.bottom + offset.y,
        )


Rock.DEFAULT_ROCKS = [
    Rock.from_rock_text("####"),
    Rock.from_rock_text(".#.\n###\n.#."),
    Rock.from_rock_text("###\n..#\n..#"),
    Rock.from_rock_text("#\n#\n#\n#"),
    Rock.from_rock_text("##\n##"),
]


Challenge.main()
challenge = Challenge()
