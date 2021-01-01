#!/usr/bin/env python3
import utils

from year_2019.day_20.part_a import parse_map_walkways, parse_map_portals,\
    combine_map_walkways_and_portals, find_path_length


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        7180
        """
        walkways = parse_map_walkways(_input)
        portals = parse_map_portals(_input, walkways)
        walkways_neighbours, free_portals = \
            combine_map_walkways_and_portals(walkways, portals)
        walkways_neighbours, free_portals = \
            LazyMultiMap.from_map(
                walkways_neighbours, free_portals, max_levels=200)
        return walkways_neighbours.find_path_length(
            free_portals['AA'], free_portals['ZZ'])


class LazyMultiMap:
    @classmethod
    def from_map(cls, walkways_neighbours, free_portals, max_levels=20):
        multi_free_portals = cls.convert_free_portals(free_portals)
        return cls(walkways_neighbours, free_portals, max_levels), \
            multi_free_portals

    @classmethod
    def convert_free_portals(cls, free_portals):
        """
        >>> LazyMultiMap.convert_free_portals({'AA': (3, 4), 'ZZ': (15, 3)})
        {'AA': (0, (3, 4)), 'ZZ': (0, (15, 3))}
        """
        return {
            label: (0, position)
            for label, position in free_portals.items()
        }

    def __init__(self, walkways_neighbours, free_portals, max_levels=20):
        self.walkways_neighbours = walkways_neighbours
        self.free_portals = free_portals
        self.inner_portals, self.outer_portals = \
            split_portals(self.walkways_neighbours)
        self.portals = self.inner_portals | self.outer_portals
        self.maps = {}
        self.max_levels = max_levels

    def __repr__(self):
        return repr(self.maps)

    def __getitem__(self, item):
        try:
            level, position = item
        except Exception as e:
            raise Exception(f"{e}: {item}")
        if not isinstance(position, tuple) or len(position) != 2:
            raise KeyError(
                f"Got a raw point instead of a level and point: {item}")
        if level > self.max_levels:
            raise KeyError(
                f"Level {level} is more than max {self.max_levels}")
        self.ensure_level(level)

        _map = self.maps[level]
        try:
            return _map[(level, position)]
        except KeyError:
            raise KeyError(
                f"Could not find {position} at level {level}. Original "
                f"position contained {self.walkways_neighbours.get(position)}"
                f", and original free portals were {self.free_portals}")

    def create_for_level(self, level):
        """
        >>> map_text_a = (
        ...     "         A           \\n"
        ...     "         A           \\n"
        ...     "  #######.#########  \\n"
        ...     "  #######.........#  \\n"
        ...     "  #######.#######.#  \\n"
        ...     "  #######.#######.#  \\n"
        ...     "  #######.#######.#  \\n"
        ...     "  #####  B    ###.#  \\n"
        ...     "BC...##  C    ###.#  \\n"
        ...     "  ##.##       ###.#  \\n"
        ...     "  ##...DE  F  ###.#  \\n"
        ...     "  #####    G  ###.#  \\n"
        ...     "  #########.#####.#  \\n"
        ...     "DE..#######...###.#  \\n"
        ...     "  #.#########.###.#  \\n"
        ...     "FG..#########.....#  \\n"
        ...     "  ###########.#####  \\n"
        ...     "             Z       \\n"
        ...     "             Z       \\n"
        ... )
        >>> walkways_a = parse_map_walkways(map_text_a)
        >>> portals_a = parse_map_portals(map_text_a, walkways_a)
        >>> walkways_neighbours_a, free_portals_a = \\
        ...     combine_map_walkways_and_portals(walkways_a, portals_a)
        >>> multi_walkways_neighbours_a, multi_free_portals_a = \\
        ...     LazyMultiMap.from_map(walkways_neighbours_a, free_portals_a)
        >>> def check_keys_have_levels(_map):
        ...     return all(
        ...         isinstance(walkway_and_point, tuple)
        ...         and len(walkway_and_point) == 2
        ...         and isinstance(walkway_and_point[0], int)
        ...         and isinstance(walkway_and_point[1], tuple)
        ...         and len(walkway_and_point[1]) == 2
        ...         for walkway_and_point in _map
        ...     )
        >>> def check_keys_levels_are_correct(_map, _level):
        ...     return all(
        ...         walkway_level == _level
        ...         for (walkway_level, _), neighbours in _map.items()
        ...     )
        >>> def check_values_have_levels(_map):
        ...     return all(
        ...         isinstance(walkway_and_point, tuple)
        ...         and len(walkway_and_point) == 2
        ...         and isinstance(walkway_and_point[0], int)
        ...         and isinstance(walkway_and_point[1], tuple)
        ...         and len(walkway_and_point[1]) == 2
        ...         for neighbours in _map.values()
        ...         for walkway_and_point in neighbours
        ...     )
        >>> def check_neighbour_levels_are_correct(_map):
        ...     return tuple(sorted(
        ...         ((walkway_level, walkway), neighbours)
        ...         for (walkway_level, walkway), neighbours in _map.items()
        ...         for (neighbour_level, neighbour) in neighbours
        ...         if abs(walkway_level - neighbour_level) != (
        ...             0
        ...             if are_next_to_each_other(walkway, neighbour) else
        ...             1
        ...         )
        ...     ))
        >>> map_0 = multi_walkways_neighbours_a.create_for_level(0)
        >>> check_keys_have_levels(map_0)
        True
        >>> check_keys_levels_are_correct(map_0, 0)
        True
        >>> check_values_have_levels(map_0)
        True
        >>> check_neighbour_levels_are_correct(map_0)
        ()
        >>> map_0[(0, (2, 8))]
        ((0, (3, 8)),)
        >>> map_0[(0, (6, 10))]
        ((1, (2, 13)), (0, (5, 10)))
        >>> map_1 = multi_walkways_neighbours_a.create_for_level(1)
        >>> check_keys_have_levels(map_1)
        True
        >>> check_keys_levels_are_correct(map_1, 1)
        True
        >>> check_values_have_levels(map_1)
        True
        >>> check_neighbour_levels_are_correct(map_1)
        ()
        >>> map_1[(1, (2, 8))]
        ((1, (3, 8)), (0, (9, 6)))
        >>> map_1[(1, (6, 10))]
        ((2, (2, 13)), (1, (5, 10)))
        >>> map_5 = multi_walkways_neighbours_a.create_for_level(5)
        >>> check_keys_have_levels(map_5)
        True
        >>> check_keys_levels_are_correct(map_5, 5)
        True
        >>> check_values_have_levels(map_5)
        True
        >>> check_neighbour_levels_are_correct(map_5)
        ()
        >>> map_5[(5, (2, 8))]
        ((5, (3, 8)), (4, (9, 6)))
        >>> map_5[(5, (6, 10))]
        ((6, (2, 13)), (5, (5, 10)))
        >>> map_6 = multi_walkways_neighbours_a.create_for_level(6)
        >>> check_keys_have_levels(map_6)
        True
        >>> check_keys_levels_are_correct(map_6, 6)
        True
        >>> check_values_have_levels(map_6)
        True
        >>> check_neighbour_levels_are_correct(map_6)
        ()
        >>> map_6[(6, (2, 8))]
        ((6, (3, 8)), (5, (9, 6)))
        >>> map_6[(6, (6, 10))]
        ((7, (2, 13)), (6, (5, 10)))
        >>> def check_keys_are_the_same(map_a, level_a, map_b, level_b):
        ...     return all(
        ...         (_level, position) in _map
        ...         for position in {
        ...             position
        ...             for _map in [map_a, map_b]
        ...             for _, position in _map
        ...         }
        ...         for _map, _level in [(map_a, level_a), (map_b, level_b)]
        ...     )
        >>> def check_neighbours_are_the_same(map_a, level_a, map_b, level_b):
        ...     return all(
        ...         map_b[(level_b, position)] == tuple(
        ...             (neighbour_level - level_a + level_b, neighbour)
        ...             for neighbour_level, neighbour
        ...             in map_a[(level_a, position)]
        ...         )
        ...         for _, position in map_a
        ...     )
        >>> check_keys_are_the_same(map_0, 0, map_1, 1)
        True
        >>> check_keys_are_the_same(map_1, 1, map_5, 5)
        True
        >>> check_keys_are_the_same(map_5, 5, map_6, 6)
        True
        >>> check_neighbours_are_the_same(map_0, 0, map_1, 1)
        False
        >>> check_neighbours_are_the_same(map_1, 1, map_5, 5)
        True
        >>> check_neighbours_are_the_same(map_5, 5, map_6, 6)
        True
        >>> map_text_b = (
        ...   "     A       \\n"
        ...   "     A       \\n"
        ...   "  ###.#####  \\n"
        ...   "  ###.#####  \\n"
        ...   "  ## B   ##  \\n"
        ...   "  ## C   ##  \\n"
        ...   "  ##   DE..ZZ\\n"
        ...   "DE..BC   ##  \\n"
        ...   "  #########  \\n"
        ...   "  #########  \\n"
        ...   "             \\n"
        ...   "             \\n"
        ... )
        >>> walkways_b = parse_map_walkways(map_text_b)
        >>> portals_b = parse_map_portals(map_text_b, walkways_b)
        >>> walkways_neighbours_b, free_portals_b = \\
        ...     combine_map_walkways_and_portals(walkways_b, portals_b)
        >>> multi_walkways_neighbours_b, multi_free_portals_b = \\
        ...     LazyMultiMap.from_map(walkways_neighbours_b, free_portals_b)
        >>> map_b_0 = multi_walkways_neighbours_b.create_for_level(0)
        >>> check_keys_have_levels(map_b_0)
        True
        >>> check_keys_levels_are_correct(map_b_0, 0)
        True
        >>> check_values_have_levels(map_b_0)
        True
        >>> check_neighbour_levels_are_correct(map_b_0)
        ()
        >>> map_b_1 = multi_walkways_neighbours_b.create_for_level(1)
        >>> check_keys_have_levels(map_b_1)
        True
        >>> check_keys_levels_are_correct(map_b_1, 1)
        True
        >>> check_values_have_levels(map_b_1)
        True
        >>> check_neighbour_levels_are_correct(map_b_1)
        ()
        >>> # [((0, (5, 2)), 0), ((0, (5, 3)), 1), ((1, (3, 7)), 2), ((1, (2, 7)), 3), ((0, (9, 6)), 4), ((0, (10, 6), 5)]
        >>> map_b_0[(0, (5, 2))]
        ((0, (5, 3)),)
        >>> map_b_0[(0, (5, 3))]
        ((1, (3, 7)), (0, (5, 2)))
        >>> map_b_1[(1, (3, 7))]
        ((1, (2, 7)), (0, (5, 3)))
        """
        return {
            (level, walkway): (
                tuple(
                    (level, neighbour)
                    for neighbour in neighbours
                )
                if walkway not in self.portals else
                tuple(
                    (neighbour_level, neighbour)
                    for neighbour_level, neighbour in (
                        ((
                             level
                             if are_next_to_each_other(walkway, neighbour) else
                             (
                                 level + 1
                                 if walkway in self.inner_portals else
                                 level - 1
                             )
                         ), neighbour)
                        for neighbour in neighbours
                    )
                    if neighbour_level >= 0
                )
            )
            for walkway, neighbours in self.walkways_neighbours.items()
        }

    def ensure_level(self, level):
        if level not in self.maps:
            self.maps[level] = self.create_for_level(level)

        return self.maps[level]

    def find_path_length(self, start, end, include_visits=False):
        """
        >>> map_text_a = (
        ...   "     A       \\n"
        ...   "     A       \\n"
        ...   "  ###.#####  \\n"
        ...   "  ###.#####  \\n"
        ...   "  ## B   ##  \\n"
        ...   "  ## C   ##  \\n"
        ...   "  ##   DE..ZZ\\n"
        ...   "DE..BC   ##  \\n"
        ...   "  #########  \\n"
        ...   "  #########  \\n"
        ...   "             \\n"
        ...   "             \\n"
        ... )
        >>> walkways_a = parse_map_walkways(map_text_a)
        >>> portals_a = parse_map_portals(map_text_a, walkways_a)
        >>> walkways_neighbours_a, free_portals_a = \\
        ...     combine_map_walkways_and_portals(walkways_a, portals_a)
        >>> multi_walkways_neighbours_a, multi_free_portals_a = \\
        ...     LazyMultiMap.from_map(walkways_neighbours_a, free_portals_a)
        >>> multi_free_portals_a['AA'], multi_free_portals_a['ZZ']
        ((0, (5, 2)), (0, (10, 6)))
        >>> multi_walkways_neighbours_a.find_path_length(
        ...     multi_free_portals_a['AA'], multi_free_portals_a['ZZ'],
        ...     include_visits=True)
        (5, [((0, (5, 2)), 0), ((0, (5, 3)), 1), ((1, (3, 7)), 2), ((1, (2, 7)), 3), ((0, (9, 6)), 4)])
        >>> multi_walkways_neighbours_a.find_path_length(
        ...     multi_free_portals_a['AA'], multi_free_portals_a['ZZ'])
        5
        >>> map_text_b = (
        ...   "             Z L X W       C                 \\n"
        ...   "             Z P Q B       K                 \\n"
        ...   "  ###########.#.#.#.#######.###############  \\n"
        ...   "  #...#.......#.#.......#.#.......#.#.#...#  \\n"
        ...   "  ###.#.#.#.#.#.#.#.###.#.#.#######.#.#.###  \\n"
        ...   "  #.#...#.#.#...#.#.#...#...#...#.#.......#  \\n"
        ...   "  #.###.#######.###.###.#.###.###.#.#######  \\n"
        ...   "  #...#.......#.#...#...#.............#...#  \\n"
        ...   "  #.#########.#######.#.#######.#######.###  \\n"
        ...   "  #...#.#    F       R I       Z    #.#.#.#  \\n"
        ...   "  #.###.#    D       E C       H    #.#.#.#  \\n"
        ...   "  #.#...#                           #...#.#  \\n"
        ...   "  #.###.#                           #.###.#  \\n"
        ...   "  #.#....OA                       WB..#.#..ZH\\n"
        ...   "  #.###.#                           #.#.#.#  \\n"
        ...   "CJ......#                           #.....#  \\n"
        ...   "  #######                           #######  \\n"
        ...   "  #.#....CK                         #......IC\\n"
        ...   "  #.###.#                           #.###.#  \\n"
        ...   "  #.....#                           #...#.#  \\n"
        ...   "  ###.###                           #.#.#.#  \\n"
        ...   "XF....#.#                         RF..#.#.#  \\n"
        ...   "  #####.#                           #######  \\n"
        ...   "  #......CJ                       NM..#...#  \\n"
        ...   "  ###.#.#                           #.###.#  \\n"
        ...   "RE....#.#                           #......RF\\n"
        ...   "  ###.###        X   X       L      #.#.#.#  \\n"
        ...   "  #.....#        F   Q       P      #.#.#.#  \\n"
        ...   "  ###.###########.###.#######.#########.###  \\n"
        ...   "  #.....#...#.....#.......#...#.....#.#...#  \\n"
        ...   "  #####.#.###.#######.#######.###.###.#.#.#  \\n"
        ...   "  #.......#.......#.#.#.#.#...#...#...#.#.#  \\n"
        ...   "  #####.###.#####.#.#.#.#.###.###.#.###.###  \\n"
        ...   "  #.......#.....#.#...#...............#...#  \\n"
        ...   "  #############.#.#.###.###################  \\n"
        ...   "               A O F   N                     \\n"
        ...   "               A A D   M                     \\n"
        ... )
        >>> walkways_b = parse_map_walkways(map_text_b)
        >>> portals_b = parse_map_portals(map_text_b, walkways_b)
        >>> walkways_neighbours_b, free_portals_b = \\
        ...     combine_map_walkways_and_portals(walkways_b, portals_b)
        >>> multi_walkways_neighbours_b, multi_free_portals_b = \\
        ...     LazyMultiMap.from_map(
        ...         walkways_neighbours_b, free_portals_b, max_levels=50)
        >>> multi_free_portals_b['AA'], multi_free_portals_b['ZZ']
        ((0, (15, 34)), (0, (13, 2)))
        >>> multi_walkways_neighbours_b.find_path_length(
        ...     multi_free_portals_b['AA'], multi_free_portals_b['ZZ'])
        396
        """
        return find_path_length(
            self, start, end, include_visits=include_visits)


def are_next_to_each_other(lhs, rhs):
    """
    >>> are_next_to_each_other((0, 0), (0, 1))
    True
    >>> are_next_to_each_other((0, 0), (10, 1))
    False
    >>> are_next_to_each_other((0, 0), (10, 0))
    False
    >>> are_next_to_each_other((0, 0), (0, -2))
    False
    >>> are_next_to_each_other((0, 0), (0, -1))
    True
    >>> are_next_to_each_other((0, 1), (0, 0))
    True
    >>> are_next_to_each_other((10, 1), (0, 0))
    False
    >>> are_next_to_each_other((10, 0), (0, 0))
    False
    >>> are_next_to_each_other((0, -2), (0, 0))
    False
    >>> are_next_to_each_other((0, -1), (0, 0))
    True
    >>> are_next_to_each_other((0, -1), (10, 0))
    False
    >>> are_next_to_each_other((4, 5), (4, 4))
    True
    """
    l_x, l_y = lhs
    r_x, r_y = rhs

    return {abs(l_x - r_x), abs(l_y - r_y)} == {0, 1}


def split_portals(walkways_neighbours):
    """
    >>> map_text_a = (
    ...     "         A           \\n"
    ...     "         A           \\n"
    ...     "  #######.#########  \\n"
    ...     "  #######.........#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #####  B    ###.#  \\n"
    ...     "BC...##  C    ###.#  \\n"
    ...     "  ##.##       ###.#  \\n"
    ...     "  ##...DE  F  ###.#  \\n"
    ...     "  #####    G  ###.#  \\n"
    ...     "  #########.#####.#  \\n"
    ...     "DE..#######...###.#  \\n"
    ...     "  #.#########.###.#  \\n"
    ...     "FG..#########.....#  \\n"
    ...     "  ###########.#####  \\n"
    ...     "             Z       \\n"
    ...     "             Z       \\n"
    ... )
    >>> walkways_a = parse_map_walkways(map_text_a)
    >>> portals_a = parse_map_portals(map_text_a, walkways_a)
    >>> walkways_neighbours_a, free_portals_a = \\
    ...     combine_map_walkways_and_portals(walkways_a, portals_a)
    >>> tuple(map(list, map(sorted, split_portals(walkways_neighbours_a))))
    ([(6, 10), (9, 6), (11, 12)], [(2, 8), (2, 13), (2, 15)])
    """
    xs = [x for x, _ in walkways_neighbours]
    ys = [y for _, y in walkways_neighbours]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    portals = get_portals(walkways_neighbours)
    outer_portals = {
        (x, y)
        for x, y in portals
        if (
            x in (min_x, max_x)
            or y in (min_y, max_y)
        )
    }
    inner_portals = set(portals) - outer_portals
    return inner_portals, outer_portals


def get_portals(walkways_neighbours):
    """
    >>> map_text_a = (
    ...     "         A           \\n"
    ...     "         A           \\n"
    ...     "  #######.#########  \\n"
    ...     "  #######.........#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #######.#######.#  \\n"
    ...     "  #####  B    ###.#  \\n"
    ...     "BC...##  C    ###.#  \\n"
    ...     "  ##.##       ###.#  \\n"
    ...     "  ##...DE  F  ###.#  \\n"
    ...     "  #####    G  ###.#  \\n"
    ...     "  #########.#####.#  \\n"
    ...     "DE..#######...###.#  \\n"
    ...     "  #.#########.###.#  \\n"
    ...     "FG..#########.....#  \\n"
    ...     "  ###########.#####  \\n"
    ...     "             Z       \\n"
    ...     "             Z       \\n"
    ... )
    >>> walkways_a = parse_map_walkways(map_text_a)
    >>> portals_a = parse_map_portals(map_text_a, walkways_a)
    >>> walkways_neighbours_a, free_portals_a = \\
    ...     combine_map_walkways_and_portals(walkways_a, portals_a)
    >>> get_portals(walkways_neighbours_a)
    [(2, 8), (2, 13), (2, 15), (6, 10), (9, 6), (11, 12)]
    """
    return sorted(
        walkway
        for walkway, neighbours in walkways_neighbours.items()
        if any(
            not are_next_to_each_other(walkway, neighbour)
            for neighbour in neighbours
        )
    )


challenge = Challenge()
challenge.main()
