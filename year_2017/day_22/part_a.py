#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Set, Tuple, Dict

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        5460
        """
        return Grid.from_grid_text(_input).step_many(10000).infection_count


@dataclass
class Grid:
    DIRECTION_UP = (0, -1)
    DIRECTION_DOWN = (0, 1)
    DIRECTION_LEFT = (-1, 0)
    DIRECTION_RIGHT = (1, 0)

    STATE_CLEAN = 'clean'
    STATE_INFECTED = 'infected'
    STATES = [STATE_CLEAN, STATE_INFECTED]

    nodes: Dict[utils.Point2D, str]
    position: utils.Point2D = utils.Point2D.ZERO_POINT
    direction: Tuple[int, int] = DIRECTION_UP
    infection_count: int = 0

    DIRECTIONS_CLOCKWISE = [
        DIRECTION_UP,
        DIRECTION_RIGHT,
        DIRECTION_DOWN,
        DIRECTION_LEFT,
    ]

    PARSE_MAP = {
        '.': STATE_CLEAN,
        '#': STATE_INFECTED,
    }

    @classmethod
    def from_grid_text(cls, grid_text, offset=None,
                       position=utils.Point2D.ZERO_POINT,
                       direction=DIRECTION_UP, infection_count=0):
        """
        >>> Grid.from_grid_text('..#\\n#..\\n...')
        Grid(nodes={Point2D(x=1, y=-1): 'infected',
            Point2D(x=-1, y=0): 'infected'}, position=Point2D(x=0, y=0),
            direction=(0, -1), infection_count=0)
        """
        lines = list(grid_text.strip().splitlines())
        extra_characters = set("".join(lines)) - set(cls.PARSE_MAP)
        if extra_characters:
            raise Exception(
                f"Expected only {sorted(cls.PARSE_MAP)}, but also got "
                f"'{sorted(extra_characters)}'")
        x_sizes = set(map(len, lines))
        if len(x_sizes) != 1:
            raise Exception(f"Got different length of lines: {sorted(x_sizes)}")
        x_size, = x_sizes
        y_size = len(lines)
        if offset is None:
            if x_size % 2 != 1 or y_size % 2 != 1:
                raise Exception(
                    f"If a map is of odd size on both axis a position must be "
                    f"provided")
            offset_x = -x_size // 2 + 1
            offset_y = -y_size // 2 + 1
        else:
            offset_x, offset_y = offset
        return cls({
            utils.Point2D(x + offset_x, y + offset_y): cls.PARSE_MAP[content]
            for y, line in enumerate(lines)
            for x, content in enumerate(line)
            if cls.PARSE_MAP[content] != cls.STATE_CLEAN
        }, position, direction, infection_count)

    def __getitem__(self, item):
        if not isinstance(item, utils.Point2D):
            raise ValueError(f"Expected Point2D not {type(item).__name__}")
        return self.nodes.get(item, self.STATE_CLEAN)

    def __setitem__(self, key, value):
        if not isinstance(key, utils.Point2D):
            raise ValueError(f"Expected Point2D not {type(key).__name__}")
        if value not in self.STATES:
            raise ValueError(f"Unknown state '{value}'")
        if value == self.STATE_CLEAN:
            if key in self.nodes:
                del self.nodes[key]
        else:
            self.nodes[key] = value

    def step_many(self, count):
        """
        >>> print(Grid.from_grid_text(
        ...     '..#\\n#..\\n...').step_many(6).show(4, 4, False))
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        . . #[#]. # . . .
        . . # # # . . . .
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        >>> grid = Grid.from_grid_text('..#\\n#..\\n...')
        >>> print(grid.step_many(70).show(4, 4, False))
        . . . . . # # . .
        . . . . # . . # .
        . . . # . . . . #
        . . # . #[.]. . #
        . . # . # . . # .
        . . . . . # # . .
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        >>> grid.infection_count
        41
        >>> Grid.from_grid_text('..#\\n#..\\n...')\\
        ...     .step_many(10000).infection_count
        5587
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> grid = Grid.from_grid_text('..#\\n#..\\n...')
        >>> print(grid.step().show(4, 4))
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        . . . . . # . . .
        . . .<#<# . . . .
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        . . . . . . . . .
        >>> grid.infection_count
        1
        """
        self.direction = self.get_new_direction()
        new_state = self.get_new_state()
        self[self.position] = new_state
        if new_state == self.STATE_INFECTED:
            self.infection_count += 1
        self.position = self.position.offset(self.direction)

        return self

    def get_new_direction(self):
        return self.get_new_direction_for_state(self[self.position])

    def get_new_direction_for_state(self, state):
        if state == self.STATE_INFECTED:
            return self.rotate_direction_right(self.direction)
        elif state == self.STATE_CLEAN:
            return self.rotate_direction_left(self.direction)
        else:
            raise Exception(f"Unknown state '{state}'")

    def get_new_state(self):
        return self.get_new_state_for_state(self[self.position])

    def get_new_state_for_state(self, state):
        if state == self.STATE_INFECTED:
            return self.STATE_CLEAN
        elif state == self.STATE_CLEAN:
            return self.STATE_INFECTED
        else:
            raise Exception(f"Unknown state '{state}'")

    def rotate_direction_left(self, direction):
        return self.DIRECTIONS_CLOCKWISE[
            (self.DIRECTIONS_CLOCKWISE.index(direction) - 1)
            % len(self.DIRECTIONS_CLOCKWISE)]

    def rotate_direction_right(self, direction):
        return self.DIRECTIONS_CLOCKWISE[
            (self.DIRECTIONS_CLOCKWISE.index(direction) + 1)
            % len(self.DIRECTIONS_CLOCKWISE)]

    SHOW_MAP = {
        content: state
        for state, content in PARSE_MAP.items()
    }

    DIRECTION_SHOW_MAP = {
        DIRECTION_UP: ('^', '^'),
        DIRECTION_DOWN: ('v', 'v'),
        DIRECTION_LEFT: ('<', '<'),
        DIRECTION_RIGHT: ('>', '>'),
    }

    def show(self, x_range_or_depth=None, y_range_or_depth=None,
             show_direction=True):
        """
        >>> print(Grid.from_grid_text('..#\\n#..\\n...').show())
        . . #
        #^.^.
        . . .
        """
        x_range = self.get_axis_range(x_range_or_depth, 0, 'X')
        y_range = self.get_axis_range(y_range_or_depth, 1, 'Y')

        return "\n".join(
            "".join(
                (
                    "{{}}{}".format(
                        (
                            self.DIRECTION_SHOW_MAP[self.direction][0]
                            if show_direction else
                            "["
                        ),
                    )
                    if x + 1 in x_range and self.position == (x + 1, y) else
                    "{{}}{}".format(
                        (
                            self.DIRECTION_SHOW_MAP[self.direction][1]
                            if show_direction else
                            "]"
                        ),
                    )
                    if x + 1 in x_range and self.position == (x, y) else
                    "{} "
                    if x + 1 in x_range else
                    "{}"
                ).format(self.SHOW_MAP[self[utils.Point2D(x, y)]])
                for x in x_range
            )
            for y in y_range
        )

    def get_axis_range(self, range_or_depth, index, name):
        if range_or_depth is None:
            _min = min(self.position[index], min(
                (point[index] for point in self.nodes), default=0))
            _max = max(self.position[index], max(
                (point[index] for point in self.nodes), default=0))
            depth = max(abs(_min), abs(_max))
            _range = range(-depth, depth + 1)
        elif isinstance(range_or_depth, int):
            depth = range_or_depth
            _range = range(-depth, depth + 1)
        elif isinstance(range_or_depth, range):
            _range = range_or_depth
        else:
            raise Exception(
                f"{name} range or depth must be a range or an int, not "
                f"{type(range_or_depth)}")
        return _range


Challenge.main()
challenge = Challenge()
