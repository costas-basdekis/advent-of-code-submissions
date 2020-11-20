#!/usr/bin/env python3
import functools

import utils
from year_2017.day_14 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1018
        """
        return DiskExtended.from_hash_input(_input.strip()).get_region_count()


class DiskExtended(part_a.Disk):
    def get_region_count(self):
        """
        >>> DiskExtended.from_hash_input('flqrgnkx').get_region_count()
        1242
        """
        return len(self.get_regions())

    def get_regions(self):
        """
        >>> disk_a = DiskExtended.from_hash_input('flqrgnkx')
        >>> functools.reduce(set.__or__, disk_a.get_regions()) \\
        ...     == set(disk_a.get_cells())
        True
        """
        regions_by_cell = self.get_regions_by_cell()
        regions = []
        remaining_cells = set(regions_by_cell)
        while remaining_cells:
            cell = remaining_cells.pop()
            region = regions_by_cell[cell]
            regions.append(region)
            remaining_cells.difference_update(region)

        return regions

    def get_region_ids_by_cell(self):
        regions = self.get_regions()
        return {
            inhabitant: _id
            for _id, region in enumerate(regions, 1)
            for inhabitant in region
        }

    def get_regions_by_cell(self):
        """
        >>> regions_by_cell_a = DiskExtended.from_hash_input('flqrgnkx')\\
        ...     .get_regions_by_cell()
        >>> sorted(regions_by_cell_a[utils.Point2D(0, 0)])
        [Point2D(x=0, y=0), Point2D(x=1, y=0), Point2D(x=1, y=1)]
        >>> sorted(regions_by_cell_a[utils.Point2D(1, 0)])
        [Point2D(x=0, y=0), Point2D(x=1, y=0), Point2D(x=1, y=1)]
        >>> sorted(regions_by_cell_a[utils.Point2D(1, 1)])
        [Point2D(x=0, y=0), Point2D(x=1, y=0), Point2D(x=1, y=1)]
        """
        cells = self.get_cells()

        return self.group_cells(cells)

    def group_cells(self, cells):
        """
        >>> groups = DiskExtended([]).group_cells(
        ...     [utils.Point2D(0, 0), utils.Point2D(1, 0), utils.Point2D(1, 1)])
        >>> sorted((cell, sorted(group)) for cell, group in groups.items())
        [(Point2D(x=0, y=0), [Point2D(x=0, y=0), Point2D(x=1, y=0),
            Point2D(x=1, y=1)]),
            (Point2D(x=1, y=0), [Point2D(x=0, y=0), Point2D(x=1, y=0),
                Point2D(x=1, y=1)]),
            (Point2D(x=1, y=1), [Point2D(x=0, y=0), Point2D(x=1, y=0),
                Point2D(x=1, y=1)])]
        """
        regions_by_cell = {}
        for cell in cells:
            neighbour_regions = [
                regions_by_cell[neighbour]
                for neighbour in cell.get_manhattan_neighbours()
                if neighbour in regions_by_cell
            ]
            if not neighbour_regions:
                region = {cell}
            else:
                region = (
                    functools.reduce(set.__or__, neighbour_regions)
                    | {cell}
                )
            for inhabitant in region:
                regions_by_cell[inhabitant] = region

        return regions_by_cell


challenge = Challenge()
challenge.main()
