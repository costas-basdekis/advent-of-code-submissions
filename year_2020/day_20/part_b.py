#!/usr/bin/env python3
import itertools
import math

import utils
from year_2020.day_20 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1714
        """
        tile_border_arrangement = TileBorderArrangementExtended.from_tile_set(
            TileSetExtended.from_tiles_text(_input))
        tile_border_arrangement.solve_arrangement()
        tile_arrangement = TileArrangement\
            .from_tile_border_arrangement(tile_border_arrangement)
        big_tile = tile_arrangement.to_tile()
        monster = big_tile.parse_pattern(
            "                  # \n"
            "#    ##    ##    ###\n"
            " #  #  #  #  #  #   \n"
        )
        monsters, permutation = big_tile\
            .find_single_permutation_with_pattern(monster)
        return len(permutation.points - monsters)


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
        >>> TileArrangement.from_tile_set(TileSetExtended.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ))
        TileArrangementOfSize1
        >>> TileArrangement.from_tile_set(TileSetExtended.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )).matrix
        [[TileExtendedOfSize3(id=2473, ...)]]
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
                tile
                for tile in tiles[start:start + cls.size]
            ]
            for start in range(0, len(tiles), cls.size)
        ])

    @classmethod
    def from_tile_border_arrangement(cls, tile_border_arrangement):
        return cls([
            [
                tile_border_arrangement.tiles_by_id[border.id]
                .orient_with_border(border)
                for border in row
            ]
            for row in tile_border_arrangement.matrix
        ])

    def __init__(self, matrix):
        self.matrix = matrix

    def __repr__(self):
        return f"{type(self).__name__}"

    def to_tile(self):
        return TileExtended\
            .from_tile_text(f"Tile 1:\n{self.show_borderless()}")

    def show_borderless(self):
        """
        >>> print(TileArrangement.from_tile_set(TileSetExtended.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )).show_borderless())
        .
        >>> print("!", TileArrangement.from_tile_set(
        ...     TileSetExtended.from_tiles_text("\\n".join(
        ...         f"Tile {_id}:\\n"
        ...         ".##\\n"
        ...         "#..\\n"
        ...         "#.#\\n"
        ...         "\\n"
        ...         for _id in range(9)
        ...     ))).show_borderless())
        ! ...
        ...
        ...
        """
        return "\n".join(
            self.show_borderless_row([
                tile.show(False)
                for tile in row
            ])
            for row in self.matrix
        )

    def show_borderless_row(self, tile_show_row):
        """
        >>> print(TileArrangement([]).show_borderless_row([]))
        <BLANKLINE>
        >>> print(TileArrangement([]).show_borderless_row([TileExtended.from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False)]))
        .
        >>> print("!", TileArrangement([]).show_borderless_row([TileExtended.from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False)] * 3))
        ! ...
        """
        return "\n".join([
            "".join(sub_line[1:-1] for sub_line in sub_row)
            for sub_row in zip(*(
                show.splitlines()
                for show in tile_show_row
            ))
        ][1:-1])

    def show(self):
        """
        >>> print(TileArrangement.from_tile_set(TileSetExtended.from_tiles_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... )).show())
        .##
        #..
        #.#
        >>> print(TileArrangement.from_tile_set(
        ...     TileSetExtended.from_tiles_text("\\n".join(
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
                tile.show(False)
                for tile in row
            ])
            for row in self.matrix
        )

    def show_row(self, tile_show_row):
        """
        >>> print(TileArrangement([]).show_row([]))
        <BLANKLINE>
        >>> print(TileArrangement([]).show_row([TileExtended.from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False)]))
        .##
        #..
        #.#
        >>> print(TileArrangement([]).show_row([TileExtended.from_tile_text(
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


class TileBorderArrangementExtended(part_a.TileBorderArrangement):
    classes_by_size = {}

    def __init__(self, matrix, tiles_by_id):
        super().__init__(matrix, tiles_by_id)
        self.borders_by_id = {
            border.id: border
            for row in self.matrix
            for border in row
        }

    def solve_arrangement(self):
        unique_border_sides = {
            (name, side, transformed)
            for border in self.borders_by_id.values()
            for transformed in border.get_all_permutations()
            for (name, side) in transformed.named_sides
        }
        borders_by_named_side = {
            key: {
                border
                for _, _, border in items
            }
            for key, items in itertools.groupby(
                sorted(unique_border_sides),
                key=lambda item: (item[0], item[1]))
        }
        neighbours_by_named_side_by_id = {
            border.id: {
                name: {
                    transformed
                    for transformed
                    in borders_by_named_side.get((
                        TileBorderExtended.OPPOSITE_SIDE_MAP[name], side),
                        set())
                    if transformed.id != border.id
                }
                for (name, side) in (
                    ('top', border.top),
                    ('right', border.right),
                    ('bottom', border.bottom),
                    ('left', border.left),
                )
            }
            for border in self.borders_by_id.values()
        }
        self.check_solubility_with_counts(neighbours_by_named_side_by_id)
        matrix = []
        while len(matrix) < self.size:
            row = []
            matrix.append(row)
            if len(matrix) < 2:
                a_corner = self.get_a_corner(neighbours_by_named_side_by_id)
                first_item = a_corner
            else:
                first_item = self.get_next_item_for_matrix(
                    matrix, borders_by_named_side)
            oriented_first_item = self.orient_item_for_matrix(
                first_item, matrix, borders_by_named_side)
            row.append(oriented_first_item)
            self.check_matrix_last_item_fitness(matrix)
            while len(row) < self.size:
                next_item = self.get_next_item_for_matrix(
                    matrix, borders_by_named_side)
                row.append(next_item)
                self.check_matrix_last_item_fitness(matrix)

        self.matrix = matrix

    def get_next_item_for_matrix(self, matrix, borders_by_named_side):
        row = matrix[-1]
        if len(matrix) > 1:
            row_above = matrix[-2]
            item_above = row_above[len(row)]
            candidates_above = \
                borders_by_named_side[('top', item_above.bottom)]
        else:
            candidates_above = None
        if len(row) > 0:
            item_before = row[-1]
            candidates_before = \
                borders_by_named_side[('left', item_before.right)]
        else:
            candidates_before = None

        if candidates_above is not None and candidates_before is not None:
            candidates = candidates_above & candidates_before
        elif candidates_above is not None:
            candidates = candidates_above
        elif candidates_before is not None:
            candidates = candidates_before
        else:
            raise Exception(f"Use `get_a_corner` to get a corner")

        matrix_ids = {
            border.id
            for border in sum(matrix, [])
        }
        candidates = {
            candidate
            for candidate in candidates
            if candidate.id not in matrix_ids
        }

        if not candidates:
            # import ipdb;ipdb.set_trace()
            raise Exception(
                f"Could not find candidates for "
                f"({len(row) + 1}, {len(matrix)}): "
                f"{candidates_above} {candidates_before}")
        if len(candidates) > 1:
            # import ipdb;ipdb.set_trace()
            raise Exception(
                f"Too many candidates for "
                f"({len(row) + 1}, {len(matrix)}): {len(candidates)} "
                f"{candidates_above} {candidates_before}")
        candidate, = candidates

        return candidate

    def check_matrix_last_item_fitness(self, matrix):
        row = matrix[-1]
        item = row[-1]
        if len(matrix) > 1:
            row_above = matrix[-2]
            item_above = row_above[len(row) - 1]
            if item.top != item_above.bottom:
                raise Exception(
                    f"Item on ({len(row)}, {len(matrix)}) ({item}) doesn't "
                    f"fit with item above ({item_above})")
        if len(row) > 1:
            item_before = row[-2]
            if item.left != item_before.right:
                raise Exception(
                    f"Item on ({len(row)}, {len(matrix)}) ({item}) doesn't "
                    f"fit with item before ({item_before})")

    def orient_item_for_matrix(self, item, matrix, borders_by_named_side):
        if len(matrix) < 2:
            item_above = None
        else:
            row_above = matrix[-2]
            first_item_above = row_above[0]
            item_above = first_item_above
        row = matrix[-1]
        if len(row) < 1:
            item_before = None
        else:
            item_before = row[-1]

        def get_other_item(name, side):
            others = {
                border
                for border
                in borders_by_named_side[(name, side)]
                if border.id != item.id
            }
            if not others:
                return None
            other, = others
            return other

        orientations = [
            transformed
            for transformed in item.get_all_permutations()
            if (
                get_other_item('bottom', transformed.top) == item_above
            )
            and (
                get_other_item('right', transformed.left) == item_before
            )
        ]
        if not orientations:
            raise Exception(
                f"Cannot orient new item at position "
                f"({len(row) + 1}, {len(matrix)}) "
                f"\n{item}\nabove is {item_above}\nbefore is {item_before}")
        if not item_above and not item_before:
            if len(orientations) != 2:
                raise Exception(
                    f"Expected 2 orientations for top left corner, but found "
                    f"{len(orientations)}")
        else:
            if len(orientations) > 1:
                raise Exception(
                    f"Expected 1 orientation for item, but found "
                    f"{len(orientations)}")
        oriented_item = orientations[0]

        return oriented_item

    def get_a_corner(self, neighbours_by_named_side_by_id):
        corner_candidates = (
            _id
            for _id, neighbours_map
            in neighbours_by_named_side_by_id.items()
            if sum(
                1
                for neighbours in neighbours_map.values()
                if {
                    neighbour.id
                    for neighbour in neighbours
                }
            ) == 2
        )
        a_corner_id = next(corner_candidates)
        a_corner = self.borders_by_id[a_corner_id]
        return a_corner

    def check_solubility_with_counts(self, neighbours_by_named_side_by_id):
        neighbour_candidate_counts = {
            len({
                neighbour.id
                for neighbour in neighbours
            })
            for neighbours_map in neighbours_by_named_side_by_id.values()
            for neighbours in neighbours_map.values()
        }
        if neighbour_candidate_counts != {0, 1}:
            raise Exception(
                f"Cannot solve arrangement, as neighbour candidates are not "
                f"unique: {sorted(neighbour_candidate_counts)}")
        neighbour_count_counts = {
            count: len(list(items))
            for count, items in itertools.groupby(sorted(
                sum(
                    1
                    for neighbours in neighbours_map.values()
                    if {
                        neighbour.id
                        for neighbour in neighbours
                    }
                )
                for neighbours_map in neighbours_by_named_side_by_id.values()
            ))
        }
        if neighbour_count_counts.get(2, 0) != 4:
            raise Exception(
                f"Cannot solve arrangement, as there are not exactly 4 corner "
                f"candidates: there are {neighbour_count_counts.get(2, 0)}")
        if neighbour_count_counts.get(3, 0) != (self.size - 2) * 4:
            raise Exception(
                f"Cannot solve arrangement, as there are not exactly "
                f"{(self.size - 2) * 4} side  candidates: there are "
                f"{neighbour_count_counts.get(3, 0)}")
        if neighbour_count_counts.get(4, 0) != (self.size - 2) ** 2:
            raise Exception(
                f"Cannot solve arrangement, as there are not exactly "
                f"{(self.size - 2) ** 2} inner  candidates: there are "
                f"{neighbour_count_counts.get(4, 0)}")


class TileSetExtended(part_a.TileSet):
    pass


class TileExtended(part_a.Tile):
    classes_by_size = {}

    @classmethod
    def parse_pattern(cls, text, use='#'):
        """
        >>> sorted(TileExtended.parse_pattern(
        ...     "                  # \\n"
        ...     "#    ##    ##    ###\\n"
        ...     " #  #  #  #  #  #   \\n"
        ... ))
        [(0, 1), (1, 2), (4, 2), (5, 1), (6, 1), (7, 2), (10, 2), (11, 1),
            (12, 1), (13, 2), (16, 2), (17, 1), (18, 0), (18, 1), (19, 1)]
        """
        non_empty_lines = filter(None, text.splitlines())
        return {
            (x, y)
            for y, line in enumerate(non_empty_lines)
            for x, spot in enumerate(line)
            if spot in use
        }

    def find_single_permutation_with_pattern(self, pattern):
        pattern_and_permutations = [
            (monsters, permutation)
            for monsters, permutation in (
                (permutation.find_pattern(pattern), permutation)
                for permutation in self.get_all_permutations()
            )
            if monsters
        ]
        if not pattern_and_permutations:
            raise Exception("No pattern found anywhere")
        if len(pattern_and_permutations) > 1:
            raise Exception(
                f"Too many permutations had pattern: "
                f"{len(pattern_and_permutations)}")
        (pattern, permutation), = pattern_and_permutations

        return pattern, permutation

    def find_pattern(self, pattern):
        min_x = min(x for x, _ in pattern)
        min_y = min(y for _, y in pattern)
        if (min_x, min_y) != (0, 0):
            pattern = {
                (x - min_x, y - min_y)
                for x, y in pattern
            }
        width = max(x for x, _ in pattern) + 1
        height = max(y for _, y in pattern) + 1
        if width > self.size or height > self.size:
            return set()

        matching = set()
        for offset_x in range(self.size - width + 1):
            for offset_y in range(self.size - height + 1):
                repositioned_pattern = {
                    (x + offset_x, y + offset_y)
                    for x, y in pattern
                }
                if repositioned_pattern - self.points:
                    continue
                matching.update(repositioned_pattern)

        return matching

    def orient_with_border(self, border):
        """
        >>> tile_a = TileExtended.from_tile_text(
        ...     "Tile 1:\\n"
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "#..\\n"
        ... )
        >>> print(tile_a.orient_with_border(
        ...     tile_a.to_border().rotate().flip()).show(False))
        .#.
        ..#
        #..
        """
        if self.id != border.id:
            raise Exception(f"Mismatched ids: {border.id} != {self.id}")
        matching_orientations = [
            permutation
            for permutation in self.get_all_permutations()
            if permutation.to_border() == border
        ]
        if not matching_orientations:
            raise Exception("Border was not for same tile")
        if len(matching_orientations) > 1:
            raise Exception(
                f"Too many orientations matched: {len(matching_orientations)}")
        orientation, = matching_orientations

        return orientation

    def get_all_permutations(self):
        """
        >>> tile_a = TileExtended.from_tile_text(
        ...     "Tile 1:\\n"
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "#..\\n"
        ... )
        >>> print("\\n-\\n".join(sorted(
        ...     permutation.show(False) for permutation
        ...     in tile_a.get_all_permutations())))
        #..
        ..#
        .#.
        -
        .#.
        #..
        ..#
        -
        .#.
        ..#
        #..
        -
        ..#
        #..
        .#.
        """
        permutations = {}
        rotated = self
        permutations[tuple(sorted(self.points))] = self
        for _ in range(3):
            rotated = rotated.rotate()
            permutations[tuple(sorted(rotated.points))] = rotated
        rotated = self.flip()
        permutations[tuple(sorted(rotated.points))] = rotated
        for _ in range(3):
            rotated = rotated.rotate()
            permutations[tuple(sorted(rotated.points))] = rotated
        return list(permutations.values())

    def rotate(self):
        """
        >>> tile_a = TileExtended.from_tile_text(
        ...     "Tile 1:\\n"
        ...     ".#\\n"
        ...     "..\\n"
        ... )
        >>> tile_a = tile_a.rotate();print(tile_a.show(False))
        #.
        ..
        >>> tile_a = tile_a.rotate();print(tile_a.show(False))
        ..
        #.
        >>> tile_a = tile_a.rotate();print(tile_a.show(False))
        ..
        .#
        >>> tile_a = tile_a.rotate();print(tile_a.show(False))
        .#
        ..
        """
        cls = type(self)
        return cls(self.id, {
            (y, self.size - 1 - x)
            for x, y in self.points
        })

    def flip(self):
        """
        >>> tile_a = TileExtended.from_tile_text(
        ...     "Tile 1:\\n"
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "#..\\n"
        ... )
        >>> tile_a = tile_a.flip();print(tile_a.show(False))
        .#.
        #..
        ..#
        >>> tile_a = tile_a.flip();print(tile_a.show(False))
        .#.
        ..#
        #..
        """
        cls = type(self)
        return cls(self.id, {
            (self.size - 1 - x, y)
            for x, y in self.points
        })

    def show(self, include_id=True, highlight=(), show_only_highlighted=False):
        """
        >>> print(TileExtended.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show())
        Tile 2473:
        .##
        #..
        #.#
        >>> print(TileExtended.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False))
        .##
        #..
        #.#
        >>> print(TileExtended.of_size(3).from_tile_text(
        ...     "Tile 2473:\\n"
        ...     ".##\\n"
        ...     "#..\\n"
        ...     "#.#\\n"
        ... ).show(False, highlight={(0, 0), (1, 0), (2, 0)}))
        .OO
        #..
        #.#
        """
        content = "\n".join(
            "".join(
                (
                    "O"
                    if (x, y) in highlight else
                    (
                        " "
                        if show_only_highlighted else
                        "#"
                    )
                )
                if (x, y) in self.points else
                (
                    " "
                    if show_only_highlighted else
                    "."
                )
                for x in range(self.size)
            )
            for y in range(self.size)
        )
        if not include_id:
            return content
        tile_id = f"Tile {self.id}:"
        return f"{tile_id}\n{content}"


TileSetExtended.tile_class = TileExtended


class TileBorderExtended(part_a.TileBorder):
    tile_class = TileExtended
    classes_by_size = {}


TileExtended.border_class = TileBorderExtended


challenge = Challenge()
challenge.main()
