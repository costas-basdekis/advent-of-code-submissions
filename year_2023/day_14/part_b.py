#!/usr/bin/env python3
from typing import Dict, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D
from year_2023.day_14 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        93736
        """
        return DishExtended.from_map(_input).tilt_cycles(1000000000, debugger=debugger).get_load_factor()


class DishExtended(part_a.Dish):
    def tilt_cycles(self, count: int, debugger: Debugger = Debugger(enabled=False)) -> "DishExtended":
        """
        >>> _dish = DishExtended.from_map('''
        ...     O....#....
        ...     O.OO#....#
        ...     .....##...
        ...     OO.#O....O
        ...     .O.....O#.
        ...     O.#..O.#.#
        ...     ..O..#O..O
        ...     .......O..
        ...     #....###..
        ...     #OO..#....
        ... ''')
        >>> print("!" + str(_dish.tilt_cycles(1)))
        !.....#....
        ....#...O#
        ...OO##...
        .OO#......
        .....OOO#.
        .O#...O#.#
        ....O#....
        ......OOOO
        #...O###..
        #..OO#....
        >>> print("!" + str(_dish.tilt_cycles(2)))
        !.....#....
        ....#...O#
        .....##...
        ..O#......
        .....OOO#.
        .O#...O#.#
        ....O#...O
        .......OOO
        #..OO###..
        #.OOO#...O
        >>> print("!" + str(_dish.tilt_cycles(3)))
        !.....#....
        ....#...O#
        .....##...
        ..O#......
        .....OOO#.
        .O#...O#.#
        ....O#...O
        .......OOO
        #...O###.O
        #.OOO#...O
        >>> _dish.tilt_cycles(1000000000).get_load_factor()
        64
        """
        cache: Dict[Tuple[Point2D, ...], int] = {}
        dish_per_round: List[DishExtended] = [self]
        dish: DishExtended = self
        caches: Tuple[Optional[Dict[Point2D, Point2D]], Optional[Dict[Point2D, Point2D]], Optional[Dict[Point2D, Point2D]], Optional[Dict[Point2D, Point2D]]] = {}, {}, {}, {}
        for _round in debugger.stepping(range(1, count + 1)):
            key = tuple(sorted(dish.rounded_rocks))
            if key in cache:
                previous_round = cache[key]
                target_round = (count - previous_round) % (_round - previous_round) + previous_round
                return dish_per_round[target_round]
            dish = dish.tilt_cycle(caches)
            cache[key] = _round
            dish_per_round.append(dish)
            if debugger.should_report():
                debugger.default_report_if(f"")
        return dish

    def tilt_cycle(self, caches: Optional[Tuple[Optional[Dict[Point2D, Point2D]], Optional[Dict[Point2D, Point2D]], Optional[Dict[Point2D, Point2D]], Optional[Dict[Point2D, Point2D]]]] = None) -> "DishExtended":
        """
        >>> print("!" + str(DishExtended.from_map('''
        ...     O....#....
        ...     O.OO#....#
        ...     .....##...
        ...     OO.#O....O
        ...     .O.....O#.
        ...     O.#..O.#.#
        ...     ..O..#O..O
        ...     .......O..
        ...     #....###..
        ...     #OO..#....
        ... ''').tilt_cycle()))
        !.....#....
        ....#...O#
        ...OO##...
        .OO#......
        .....OOO#.
        .O#...O#.#
        ....O#....
        ......OOOO
        #...O###..
        #..OO#....
        """
        if caches is None:
            caches = None, None, None, None
        cache_north, cache_west, cache_south, cache_east = caches
        return self.tilt_north(cache_north).tilt_west(cache_west).tilt_south(cache_south).tilt_east(cache_east)

    def tilt_west(self, cache: Optional[Dict[Point2D, Point2D]] = None) -> "DishExtended":
        """
        >>> print(DishExtended.from_map('''
        ...     OOOO.#.O..
        ...     OO..#....#
        ...     OO..O##..O
        ...     O..#.OO...
        ...     ........#.
        ...     ..#....#.#
        ...     ..O..#.O.O
        ...     ..O.......
        ...     #....###..
        ...     #....#....
        ... ''').tilt_west())
        OOOO.#O...
        OO..#....#
        OOO..##O..
        O..#OO....
        ........#.
        ..#....#.#
        O....#OO..
        O.........
        #....###..
        #....#....
        """
        rounded_count_per_square: Dict[Point2D, int] = {}
        if cache is None:
            cache = {}
        for rounded in self.rounded_rocks:
            for x in range(rounded.x, -1, -1):
                point = Point2D(x, rounded.y)
                if point in cache:
                    target = cache[point]
                    rounded_count_per_square.setdefault(target, 0)
                    rounded_count_per_square[target] += 1
                    for x2 in range(point.x + 1, rounded.x + 1):
                        cache[Point2D(x2, point.y)] = target
                    break
                elif point in self.square_rocks:
                    rounded_count_per_square.setdefault(point, 0)
                    rounded_count_per_square[point] += 1
                    for x2 in range(point.x + 1, rounded.x + 1):
                        cache[Point2D(x2, point.y)] = point
                    break
            else:
                point = Point2D(-1, rounded.y)
                rounded_count_per_square.setdefault(point, 0)
                rounded_count_per_square[point] += 1
        new_rounded_rocks = set()
        for square, count in rounded_count_per_square.items():
            for x in range(square.x + 1, square.x + count + 1):
                new_rounded_rocks.add(Point2D(x, square.y))
        cls = type(self)
        return cls(
            rounded_rocks=new_rounded_rocks,
            square_rocks=self.square_rocks,
            width=self.width, height=self.height,
        )

    def tilt_south(self, cache: Optional[Dict[Point2D, Point2D]] = None) -> "Dish":
        """
        >>> print("!" + str(DishExtended.from_map('''
        ...     OOOO.#O...
        ...     OO..#....#
        ...     OOO..##O..
        ...     O..#OO....
        ...     ........#.
        ...     ..#....#.#
        ...     O....#OO..
        ...     O.........
        ...     #....###..
        ...     #....#....
        ... ''').tilt_south()))
        !.....#....
        ....#.O..#
        O..O.##...
        O.O#......
        O.O....O#.
        O.#..O.#.#
        O....#....
        OO....OO..
        #O...###..
        #O..O#....
        """
        rounded_count_per_square: Dict[Point2D, int] = {}
        if cache is None:
            cache = {}
        for rounded in self.rounded_rocks:
            for y in range(rounded.y, self.height):
                point = Point2D(rounded.x, y)
                if point in cache:
                    target = cache[point]
                    rounded_count_per_square.setdefault(target, 0)
                    rounded_count_per_square[target] += 1
                    for y2 in range(point.y - 1, rounded.y - 1, -1):
                        cache[Point2D(point.x, y2)] = target
                    break
                elif point in self.square_rocks:
                    rounded_count_per_square.setdefault(point, 0)
                    rounded_count_per_square[point] += 1
                    for y2 in range(point.y - 1, rounded.y - 1, -1):
                        cache[Point2D(point.x, y2)] = point
                    break
            else:
                point = Point2D(rounded.x, self.height)
                rounded_count_per_square.setdefault(point, 0)
                rounded_count_per_square[point] += 1
        new_rounded_rocks = set()
        for square, count in rounded_count_per_square.items():
            for y in range(square.y - 1, square.y - count - 1, -1):
                new_rounded_rocks.add(Point2D(square.x, y))
        cls = type(self)
        return cls(
            rounded_rocks=new_rounded_rocks,
            square_rocks=self.square_rocks,
            width=self.width, height=self.height,
        )

    def tilt_east(self, cache: Optional[Dict[Point2D, Point2D]] = None) -> "DishExtended":
        """
        >>> print("!" + str(DishExtended.from_map('''
        ...     .....#....
        ...     ....#.O..#
        ...     O..O.##...
        ...     O.O#......
        ...     O.O....O#.
        ...     O.#..O.#.#
        ...     O....#....
        ...     OO....OO..
        ...     #O...###..
        ...     #O..O#....
        ... ''').tilt_east()))
        !.....#....
        ....#...O#
        ...OO##...
        .OO#......
        .....OOO#.
        .O#...O#.#
        ....O#....
        ......OOOO
        #...O###..
        #..OO#....
        """
        rounded_count_per_square: Dict[Point2D, int] = {}
        if cache is None:
            cache = {}
        for rounded in self.rounded_rocks:
            for x in range(rounded.x, self.width):
                point = Point2D(x, rounded.y)
                if point in cache:
                    target = cache[point]
                    rounded_count_per_square.setdefault(target, 0)
                    rounded_count_per_square[target] += 1
                    for x2 in range(point.x - 1, rounded.x - 1, -1):
                        cache[Point2D(x2, point.y)] = target
                    break
                elif point in self.square_rocks:
                    rounded_count_per_square.setdefault(point, 0)
                    rounded_count_per_square[point] += 1
                    for x2 in range(point.x - 1, rounded.x - 1, -1):
                        cache[Point2D(x2, point.y)] = point
                    break
            else:
                point = Point2D(self.width, rounded.y)
                rounded_count_per_square.setdefault(point, 0)
                rounded_count_per_square[point] += 1
        new_rounded_rocks = set()
        for square, count in rounded_count_per_square.items():
            for x in range(square.x - 1, square.x - count - 1, -1):
                new_rounded_rocks.add(Point2D(x, square.y))
        cls = type(self)
        return cls(
            rounded_rocks=new_rounded_rocks,
            square_rocks=self.square_rocks,
            width=self.width, height=self.height,
        )



Challenge.main()
challenge = Challenge()
