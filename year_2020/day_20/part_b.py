#!/usr/bin/env python3
import functools
import itertools

import utils
from year_2020.day_20 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        42
        """
        tile_arrangement = TileArrangementExtended.from_tile_set(
            part_a.TileSet.from_tiles_text(_input))
        tile_arrangement.solve_arrangement()


class TileArrangementExtended(part_a.TileArrangement):
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
                        part_a.TileBorder.OPPOSITE_SIDE_MAP[name], side),
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
        a_corner = self.get_a_corner(neighbours_by_named_side_by_id)
        neighbour_by_named_side_by_id = {
            _id: {
                name: next(iter(neighbours), None)
                for name, neighbours
                in neighbours_by_named_side.items()
            }
            for _id, neighbours_by_named_side
            in neighbours_by_named_side_by_id.items()
        }
        matrix = []
        while len(matrix) < self.size:
            if len(matrix) < 1:
                first_item = a_corner
            else:
                raise Exception("Ok")
            row = []
            matrix.append(row)
            oriented_first_item = self.orient_item_for_matrix(
                first_item, matrix, borders_by_named_side)
            row.append(oriented_first_item)
            self.check_matrix_last_item_fitness(matrix)
            while len(row) < self.size:
                item_before = row[-1]

            raise Exception("Ok")

    def check_matrix_last_item_fitness(self, matrix):
        row = matrix[-1]
        item = row[-1]
        if len(matrix) > 1:
            row_above = matrix[-2]
            item_above = row_above[0]
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


class TileArrangementExtendedOld(part_a.TileArrangement):
    def __init__(self, matrix, tiles_by_id):
        super().__init__(matrix, tiles_by_id)
        self.borders_by_id = {
            border.id: border
            for row in self.matrix
            for border in row
        }

    def solve_arrangement(self):
        borders_by_side = self.group_matrix_by_possible_side()
        neighbour_ids_by_side_by_id = self.group_borders_by_id(borders_by_side)
        self.check_solubility_with_counts(neighbour_ids_by_side_by_id)
        neighbour_id_by_side_by_id = {
            _id: {
                side: next(iter(neighbour_ids))
                for side, neighbour_ids in borders_by_side.items()
            }
            for _id, borders_by_side in neighbour_ids_by_side_by_id.items()
        }
        matrix = []
        while len(matrix) < self.size:
            if not matrix:
                a_corner = self.get_a_starting_corner(
                    neighbour_ids_by_side_by_id)
                first_item = a_corner
            else:
                previous_row = matrix[-1]
                previous_first_item = previous_row[0]
                first_item_id = neighbour_id_by_side_by_id[
                    previous_first_item.id][previous_first_item.bottom]
                first_item = self.borders_by_id[first_item_id]
            row = []
            matrix.append(row)
            oriented_first_item = self.orient_item_to_fit_matrix(
                first_item, matrix, neighbour_id_by_side_by_id)
            row.append(oriented_first_item)
            self.check_matrix_last_item_fitness(matrix)
            while len(row) < self.size:
                item = row[-1]
                next_item_id = neighbour_id_by_side_by_id[item.id][item.right]
                next_item = self.borders_by_id[next_item_id]
                oriented_next_item = self.orient_item_to_fit_matrix(
                    next_item, matrix, neighbour_id_by_side_by_id)
                row.append(oriented_next_item)
                self.check_matrix_last_item_fitness(matrix)

        self.matrix = matrix

    def check_matrix_last_item_fitness(self, matrix):
        row = matrix[-1]
        item = row[-1]
        if len(matrix) > 1:
            row_above = matrix[-2]
            item_above = row_above[0]
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

    def orient_item_to_fit_matrix(self, item, matrix,
                                  neighbour_id_by_side_by_id):
        if len(matrix) == 1:
            item_above = None
        else:
            previous_row = matrix[-2]
            previous_first_item = previous_row[0]
            item_above = previous_first_item
        row = matrix[-1]
        if len(row) == 0:
            item_before = None
        else:
            previous_item = row[-1]
            item_before = previous_item
        item_neighbour_id_by_side = neighbour_id_by_side_by_id[item.id]

        orientations = [
            oriented
            for oriented in item.get_all_permutations()
            if (
                item_neighbour_id_by_side.get(oriented.top) is None
                if item_above is None else
                oriented.top == item_above.bottom
            )
            and (
                item_neighbour_id_by_side.get(oriented.left) is None
                if item_before is None else
                oriented.left == item_before.right
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

    def check_solubility_with_counts(self, neighbour_ids_by_side_by_id):
        neighbour_candidate_counts = {
            count
            for count, items in itertools.groupby(sorted(
                len(neighbours_ids)
                for by_side in neighbour_ids_by_side_by_id.values()
                for neighbours_ids in by_side.values()
            ))
        }
        if neighbour_candidate_counts != {1}:
            raise Exception(
                f"Cannot solve arrangement, as neighbour candidates are not "
                f"unique: {neighbour_candidate_counts}")
        neighbour_count_counts = {
            count: len(list(items))
            for count, items
            in itertools.groupby(sorted(
                len(functools.reduce(
                    set.__or__, neighbour_ids_by_side.values()))
                for neighbour_ids_by_side
                in neighbour_ids_by_side_by_id.values()
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

    def get_a_starting_corner(self, neighbour_ids_by_side_by_id):
        corner_candidates = self.get_corner_candidates(
            neighbour_ids_by_side_by_id)
        a_corner_id = corner_candidates[0]
        a_corner = self.borders_by_id[a_corner_id]
        return a_corner


challenge = Challenge()
challenge.main()
