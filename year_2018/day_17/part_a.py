#!/usr/bin/env python3
import itertools
import re

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        26910
        """
        ground = Ground.from_ground_text(_input)
        ground.step_many()
        from pathlib import Path
        Path(__file__).parent.joinpath("./part_a_watered_output.txt")\
            .write_text(ground.show())
        return ground.get_water_reach()


class Ground:
    @classmethod
    def from_ground_text(cls, ground_text, spring_location=(500, 0)):
        """
        >>> len(Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... ).walls)
        34
        """
        non_empty_lines = filter(None, ground_text.splitlines())
        point_sets = map(cls.points_from_text, non_empty_lines)
        walls = {
            point
            for points in point_sets
            for point in points
        }

        return cls(walls, spring_location)

    re_line = re.compile(
        r"([xy])=(\d+)(?:\.\.(\d+))?, ([xy])=(\d+)(?:\.\.(\d+))?")

    @classmethod
    def points_from_text(cls, specification_text):
        """
        >>> sorted(Ground.points_from_text("x=495, y=2..7"))
        [(495, 2), (495, 3), (495, 4), (495, 5), (495, 6), (495, 7)]
        >>> sorted(Ground.points_from_text("x=495, y=7..2"))
        [(495, 2), (495, 3), (495, 4), (495, 5), (495, 6), (495, 7)]
        >>> sorted(Ground.points_from_text("y=7, x=495..501"))
        [(495, 7), (496, 7), (497, 7), (498, 7), (499, 7), (500, 7), (501, 7)]
        >>> sorted(Ground.points_from_text("y=7, x=501..495"))
        [(495, 7), (496, 7), (497, 7), (498, 7), (499, 7), (500, 7), (501, 7)]
        >>> sorted(Ground.points_from_text("x=495, y=2"))
        [(495, 2)]
        >>> sorted(Ground.points_from_text("y=7, x=495"))
        [(495, 7)]
        """
        match = cls.re_line.match(specification_text)
        if not match:
            raise Exception(f"Could not parse '{specification_text}'")
        (
            first_axis, first_start_str, first_end_str,
            second_axis, second_start_str, second_end_str,
        ) = match.groups()
        if (first_axis, second_axis) == ('x', 'y'):
            x_start_str, x_end_str = first_start_str, first_end_str
            y_start_str, y_end_str = second_start_str, second_end_str
        elif (first_axis, second_axis) == ('y', 'x'):
            x_start_str, x_end_str = second_start_str, second_end_str
            y_start_str, y_end_str = first_start_str, first_end_str
        else:
            raise Exception(
                f"Expected one axis x and another y, got: "
                f"{first_axis} and {second_axis}")

        if x_end_str is None:
            x_end_str = x_start_str
        if y_end_str is None:
            y_end_str = y_start_str

        x_start, x_end = int(x_start_str), int(x_end_str)
        if x_end < x_start:
            x_start, x_end = x_end, x_start
        y_start, y_end = int(y_start_str), int(y_end_str)
        if y_end < y_start:
            y_start, y_end = y_end, y_start

        if x_end > x_start and y_end > y_start:
            raise Exception(f"Got square specification: {specification_text}")

        return (
            (x, y)
            for x in range(x_start, x_end + 1)
            for y in range(y_start, y_end + 1)
        )

    @classmethod
    def from_visual(cls, visual, spring_location=(500, 0),
                    spring_water_points=True):
        """
        >>> sorted(Ground.from_visual(
        ...     ".....+......\\n"
        ...     "...........#\\n"
        ...     "...........#\\n"
        ... ).walls)
        [(506, 1), (506, 2)]
        >>> sorted(Ground.from_visual(
        ...     ".+.\\n"
        ...     "..#\\n"
        ...     "#..\\n"
        ... ).walls)
        [(499, 2), (501, 1)]
        >>> print("!" + Ground.from_visual(
        ...     ".....+......\\n"
        ...     ".....|.....#\\n"
        ...     "#..#||||...#\\n"
        ...     "#..#~~#|....\\n"
        ...     "#..#~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#######|....\\n"
        ...     ".......|....\\n"
        ...     "..|||||||||.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#######|.\\n"
        ... , spring_water_points=False).show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        ..|||||||||.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#######|.
        >>> print("!" + Ground.from_visual(
        ...     ".....+......\\n"
        ...     ".....|.....#\\n"
        ...     "#..#||||...#\\n"
        ...     "#..#~~#|....\\n"
        ...     "#..#~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#######|....\\n"
        ...     ".......|....\\n"
        ...     "..|||||||||.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..v#######v.\\n"
        ... , spring_water_points=False).show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        ..|||||||||.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..v#######v.
        """
        non_empty_lines = filter(None, visual.splitlines())
        non_sand = {
            (x, y): spot
            for y, line in enumerate(non_empty_lines)
            for x, spot in enumerate(line)
            if spot != '.'
        }
        extra_visuals = set(non_sand.values()) - {'#', '+', '~', '|', 'v'}
        if extra_visuals:
            raise Exception(f"Unknown spots: {extra_visuals}")
        relative_spring_locations = [
            location
            for location, spot in non_sand.items()
            if spot == '+'
        ]
        if not relative_spring_locations:
            raise Exception("No spring ('+') was included")
        if len(relative_spring_locations) > 1:
            raise Exception(
                f"Too many springs ('+') were included: "
                f"{relative_spring_locations}")
        (relative_spring_x, relative_spring_y), = relative_spring_locations
        spring_x, spring_y = spring_location
        offset_x = spring_x - relative_spring_x
        offset_y = spring_y - relative_spring_y

        walls = {
            (x + offset_x, y + offset_y)
            for (x, y), spot in non_sand.items()
            if spot == "#"
        }
        running_water = {
            (x + offset_x, y + offset_y)
            for (x, y), spot in non_sand.items()
            if spot in ("|", "v")
        }
        settled_water = {
            (x + offset_x, y + offset_y)
            for (x, y), spot in non_sand.items()
            if spot == "~"
        }
        water_points = {
            (x + offset_x, y + offset_y)
            for (x, y), spot in non_sand.items()
            if spot == "v"
            or spring_water_points and spot == "+"
        }

        return cls(
            walls, spring_location, running_water=running_water,
            settled_water=settled_water, water_points=water_points)

    def __init__(self, walls, spring_location=(500, 0), running_water=None,
                 settled_water=None, water_points=None):
        self.walls = walls
        self.min_x = min(x for x, _ in self.walls)
        self.max_x = max(x for x, _ in self.walls)
        self.min_y = 1
        self.max_y = max(y for _, y in self.walls)
        self.min_wall_y = min(y for _, y in self.walls)
        if running_water is None:
            running_water = set()
        self.running_water = running_water
        if settled_water is None:
            settled_water = set()
        self.settled_water = settled_water
        self.spring_location = spring_location
        if water_points is None:
            water_points = {spring_location}
        self.water_points = water_points

    SPRING = 'spring'
    WALL = 'wall'
    RUNNING_WATER = 'running-water'
    SETTLED_WATER = 'settled-water'
    EMPTY = 'empty'

    def __getitem__(self, item):
        if item in self.walls:
            return self.WALL
        elif item in self.running_water:
            return self.RUNNING_WATER
        elif item in self.settled_water:
            return self.SETTLED_WATER
        elif item == self.spring_location:
            return self.SPRING
        else:
            return self.EMPTY

    def __setitem__(self, key, value):
        content = self[key]
        if content == value:
            if content == self.RUNNING_WATER and key in self.water_points:
                self.water_points.remove(key)
            return

        if content == self.RUNNING_WATER:
            self.running_water.remove(key)
        elif content == self.SETTLED_WATER:
            self.settled_water.remove(key)
        elif content in (self.SPRING, self.WALL):
            raise Exception(f"Cannot override spring or wall at {key}")

        if value == self.RUNNING_WATER:
            self.running_water.add(key)
        elif value == self.SETTLED_WATER:
            self.settled_water.add(key)
        elif value in (self.SPRING, self.WALL, self.EMPTY):
            raise Exception(f"Cannot set spring, wall, or empty, to {key}")
        else:
            raise Exception(f"Unknown content {value}")

        if key in self.water_points:
            self.water_points.remove(key)

    def get_water_reach(self):
        """
        >>> Ground.from_visual(
        ...     ".....+......\\n"
        ...     ".....|.....#\\n"
        ...     "#..#||||...#\\n"
        ...     "#..#~~#|....\\n"
        ...     "#..#~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#######|....\\n"
        ...     ".......|....\\n"
        ...     "..|||||||||.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#######|.\\n"
        ... , spring_water_points=False).get_water_reach()
        57
        >>> Ground.from_visual(
        ...     ".....+......\\n"
        ...     ".....|......\\n"
        ...     "#..#||||...#\\n"
        ...     "#..#~~#|....\\n"
        ...     "#..#~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#~~~~~#|....\\n"
        ...     "#######|....\\n"
        ...     ".......|....\\n"
        ...     "..|||||||||.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#~~~~~#|.\\n"
        ...     "..|#######|.\\n"
        ... , spring_water_points=False).get_water_reach()
        56
        """
        return sum(
            1
            for _, y in self.running_water | self.settled_water
            if y >= self.min_wall_y
        )

    def step_many(self, count=None):
        """
        >>> ground_a = Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... )
        >>> ground_a.step_many(6)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#.|.....#
        #..#.|#.....
        #..#.|#.....
        #....|#.....
        #....v#.....
        #######.....
        ............
        ............
        ...#.....#..
        ...#.....#..
        ...#.....#..
        ...#######..
        >>> ground_a.step_many(1)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#.|.....#
        #..#.|#.....
        #..#.|#.....
        #....v#.....
        #~~~~~#.....
        #######.....
        ............
        ............
        ...#.....#..
        ...#.....#..
        ...#.....#..
        ...#######..
        >>> ground_a.step_many(3)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#.v.....#
        #..#~~#.....
        #..#~~#.....
        #~~~~~#.....
        #~~~~~#.....
        #######.....
        ............
        ............
        ...#.....#..
        ...#.....#..
        ...#.....#..
        ...#######..
        >>> ground_a.step_many(1)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#|||v...#
        #..#~~#.....
        #..#~~#.....
        #~~~~~#.....
        #~~~~~#.....
        #######.....
        ............
        ............
        ...#.....#..
        ...#.....#..
        ...#.....#..
        ...#######..
        >>> ground_a.step_many(10)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        .......|....
        ...#...|.#..
        ...#...|.#..
        ...#...v.#..
        ...#######..
        >>> ground_a.step_many(3)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        .......v....
        ...#~~~~~#..
        ...#~~~~~#..
        ...#~~~~~#..
        ...#######..
        >>> ground_a.step_many(5)
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        ..||||||||v.
        ..|#~~~~~#..
        ..|#~~~~~#..
        ..|#~~~~~#..
        ..v#######..
        >>> ground_a.step_many(5)
        False
        >>> ground_a.step_many(1)
        True
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        ..|||||||||.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#######|.
        >>> ground_a.step_many(1)
        True
        >>> ground_a.step_many(1)
        True
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....|.....#
        #..#||||...#
        #..#~~#|....
        #..#~~#|....
        #~~~~~#|....
        #~~~~~#|....
        #######|....
        .......|....
        ..|||||||||.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#~~~~~#|.
        ..|#######|.
        """
        if not self.water_points:
            return True
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        for _ in steps:
            if self.step():
                finished = True
                break
        else:
            finished = False

        return finished

    def step(self):
        """
        >>> ground_a = Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... )
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !....+......
        .....v.....#
        #..#.......#
        #..#..#.....
        #..#..#.....
        #.....#.....
        #.....#.....
        #######.....
        ............
        ............
        ...#.....#..
        ...#.....#..
        ...#.....#..
        ...#######..
        >>> ground_a = Ground.from_visual(
        ...     "#..+..#\\n"
        ...     "...v...\\n"
        ...     "..###..\\n"
        ...     "#.....#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False)
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !..+..#
        .v|||v.
        ..###..
        #.....#
        #.....#
        #######
        >>> {ground_a.step() for _ in range(3)}
        {False}
        >>> print("!" + ground_a.show()[1:])
        !..+..#
        .||||v.
        .|###..
        #|....#
        #v....#
        #######
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !..+..#
        .||||v.
        .|###..
        #v....#
        #~~~~~#
        #######
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !..+..#
        .||||v.
        .v###..
        #~~~~~#
        #~~~~~#
        #######
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !#..+..#
        ..||||v.
        v||###..
        .#~~~~~#
        .#~~~~~#
        .#######
        >>> {ground_a.step() for _ in range(4)}
        {False}
        >>> print("!" + ground_a.show()[1:])
        !#..+..#
        ..||||v.
        |||###..
        |#~~~~~#
        |#~~~~~#
        |#######
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !#..+..#
        ..|||||.
        |||###v.
        |#~~~~~#
        |#~~~~~#
        |#######
        >>> {ground_a.step() for _ in range(4)}
        {False}
        >>> ground_a.step()
        True
        >>> print("!" + ground_a.show()[1:])
        !#..+..#.
        ..|||||..
        |||###|||
        |#~~~~~#|
        |#~~~~~#|
        |#######|
        >>> ground_a = Ground.from_visual(
        ...     "#..+..#\\n"
        ...     "#..|...\\n"
        ...     "#v|||v#\\n"
        ...     "#~###.#\\n"
        ...     "#~~~~~#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False)
        >>> ground_a.step()
        False
        >>> print("!" + ground_a.show()[1:])
        !..+..#
        #..|...
        #||||v#
        #~###.#
        #~~~~~#
        #######
        """
        if not self.water_points:
            return False

        water_point = min(self.water_points)
        self.step_water_point(water_point)
        return not bool(self.water_points)

    def step_water_point(self, water_point):
        """
        >>> ground_a = Ground.from_visual(
        ...     "#..+..#\\n"
        ...     ".|||||.\\n"
        ...     ".|###|.\\n"
        ...     "#|...|#\\n"
        ...     "#v...v#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False)
        >>> ground_a.step_water_point(min(ground_a.water_points))
        False
        >>> print("!" + ground_a.show()[1:])
        !..+..#
        .|||||.
        .|###|.
        #v...|#
        #~~~~~#
        #######
        >>> sorted(ground_a.water_points)
        [(498, 3)]
        """
        water_x, water_y = water_point
        if water_y >= self.max_y:
            self.water_points.remove(water_point)
            return True

        new_water_point = (water_x, water_y + 1)
        _, new_water_y = new_water_point
        new_content = self[new_water_point]
        if new_content in (self.WALL, self.SETTLED_WATER):
            (left_x, _), left_settled, left_run_down = \
                self.find_left_boundary(water_point)
            (right_x, _), right_settled, right_run_down = \
                self.find_right_boundary(water_point)
            if left_settled and right_settled:
                for x in range(left_x, right_x + 1):
                    self[(x, water_y)] = self.SETTLED_WATER
                new_water_point = (water_x, water_y - 1)
                self.water_points.add(new_water_point)
                return False
            elif left_run_down or right_run_down:
                new_water_points = []
                if left_run_down:
                    new_water_points.append((left_x, water_y))
                if right_run_down:
                    new_water_points.append((right_x, water_y))
                for x in range(left_x, right_x + 1):
                    self[(x, water_y)] = self.RUNNING_WATER
                self.water_points.update(new_water_points)
                return False
            else:
                self.water_points.remove(water_point)
                return False
        elif new_content == self.RUNNING_WATER:
            self.water_points.remove(water_point)
            return False
        elif new_content != self.EMPTY:
            raise Exception(
                f"Unexpected content beneath {water_point}: {new_content}")
        else:
            self[new_water_point] = self.RUNNING_WATER
            self.running_water.add(new_water_point)
            self.water_points.remove(water_point)
            self.water_points.add(new_water_point)
            return False

    def find_left_boundary(self, start):
        """
        >>> Ground.from_visual(
        ...     "#..+..#\\n"
        ...     ".||||v.\\n"
        ...     ".v###..\\n"
        ...     "#~~~~~#\\n"
        ...     "#~~~~~#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False).find_left_boundary((498, 2))
        ((496, 2), False, True)
        >>> Ground.from_visual(
        ...     "#..+..#\\n"
        ...     "#..|...\\n"
        ...     "#v|||v#\\n"
        ...     "#~###.#\\n"
        ...     "#~~~~~#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False).find_left_boundary((498, 2))
        ((498, 2), True, False)
        >>> Ground.from_visual(
        ...     "#..+..#\\n"
        ...     ".|||||.\\n"
        ...     ".|###|.\\n"
        ...     "#|...|#\\n"
        ...     "#v...v#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False).find_left_boundary((498, 4))
        ((498, 4), True, False)
        """
        return self.find_boundary(start, -1, "left")

    def find_right_boundary(self, start):
        """
        >>> Ground.from_visual(
        ...     "#..+..#\\n"
        ...     ".||||v.\\n"
        ...     ".v###..\\n"
        ...     "#~~~~~#\\n"
        ...     "#~~~~~#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False).find_right_boundary((498, 2))
        ((498, 2), True, False)
        >>> Ground.from_visual(
        ...     "#..+..#\\n"
        ...     "#..|...\\n"
        ...     "#v|||v#\\n"
        ...     "#~###.#\\n"
        ...     "#~~~~~#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False).find_right_boundary((498, 2))
        ((502, 2), False, True)
        >>> Ground.from_visual(
        ...     "#..+..#\\n"
        ...     ".|||||.\\n"
        ...     ".|###|.\\n"
        ...     "#|...|#\\n"
        ...     "#v...v#\\n"
        ...     "#######\\n"
        ... , spring_water_points=False).find_right_boundary((498, 4))
        ((502, 4), True, False)
        """
        return self.find_boundary(start, 1, "right")

    def find_boundary(self, start, delta, name):
        start_x, start_y = start
        if not (self.min_x <= start_x <= self.max_x) \
                or not (self.min_y <= start_y <= self.max_y):
            raise Exception(
                f"{start} is not within x ({self.min_x}, {self.max_x}) "
                f"or y ({self.min_y}, {self.max_x}) boundary")
        start_content = self[start]
        if start_content not in (self.EMPTY, self.RUNNING_WATER):
            raise Exception(
                f"{start} is not in an empty position or with running water: "
                f"{start_content}")
        beneath = (start_x, start_y + 1)
        beneath_content = self[beneath]
        if beneath_content not in (self.WALL, self.SETTLED_WATER):
            raise Exception(
                f"{start} is not above a wall or settled water: "
                f"{beneath_content}")

        if delta == 1:
            end_x = self.max_x + delta * 2
        elif delta == -1:
            end_x = self.min_x + delta * 2
        else:
            raise Exception(f"Only 1/-1 are acceptable deltas, not {delta}")
        x_values = range(start_x + delta, end_x, delta)
        for x in x_values:
            point = (x, start_y)
            point_beneath = (x, start_y + 1)
            content = self[point]
            content_beneath = self[point_beneath]
            if content == self.WALL:
                point = (x - delta, start_y)
                settled = True
                run_down = False
                return point, settled, run_down
            # elif content == self.RUNNING_WATER:
            #     point = (x - delta, start_y)
            #     settled = False
            #     run_down = False
            #     return point, settled, run_down
            elif content not in (self.EMPTY, self.RUNNING_WATER):
                raise Exception(
                    f"Unexpected content found at {(x, start_y)}: {content}")
            if content_beneath in self.RUNNING_WATER:
                point = (x, start_y)
                settled = False
                run_down = False
                return point, settled, run_down
            elif content_beneath == self.EMPTY:
                point = (x, start_y)
                settled = False
                run_down = True
                return point, settled, run_down
            elif content_beneath not in (self.WALL, self.SETTLED_WATER):
                raise Exception(
                    f"Unexpected content found beneath {(x, start_y)}: "
                    f"{content_beneath}")

        raise Exception(
            f"Didn't find {name} boundary of {start}: looked at "
            f"{list(x_values)} ({x_values})")

    def get_groups(self):
        """
        >>> len(Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... ).get_groups())
        4
        """
        return Groups.pick(self.walls)

    SHOW_MAP = {
        WALL: "#",
        RUNNING_WATER: "|",
        SETTLED_WATER: "~",
        EMPTY: ".",
        SPRING: "+"
    }

    def show(self):
        """
        >>> print("!" + Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... ).show()[1:])
        !....v......
        ...........#
        #..#.......#
        #..#..#.....
        #..#..#.....
        #.....#.....
        #.....#.....
        #######.....
        ............
        ............
        ...#.....#..
        ...#.....#..
        ...#.....#..
        ...#######..
        """
        spring_x, spring_y = self.spring_location
        points = (
            self.walls
            | self.running_water
            | self.water_points
            | {self.spring_location}
        )
        min_x = min(x for x, _ in points)
        max_x = max(x for x, _ in points)
        min_y = min(y for _, y in points)
        max_y = max(y for _, y in points)

        return "\n".join(
            "".join(
                "v"
                if (x, y) in self.water_points else
                self.SHOW_MAP[self[(x, y)]]
                for x in range(min_x, max_x + 1)
            )
            for y in range(min_y, max_y + 1)
        )


class Groups:
    @classmethod
    def pick(cls, walls):
        """
        >>> ground = Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... )
        >>> groups_a = sorted(map(sorted, Groups.pick(ground.walls)))
        >>> list(map(len, groups_a))
        [16, 3, 13, 2]
        >>> groups_a[3]
        [(506, 1), (506, 2)]
        >>> groups_a[1]
        [(498, 2), (498, 3), (498, 4)]
        """
        remaining_walls = set(walls)
        groups = []
        while remaining_walls:
            start = next(iter(remaining_walls))
            group = Group.pick(start, remaining_walls)
            groups.append(group)

        return cls(groups)

    def __init__(self, groups):
        self.groups = groups

    def __len__(self):
        return len(self.groups)

    def __iter__(self):
        return iter(self.groups)

    def group_by_type(self):
        """
        >>> {_type: len(groups) for _type, groups in sorted(Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... ).get_groups().group_by_type().items())}
        {'box': 2, 'bucket': 2}
        """
        return {
            _type: [group for _, group in items]
            for _type, items in itertools.groupby(sorted((
                (group.get_type(), group)
                for group in self.groups
            ), key=lambda item: item[0]), key=lambda item: item[0])
        }


class Group:
    @classmethod
    def pick(cls, start, remaining_walls):
        """
        >>> ground = Ground.from_ground_text(
        ...     "x=495, y=2..7\\n"
        ...     "y=7, x=495..501\\n"
        ...     "x=501, y=3..7\\n"
        ...     "x=498, y=2..4\\n"
        ...     "x=506, y=1..2\\n"
        ...     "x=498, y=10..13\\n"
        ...     "x=504, y=10..13\\n"
        ...     "y=13, x=498..504\\n"
        ... )
        >>> Group.pick((0, 0), set())
        set()
        >>> sorted(Group.pick((506, 1), set(ground.walls)))
        [(506, 1), (506, 2)]
        >>> sorted(Group.pick((498, 3), set(ground.walls)))
        [(498, 2), (498, 3), (498, 4)]
        >>> len(Group.pick((500, 13), set(ground.walls)))
        13
        >>> len(Group.pick((500, 7), set(ground.walls)))
        16
        >>> remaining_walls_a = set(ground.walls)
        >>> sorted(Group.pick((506, 1), remaining_walls_a))
        [(506, 1), (506, 2)]
        >>> sorted(Group.pick((506, 1), remaining_walls_a))
        []
        >>> sorted(Group.pick((498, 3), remaining_walls_a))
        [(498, 2), (498, 3), (498, 4)]
        >>> len(Group.pick((500, 13), remaining_walls_a))
        13
        >>> len(Group.pick((500, 7), remaining_walls_a))
        16
        >>> remaining_walls_a
        set()
        """
        if start not in remaining_walls:
            return set()
        group = {start}
        remaining_walls.remove(start)
        stack = [start]
        while stack:
            current = stack.pop(0)
            new_neighbours = {
                neighbour
                for neighbour in cls.get_neighbours(current)
                if neighbour in remaining_walls
            }
            group.update(new_neighbours)
            remaining_walls -= new_neighbours
            stack.extend(new_neighbours)

        return cls(group)

    @classmethod
    def from_visual(cls, visual, spring_location=(500, 0)):
        """
        >>> sorted(Group.from_visual(
        ...     "..+..\\n"
        ...     ".#.#.\\n"
        ...     ".#.#.\\n"
        ...     ".###.\\n"
        ... ).points)
        [(499, 1), (499, 2), (499, 3), (500, 3), (501, 1), (501, 2), (501, 3)]
        """
        walls = Ground.from_visual(visual, spring_location).walls
        first_wall = next(iter(walls))
        remaining_walls = set(walls)
        group = cls.pick(first_wall, remaining_walls)
        if remaining_walls:
            raise Exception(
                "There were {len(remaining_walls)} extraneous points")

        return group

    OFFSETS = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0),
    ]

    @classmethod
    def get_neighbours(cls, position):
        """
        >>> sorted(Group.get_neighbours((1, 2)))
        [(0, 2), (1, 1), (1, 3), (2, 2)]
        """
        x, y = position
        return [
            (x + d_x, y + d_y)
            for d_x, d_y in cls.OFFSETS
        ]

    def __init__(self, points):
        self.points = points

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def get_type(self):
        """
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".#...\\n"
        ...     ".#...\\n"
        ...     ".....\\n"
        ... ).get_type()
        'box'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".##..\\n"
        ...     ".#...\\n"
        ...     ".....\\n"
        ... ).get_type()
        'other'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".##..\\n"
        ...     ".##..\\n"
        ...     ".....\\n"
        ... ).get_type()
        'box'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".#.#.\\n"
        ...     ".###.\\n"
        ...     ".....\\n"
        ... ).get_type()
        'bucket'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".###.\\n"
        ...     ".###.\\n"
        ...     ".....\\n"
        ... ).get_type()
        'box'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".###.\\n"
        ...     ".###.\\n"
        ...     ".###.\\n"
        ... ).get_type()
        'other'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".###.\\n"
        ...     ".#.#.\\n"
        ...     ".###.\\n"
        ... ).get_type()
        'box'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     "..##.\\n"
        ...     ".#.#.\\n"
        ...     ".###.\\n"
        ... ).get_type()
        'other'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".###.\\n"
        ...     "...#.\\n"
        ...     ".###.\\n"
        ... ).get_type()
        'other'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     ".#.#.\\n"
        ...     ".#.#.\\n"
        ...     ".###.\\n"
        ... ).get_type()
        'bucket'
        >>> Group.from_visual(
        ...     "..+..\\n"
        ...     "####.\\n"
        ...     ".#.#.\\n"
        ...     ".###.\\n"
        ... ).get_type()
        'other'
        """
        type_map = {
            'bucket': self.is_bucket(),
            'box': self.is_box(),
        }
        types = [
            _type
            for _type, is_of_type in type_map.items()
            if is_of_type
        ]
        if not types:
            return 'other'
        if len(types) > 1:
            raise Exception(f"Multiple types: {types}")

        _type, = types

        return _type

    def is_bucket(self):
        min_x = min(x for x, _ in self.points)
        max_x = max(x for x, _ in self.points)
        if min_x > max_x - 2:
            return False

        min_y_for_min_x = min(y for x, y in self.points if x == min_x)
        max_y_for_min_x = max(y for x, y in self.points if x == min_x)
        min_y_for_max_x = min(y for x, y in self.points if x == max_x)
        max_y_for_max_x = max(y for x, y in self.points if x == max_x)
        if max_y_for_min_x != max_y_for_max_x:
            return False

        return self.points == {
            (x, y)
            for x_range, y_range in (
                ((min_x,), range(min_y_for_min_x, max_y_for_min_x + 1)),
                ((max_x,), range(min_y_for_max_x, max_y_for_max_x + 1)),
                (range(min_x, max_x + 1), (max_y_for_min_x,)),
            )
            for x in x_range
            for y in y_range
        }

    def is_box(self):
        min_x, min_y = min(self)
        max_x, max_y = max(self)

        return self.points == ({
            (x, y)
            for x_range, y_range in (
                (range(min_x, max_x + 1), (min_y, max_y)),
                ((min_x, max_x), range(min_y, max_y + 1)),
            )
            for x in x_range
            for y in y_range
        })


Challenge.main()
challenge = Challenge()
