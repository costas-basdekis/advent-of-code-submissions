#!/usr/bin/env python3
import functools

import utils
from year_2020.day_24 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3937
        """
        return Game.from_paths_text(_input).step_many(100).get_tile_count()


class Game:
    @classmethod
    def from_paths_text(cls, paths_text):
        return cls.from_path_set(part_a.PathSet.from_paths_text(paths_text))

    @classmethod
    def from_path_set(cls, path_set):
        return cls(set(path_set.get_flipped_destinations()))

    def __init__(self, black_tiles):
        self.black_tiles = black_tiles

    def step_many(self, count):
        """
        >>> game_a = Game.from_paths_text(
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
        ... )
        >>> game_a.get_tile_count()
        10
        >>> game_a.step_many(100).get_tile_count()
        2208
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> game_a = Game.from_paths_text(
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
        ... )
        >>> game_a.get_tile_count()
        10
        >>> game_a.step().get_tile_count()
        15
        """
        neighbours = (
            self.black_tiles
            | functools.reduce(set.__or__, map(set, map(
                part_a.Path.get_neighbours, self.black_tiles)))
        )
        self.black_tiles = {
            tile
            for tile in neighbours
            if self.should_exist(tile)
        }

        return self

    def get_tile_count(self):
        return len(self.black_tiles)

    def should_exist(self, tile):
        neighbour_count = self.get_neighbour_count(tile)
        if tile in self.black_tiles:
            return neighbour_count in (1, 2)
        else:
            return neighbour_count == 2

    def get_neighbour_count(self, tile):
        return len(set(part_a.Path.get_neighbours(tile)) & self.black_tiles)


challenge = Challenge()
challenge.main()
