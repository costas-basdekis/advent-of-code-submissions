#!/usr/bin/env python3
from abc import ABC
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1956
        """

        return Program.from_program_text(_input).run().manhattan_distance()


class BaseShip:
    position = NotImplemented

    def move(self, delta):
        raise NotImplementedError()

    def move_forward(self, count):
        raise NotImplementedError()

    def rotate(self, quarter_turns):
        raise NotImplementedError()

    def manhattan_distance(self):
        """
        >>> Ship().manhattan_distance()
        0
        >>> Ship((2, 3)).manhattan_distance()
        5
        >>> Ship((-2, 3)).manhattan_distance()
        5
        >>> Ship((2, -3)).manhattan_distance()
        5
        >>> Ship((-2, -3)).manhattan_distance()
        5
        >>> Ship((17, 8)).manhattan_distance()
        25
        """
        x, y = self.position
        return abs(x) + abs(y)


class Ship(namedtuple("Ship", ("position", "direction")), BaseShip):
    DIRECTION_EAST = 'east'
    DIRECTION_WEST = 'west'
    DIRECTION_NORTH = 'north'
    DIRECTION_SOUTH = 'south'

    DIRECTION_SEQUENCE = [
        DIRECTION_EAST,
        DIRECTION_SOUTH,
        DIRECTION_WEST,
        DIRECTION_NORTH,
    ]

    DIRECTION_OFFSET = {
        DIRECTION_EAST: (1, 0),
        DIRECTION_WEST: (-1, 0),
        DIRECTION_SOUTH: (0, 1),
        DIRECTION_NORTH: (0, -1),
    }

    def __new__(cls, *args, **kwargs):
        """
        >>> Ship()
        Ship(position=(0, 0), direction='east')
        >>> Ship(position=(2, 3))
        Ship(position=(2, 3), direction='east')
        >>> Ship((2, 3))
        Ship(position=(2, 3), direction='east')
        >>> Ship(direction='west')
        Ship(position=(0, 0), direction='west')
        """
        if len(args) < 1:
            kwargs.setdefault("position", (0, 0))
        if len(args) < 2:
            kwargs.setdefault("direction", cls.DIRECTION_EAST)
        return super().__new__(cls, *args, **kwargs)

    def move(self, delta):
        """
        >>> Ship().move((2, 3))
        Ship(position=(2, 3), direction='east')
        """
        d_x, d_y = delta
        x, y = self.position
        return self._replace(position=(x + d_x, y + d_y))

    def move_forward(self, count):
        """
        >>> Ship().move_forward(3)
        Ship(position=(3, 0), direction='east')
        >>> Ship(direction=Ship.DIRECTION_NORTH).move_forward(3)
        Ship(position=(0, -3), direction='north')
        >>> Ship(position=(2, 5), direction=Ship.DIRECTION_NORTH).move_forward(3)
        Ship(position=(2, 2), direction='north')
        """
        d_x, d_y = self.DIRECTION_OFFSET[self.direction]
        return self.move((d_x * count, d_y * count))

    def rotate(self, quarter_turns):
        """
        >>> Ship().rotate(1)
        Ship(position=(0, 0), direction='south')
        >>> Ship().rotate(3)
        Ship(position=(0, 0), direction='north')
        >>> Ship((2, 3)).rotate(3)
        Ship(position=(2, 3), direction='north')
        >>> Ship((2, 3), 'west').rotate(3)
        Ship(position=(2, 3), direction='south')
        """
        direction_index = self.DIRECTION_SEQUENCE.index(self.direction)
        new_direction_index = (
            (direction_index + quarter_turns) % len(self.DIRECTION_SEQUENCE)
        )
        new_direction = self.DIRECTION_SEQUENCE[new_direction_index]
        return self._replace(direction=new_direction)


class Program:
    ship_class = Ship

    @classmethod
    def from_program_text(cls, program_text):
        """
        >>> Program.from_program_text(
        ...     "F10\\nN3\\nF7\\nR90\\nF11\\n").instructions
        [GoForward(10), GoNorth(3), GoForward(7), TurnRight(1), GoForward(11)]
        """
        return cls(list(map(
            Instruction.parse, filter(None, program_text.splitlines()))))

    def __init__(self, instructions):
        self.instructions = instructions

    def run(self, ship=None):
        """
        >>> Program.from_program_text(
        ...     "F10\\nN3\\nF7\\nR90\\nF11\\n").run()
        Ship(position=(17, 8), direction='south')
        """
        if ship is None:
            ship = self.ship_class()

        for instruction in self.instructions:
            ship = instruction.step(ship)

        return ship


class Instruction:
    name = NotImplemented

    instruction_classes = {}

    @classmethod
    def register(cls, instruction_class):
        if instruction_class.name is NotImplemented:
            raise Exception(
                f"Tried to register instruction class without name "
                f"{instruction_class.__name__}")
        cls.instruction_classes[instruction_class.name] = instruction_class

        return instruction_class

    @classmethod
    def parse(cls, text):
        for instruction_class in cls.instruction_classes.values():
            instruction = instruction_class.try_parse(text)
            if instruction is not None:
                break
        else:
            raise Exception(f"Could not parse '{text}'")

        return instruction

    @classmethod
    def try_parse(cls, text):
        raise NotImplementedError()

    def step(self, ship):
        raise NotImplementedError()


class SingleLetterSingleNumberInstruction(Instruction, ABC):
    letter = NotImplemented

    @classmethod
    def try_parse(cls, text):
        text = text.strip()
        if text[0] != cls.letter:
            return None
        try:
            value = int(text[1:])
        except ValueError:
            return None

        return cls(cls.pre_process_value(value))

    @classmethod
    def pre_process_value(cls, value):
        return value

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{type(self).__name__}({self.value})"


class MoveInstruction(SingleLetterSingleNumberInstruction, ABC):
    offset = NotImplemented

    def step(self, ship):
        d_x, d_y = self.offset
        return ship.move((d_x * self.value, d_y * self.value))


@Instruction.register
class GoNorth(MoveInstruction):
    """
    >>> GoNorth(3).step(Ship())
    Ship(position=(0, -3), direction='east')
    """
    name = 'go-north'
    letter = 'N'
    offset = (0, -1)


@Instruction.register
class GoSouth(MoveInstruction):
    """
    >>> GoSouth(3).step(Ship())
    Ship(position=(0, 3), direction='east')
    """
    name = 'go-south'
    letter = 'S'
    offset = (0, 1)


@Instruction.register
class GoEast(MoveInstruction):
    """
    >>> GoEast(3).step(Ship())
    Ship(position=(3, 0), direction='east')
    """
    name = 'go-east'
    letter = 'E'
    offset = (1, 0)


@Instruction.register
class GoWest(MoveInstruction):
    """
    >>> GoWest(3).step(Ship())
    Ship(position=(-3, 0), direction='east')
    """
    name = 'go-west'
    letter = 'W'
    offset = (-1, 0)


class TurnInstruction(SingleLetterSingleNumberInstruction, ABC):
    multiplier = NotImplemented

    @classmethod
    def pre_process_value(cls, value):
        if value % 90 != 0:
            raise Exception(f"Value {value} was not a multiple of 90")
        return value // 90

    def step(self, ship):
        return ship.rotate(self.value * self.multiplier)


@Instruction.register
class TurnLeft(TurnInstruction):
    """
    >>> TurnLeft(1).step(Ship())
    Ship(position=(0, 0), direction='north')
    >>> TurnLeft(6).step(Ship())
    Ship(position=(0, 0), direction='west')
    """
    name = 'turn-left'
    letter = 'L'
    multiplier = -1


@Instruction.register
class TurnRight(TurnInstruction):
    """
    >>> TurnRight(1).step(Ship())
    Ship(position=(0, 0), direction='south')
    >>> TurnRight(6).step(Ship())
    Ship(position=(0, 0), direction='west')
    """
    name = 'turn-right'
    letter = 'R'
    multiplier = 1


@Instruction.register
class GoForward(SingleLetterSingleNumberInstruction):
    """
    >>> GoForward(3).step(Ship())
    Ship(position=(3, 0), direction='east')
    """
    name = 'go-forward'
    letter = 'F'

    def step(self, ship):
        return ship.move_forward(self.value)


Challenge.main()
challenge = Challenge()
