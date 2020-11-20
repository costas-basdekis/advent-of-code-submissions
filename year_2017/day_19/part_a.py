#!/usr/bin/env python3
import itertools
import string

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        42
        """
        return Diagram.from_diagram_text(_input).get_collected_word()


class Diagram:
    CONTENT_HORIZONTAL = '-'
    CONTENT_VERTICAL = '|'
    CONTENT_TURN = '+'
    CONTENT_LETTERS = list(string.ascii_uppercase)
    CONTENTS = [
        CONTENT_HORIZONTAL,
        CONTENT_VERTICAL,
        CONTENT_TURN,
    ] + CONTENT_LETTERS
    SPACE = ' '

    @classmethod
    def from_diagram_text(cls, diagram_text):
        """
        >>> diagram = Diagram.from_diagram_text(
        ...     "     |          \\n"
        ...     "     |  +--+    \\n"
        ...     "     A  |  C    \\n"
        ...     " F---|----E|--+ \\n"
        ...     "     |  |  |  D \\n"
        ...     "     +B-+  +--+ \\n"
        ... )
        >>> diagram.start_point
        Point2D(x=5, y=0)
        >>> sorted(diagram.letters.values())
        ['A', 'B', 'C', 'D', 'E', 'F']
        """
        lines = diagram_text.strip('\n').splitlines()
        contents = {
            utils.Point2D(x, y): content
            for y, line in enumerate(lines)
            for x, content in enumerate(line)
            if cls.check_content(content)
        }
        neighbours = {
            point: cls.get_neighbours(contents, point)
            for point in contents
        }
        letters = {
            point: content
            for point, content in contents.items()
            if content in cls.CONTENT_LETTERS
        }
        start_points = {
            point
            for point in neighbours
            if point.y == 0
        }
        if not start_points:
            raise Exception(
                f"Could not find start point, min y was "
                f"{min(point.y for point in neighbours)}")
        if len(start_points) > 1:
            raise Exception(f"Expected a single start point but got "
                            f"{len(start_points)}: {sorted(start_points)}")
        start_point, = start_points

        return cls(neighbours, letters, start_point)

    @classmethod
    def get_neighbours(cls, contents, point):
        content = contents[point]
        neighbours = {
            neighbour
            for neighbour in point.get_manhattan_neighbours()
            if neighbour in contents
        }
        horizontal_neighbours = {
            point.offset((-1, 0)),
            point.offset((1, 0)),
        }
        vertical_neighbours = {
            point.offset((0, -1)),
            point.offset((0, 1)),
        }
        is_horizontal = horizontal_neighbours.issubset(neighbours)
        is_vertical = vertical_neighbours.issubset(neighbours)
        if content == cls.CONTENT_HORIZONTAL:
            if not is_horizontal \
                    and not neighbours.issubset(horizontal_neighbours):
                raise Exception(
                    f"Expected two horizontal neighbours around '{content}' in "
                    f"{point} but it didn't, it's neighbours were {neighbours}")
            elif is_vertical and is_horizontal:
                return neighbours
            return neighbours & horizontal_neighbours
        elif content == cls.CONTENT_VERTICAL:
            if not is_vertical and not neighbours.issubset(vertical_neighbours):
                raise Exception(
                    f"Expected two vertical neighbours around '{content}' in "
                    f"{point} but it didn't, it's neighbours were {neighbours}")
            elif is_vertical and is_horizontal:
                return neighbours
            return neighbours & vertical_neighbours
        elif content == cls.CONTENT_TURN:
            if len(neighbours) != 2:
                raise Exception(
                    f"Expected 2 neighbours around '{content}' in {point}, but "
                    f"got {len(neighbours)}")
            if is_horizontal or is_vertical:
                raise Exception(
                    f"Expected turn to be neither "
                    f"horizontal{'(it was)' if is_horizontal else ''} nor "
                    f"vertical{'(it was)' if is_vertical else ''}, it's "
                    f"neighbours were {neighbours}")
            return neighbours
        elif content in cls.CONTENT_LETTERS:
            if len(neighbours) == 1:
                return neighbours
            if len(neighbours) != 2:
                raise Exception(
                    f"Expected 2 neighbours around '{content}' in {point}, but "
                    f"got {len(neighbours)}")
            if not is_horizontal and not is_vertical:
                raise Exception(
                    f"Expected letter '{content}; in {point} to be part of "
                    f"either a horizontal or a vertical line, but it was "
                    f"neither, it had neighbours {neighbours}")
            elif is_horizontal and is_vertical:
                raise Exception(
                    f"Expected letter '{content}; in {point} to be part of "
                    f"either a horizontal or a vertical line, but it was "
                    f"both, it had neighbours {neighbours}")
            if is_horizontal:
                return horizontal_neighbours
            else:
                return vertical_neighbours
        else:
            raise Exception(f"Unexpected content '{content}'")

    @classmethod
    def check_content(cls, content):
        if content == cls.SPACE:
            return False
        if content in cls.CONTENTS:
            return True

        raise Exception(f"Got unexpected content '{content}'")

    def __init__(self, neighbours, letters, start_point):
        self.neighbours = neighbours
        self.letters = letters
        self.start_point = start_point

    def get_collected_word(self):
        """
        >>> Diagram.from_diagram_text(
        ...     "     |          \\n"
        ...     "     |  +--+    \\n"
        ...     "     A  |  C    \\n"
        ...     " F---|----E|--+ \\n"
        ...     "     |  |  |  D \\n"
        ...     "     +B-+  +--+ \\n"
        ... ).get_collected_word()
        'ABCDEF'
        """
        packet = Packet(self)
        packet.step_many()
        return "".join(packet.collected_letters)


class Packet:
    @classmethod
    def from_diagram_text(cls, diagram_text):
        """
        >>> Packet.from_diagram_text(
        ...     "     |          \\n"
        ...     "     |  +--+    \\n"
        ...     "     A  |  C    \\n"
        ...     " F---|----E|--+ \\n"
        ...     "     |  |  |  D \\n"
        ...     "     +B-+  +--+ \\n"
        ... )
        Packet(None -> Point2D(x=5, y=0), [])
        """
        diagram = Diagram.from_diagram_text(diagram_text)
        return cls(diagram)

    def __init__(self, diagram, position=None, previous_position=None,
                 collected_letters=()):
        if position is None:
            if previous_position is not None:
                raise Exception(
                    f"Cannot set previous position if position is not set")
            position = diagram.start_point
            previous_position = None
        elif previous_position is not None:
            if previous_position not in diagram.neighbours[position]:
                raise Exception(
                    f"Previous position {previous_position} is not a neighbour "
                    f"of {position}")
        else:
            if len(diagram.neighbours[position]) != 1:
                raise Exception(
                    f"Need to set previous position for {position} since it "
                    f"has more than 1 neighbours")
        self.diagram = diagram
        self.position = position
        self.previous_position = previous_position
        self.collected_letters = list(collected_letters)

    def __repr__(self):
        return (
            f"{type(self).__name__}("
            f"{self.previous_position} -> {self.position}, "
            f"{self.collected_letters}"
            f")"
        )

    def step_many(self, count=None):
        """
        >>> packet = Packet.from_diagram_text(
        ...     "     |          \\n"
        ...     "     |  +--+    \\n"
        ...     "     A  |  C    \\n"
        ...     " F---|----E|--+ \\n"
        ...     "     |  |  |  D \\n"
        ...     "     +B-+  +--+ \\n"
        ... )
        >>> packet.step_many()
        True
        >>> packet
        Packet(Point2D(x=2, y=3) -> Point2D(x=1, y=3),
            ['A', 'B', 'C', 'D', 'E', 'F'])
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        for _ in steps:
            finished = self.step()
            if finished:
                break
        else:
            finished = False

        return finished

    def step(self):
        """
        >>> packet = Packet.from_diagram_text(
        ...     "     |          \\n"
        ...     "     |  +--+    \\n"
        ...     "     A  |  C    \\n"
        ...     " F---|----E|--+ \\n"
        ...     "     |  |  |  D \\n"
        ...     "     +B-+  +--+ \\n"
        ... )
        >>> packet.step()
        False
        >>> packet
        Packet(Point2D(x=5, y=0) -> Point2D(x=5, y=1), [])
        """
        next_position = self.get_next_position()
        if next_position is None:
            return True
        self.previous_position, self.position = self.position, next_position
        letter = self.diagram.letters.get(self.position)
        if letter:
            self.collected_letters += letter

        return False

    def get_next_position(self):
        neighbours = self.diagram.neighbours[self.position]
        if self.previous_position is None:
            next_neighbours = neighbours - {self.position}
        else:
            next_neighbours = \
                neighbours - {self.position, self.previous_position}
        if not next_neighbours:
            return None
        elif len(next_neighbours) > 1:
            if not self.previous_position:
                raise Exception(
                    f"Got too many next neighbours ({len(next_neighbours)}) at "
                    f"{self.position} (previous was {self.previous_position}): "
                    f"{next_neighbours}")
            direction = self.position.difference(self.previous_position)
            expected_next_neighbour = self.position.offset(direction)
            if expected_next_neighbour not in next_neighbours:
                raise Exception(
                    f"Got too many next neighbours ({len(next_neighbours)}) at "
                    f"{self.position} (previous was {self.previous_position}): "
                    f"{next_neighbours}")
            next_neighbours = {expected_next_neighbour}
        next_position, = next_neighbours

        return next_position


challenge = Challenge()
challenge.main()
