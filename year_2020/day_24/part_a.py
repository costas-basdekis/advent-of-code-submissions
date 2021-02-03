#!/usr/bin/env python3
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        375
        """
        return PathSet.from_paths_text(_input).get_black_count()


class PathSet:
    @classmethod
    def from_paths_text(cls, paths_text):
        """
        >>> PathSet.from_paths_text(
        ...     "sesenw\\n"
        ...     "neeene\\n"
        ...     "seswne\\n"
        ... )
        PathSet([Path(('se', 'se', 'nw')), Path(('ne', 'e', 'e', 'ne')),
            Path(('se', 'sw', 'ne'))])
        """
        non_emtpy_lines = filter(None, paths_text.splitlines())
        return cls(list(map(Path.from_path_text, non_emtpy_lines)))

    def __init__(self, paths):
        self.paths = paths

    def __repr__(self):
        return f"{type(self).__name__}({self.paths})"

    def get_black_count(self, start=(0, 0)):
        """
        >>> PathSet.from_paths_text(
        ...     "sesenwnenenewseeswwswswwnenewsewsw\\n"
        ...     "neeenesenwnwwswnenewnwwsewnenwseswesw\\n"
        ...     "seswneswswsenwwnwse\\n"
        ...     "nwnwneseeswswnenewneswwnewseswneseene\\n"
        ...     "swweswneswnenwsewnwneneseenw\\n"
        ...     "eesenwseswswnenwswnwnwsewwnwsene\\n"
        ...     "sewnenenenesenwsewnenwwwse\\n"
        ...     "wenwwweseeeweswwwnwwe\\n"
        ...     "wsweesenenewnwwnwsenewsenwwsesesenwne\\n"
        ...     "neeswseenwwswnwswswnw\\n"
        ...     "nenwswwsewswnenenewsenwsenwnesesenew\\n"
        ...     "enewnwewneswsewnwswenweswnenwsenwsw\\n"
        ...     "sweneswneswneneenwnewenewwneswswnese\\n"
        ...     "swwesenesewenwneswnwwneseswwne\\n"
        ...     "enesenwswwswneneswsenwnewswseenwsese\\n"
        ...     "wnwnesenesenenwwnenwsewesewsesesew\\n"
        ...     "nenewswnwewswnenesenwnesewesw\\n"
        ...     "eneswnwswnwsenenwnwnwwseeswneewsenese\\n"
        ...     "neswnwewnwnwseenwseesewsenwsweewe\\n"
        ...     "wseweeenwnesenwwwswnew\\n"
        ... ).get_black_count()
        10
        """
        flipped_destinations = self.get_flipped_destinations(start)
        return len(flipped_destinations)

    def get_flipped_destinations(self, start=(0, 0)):
        destinations = self.get_destinations(start)
        flip_counts = {
            destination: len(list(items))
            for destination, items in itertools.groupby(sorted(destinations))
        }
        return [
            destination
            for destination in destinations
            if flip_counts[destination] % 2 == 1
        ]

    def get_destinations(self, start=(0, 0)):
        """
        >>> PathSet.from_paths_text(
        ...     "sesenwnenenewseeswwswswwnenewsewsw\\n"
        ...     "neeenesenwnwwswnenewnwwsewnenwseswesw\\n"
        ...     "seswneswswsenwwnwse\\n"
        ...     "nwnwneseeswswnenewneswwnewseswneseene\\n"
        ...     "swweswneswnenwsewnwneneseenw\\n"
        ...     "eesenwseswswnenwswnwnwsewwnwsene\\n"
        ...     "sewnenenenesenwsewnenwwwse\\n"
        ...     "wenwwweseeeweswwwnwwe\\n"
        ...     "wsweesenenewnwwnwsenewsenwwsesesenwne\\n"
        ...     "neeswseenwwswnwswswnw\\n"
        ...     "nenwswwsewswnenenewsenwsenwnesesenew\\n"
        ...     "enewnwewneswsewnwswenweswnenwsenwsw\\n"
        ...     "sweneswneswneneenwnewenewwneswswnese\\n"
        ...     "swwesenesewenwneswnwwneseswwne\\n"
        ...     "enesenwswwswneneswsenwnewswseenwsese\\n"
        ...     "wnwnesenesenenwwnenwsewesewsesesew\\n"
        ...     "nenewswnwewswnenesenwnesewesw\\n"
        ...     "eneswnwswnwsenenwnwnwwseeswneewsenese\\n"
        ...     "neswnwewnwnwseenwseesewsenwsweewe\\n"
        ...     "wseweeenwnesenwwwswnew\\n"
        ... ).get_destinations()
        [(-2, 2), (-1, -3), (-2, 3), ...]
        """
        return [
            path.get_destination(start)
            for path in self.paths
        ]


class Path:
    DIRECTION_OFFSETS = {
        0: {
            'e': (1, 0),
            'se': (0, 1),
            'ne': (0, -1),
            'w': (-1, 0),
            'nw': (-1, -1),
            'sw': (-1, 1),
        },
        1: {
            'e': (1, 0),
            'se': (1, 1),
            'ne': (1, -1),
            'w': (-1, 0),
            'nw': (0, -1),
            'sw': (0, 1),
        },
    }
    INSTRUCTIONS = sorted(DIRECTION_OFFSETS[0])

    @classmethod
    def from_path_text(cls, path_text):
        """
        >>> Path.from_path_text("esenee")
        Path(('e', 'se', 'ne', 'e'))
        """
        instruction_path = ()
        while path_text:
            instruction = path_text[:2]
            if instruction not in cls.DIRECTION_OFFSETS[0]:
                instruction = path_text[:1]
                if instruction not in cls.DIRECTION_OFFSETS[0]:
                    raise Exception(
                        f"Unknown instruction '{instruction}', expected one "
                        f"of {', '.join(cls.INSTRUCTIONS)}")
            instruction_path += (instruction,)
            path_text = path_text[len(instruction):]

        return cls(instruction_path)

    @classmethod
    def add(cls, lhs, rhs):
        """
        >>> Path.add((0, 0), (0, 0))
        (0, 0)
        >>> Path.add((1, -2), (-3, 4))
        (-2, 2)
        """
        l_x, l_y = lhs
        r_x, r_y = rhs

        return l_x + r_x, l_y + r_y

    def __init__(self, direction_path):
        self.direction_path = direction_path

    def __repr__(self):
        return f"{type(self).__name__}({self.direction_path})"

    def get_destination(self, start=(0, 0)):
        """
        >>> Path.from_path_text("").get_destination()
        (0, 0)
        >>> Path.from_path_text("esenee").get_destination()
        (3, 0)
        >>> Path.from_path_text("esew").get_destination()
        (0, 1)
        >>> Path.from_path_text("nwwswee").get_destination()
        (0, 0)
        """
        position = start
        for instruction in self.direction_path:
            position = self.get_neighbour(position, instruction)

        return position

    @classmethod
    def get_neighbours(cls, position):
        return [
            cls.get_neighbour(position, instruction)
            for instruction in cls.INSTRUCTIONS
        ]

    @classmethod
    def get_neighbour(cls, position, instruction):
        _, y = position
        offset = cls.DIRECTION_OFFSETS[y % 2][instruction]
        position = cls.add(position, offset)

        return position


Challenge.main()
challenge = Challenge()
