#!/usr/bin/env python3
import functools
import itertools
import math
import re
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        5966506063747
        """
        return TileSet\
            .from_tiles_text(_input)\
            .to_arrangement()\
            .get_corner_hash()


class TileArrangement:
    size = None
    classes_by_size = {}

    @classmethod
    def of_size(cls, size):
        """
        >>> TileArrangement.of_size(20)([])
        TileArrangementOfSize20
        >>> TileArrangement.of_size(20).size
        20
        """
        if size in cls.classes_by_size:
            return cls.classes_by_size[size]
        _size = size

        class TileArrangementOfSize(cls):
            size = _size

        TileArrangementOfSize.__name__ = f"{cls.__name__}OfSize{size}"
        cls.classes_by_size[size] = TileArrangementOfSize

        return TileArrangementOfSize

    @classmethod
    def from_tile_set(cls, tile_set):
        """
        >>> TileArrangement.from_tile_set(TileSet.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ))
        TileArrangementOfSize1
        >>> TileArrangement.from_tile_set(TileSet.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )).matrix
        [[TileBorderOfSize3(id=2473, ...)]]
        """
        count = len(tile_set.tiles_by_id)
        size = int(math.sqrt(count))
        if size * size != count:
            raise Exception(f"Got non-square number of tiles: {count}")
        if cls.size != size:
            if cls.size is None:
                return cls.of_size(size).from_tile_set(tile_set)
            raise Exception(
                f"Expected {cls.size} ** 2 = {cls.size * cls.size} tiles, but "
                f"got {size}")

        tiles = sorted(tile_set.tiles_by_id.values(), key=lambda tile: tile.id)
        return cls([
            [
                tile.to_border()
                for tile in tiles[start:start + cls.size]
            ]
            for start in range(0, len(tiles), cls.size)
        ])

    def __init__(self, matrix):
        self.matrix = matrix

    def __repr__(self):
        return f"{type(self).__name__}"

    def get_corner_hash(self):
        """
        >>> TileSet.from_tiles_text(
        ...     "Tile 2311:\\n"
        ...     "..##.#..#.\\n"
        ...     "##..#.....\\n"
        ...     "#...##..#.\\n"
        ...     "####.#...#\\n"
        ...     "##.##.###.\\n"
        ...     "##...#.###\\n"
        ...     ".#.#.#..##\\n"
        ...     "..#....#..\\n"
        ...     "###...#.#.\\n"
        ...     "..###..###\\n"
        ...     "\\n"
        ...     "Tile 1951:\\n"
        ...     "#.##...##.\\n"
        ...     "#.####...#\\n"
        ...     ".....#..##\\n"
        ...     "#...######\\n"
        ...     ".##.#....#\\n"
        ...     ".###.#####\\n"
        ...     "###.##.##.\\n"
        ...     ".###....#.\\n"
        ...     "..#.#..#.#\\n"
        ...     "#...##.#..\\n"
        ...     "\\n"
        ...     "Tile 1171:\\n"
        ...     "####...##.\\n"
        ...     "#..##.#..#\\n"
        ...     "##.#..#.#.\\n"
        ...     ".###.####.\\n"
        ...     "..###.####\\n"
        ...     ".##....##.\\n"
        ...     ".#...####.\\n"
        ...     "#.##.####.\\n"
        ...     "####..#...\\n"
        ...     ".....##...\\n"
        ...     "\\n"
        ...     "Tile 1427:\\n"
        ...     "###.##.#..\\n"
        ...     ".#..#.##..\\n"
        ...     ".#.##.#..#\\n"
        ...     "#.#.#.##.#\\n"
        ...     "....#...##\\n"
        ...     "...##..##.\\n"
        ...     "...#.#####\\n"
        ...     ".#.####.#.\\n"
        ...     "..#..###.#\\n"
        ...     "..##.#..#.\\n"
        ...     "\\n"
        ...     "Tile 1489:\\n"
        ...     "##.#.#....\\n"
        ...     "..##...#..\\n"
        ...     ".##..##...\\n"
        ...     "..#...#...\\n"
        ...     "#####...#.\\n"
        ...     "#..#.#.#.#\\n"
        ...     "...#.#.#..\\n"
        ...     "##.#...##.\\n"
        ...     "..##.##.##\\n"
        ...     "###.##.#..\\n"
        ...     "\\n"
        ...     "Tile 2473:\\n"
        ...     "#....####.\\n"
        ...     "#..#.##...\\n"
        ...     "#.##..#...\\n"
        ...     "######.#.#\\n"
        ...     ".#...#.#.#\\n"
        ...     ".#########\\n"
        ...     ".###.#..#.\\n"
        ...     "########.#\\n"
        ...     "##...##.#.\\n"
        ...     "..###.#.#.\\n"
        ...     "\\n"
        ...     "Tile 2971:\\n"
        ...     "..#.#....#\\n"
        ...     "#...###...\\n"
        ...     "#.#.###...\\n"
        ...     "##.##..#..\\n"
        ...     ".#####..##\\n"
        ...     ".#..####.#\\n"
        ...     "#..#.#..#.\\n"
        ...     "..####.###\\n"
        ...     "..#.#.###.\\n"
        ...     "...#.#.#.#\\n"
        ...     "\\n"
        ...     "Tile 2729:\\n"
        ...     "...#.#.#.#\\n"
        ...     "####.#....\\n"
        ...     "..#.#.....\\n"
        ...     "....#..#.#\\n"
        ...     ".##..##.#.\\n"
        ...     ".#.####...\\n"
        ...     "####.#.#..\\n"
        ...     "##.####...\\n"
        ...     "##..#.##..\\n"
        ...     "#.##...##.\\n"
        ...     "\\n"
        ...     "Tile 3079:\\n"
        ...     "#.#.#####.\\n"
        ...     ".#..######\\n"
        ...     "..#.......\\n"
        ...     "######....\\n"
        ...     "####.#..#.\\n"
        ...     ".#...#.##.\\n"
        ...     "#.#####.##\\n"
        ...     "..#.###...\\n"
        ...     "..#.......\\n"
        ...     "..#.###...\\n"
        ... ).to_arrangement().get_corner_hash()
        20899048083289
        """
        borders_by_side = self.group_matrix_by_possible_side()
        borders_by_side_by_id = self.group_borders_by_id(borders_by_side)
        corner_candidates = self.get_corner_candidates(borders_by_side_by_id)
        if len(corner_candidates) != 4:
            raise Exception(
                f"Can only solve if there are exactly 4 corner candidates")

        return functools.reduce(int.__mul__, corner_candidates)

    def get_corner_candidates(self, borders_by_side_by_id):
        return [
            _id
            for _id, neighbours in (
                (_id, functools.reduce(set.__or__, neighbour_map.values()))
                for _id, neighbour_map
                in borders_by_side_by_id.items()
            )
            if len(neighbours) == 2
        ]

    def group_borders_by_id(self, borders_by_side):
        return {
            _id: {
                side: neighbours
                for side, neighbours in (
                    (side, {
                        neighbour
                        for _, _, neighbours in sub_items
                        for neighbour in neighbours
                        if neighbour.id != _id
                    })
                    for side, sub_items in itertools.groupby(sorted(
                        items, key=lambda item: item[1]),
                        key=lambda item: item[1])
                )
                if neighbours
            }
            for _id, items in itertools.groupby(sorted((
                (border.id, side, borders)
                for side, borders in borders_by_side.items()
                for border in borders
            ), key=lambda x: x[0]), key=lambda x: x[0])
        }

    def group_matrix_by_possible_side(self):
        return {
            side: {
                border
                for _, border in items
            }
            for side, items in itertools.groupby(sorted(
                (side, border)
                for row in self.matrix
                for border in row
                for transformed in border.get_all_permutations()
                for side in transformed.sides
            ), key=lambda item: item[0])
        }

    def show_ids(self):
        """
        >>> print(TileArrangement.from_tile_set(TileSet.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )).show_ids())
        2473
        >>> print(TileArrangement.from_tile_set(
        ...     TileSet.from_tiles_text("\\n".join(
        ...         f"Tile {_id}:\\n"
        ...         ".##\\n"
        ...         "#..\\n"
        ...         "#.#\\n"
        ...         "\\n"
        ...         for _id in range(1, 10)
        ...     ))).show_ids())
        1       2       3
        4       5       6
        7       8       9
        """
        return "\n".join(
            "".join(
                "{: <8}".format(border.id)
                for border in row
            )
            for row in self.matrix
        )

    def show(self):
        """
        >>> print(TileArrangement.from_tile_set(TileSet.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )).show())
        .##
        #..
        #.#
        >>> print(TileArrangement.from_tile_set(
        ...     TileSet.from_tiles_text("\\n".join(
        ...         f"Tile {_id}:\\n"
        ...         ".##\\n"
        ...         "#..\\n"
        ...         "#.#\\n"
        ...         "\\n"
        ...         for _id in range(9)
        ...     ))).show())
        .## .## .##
        #.. #.. #..
        #.# #.# #.#
        <BLANKLINE>
        .## .## .##
        #.. #.. #..
        #.# #.# #.#
        <BLANKLINE>
        .## .## .##
        #.. #.. #..
        #.# #.# #.#
        """
        return "\n\n".join(
            self.show_row([
                border.to_tile().show(False)
                for border in row
            ])
            for row in self.matrix
        )

    def show_row(self, tile_show_row):
        """
        >>> print(TileArrangement([]).show_row([]))
        <BLANKLINE>
        >>> print(TileArrangement([]).show_row([Tile.from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False)]))
        .##
        #..
        #.#
        >>> print(TileArrangement([]).show_row([Tile.from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False)] * 3))
        .## .## .##
        #.. #.. #..
        #.# #.# #.#
        """
        return "\n".join(
            " ".join(sub_row)
            for sub_row in zip(*(
                show.splitlines()
                for show in tile_show_row
            ))
        )


class TileSet:
    @classmethod
    def from_tiles_text(cls, tiles_text):
        """
        >>> TileSet.from_tiles_text("").tiles_by_id
        {}
        >>> tile_set_a = TileSet.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )
        >>> tile_set_a.tiles_by_id
        {2473: TileOfSize3(id=2473, points={...(0, 1)...})}
        >>> sorted(tile_set_a.tiles_by_id[2473].points)
        [(0, 1), (0, 2), (1, 0), (2, 0), (2, 2)]
        >>> TileSet.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ...     "\\n"
        ...     "Tile 5:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).tiles_by_id
        {2473: TileOfSize3(id=2473, points={...(0, 1)...}),
            5: TileOfSize3(id=5, points={...(0, 1)...})}
        """
        non_empty_lines = filter(None, tiles_text.strip().split("\n\n"))
        tiles_by_id = {
            tile.id: tile
            for tile in map(Tile.from_tile_text, non_empty_lines)
        }
        sizes = {tile.size for tile in tiles_by_id.values()}
        if len(sizes) > 1:
            raise Exception(f"Got different sizes of tiles: {sorted(sizes)}")
        return cls(tiles_by_id)

    def __init__(self, tiles_by_id):
        self.tiles_by_id = tiles_by_id

    def __repr__(self):
        return f"{type(self).__name__}"

    def to_arrangement(self):
        return TileArrangement.from_tile_set(self)


class Tile(namedtuple("Tile", ("id", "points"))):
    size = None
    classes_by_size = {}
    border_class = NotImplemented
    re_id = re.compile(r"^Tile (\d+):$")

    @classmethod
    def of_size(cls, size):
        """
        >>> Tile.of_size(20)(None, None)
        TileOfSize20(id=None, points=None)
        >>> Tile.of_size(20).size
        20
        >>> Tile.of_size(20).border_class(None, None, None, None, None)
        TileBorderOfSize20(id=None,
            top=None, right=None, bottom=None, left=None)
        """
        if size in cls.classes_by_size:
            return cls.classes_by_size[size]
        _size = size

        class TileOfSize(cls):
            size = _size
            border_class = cls.border_class.of_size(size)

        TileOfSize.__name__ = f"{cls.__name__}OfSize{size}"
        cls.classes_by_size[size] = TileOfSize

        return TileOfSize

    @classmethod
    def from_tile_text(cls, tile_text):
        """
        >>> tile_a = Tile.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )
        >>> tile_a
        TileOfSize3(id=2473, points={...(0, 1)...})
        >>> sorted(tile_a.points)
        [(0, 1), (0, 2), (1, 0), (2, 0), (2, 2)]
        """
        id_line, *pixel_lines = tile_text.strip().splitlines()
        match = cls.re_id.match(id_line)
        if not match:
            raise Exception(f"First line was not about tile id: '{id_line}'")
        _id_str, = match.groups()
        if len(pixel_lines) != cls.size:
            if cls.size is None:
                return cls.of_size(len(pixel_lines)).from_tile_text(tile_text)
            raise Exception(
                f"Expected size of {cls.size} but got height of "
                f"{len(pixel_lines)}")
        lengths = set(map(len, pixel_lines))
        if lengths != {cls.size}:
            if len(lengths) == 1:
                width, = lengths
                raise Exception(
                    f"Expected size of {cls.size} but got width of {width}")
            raise Exception(
                f"Expected size of {cls.size} but got multiple lengths: "
                f"{sorted(lengths)}")
        points = {
            (x, y)
            for y, line in enumerate(pixel_lines)
            for x, spot in enumerate(line)
            if spot == "#"
        }

        return cls(int(_id_str), points)

    @classmethod
    def from_border(cls, border):
        """
        >>> print(Tile.from_border(TileBorder.of_size(4)(
        ...     1, (1, 2), (1, 2), (1, 2), (1, 2))).show())
        Tile 1:
        .##.
        #..#
        #..#
        .##.
        >>> print(Tile.from_border(Tile.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "##.\\n"
        ...     "#.#\\n"
        ... ).to_border()).show())
        Tile 2473:
        .##
        #..
        #.#
        """
        if cls.size != border.size:
            return cls.of_size(border.size).from_border(border)
        return cls(border.id, {
            (x, 0)
            for x in border.top
        } | {
            (cls.size - 1, y)
            for y in border.right
        } | {
            (x, cls.size - 1)
            for x in border.bottom
        } | {
            (0, y)
            for y in border.left
        })

    def to_border(self):
        """
        >>> Tile.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).to_border()
        TileBorderOfSize3(id=2473,
            top=(1, 2), right=(0, 2), bottom=(0, 2), left=(1, 2))
        """
        return self.border_class.from_tile(self)

    def show(self, include_id=True):
        """
        >>> print(Tile.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show())
        Tile 2473:
        .##
        #..
        #.#
        >>> print(Tile.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False))
        .##
        #..
        #.#
        """
        content = "\n".join(
            "".join(
                "#"
                if (x, y) in self.points else
                "."
                for x in range(self.size)
            )
            for y in range(self.size)
        )
        if not include_id:
            return content
        tile_id = f"Tile {self.id}:"
        return f"{tile_id}\n{content}"


class TileBorder(namedtuple(
        "TileBorder", ("id", "top", "right", "bottom", "left"))):
    size = None
    classes_by_size = {}

    @classmethod
    def of_size(cls, size):
        """
        >>> TileBorder.of_size(20)(None, None, None, None, None)
        TileBorderOfSize20(id=None,
            top=None, right=None, bottom=None, left=None)
        >>> TileBorder.of_size(20).size
        20
        """
        if size in cls.classes_by_size:
            return cls.classes_by_size[size]
        _size = size

        class TileBorderOfSize(cls):
            size = _size

        TileBorderOfSize.__name__ = f"{cls.__name__}OfSize{size}"
        cls.classes_by_size[size] = TileBorderOfSize

        return TileBorderOfSize

    @classmethod
    def from_tile(cls, tile):
        """
        >>> TileBorder.from_tile(Tile.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ))
        TileBorderOfSize3(id=2473,
            top=(1, 2), right=(0, 2), bottom=(0, 2), left=(1, 2))
        """
        if cls.size != tile.size:
            return cls.of_size(tile.size).from_tile(tile)
        indexes = range(cls.size)
        last_index = cls.size - 1
        points = tile.points
        # noinspection PyArgumentList
        return cls(
            tile.id,
            tuple(
                x
                for x in indexes
                if (x, 0) in points
            ),
            tuple(
                y
                for y in indexes
                if (last_index, y) in points
            ),
            tuple(
                x
                for x in indexes
                if (x, last_index) in points
            ),
            tuple(
                y
                for y in indexes
                if (0, y) in points
            ),
        )

    def to_tile(self):
        return Tile.from_border(self)

    @property
    def sides(self):
        return {self.top, self.right, self.bottom, self.left}

    def get_all_permutations(self):
        """
        >>> TileBorder.of_size(10)(1, (), (), (), ()).get_all_permutations()
        {TileBorderOfSize10(id=1, top=(), right=(), bottom=(), left=())}
        >>> TileBorder.of_size(2)(1, (0, 1), (0, 1), (0, 1), (0, 1))\\
        ...     .get_all_permutations()
        {TileBorderOfSize2(id=1, top=(0, 1), right=(0, 1), bottom=(0, 1),
            left=(0, 1))}
        >>> actual_b = TileBorder.of_size(10)(
        ...     1, (1, 2), (3, 4), (5, 6), (7, 8)).get_all_permutations()
        >>> expected_b = {
        ...     TileBorder(1, (1, 2), (3, 4), (5, 6), (7, 8)),
        ...     TileBorder(1, (3, 4), (3, 4), (7, 8), (7, 8)),
        ...     TileBorder(1, (3, 4), (1, 2), (7, 8), (5, 6)),
        ...     TileBorder(1, (1, 2), (1, 2), (5, 6), (5, 6)),
        ...     TileBorder(1, (1, 2), (7, 8), (5, 6), (3, 4)),
        ...     TileBorder(1, (7, 8), (3, 4), (3, 4), (7, 8)),
        ...     TileBorder(1, (3, 4), (5, 6), (7, 8), (1, 2)),
        ...     TileBorder(1, (5, 6), (1, 2), (1, 2), (5, 6)),
        ... }
        >>> actual_b - expected_b, expected_b - actual_b
        (set(), set())
        """
        permutations = set()
        rotated = self
        permutations.add(rotated)
        for _ in range(3):
            rotated = rotated.rotate()
            permutations.add(rotated)
        rotated = self.flip()
        permutations.add(rotated)
        for _ in range(3):
            rotated = rotated.rotate()
            permutations.add(rotated)
        return permutations

    def rotate(self):
        """
        >>> TileBorder.of_size(10)(1, (1, 2), (3, 4), (5, 6), (7, 8)).rotate()
        TileBorderOfSize10(id=1,
            top=(3, 4), right=(3, 4), bottom=(7, 8), left=(7, 8))
        """
        cls = type(self)
        return cls(
            self.id,
            self.right,
            self.inverse_side(self.bottom),
            self.left,
            self.inverse_side(self.top),
        )

    def inverse_side(self, side):
        """
        >>> TileBorder.of_size(4)(1, None, None, None, None)\\
        ...     .inverse_side((1, 3))
        (0, 2)
        >>> TileBorder.of_size(4)(1, None, None, None, None)\\
        ...     .inverse_side((0, 3))
        (0, 3)
        >>> TileBorder.of_size(4)(1, None, None, None, None)\\
        ...     .inverse_side((0, 1, 2, 3))
        (0, 1, 2, 3)
        """
        return tuple(sorted(
            self.size - 1 - index
            for index in side
        ))

    def flip(self):
        """
        >>> TileBorder(1, (1, 2), (3, 4), (5, 6), (7, 8)).flip()
        TileBorder(id=1, top=(1, 2), right=(7, 8), bottom=(5, 6), left=(3, 4))
        """
        cls = type(self)
        return cls(self.id, self.top, self.left, self.bottom, self.right)


Tile.border_class = TileBorder


challenge = Challenge()
challenge.main()
