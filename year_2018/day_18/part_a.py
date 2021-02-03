#!/usr/bin/env python3
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        644640
        """
        return Area.from_area_text(_input).step_many(10).get_hash()


class Area:
    TREE = 'tree'
    CAMP = 'camp'
    OPEN = 'open'
    PARSE_MAP = {
        '.': OPEN,
        '|': TREE,
        '#': CAMP,
    }

    @classmethod
    def from_area_text(cls, area_text, width=None, height=None):
        """
        >>> len(Area.from_area_text(
        ...     ".#.#...|#.\\n"
        ...     ".....#|##|\\n"
        ...     ".|..|...#.\\n"
        ...     "..|#.....#\\n"
        ...     "#.#|||#|#|\\n"
        ...     "...#.||...\\n"
        ...     ".|....|...\\n"
        ...     "||...#|.#|\\n"
        ...     "|.||||..|.\\n"
        ...     "...#.|..|.\\n"
        ... ).contents)
        44
        """
        non_empty_lines = list(filter(None, area_text.splitlines()))
        if height is None:
            height = len(non_empty_lines)
        if width is None:
            width = len(non_empty_lines[0])
        contents = {
            (x, y): cls.PARSE_MAP[spot]
            for y, line in enumerate(non_empty_lines)
            for x, spot in enumerate(line)
            if cls.PARSE_MAP[spot] != cls.OPEN
        }

        return cls(contents, width, height)

    def __init__(self, contents, width, height):
        self.contents = contents
        self.width = width
        self.height = height

    def get_hash(self):
        """
        >>> Area.from_area_text(
        ...     ".||##.....\\n"
        ...     "||###.....\\n"
        ...     "||##......\\n"
        ...     "|##.....##\\n"
        ...     "|##.....##\\n"
        ...     "|##....##|\\n"
        ...     "||##.####|\\n"
        ...     "||#####|||\\n"
        ...     "||||#|||||\\n"
        ...     "||||||||||\\n"
        ... ).get_hash()
        1147
        """
        counts = self.get_counts()
        return counts['tree'] * counts['camp']

    def get_counts(self):
        """
        >>> Area.from_area_text(
        ...     ".||##.....\\n"
        ...     "||###.....\\n"
        ...     "||##......\\n"
        ...     "|##.....##\\n"
        ...     "|##.....##\\n"
        ...     "|##....##|\\n"
        ...     "||##.####|\\n"
        ...     "||#####|||\\n"
        ...     "||||#|||||\\n"
        ...     "||||||||||\\n"
        ... ).get_counts()
        {'tree': 37, 'camp': 31}
        """
        return self.aggregate_counts(self.contents.values())

    SHOW_MAP = {
        content: spot
        for spot, content in PARSE_MAP.items()
    }

    def show(self):
        """
        >>> print(Area.from_area_text(
        ...     ".#.#...|#.\\n"
        ...     ".....#|##|\\n"
        ...     ".|..|...#.\\n"
        ...     "..|#.....#\\n"
        ...     "#.#|||#|#|\\n"
        ...     "...#.||...\\n"
        ...     ".|....|...\\n"
        ...     "||...#|.#|\\n"
        ...     "|.||||..|.\\n"
        ...     "...#.|..|.\\n"
        ... ).show())
        .#.#...|#.
        .....#|##|
        .|..|...#.
        ..|#.....#
        #.#|||#|#|
        ...#.||...
        .|....|...
        ||...#|.#|
        |.||||..|.
        ...#.|..|.
        """
        return "\n".join(
            "".join(
                self.SHOW_MAP[self.contents.get((x, y), self.OPEN)]
                for x in range(self.width)
            )
            for y in range(self.height)
        )

    def step_many(self, count):
        """
        >>> print("!" + Area.from_area_text(
        ...     ".#.#...|#.\\n"
        ...     ".....#|##|\\n"
        ...     ".|..|...#.\\n"
        ...     "..|#.....#\\n"
        ...     "#.#|||#|#|\\n"
        ...     "...#.||...\\n"
        ...     ".|....|...\\n"
        ...     "||...#|.#|\\n"
        ...     "|.||||..|.\\n"
        ...     "...#.|..|.\\n"
        ... ).step_many(10).show()[1:])
        !||##.....
        ||###.....
        ||##......
        |##.....##
        |##.....##
        |##....##|
        ||##.####|
        ||#####|||
        ||||#|||||
        ||||||||||
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> print("!" + Area.from_area_text(
        ...     ".#.#...|#.\\n"
        ...     ".....#|##|\\n"
        ...     ".|..|...#.\\n"
        ...     "..|#.....#\\n"
        ...     "#.#|||#|#|\\n"
        ...     "...#.||...\\n"
        ...     ".|....|...\\n"
        ...     "||...#|.#|\\n"
        ...     "|.||||..|.\\n"
        ...     "...#.|..|.\\n"
        ... ).step().show()[1:])
        !......##.
        ......|###
        .|..|...#.
        ..|#||...#
        ..##||.|#|
        ...#||||..
        ||...|||..
        |||||.||.|
        ||||||||||
        ....||..|.
        """
        points = set(self.contents) | {
            neighbour
            for point in self.contents
            for neighbour in self.get_neighbours(point)
        }
        self.contents = {
            point: next_spot
            for point, next_spot in (
                (point, self.get_next_spot_at_point(point))
                for point in points
            )
            if next_spot != self.OPEN
        }
        return self

    def get_next_spot_at_point(self, point):
        """
        >>> Area({(0, 0): 'camp'}, 10, 10).get_next_spot_at_point((0, 0))
        'open'
        >>> Area({(0, 0): 'camp', (0, 1): 'camp', (1, 0): 'tree'}, 10, 10)\\
        ...     .get_next_spot_at_point((0, 0))
        'camp'
        """
        neighbour_counts = self.get_neighbour_counts(point)
        spot = self.contents.get(point, self.OPEN)
        return self.get_next_spot(spot, neighbour_counts)

    def get_next_spot(self, spot, neighbour_counts):
        """
        >>> Area({}, 1, 1).get_next_spot('camp', {'tree': 0, 'camp': 0})
        'open'
        >>> Area({}, 1, 1).get_next_spot('camp', {'tree': 0, 'camp': 1})
        'open'
        >>> Area({}, 1, 1).get_next_spot('camp', {'tree': 2, 'camp': 0})
        'open'
        >>> Area({}, 1, 1).get_next_spot('camp', {'tree': 2, 'camp': 1})
        'camp'
        >>> Area({}, 1, 1).get_next_spot('tree', {'tree': 0, 'camp': 0})
        'tree'
        >>> Area({}, 1, 1).get_next_spot('tree', {'tree': 3, 'camp': 0})
        'tree'
        >>> Area({}, 1, 1).get_next_spot('tree', {'tree': 0, 'camp': 3})
        'camp'
        >>> Area({}, 1, 1).get_next_spot('tree', {'tree': 3, 'camp': 3})
        'camp'
        >>> Area({}, 1, 1).get_next_spot('open', {'tree': 0, 'camp': 3})
        'open'
        >>> Area({}, 1, 1).get_next_spot('open', {'tree': 3, 'camp': 0})
        'tree'
        >>> Area({}, 1, 1).get_next_spot('open', {'tree': 3, 'camp': 3})
        'tree'
        """
        if spot == self.TREE:
            if neighbour_counts[self.CAMP] >= 3:
                return self.CAMP
            else:
                return self.TREE
        elif spot == self.CAMP:
            if neighbour_counts[self.TREE] < 1 \
                    or neighbour_counts[self.CAMP] < 1:
                return self.OPEN
            else:
                return self.CAMP
        elif spot == self.OPEN:
            if neighbour_counts[self.TREE] >= 3:
                return self.TREE
            else:
                return self.OPEN

        raise Exception(f"Invalid spot '{spot}'")

    def get_neighbour_counts(self, point):
        """
        >>> Area({}, 1, 1).get_neighbour_counts((0, 0))
        {'tree': 0, 'camp': 0}
        >>> Area({(1, 1): 'tree', (3, 5): 'tree'}, 10, 10)\\
        ...     .get_neighbour_counts((1, 1))
        {'tree': 0, 'camp': 0}
        >>> Area({
        ...     (2, 2): 'tree', (3, 5): 'tree', (2, 1): 'camp',
        ...     (1, 2): 'camp',
        ... }, 10, 10).get_neighbour_counts((1, 1))
        {'tree': 1, 'camp': 2}
        """
        neighbours = self.get_neighbours(point)
        return self.aggregate_counts(
            self.contents.get(neighbour, self.OPEN)
            for neighbour in neighbours
        )

    def aggregate_counts(self, spots):
        """
        >>> Area({}, 1, 1).aggregate_counts([
        ...     'tree', 'camp', 'tree', 'camp', 'open', 'tree'])
        {'tree': 3, 'camp': 2}
        """
        return {
            self.TREE: 0,
            self.CAMP: 0,
            **{
                spot: len(list(items))
                for spot, items in itertools.groupby(sorted(spots))
                if spot != self.OPEN
            },
        }

    NEIGHBOUR_OFFSETS = [
        (d_x, d_y)
        for d_x in range(-1, 2)
        for d_y in range(-1, 2)
        if (d_x, d_y) != (0, 0)
    ]

    def get_neighbours(self, point):
        """
        >>> sorted(Area({}, 10, 10).get_neighbours((2, -3)))
        []
        >>> sorted(Area({}, 10, 10).get_neighbours((0, 0)))
        [(0, 1), (1, 0), (1, 1)]
        >>> sorted(Area({}, 10, 10).get_neighbours((2, 4)))
        [(1, 3), (1, 4), (1, 5), (2, 3), (2, 5), (3, 3), (3, 4), (3, 5)]
        """
        x, y = point
        return (
            neighbour
            for neighbour in (
                (x + d_x, y + d_y)
                for d_x, d_y in self.NEIGHBOUR_OFFSETS
            )
            if self.is_within_area(neighbour)
        )

    def is_within_area(self, point):
        x, y = point
        return (
            0 <= x < self.width
            and 0 <= y < self.height
        )


Challenge.main()
challenge = Challenge()
