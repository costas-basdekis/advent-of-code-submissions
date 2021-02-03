#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1972
        """
        return Grid4.from_grid_text(_input).step_many(6).get_active_count()


class Grid4:
    @classmethod
    def from_grid_text(cls, grid_text):
        """
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... )
        Grid4([(0, 2, 0, 0), (1, 0, 0, 0), (1, 2, 0, 0), (2, 1, 0, 0), (2, 2, 0, 0)])
        """
        non_empty_lines = filter(None, grid_text.splitlines())
        return cls({
            (x, y, 0, 0)
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
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).step_many(6).get_active_count()
        848
        """
        return len(self.points)

    def step_many(self, count):
        """
        >>> print(Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).step_many(2).show())
        z=-2, w=-2
        .....
        .....
        ..#..
        .....
        .....
        <BLANKLINE>
        z=0, w=-2
        ###..
        ##.##
        #...#
        .#..#
        .###.
        <BLANKLINE>
        z=2, w=-2
        .....
        .....
        ..#..
        .....
        .....
        <BLANKLINE>
        z=-2, w=0
        ###..
        ##.##
        #...#
        .#..#
        .###.
        <BLANKLINE>
        z=2, w=0
        ###..
        ##.##
        #...#
        .#..#
        .###.
        <BLANKLINE>
        z=-2, w=2
        .....
        .....
        ..#..
        .....
        .....
        <BLANKLINE>
        z=0, w=2
        ###..
        ##.##
        #...#
        .#..#
        .###.
        <BLANKLINE>
        z=2, w=2
        .....
        .....
        ..#..
        .....
        .....
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> print(Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).step().show())
        z=-1, w=-1
        #..
        ..#
        .#.
        <BLANKLINE>
        z=0, w=-1
        #..
        ..#
        .#.
        <BLANKLINE>
        z=1, w=-1
        #..
        ..#
        .#.
        <BLANKLINE>
        z=-1, w=0
        #..
        ..#
        .#.
        <BLANKLINE>
        z=0, w=0
        #.#
        .##
        .#.
        <BLANKLINE>
        z=1, w=0
        #..
        ..#
        .#.
        <BLANKLINE>
        z=-1, w=1
        #..
        ..#
        .#.
        <BLANKLINE>
        z=0, w=1
        #..
        ..#
        .#.
        <BLANKLINE>
        z=1, w=1
        #..
        ..#
        .#.
        """
        min_x, max_x, min_y, max_y, min_z, max_z, min_w, max_w = \
            self.get_ranges()
        self.points = {
            (x, y, z, w)
            for x in range(min_x - 1, max_x + 2)
            for y in range(min_y - 1, max_y + 2)
            for z in range(min_z - 1, max_z + 2)
            for w in range(min_w - 1, max_w + 2)
            if self.get_new_value((x, y, z, w))
        }
        return self

    def get_new_value(self, position):
        """
        >>> Grid4({}).get_new_value((0, 0, 0, 0))
        False
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((0, 0, 0, 0))
        False
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((1, 1, 0, 0))
        False
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((0, 1, 0, 0))
        True
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_new_value((2, 1, 0, 0))
        True
        """
        neighbour_count = self.get_neighbour_count(position)
        if position in self.points:
            return neighbour_count in (2, 3)
        else:
            return neighbour_count == 3

    def get_neighbour_count(self, position):
        """
        >>> Grid4({}).get_neighbour_count((0, 0, 0, 0))
        0
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((0, 0, 0, 0))
        1
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, 0, 0))
        5
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, 1, 0))
        5
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, -1, 0))
        5
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_neighbour_count((1, 1, 2, 0))
        0
        """
        return sum(
            1
            for neighbour in self.get_neighbours(position)
            if neighbour in self.points
        )

    NEIGHBOUR_OFFSETS = [
        (x, y, z, w)
        for x in range(-1, 2)
        for y in range(-1, 2)
        for z in range(-1, 2)
        for w in range(-1, 2)
        if (x, y, z, w) != (0, 0, 0, 0)
    ]

    def get_neighbours(self, position):
        """
        >>> sorted(Grid4({}).get_neighbours((1, 2, 3, 4)))
        [(0, 1, 2, 3), (0, 1, 2, 4), (0, 1, 2, 5), ..., (2, 3, 4, 5)]
        >>> len(Grid4({}).get_neighbours((1, 2, 3, 4)))
        80
        >>> (1, 2, 3, 4) in Grid4({}).get_neighbours((1, 2, 3, 4))
        False
        """
        x, y, z, w = position
        return [
            (x + d_x, y + d_y, z + d_z, w + d_w)
            for d_x, d_y, d_z, d_w in self.NEIGHBOUR_OFFSETS
        ]

    def get_ranges(self):
        """
        >>> Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).get_ranges()
        (0, 2, 0, 2, 0, 0, 0, 0)
        """
        min_x = min(x for x, _, _, _ in self.points)
        max_x = max(x for x, _, _, _ in self.points)
        min_y = min(y for _, y, _, _ in self.points)
        max_y = max(y for _, y, _, _ in self.points)
        min_z = min(z for _, _, z, _ in self.points)
        max_z = max(z for _, _, z, _ in self.points)
        min_w = min(w for _, _, _, w in self.points)
        max_w = max(w for _, _, _, w in self.points)

        return min_x, max_x, min_y, max_y, min_z, max_z, min_w, max_w

    def show(self):
        """
        >>> print(Grid4.from_grid_text(
        ...     ".#.\\n"
        ...     "..#\\n"
        ...     "###\\n"
        ... ).show())
        z=0, w=0
        .#.
        ..#
        ###
        """
        if not self.points:
            return ""
        min_x, max_x, min_y, max_y, _, _, _, _ = self.get_ranges()
        w_z_values = sorted({(w, z) for _, _, z, w in self.points})

        return "\n\n".join(
            "z={z}, w={w}\n{level}".format(
                z=z, w=w,
                level="\n".join(
                    "".join(
                        "#"
                        if (x, y, z, w) in self.points else
                        "."
                        for x in range(min_x, max_x + 1)
                    )
                    for y in range(min_y, max_y + 1)
                )
            )
            for w, z in w_z_values
        )


Challenge.main()
challenge = Challenge()
