#!/usr/bin/env python3
import functools
import sys

import utils


sys.setrecursionlimit(3000)


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Part.from_instruction_text(Challenge().input).show(True) \\
        ...     == Challenge().input.strip()
        True
        >>> Challenge().default_solve()
        3835
        """
        return Area.from_instruction_text(_input).get_largest_room_distance()


class Area:
    MOVEMENT_NORTH = 'N'
    MOVEMENT_WEST = 'W'
    MOVEMENT_SOUTH = 'S'
    MOVEMENT_EAST = 'E'
    MOVEMENT_BRANCH_START = 'branch-start'
    MOVEMENT_BRANCH_END = 'branch-end'

    @classmethod
    def from_instruction_text(cls, instruction_text):
        """
        >>> {
        ...     point: sorted(connections)
        ...     for point, connections
        ...     in Area.from_instruction_text("^WNE$").connections.items()
        ... }
        {(0, 0): [(-1, 0)], (-1, 0): [(-1, -1), (0, 0)],
            (-1, -1): [(-1, 0), (0, -1)], (0, -1): [(-1, -1)]}
        """
        part = Part.from_instruction_text(instruction_text)
        return cls.from_iterating_part(part)

    @classmethod
    def from_iterating_part(cls, part):
        return cls.from_movements(part.iterate_movement())

    @classmethod
    def from_movements(cls, movements, start=(0, 0)):
        position = start
        stack = []
        connections = {}
        for movement in movements:
            if movement == cls.MOVEMENT_BRANCH_START:
                stack.append(position)
                continue
            elif movement == cls.MOVEMENT_BRANCH_END:
                if not stack:
                    raise Exception(f"Got too many branch end movements")
                position = stack.pop()
                continue

            next_position = cls.get_next_position(position, movement)
            connections.setdefault(position, set()).add(next_position)
            connections.setdefault(next_position, set()).add(position)

            position = next_position

        if stack:
            raise Exception(
                f"Got {len(stack)} unmatched branch start movements")

        return cls(connections)

    OFFSET_MAP = {
        MOVEMENT_NORTH: (0, -1),
        MOVEMENT_SOUTH: (0, 1),
        MOVEMENT_WEST: (-1, 0),
        MOVEMENT_EAST: (1, 0),
    }

    @classmethod
    def get_next_position(cls, position, movement):
        """
        >>> Area.get_next_position((0, 0), 'N')
        (0, -1)
        >>> Area.get_next_position((-2, 3), 'W')
        (-3, 3)
        """
        offset_x, offset_y = cls.OFFSET_MAP[movement]
        x, y = position
        return x + offset_x, y + offset_y

    def __init__(self, connections):
        self.connections = connections

    def get_largest_room_distance(self, start=(0, 0)):
        """
        >>> Area.from_instruction_text("^WNE$").get_largest_room_distance()
        3
        >>> Area.from_instruction_text("^ENWWW(NEEE|SSE(EE|N))$")\\
        ...     .get_largest_room_distance()
        10
        >>> Area.from_instruction_text(
        ...     "^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$")\\
        ...     .get_largest_room_distance()
        18
        >>> Area.from_instruction_text(
        ...     "^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$")\\
        ...     .get_largest_room_distance()
        23
        >>> Area.from_instruction_text(
        ...     "^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS"
        ...     "(E|SS))))$").get_largest_room_distance()
        31
        """
        distances = self.get_room_distances(start)
        return max(distances.values())

    def get_room_distances(self, start=(0, 0)):
        distances = {start: 0}
        stack = [start]
        while stack:
            position = stack.pop(0)
            distance = distances[position]
            next_distance = distance + 1
            for next_position in self.connections[position]:
                if next_position in distances:
                    continue
                distances[next_position] = next_distance
                stack.append(next_position)

        return distances

    def show(self):
        """
        >>> print(Area.from_instruction_text("^WNE$").show())
        #####
        #.|.#
        #-###
        #.|X#
        #####
        >>> print(Area.from_instruction_text("^ENWWW(NEEE|SSE(EE|N))$").show())
        #########
        #.|.|.|.#
        #-#######
        #.|.|.|.#
        #-#####-#
        #.#.#X|.#
        #-#-#####
        #.|.|.|.#
        #########
        >>> print(Area.from_instruction_text(
        ...     "^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$").show())
        ###########
        #.|.#.|.#.#
        #-###-#-#-#
        #.|.|.#.#.#
        #-#####-#-#
        #.#.#X|.#.#
        #-#-#####-#
        #.#.|.|.|.#
        #-###-###-#
        #.|.|.#.|.#
        ###########
        >>> print(Area.from_instruction_text(
        ...     "^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$").show())
        #############
        #.|.|.|.|.|.#
        #-#####-###-#
        #.#.|.#.#.#.#
        #-#-###-#-#-#
        #.#.#.|.#.|.#
        #-#-#-#####-#
        #.#.#.#X|.#.#
        #-#-#-###-#-#
        #.|.#.|.#.#.#
        ###-#-###-#-#
        #.|.#.|.|.#.#
        #############
        >>> print(Area.from_instruction_text(
        ...     "^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS"
        ...     "(E|SS))))$").show())
        ###############
        #.|.|.|.#.|.|.#
        #-###-###-#-#-#
        #.|.#.|.|.#.#.#
        #-#########-#-#
        #.#.|.|.|.|.#.#
        #-#-#########-#
        #.#.#.|X#.|.#.#
        ###-#-###-#-#-#
        #.|.#.#.|.#.|.#
        #-###-#####-###
        #.|.#.|.|.#.#.#
        #-#-#####-#-#-#
        #.#.|.|.|.#.|.#
        ###############
        """
        min_x = min(x for x, _ in self.connections)
        max_x = max(x for x, _ in self.connections)
        min_y = min(y for _, y in self.connections)
        max_y = max(y for _, y in self.connections)

        width = max_x - min_x + 1

        xs = range(min_x, max_x + 1)
        ys = range(min_y, max_y + 1)

        return "{}\n{}\n{}".format(
            "#" * (width * 2 + 1),
            "\n".join([
                self.show_horizontal_line(ys[0], xs)
            ] + sum((
                [
                    self.show_vertical_line(y, xs),
                    self.show_horizontal_line(y, xs),
                ]
                for y in ys[1:]
            ), [])),
            "#" * (width * 2 + 1),
        )

    def show_horizontal_line(self, y, xs):
        return "#{}{}#".format(
            "X" if (xs[0], y) == (0, 0) else ".",
            "".join(
                "{}{}".format(
                    (
                        "|"
                        if self.are_connected((x - 1, y), (x, y)) else
                        "#"
                    ),
                    "X" if (x, y) == (0, 0) else ".",
                )
                for x in xs[1:]
            ),
        )

    def show_vertical_line(self, y, xs):
        return "#{}#".format(
            "#".join(
                (
                    "-"
                    if self.are_connected((x, y - 1), (x, y)) else
                    "#"
                )
                for x in xs
            ),
        )

    def are_connected(self, lhs, rhs):
        return lhs in self.connections.get(rhs, set())


class Part:
    MOVEMENT_NORTH = Area.MOVEMENT_NORTH
    MOVEMENT_WEST = Area.MOVEMENT_WEST
    MOVEMENT_SOUTH = Area.MOVEMENT_SOUTH
    MOVEMENT_EAST = Area.MOVEMENT_EAST
    MOVEMENT_BRANCH_START = Area.MOVEMENT_BRANCH_START
    MOVEMENT_BRANCH_END = Area.MOVEMENT_BRANCH_END

    CHARACTER_OPEN_PAREN = '('
    CHARACTER_CLOSE_PAREN = ')'
    CHARACTER_PIPE = '|'

    DIRECTION_CHARACTERS = {
        MOVEMENT_NORTH,
        MOVEMENT_SOUTH,
        MOVEMENT_WEST,
        MOVEMENT_EAST,
    }
    PARENTHESIS_CHARACTERS = {
        CHARACTER_OPEN_PAREN,
        CHARACTER_CLOSE_PAREN,
    }
    ALL_CHARACTERS = (
        DIRECTION_CHARACTERS
        | PARENTHESIS_CHARACTERS
        | {CHARACTER_PIPE}
    )

    TYPE_LITERAL = 'literal'
    TYPE_PARENTHESIS = 'parenthesis'
    TYPE_PIPE = 'pipe'

    PIPE_DELIMITER = (TYPE_PIPE, None, None)

    @classmethod
    def from_instruction_text(cls, instruction_text):
        """
        >>> print(Part.from_instruction_text("^$").show(True))
        ^$
        >>> print(Part.from_instruction_text("^SW$").show(True))
        ^SW$
        >>> print(Part.from_instruction_text("^S|W|$").show(True))
        ^S|W|$
        >>> print(Part.from_instruction_text("^S|W(NN)E$").show(True))
        ^S|W(NN)E$
        >>> print(Part.from_instruction_text("^N(W|)S$").show(True))
        ^N(W|)S$
        """
        content = cls.get_content(instruction_text)
        parts_contents = cls.split_content(content)
        return cls.construct_part(
            (cls.TYPE_PARENTHESIS, parts_contents, {'enclose': False}))

    @classmethod
    def get_content_max_depth(cls, part_content):
        stack = [(0, part_content)]
        max_depth = 0
        while stack:
            depth, content = stack.pop(0)
            _type, sub_contents, _ = content
            if _type == cls.TYPE_LITERAL:
                continue
            elif _type == cls.TYPE_PARENTHESIS:
                if depth + 1 > max_depth:
                    max_depth = depth + 1
                for sub_content in sub_contents:
                    stack.append((depth + 1, sub_content))
            elif _type == cls.TYPE_PIPE:
                continue
            else:
                raise Exception(f"Unknown type encountered: {_type}")

        return max_depth

    @classmethod
    def construct_part(cls, part_content):
        """
        >>> Part.construct_part(('parenthesis', (
        ...     ('literal', ('N',), None),
        ...     ('parenthesis', (('literal', ('W', 'S'), None),),
        ...      {'enclose': False}),
        ...     ('literal', ('E',), None),
        ... ), {'enclose': False}))
        SeriesPart((LiteralPart(('N',)), SeriesPart((LiteralPart(('W', 'S')),)),
            LiteralPart(('E',))))
        >>> Part.construct_part(('parenthesis', (
        ...     ('literal', ('N',), None),
        ...     ('parenthesis', (
        ...         ('literal', ('W',), None),
        ...         ('parenthesis', (
        ...             ('literal', ('N', 'W', 'S'), None),
        ...             ('pipe', None, None),
        ...             ('literal', ('S', 'E'), None),
        ...         ), {'enclose': True}),
        ...         ('pipe', None, None),
        ...         ('literal', ('S',), None),
        ...     ), {'enclose': True}),
        ...     ('literal', ('E',), None),
        ... ), {'enclose': False}))
        SeriesPart((LiteralPart(('N',)),
            ChoicesPart((SeriesPart((LiteralPart(('W',)),
                ChoicesPart((LiteralPart(('N', 'W', 'S')),
                    LiteralPart(('S', 'E')))))),
                LiteralPart(('S',)))),
            LiteralPart(('E',))))
        >>> Part.construct_part((
        ...     'parenthesis', Part.split_content("N(W|)S"), {'enclose': False}))
        SeriesPart((LiteralPart(...), ChoicesPart(...), LiteralPart(...)))
        """
        _type, content, options = part_content
        if _type == cls.TYPE_PARENTHESIS and cls.PIPE_DELIMITER in content:
            _type = cls.TYPE_PIPE
            content = tuple(
                sub_part[0]
                if len(sub_part) == 1 else
                (cls.TYPE_PARENTHESIS, tuple(sub_part), {'enclose': False})
                for sub_part
                in cls.split_sequence(content, cls.PIPE_DELIMITER)
            )
            options = {'enclose': options['enclose']}

        if _type == cls.TYPE_PARENTHESIS:
            if options is None:
                raise Exception(
                    f"Expected options but got None: {part_content}")
            return SeriesPart.from_content(content, options)
        elif _type == cls.TYPE_PIPE:
            return ChoicesPart.from_content(content, options)
        elif _type == cls.TYPE_LITERAL:
            return LiteralPart.from_content(content, options)
        else:
            raise Exception(f"Unknown part type encountered: {_type}")

    @classmethod
    def split_sequence(cls, sequence, needle):
        """
        >>> Part.split_sequence(['a', 1, 'b', 'c', 1, 'd', 1, 1], 1)
        [['a'], ['b', 'c'], ['d'], [], []]
        """
        if not sequence:
            return []
        parts = [[]]
        for item in sequence:
            if item == needle:
                parts.append([])
                continue
            parts[-1].append(item)

        return parts

    @classmethod
    def from_content(cls, contents, options):
        raise NotImplementedError()

    @classmethod
    def split_content(cls, content):
        """
        >>> Part.split_content("NWSE")
        (('literal', ('N', 'W', 'S', 'E'), None),)
        >>> Part.split_content("N(WS)E")
        (('literal', ('N',), None),
            ('parenthesis', (('literal', ('W', 'S'), None),), {'enclose': True}),
            ('literal', ('E',), None))
        >>> Part.split_content("NW|SE")
        (('literal', ('N', 'W'), None),
            ('pipe', None, None), ('literal', ('S', 'E'), None))
        >>> Part.split_content("NW|")
        (('literal', ('N', 'W'), None), ('pipe', None, None))
        >>> Part.split_content("NW|NW|SE")
        (('literal', ('N', 'W'), None), ('pipe', None, None),
            ('literal', ('N', 'W'), None),
            ('pipe', None, None), ('literal', ('S', 'E'), None))
        >>> Part.split_content("N(W|S)E")
        (('literal', ('N',), None),
            ('parenthesis', (('literal', ('W',), None), ('pipe', None, None),
                ('literal', ('S',), None)), {'enclose': True}),
            ('literal', ('E',), None))
        >>> Part.split_content("N(W(NWS|SE)|S)E")
        (('literal', ('N',), None),
            ('parenthesis', (('literal', ('W',), None),
                ('parenthesis', (('literal', ('N', 'W', 'S'), None),
                    ('pipe', None, None),
                    ('literal', ('S', 'E'), None)), {'enclose': True}),
                ('pipe', None, None),
                ('literal', ('S',), None)), {'enclose': True}),
            ('literal', ('E',), None))
        >>> Part.split_content("N(W(NWS|SE)|S)E") == (
        ...     ('literal', ('N',), None),
        ...     ('parenthesis', (
        ...         ('literal', ('W',), None),
        ...         ('parenthesis', (
        ...             ('literal', ('N', 'W', 'S'), None),
        ...             ('pipe', None, None),
        ...             ('literal', ('S', 'E'), None),
        ...         ), {'enclose': True}),
        ...         ('pipe', None, None),
        ...         ('literal', ('S',), None),
        ...     ), {'enclose': True}),
        ...     ('literal', ('E',), None),
        ... )
        True
        """
        sub_parts = []
        stack = []
        for position, character in enumerate(content):
            if character in cls.DIRECTION_CHARACTERS:
                if sub_parts:
                    last_type, last_content, options = sub_parts[-1]
                    if last_type == cls.TYPE_LITERAL:
                        last_content += (character,)
                        sub_parts.pop()
                    else:
                        last_type = cls.TYPE_LITERAL
                        last_content = (character,)
                        options = None
                else:
                    last_type = cls.TYPE_LITERAL
                    last_content = (character,)
                    options = None
                sub_parts.append((last_type, last_content, options))
            elif character == cls.CHARACTER_OPEN_PAREN:
                stack.append(sub_parts)
                sub_parts = []
            elif character == cls.CHARACTER_CLOSE_PAREN:
                if not stack:
                    raise Exception(
                        f"Got mismatched closing parenthesis at {position}")
                last_type = cls.TYPE_PARENTHESIS
                last_content = tuple(sub_parts)
                options = {'enclose': True}
                sub_parts = stack.pop()
                sub_parts.append((last_type, last_content, options))
            elif character == cls.CHARACTER_PIPE:
                sub_parts.append(cls.PIPE_DELIMITER)
            else:
                raise Exception(f"Unhandled character encountered: {character}")

        if stack:
            raise Exception(f"{len(stack)} parentheses are not closed")

        return tuple(sub_parts)

    @classmethod
    def get_content(cls, instruction_text):
        """
        >>> Part.get_content("^NWSE$")
        'NWSE'
        """
        instruction_text = instruction_text.strip()
        if not instruction_text:
            raise Exception(f"Empty part given")
        if not instruction_text.startswith('^') \
                or not instruction_text.endswith('$'):
            raise Exception(
                f"Part needs to start with '^' and end with '$' not "
                f"'{instruction_text[0]}' and '{instruction_text[1]}' "
                f"({instruction_text[:5]}...{instruction_text[-5:]})")
        content = instruction_text[1:-1]
        unknown_characters = set(content) - cls.ALL_CHARACTERS
        if unknown_characters:
            raise Exception(
                f"Unknown characters for part: {sorted(unknown_characters)}")
        return content

    def show(self, is_top_part=False):
        raise NotImplementedError()

    def get_path_count(self):
        raise NotImplementedError()

    def iterate_movement(self):
        raise NotImplementedError()


class LiteralPart(Part):
    @classmethod
    def from_content(cls, contents, options):
        """
        >>> LiteralPart.from_content(('N', 'W', 'S', 'E'), None)
        LiteralPart(('N', 'W', 'S', 'E'))
        """
        return cls(contents)

    def __init__(self, movements):
        self.movements = movements

    def __repr__(self):
        return f"{type(self).__name__}({self.movements})"

    def get_path_count(self):
        return 1

    def show(self, is_top_part=False):
        """
        >>> print(LiteralPart(()).show(True))
        ^$
        >>> print(LiteralPart(('W', 'E')).show(True))
        ^WE$
        """
        text = "".join(self.movements)
        if is_top_part:
            text = f"^{text}$"

        return text

    def iterate_movement(self):
        """
        >>> list(Part.from_instruction_text("^NWSE$").iterate_movement())
        ['N', 'W', 'S', 'E']
        """
        yield from self.movements


class SeriesPart(Part):
    @classmethod
    def from_content(cls, contents, options):
        """
        >>> SeriesPart.from_content((), {'enclose': False})
        SeriesPart(())
        >>> SeriesPart.from_content((
        ...     ('literal', ('N', 'W', 'S', 'E'), None),
        ...     ('literal', ('S', 'W', 'N', 'E'), None),
        ... ), {'enclose': False})
        SeriesPart((LiteralPart(('N', 'W', 'S', 'E')),
            LiteralPart(('S', 'W', 'N', 'E'))))
        """
        if options is None:
            raise Exception(f"Expected options but got None: {contents}")
        return cls(
            tuple(map(cls.construct_part, contents)), options['enclose'])

    def __init__(self, parts, enclose=False):
        self.parts = parts
        self.enclose = enclose

    def __repr__(self):
        return (
            f"{type(self).__name__}({self.parts}"
            f"{', enclose=True' if self.enclose else ''})"
        )

    def get_path_count(self):
        """
        >>> Part.from_instruction_text("^N(W|E)S$").get_path_count()
        2
        >>> Part.from_instruction_text("^N(W|E|S)S(W|S|E)$").get_path_count()
        9
        >>> Part.from_instruction_text("^N(W|(W|S)|S)S(W|S|E)$").get_path_count()
        12
        """
        return functools.reduce(int.__mul__, (
            part.get_path_count()
            for part in self.parts
        ), 1)

    def show(self, is_top_part=False):
        """
        >>> print(SeriesPart(()).show(True))
        ^$
        >>> print(SeriesPart((LiteralPart(('W',)),
        ...     LiteralPart(('E',)))).show(True))
        ^WE$
        >>> print(SeriesPart((LiteralPart(('W',)),
        ...     SeriesPart((LiteralPart(('E',)),), True))).show(True))
        ^W(E)$
        """
        text = "".join(part.show() for part in self.parts)
        if is_top_part:
            text = f"^{text}$"
        elif self.enclose:
            text = f"({text})"

        return text

    def iterate_movement(self):
        """
        >>> list(Part.from_instruction_text("^W(E)S$").iterate_movement())
        ['W', 'E', 'S']
        """
        for part in self.parts:
            yield from part.iterate_movement()


class ChoicesPart(Part):
    @classmethod
    def from_content(cls, contents, options):
        """
        >>> ChoicesPart.from_content((), {'enclose': True})
        ChoicesPart(())
        >>> ChoicesPart.from_content((
        ...     ('literal', ('N', 'W', 'S', 'E'), None),
        ...     ('literal', ('S', 'W', 'N', 'E'), None),
        ... ), {'enclose': True})
        ChoicesPart((LiteralPart(('N', 'W', 'S', 'E')),
            LiteralPart(('S', 'W', 'N', 'E'))))
        """
        return cls(tuple(map(cls.construct_part, contents)), options['enclose'])

    def __init__(self, parts, enclose=True):
        self.parts = parts
        self.enclose = enclose

    def __repr__(self):
        return (
            f"{type(self).__name__}"
            f"({self.parts}{', enclose=False' if not self.enclose else ''})"
        )

    def get_path_count(self):
        """
        >>> Part.from_instruction_text("^W|E|$").get_path_count()
        3
        >>> Part.from_instruction_text("^W|(W|ES)|$").get_path_count()
        4
        """
        return sum(
            part.get_path_count()
            for part in self.parts
        )

    def show(self, is_top_part=False):
        """
        >>> print(ChoicesPart(()).show(True))
        ^$
        >>> print(ChoicesPart((LiteralPart(('W',)),
        ...     LiteralPart(('E',)))).show(True))
        ^W|E$
        >>> print(ChoicesPart((LiteralPart(('W',)),
        ...     SeriesPart((LiteralPart(('E',)),), True))).show(True))
        ^W|(E)$
        >>> print(ChoicesPart((LiteralPart(('W',)),
        ...     SeriesPart((LiteralPart(('E',)),), True))).show())
        (W|(E))
        >>> print(ChoicesPart((LiteralPart(('W',)),
        ...     SeriesPart((LiteralPart(('E',)),), True)), False).show())
        W|(E)
        """
        text = "|".join(part.show() for part in self.parts)
        if is_top_part:
            text = f"^{text}$"
        elif self.enclose:
            text = f"({text})"

        return text

    def iterate_movement(self):
        """
        >>> list(Part.from_instruction_text(
        ...     "^N(W|(S|E)|)NW$").iterate_movement())
        ['N',
            'branch-start', 'W', 'branch-end',
            'branch-start',
                'branch-start', 'S', 'branch-end',
                'branch-start', 'E', 'branch-end',
            'branch-end',
            'branch-start', 'branch-end',
            'N',
            'W']
        """
        for part in self.parts:
            yield self.MOVEMENT_BRANCH_START
            yield from part.iterate_movement()
            yield self.MOVEMENT_BRANCH_END


Challenge.main()
challenge = Challenge()
