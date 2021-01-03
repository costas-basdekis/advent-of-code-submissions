#!/usr/bin/env python3
import itertools
from typing import Iterable

import utils

from year_2019.day_19.part_a import get_scan_point


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        7621042
        """
        scan = DynamicScan(_input)
        common_corner = find_square(scan, 100, 100, 2000)
        if not common_corner:
            raise Exception("Could not find common corner")

        x, y = common_corner
        solution = x * 10000 + y

        return solution


def find_square(scan, width, height, count):
    """
    >>> find_square(DictScan.from_print(
    ...     "#.......\\n"
    ...     ".#......\\n"
    ...     "..##....\\n"
    ...     "...###..\\n"
    ...     "....###.\\n"
    ... ), 2, 2, 10)
    (4, 3)
    >>> find_square(DictScan.from_print(
    ...     "#..........\\n"
    ...     ".#.........\\n"
    ...     "..##.......\\n"
    ...     "...###.....\\n"
    ...     "....###....\\n"
    ...     ".....####..\\n"
    ...     "......####.\\n"
    ...     "......####.\\n"
    ...     ".......###.\\n"
    ...     "........##.\\n"
    ...     "...........\\n"
    ... ), 2, 2, 10)
    (4, 3)
    >>> find_square(DictScan.from_print(
    ...     "#.........................................\\n"
    ...     ".#........................................\\n"
    ...     "..##......................................\\n"
    ...     "...###....................................\\n"
    ...     "....###...................................\\n"
    ...     ".....####.................................\\n"
    ...     "......#####...............................\\n"
    ...     "......######..............................\\n"
    ...     ".......#######............................\\n"
    ...     "........########..........................\\n"
    ...     ".........#########........................\\n"
    ...     "..........#########.......................\\n"
    ...     "...........##########.....................\\n"
    ...     "...........############...................\\n"
    ...     "............############..................\\n"
    ...     ".............#############................\\n"
    ...     "..............##############..............\\n"
    ...     "...............###############............\\n"
    ...     "................###############...........\\n"
    ...     "................#################.........\\n"
    ...     ".................##################.......\\n"
    ...     "..................##################......\\n"
    ...     "...................###################....\\n"
    ...     "....................####################..\\n"
    ...     ".....................###################..\\n"
    ...     ".....................###################..\\n"
    ...     "......................##################..\\n"
    ...     ".......................#################..\\n"
    ...     "........................################..\\n"
    ...     ".........................###############..\\n"
    ...     "..........................##############..\\n"
    ...     "..........................##############..\\n"
    ...     "...........................#############..\\n"
    ...     "............................############..\\n"
    ...     ".............................###########..\\n"
    ... ), 10, 10, 34)
    (25, 20)
    """
    y_and_lines = enumerate(find_lines(scan, count))
    for last_n_y_and_lines in last_n_items(y_and_lines, height):
        finished, result = check_square(last_n_y_and_lines, width)
        if finished:
            return result

    return None


def check_square(y_and_lines, width):
    """
    >>> check_square(
    ...     list(enumerate([(3, 3), (4, 3)], 2)), 2)
    (True, (4, 2))
    """
    start_y, first_line = y_and_lines[0]
    _, last_line = y_and_lines[-1]
    lines = [line for _, line in y_and_lines]
    if not all(lines):
        return False, "Some lines were empty"

    common_area = find_common_area(first_line, last_line)
    if not common_area:
        return False, "There was no common area between first and last"

    start_x, common_length = common_area
    if common_length < width:
        return False, \
               f"Common length {common_length} was less than width {width}"

    return True, (start_x, start_y)


def last_n_items(iterable, count):
    """
    >>> list(last_n_items(range(5), 2))
    [(0, 1), (1, 2), (2, 3), (3, 4)]
    >>> list(last_n_items(range(10), 3))
    [(0, 1, 2), (1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 6), (5, 6, 7), (6, 7, 8), (7, 8, 9)]
    """
    stack = []
    for item in iterable:
        stack.append(item)
        if len(stack) == count:
            yield tuple(stack)
            stack.pop(0)


def get_common_areas(scan, count):
    """
    >>> get_common_areas(DictScan.from_print(
    ...     "#.........\\n"
    ...     ".#........\\n"
    ...     "..##......\\n"
    ...     "...###....\\n"
    ...     "....###...\\n"
    ...     ".....####.\\n"
    ...     "......####\\n"
    ...     "......####\\n"
    ...     ".......###\\n"
    ...     "........##\\n"
    ... ), 5)
    [None, None, (3, 1), (4, 2)]
    """
    common_areas = []
    lines = find_lines(scan, count)
    previous = next(lines)
    for current in lines:
        common_areas.append(find_common_area(previous, current))
        previous = current

    return common_areas


def find_common_area(previous, current):
    """
    >>> find_common_area((1, 1), (1, 1))
    (1, 1)
    >>> find_common_area((1, 2), (2, 1))
    (2, 1)
    >>> find_common_area((10, 5), (9, 20))
    (10, 5)
    >>> find_common_area((10, 5), (20, 20))
    >>> find_common_area((10, 5), (10, 4))
    (10, 4)
    >>> find_common_area((3, 3), (4, 3))
    (4, 2)
    """
    if not previous or not current:
        return None
    previous_start, previous_length = previous
    current_start, current_length = current

    previous_end = previous_start + previous_length - 1
    current_end = current_start + current_length - 1

    start = max(previous_start, current_start)
    end = min(previous_end, current_end)
    if end < start:
        return None

    length = end - start + 1

    return start, length


def find_lines(scan, count):
    """
    >>> list(find_lines(DictScan.from_print(
    ...     "#.........\\n"
    ...     ".#........\\n"
    ...     "..##......\\n"
    ...     "...###....\\n"
    ...     "....###...\\n"
    ...     ".....####.\\n"
    ...     "......####\\n"
    ...     "......####\\n"
    ...     ".......###\\n"
    ...     "........##\\n"
    ... ), 5))
    [(0, 1), (1, 1), (2, 2), (3, 3), (4, 3)]
    """
    previous_start, previous_length = 0, 1
    yield previous_start, previous_length

    for y in range(1, count):
        next_line = find_next_line(scan, y, previous_start, previous_length)
        yield next_line
        if next_line:
            previous_start, previous_length = next_line


def find_next_line(scan, y, previous_start, previous_length):
    """
    >>> find_next_line(
    ...     DictScan.from_list([0] * 9 + [1] * 2 + [0] * 1, 9),
    ...     9, 8, 2)
    (9, 2)
    >>> find_next_line(DictScan.from_print("...###...."), 0, 2, 2)
    (3, 3)
    >>> find_next_line(DictScan.from_print("....###..."), 0, 3, 3)
    (4, 3)
    >>> find_next_line(DictScan.from_print(".....####."), 0, 4, 3)
    (5, 4)
    """
    for x in range(previous_start, previous_start + 10):
        if scan[(x, y)]:
            start = x
            break
    else:
        return None

    previous_end = previous_start + previous_length
    end = None
    for x in itertools.count(max(previous_end - 1, start)):
        if not scan[(x, y)]:
            break
        end = x
    else:
        raise Exception(
            f"Could not find end for y={y} after x={start} with previous "
            f"{previous_start} + {previous_length}")

    if not end:
        raise Exception(
            f"Could not find end for y={y} after x={start} with previous "
            f"{previous_start} + {previous_length}")

    return start, end - start + 1


class Scan:
    def __getitem__(self, item):
        if not isinstance(item, Iterable):
            raise Exception(f"Key must be iterable not {item}")

        x, y = item
        return self.get_scan_point(x, y)

    def get_scan_point(self, x, y):
        raise NotImplementedError()

    SCAN_SHOW_MAP = {
        1: "#",
        0: ".",
    }

    def show(self, width_or_range, height_or_range):
        if isinstance(width_or_range, int):
            width = width_or_range
            width_range = list(range(width))
        else:
            width_range = list(width_or_range)
        if isinstance(height_or_range, int):
            height = height_or_range
            height_range = list(range(height))
        else:
            height_range = list(height_or_range)
        return "\n".join(
            "".join(
                self.SCAN_SHOW_MAP[self[(x, y)]]
                for x in width_range
            )
            for y in height_range
        )


class DictScan(Scan):
    @classmethod
    def from_list(cls, values, y):
        """
        >>> ds = DictScan.from_list([0] * 8 + [1] * 2 + [0] * 1, 9)
        >>> [ds[(x, 9)] for x in range(11)]
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0]
        """
        return cls({
            (x, y): value
            for x, value in enumerate(values)
        })

    SCAN_PARSE_MAP = {
        "#": 1,
        ".": 0,
    }

    @classmethod
    def from_print(cls, printed_scan):
        """
        >>> DictScan.from_print(
        ...     "#.\\n"
        ...     ".#\\n"
        ... ).static_scan
        {(0, 0): 1, (1, 0): 0, (0, 1): 0, (1, 1): 1}
        >>> print(DictScan.from_print(
        ...     "#.........\\n"
        ...     ".#........\\n"
        ...     "..##......\\n"
        ...     "...###....\\n"
        ...     "....###...\\n"
        ...     ".....####.\\n"
        ...     "......####\\n"
        ...     "......####\\n"
        ...     ".......###\\n"
        ...     "........##\\n"
        ... ).show(10, 10))
        #.........
        .#........
        ..##......
        ...###....
        ....###...
        .....####.
        ......####
        ......####
        .......###
        ........##
        """
        lines = printed_scan.splitlines()
        non_empty_lines = list(filter(None, lines))
        return cls({
            (x, y): cls.SCAN_PARSE_MAP[point]
            for y, line in enumerate(non_empty_lines)
            for x, point in enumerate(line)
        })

    def __init__(self, static_scan):
        self.static_scan = static_scan

    def get_scan_point(self, x, y):
        return self.static_scan[(x, y)]


class DynamicScan(Scan):
    def __init__(self, program_text):
        self.program_text = program_text

    def get_scan_point(self, x, y):
        return get_scan_point(self.program_text, x, y)


challenge = Challenge()
challenge.main()
