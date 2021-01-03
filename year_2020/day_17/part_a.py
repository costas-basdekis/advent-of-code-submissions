#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        295
        """
        return Grid.from_grid_text(_input).step_many(6).get_active_count()


class Grid:
    @classmethod
    def from_grid_text(cls, grid_text):
        """
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... )
        Grid([(0, 2, 0), (1, 0, 0), (1, 2, 0), (2, 1, 0), (2, 2, 0)])
        """
        non_empty_lines = filter(None, grid_text.splitlines())
        return cls({
            (x, y, 0)
            for y, line in enumerate(non_empty_lines)
            for x, spot in enumerate(line)
            if spot == '#'
        })

    def __init__(self, points):
        self.points = points

    def __repr__(self):
        return f"{type(self).__name__}({sorted(self.points)})"

    def get_active_count(self):
        """
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).step_many(6).get_active_count()
        112
        """
        return len(self.points)

    def step_many(self, count):
        """
        >>> print(Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).step_many(3).show())
        z=-2
        .......
        .......
        ..##...
        ..###..
        .......
        .......
        .......
        <BLANKLINE>
        z=-1
        ..#....
        ...#...
        #......
        .....##
        .#...#.
        ..#.#..
        ...#...
        <BLANKLINE>
        z=0
        ...#...
        .......
        #......
        .......
        .....##
        .##.#..
        ...#...
        <BLANKLINE>
        z=1
        ..#....
        ...#...
        #......
        .....##
        .#...#.
        ..#.#..
        ...#...
        <BLANKLINE>
        z=2
        .......
        .......
        ..##...
        ..###..
        .......
        .......
        .......
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> print(Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).step().show())
        z=-1
        #..
        ..#
        .#.
        <BLANKLINE>
        z=0
        #.#
        .##
        .#.
        <BLANKLINE>
        z=1
        #..
        ..#
        .#.
        """
        min_x, max_x, min_y, max_y, min_z, max_z = self.get_ranges()
        self.points = {
            (x, y, z)
            for x in range(min_x - 1, max_x + 2)
            for y in range(min_y - 1, max_y + 2)
            for z in range(min_z - 1, max_z + 2)
            if self.get_new_value((x, y, z))
        }
        return self

    def get_new_value(self, position):
        """
        >>> Grid({}).get_new_value((0, 0, 0))
        False
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((0, 0, 0))
        False
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((1, 1, 0))
        False
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((0, 1, 0))
        True
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((2, 1, 0))
        True
        """
        neighbour_count = self.get_neighbour_count(position)
        if position in self.points:
            return neighbour_count in (2, 3)
        else:
            return neighbour_count == 3

    def get_neighbour_count(self, position):
        """
        >>> Grid({}).get_neighbour_count((0, 0, 0))
        0
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((0, 0, 0))
        1
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, 0))
        5
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, 1))
        5
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, -1))
        5
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, 2))
        0
        """
        return sum(
            1
            for neighbour in self.get_neighbours(position)
            if neighbour in self.points
        )

    NEIGHBOUR_OFFSETS = [
        (x, y, z)
        for x in range(-1, 2)
        for y in range(-1, 2)
        for z in range(-1, 2)
        if (x, y, z) != (0, 0, 0)
    ]

    def get_neighbours(self, position):
        """
        >>> sorted(Grid({}).get_neighbours((1, 2, 3)))
        [(0, 1, 2), (0, 1, 3), (0, 1, 4), ..., (2, 3, 4)]
        >>> len(Grid({}).get_neighbours((1, 2, 3)))
        26
        >>> (1, 2, 3) in Grid({}).get_neighbours((1, 2, 3))
        False
        """
        x, y, z = position
        return [
            (x + d_x, y + d_y, z + d_z)
            for d_x, d_y, d_z in self.NEIGHBOUR_OFFSETS
        ]

    def get_ranges(self):
        """
        >>> Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_ranges()
        (0, 2, 0, 2, 0, 0)
        """
        min_x = min(x for x, _, _ in self.points)
        max_x = max(x for x, _, _ in self.points)
        min_y = min(y for _, y, _ in self.points)
        max_y = max(y for _, y, _ in self.points)
        min_z = min(z for _, _, z in self.points)
        max_z = max(z for _, _, z in self.points)

        return min_x, max_x, min_y, max_y, min_z, max_z

    def show(self):
        """
        >>> print(Grid.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).show())
        z=0
        .#.
        ..#
        ###
        """
        if not self.points:
            return ""
        min_x, max_x, min_y, max_y, _, _ = self.get_ranges()
        z_values = sorted({z for _, _, z in self.points})

        return "\n\n".join(
            "z={z}\n{level}".format(
                z=z,
                level="\n".join(
                    "".join(
                        "#"
                        if (x, y, z) in self.points else
                        "."
                        for x in range(min_x, max_x + 1)
                    )
                    for y in range(min_y, max_y + 1)
                )
            )
            for z in z_values
        )


challenge = Challenge()
challenge.main()
