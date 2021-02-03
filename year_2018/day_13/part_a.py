#!/usr/bin/env python3
import itertools
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '57,104'
        """

        track_map = TrackMap.from_map_text(_input)
        x, y = track_map.tick_until_crash()
        # print(track_map.show(range(50, 60), range(100, 110)))

        return f'{x},{y}'


class Cart(namedtuple(
        "Cart", ("position", "direction", "intersection_direction"))):
    DIRECTION_UP = 'up'
    DIRECTION_DOWN = 'down'
    DIRECTION_RIGHT = 'right'
    DIRECTION_LEFT = 'left'

    DIRECTION_PARSE_MAP = {
        '^': DIRECTION_UP,
        'v': DIRECTION_DOWN,
        '>': DIRECTION_RIGHT,
        '<': DIRECTION_LEFT,
    }

    DIRECTION_OFFSET_MAP = {
        DIRECTION_LEFT: (-1, 0),
        DIRECTION_RIGHT: (1, 0),
        DIRECTION_UP: (0, -1),
        DIRECTION_DOWN: (0, 1),
    }

    OPPOSITE_DIRECTION_OFFSET_MAP = {
        DIRECTION_LEFT: DIRECTION_OFFSET_MAP[DIRECTION_RIGHT],
        DIRECTION_RIGHT: DIRECTION_OFFSET_MAP[DIRECTION_LEFT],
        DIRECTION_UP: DIRECTION_OFFSET_MAP[DIRECTION_DOWN],
        DIRECTION_DOWN: DIRECTION_OFFSET_MAP[DIRECTION_UP],
    }

    OFFSET_DIRECTION_MAP = {
        offset: direction
        for direction, offset in DIRECTION_OFFSET_MAP.items()
    }

    INTERSECTION_DIRECTION_LEFT = 'left'
    INTERSECTION_DIRECTION_STRAIGHT = 'straight'
    INTERSECTION_DIRECTION_RIGHT = 'right'

    INTERSECTION_DIRECTION_SEQUENCE = [
        INTERSECTION_DIRECTION_LEFT,
        INTERSECTION_DIRECTION_STRAIGHT,
        INTERSECTION_DIRECTION_RIGHT,
    ]

    OFFSET_SEQUENCE = [
        (0, -1), (1, 0), (0, 1), (-1, 0),
    ]

    INTERSECTION_OFFSET_MAP = None

    @classmethod
    def create_intersection_offset_map(cls):
        cls.INTERSECTION_OFFSET_MAP = {
            offset: {
                intersection_direction: cls.OFFSET_SEQUENCE[
                    (offset_index + intersection_direction_index + 1)
                    % len(cls.OFFSET_SEQUENCE)
                ]
                for intersection_direction_index, intersection_direction
                in enumerate(cls.INTERSECTION_DIRECTION_SEQUENCE)
            }
            for offset_index, offset in enumerate(cls.OFFSET_SEQUENCE)
        }

    @classmethod
    def from_content(cls, point, content,
                     intersection_direction=INTERSECTION_DIRECTION_LEFT):
        """
        >>> Cart.from_content((1, 2), ">")
        Cart(position=(1, 2), direction='right', intersection_direction='left')
        """
        if content not in cls.DIRECTION_PARSE_MAP:
            return None

        return cls(
            point, cls.DIRECTION_PARSE_MAP[content],
            intersection_direction)

    def tick(self, track_offsets):
        next_position = self.get_next_position()
        opposite_offset = self.get_opposite_offset()
        next_track_offsets = track_offsets[next_position]
        if len(next_track_offsets) == 2:
            next_offset, = set(next_track_offsets) - {opposite_offset}
            next_intersection_direction = self.intersection_direction
        elif len(next_track_offsets) == 4:
            next_offset = self.get_intersection_offset()
            next_intersection_direction = \
                self.get_next_intersection_direction()
        else:
            raise Exception(
                f"Can't handle {len(next_track_offsets)} track offsets")

        next_direction = self.OFFSET_DIRECTION_MAP[next_offset]
        return type(self)(
            next_position, next_direction, next_intersection_direction)

    def get_offset(self):
        return self.DIRECTION_OFFSET_MAP[self.direction]

    def get_opposite_offset(self):
        return self.OPPOSITE_DIRECTION_OFFSET_MAP[self.direction]

    def get_next_position(self):
        x, y = self.position
        d_x, d_y = self.get_offset()

        return x + d_x, y + d_y

    def get_next_intersection_direction(self):
        current_index = self.INTERSECTION_DIRECTION_SEQUENCE.index(
            self.intersection_direction)
        next_index = (
            (current_index + 1)
            % len(self.INTERSECTION_DIRECTION_SEQUENCE)
        )
        return self.INTERSECTION_DIRECTION_SEQUENCE[next_index]

    def get_intersection_offset(self):
        opposite_offset = self.OPPOSITE_DIRECTION_OFFSET_MAP[self.direction]
        return self.INTERSECTION_OFFSET_MAP[
            opposite_offset][
            self.intersection_direction]

    SHOW_MAP = {
        direction: content
        for content, direction in DIRECTION_PARSE_MAP.items()
    }

    def show(self):
        """
        >>> Cart((0, 0), 'left', 'left').show()
        '<'
        """
        return self.SHOW_MAP[self.direction]


Cart.create_intersection_offset_map()


class TrackMap:
    TRACK_OFFSETS_MAP = {
        '+': ((0, -1), (0, 1), (-1, 0), (1, 0)),
        '|': ((0, -1), (0, 1)),
        '-': ((-1, 0), (1, 0)),
        '/': {
            (True, False, True, False): ((0, -1), (-1, 0)),
            (False, True, False, True): ((0, 1), (1, 0)),
        },
        '\\': {
            (True, False, False, True): ((0, -1), (1, 0)),
            (False, True, True, False): ((0, 1), (-1, 0)),
        },
        '>': ((-1, 0), (1, 0)),
        '<': ((-1, 0), (1, 0)),
        '^': ((0, -1), (0, 1)),
        'v': ((0, -1), (0, 1)),
    }

    @classmethod
    def from_map_text(cls, map_text):
        """
        >>> track_map_a = TrackMap.from_map_text(
        ...     "/----?\\n"
        ...     "|    |\\n"
        ...     "|    |\\n"
        ...     "?----/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_a.carts
        []
        >>> track_map_a.track_offsets[(0, 0)]
        ((0, 1), (1, 0))
        >>> len(track_map_a.track_offsets)
        16
        >>> set(map(len, track_map_a.track_offsets.values()))
        {2}
        >>> track_map_b = TrackMap.from_map_text(
        ...     "/-----?\\n"
        ...     "|     |\\n"
        ...     "|  /--+--?\\n"
        ...     "|  |  |  |\\n"
        ...     "?--+--/  |\\n"
        ...     "   |     |\\n"
        ...     "   ?-----/\\n"
        ... .replace("?", "\\\\"))
        >>> len(track_map_b.track_offsets)
        38
        >>> track_map_b.track_offsets[(6, 2)]
        ((0, -1), (0, 1), (-1, 0), (1, 0))
        >>> track_map_b.track_offsets[(3, 4)]
        ((0, -1), (0, 1), (-1, 0), (1, 0))
        >>> set(map(len, track_map_b.track_offsets.values()))
        {2, 4}
        >>> track_map_c = TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_c.carts
        [Cart(position=(2, 0), direction='right', intersection_direction='left'), Cart(position=(9, 3), direction='down', intersection_direction='left')]
        """
        track_map = dict(cls.get_points_with_content(map_text))
        track_offsets = {
            point: cls.get_track_offsets(point, content, track_map)
            for point, content in track_map.items()
        }
        carts = sorted(filter(None, (
            Cart.from_content(point, content)
            for point, content in track_map.items()
        )))

        return cls(track_offsets, carts)

    @classmethod
    def get_track_offsets(cls, point, content, tracks_map):
        """
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(1, 0): '-', (0, 1): '|'})
        ((0, 1), (1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(1, 0): '>', (0, 1): '^'})
        ((0, 1), (1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(1, 0): '<', (0, 1): 'v'})
        ((0, 1), (1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(1, 0): '+', (0, 1): '+'})
        ((0, 1), (1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(-1, 0): '-', (0, -1): '|'})
        ((0, -1), (-1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(-1, 0): '-', (0, -1): '|', (1, 0): '|'})
        ((0, -1), (-1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '/', {(-1, 0): '-', (0, -1): '|', (0, 1): '-'})
        ((0, -1), (-1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '\\\\', {(1, 0): '-', (0, -1): '|'})
        ((0, -1), (1, 0))
        >>> TrackMap.get_track_offsets(
        ...     (0, 0), '\\\\', {(-1, 0): '-', (0, 1): '|'})
        ((0, 1), (-1, 0))
        """
        offsets_or_map = cls.TRACK_OFFSETS_MAP[content]
        if isinstance(offsets_or_map, dict):
            offsets_map = offsets_or_map
            x, y = point
            goes_up = tracks_map.get((x, y - 1)) in ('|', '+', '^', 'v')
            goes_down = tracks_map.get((x, y + 1)) in ('|', '+', '^', 'v')
            goes_left = tracks_map.get((x - 1, y)) in ('-', '+', '>', '<')
            goes_right = tracks_map.get((x + 1, y)) in ('-', '+', '>', '<')
            if goes_up == goes_down:
                raise Exception(
                    f"Point {point} with content {content} goes both up and "
                    f"down")
            if goes_left == goes_right:
                raise Exception(
                    f"Point {point} with content {content} goes both left and "
                    f"right")
            offsets = offsets_map[(goes_up, goes_down, goes_left, goes_right)]
        else:
            offsets = offsets_or_map

        return offsets

    @classmethod
    def get_points_with_content(cls, map_text):
        """
        >>> list(TrackMap.get_points_with_content(
        ...     "/-\\\\\\n"
        ...     "| |\\n"
        ...     "\\-/\\n"
        ... ))
        [((0, 0), '/'), ((1, 0), '-'), ((2, 0), '\\\\'), ((0, 1), '|'), \
((2, 1), '|'), ((0, 2), '\\\\'), ((1, 2), '-'), ((2, 2), '/')]
        """
        return (
            ((x, y), content)
            for y, line in enumerate(filter(None, map_text.splitlines()))
            for x, content in enumerate(line)
            if content != ' '
        )

    def __init__(self, track_offsets, carts):
        self.track_offsets = track_offsets
        self.carts = carts

    def get_first_crash_position(self):
        """
        >>> TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\")).get_first_crash_position()
        >>> track_map_a = TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_a.tick_until_crash(14)
        (7, 3)
        >>> track_map_a.get_first_crash_position()
        (7, 3)
        """
        crashed_positions = self.get_crashed_positions()

        return min(crashed_positions, default=None)

    def tick_until_crash(self, limit=None, return_start_position=False,
                         min_start_position=None):
        """
        >>> track_map_a = TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_a.tick_until_crash(1)
        >>> print(track_map_a.show().replace('\\\\', '?'))
        /-->?
        |   |  /----?
        | /-+--+-?  |
        | | |  | |  |
        ?-+-/  ?->--/
          ?------/
        >>> track_map_b = TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_b.tick_until_crash(14) and None
        >>> print(track_map_b.show().replace('\\\\', '?'))
        /---?
        |   |  /----?
        | /-+--+-?  |
        | | |  X |  |
        ?-+-/  ?-+--/
          ?------/
        >>> track_map_b = TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_b.tick_until_crash() and None
        >>> print(track_map_b.show().replace('\\\\', '?'))
        /---?
        |   |  /----?
        | /-+--+-?  |
        | | |  X |  |
        ?-+-/  ?-+--/
          ?------/
        """
        crash_position = self.get_first_crash_position()
        if return_start_position:
            crash_position_or_positions = crash_position, None
        else:
            crash_position_or_positions = crash_position
        if crash_position:
            return crash_position_or_positions
        if limit is None:
            steps = itertools.count()
        else:
            steps = range(limit)
        for _ in steps:
            crash_position_or_positions = self.tick(
                return_start_position=return_start_position,
                min_start_position=min_start_position)
            if crash_position_or_positions:
                break

        return crash_position_or_positions

    def tick(self, return_start_position=False, min_start_position=None):
        """
        >>> track_map_a = TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_a.tick()
        >>> print(track_map_a.show().replace('\\\\', '?'))
        /-->?
        |   |  /----?
        | /-+--+-?  |
        | | |  | |  |
        ?-+-/  ?->--/
          ?------/
        """
        carts_by_position = self.get_carts_by_position()
        crash_position = self.get_first_crash_position()
        if crash_position:
            if return_start_position:
                return crash_position, None
            else:
                return crash_position
        for cart_index, cart in enumerate(sorted(self.carts)):
            if min_start_position is not None:
                if cart.position <= min_start_position:
                    continue
            next_cart = cart.tick(self.track_offsets)

            del carts_by_position[cart.position]
            carts = carts_by_position\
                .setdefault(next_cart.position, [])
            carts.append(next_cart)
            self.carts[cart_index] = next_cart
            if len(carts) > 1:
                if return_start_position:
                    return next_cart.position, cart.position
                else:
                    return next_cart.position

        if return_start_position:
            return None, None
        else:
            return None

    SHOW_MAP = {
        offsets: content
        for content, offsets_or_map in TRACK_OFFSETS_MAP.items()
        for offsets in (
            offsets_or_map.values()
            if isinstance(offsets_or_map, dict) else
            [offsets_or_map]
        )
        if content not in ('<', '>', '^', 'v')
    }

    def show(self, x_range=None, y_range=None):
        """
        >>> print(TrackMap.from_map_text(
        ...     "/----?\\n"
        ...     "|    |\\n"
        ...     "|    |\\n"
        ...     "?----/\\n"
        ... .replace("?", "\\\\")).show().replace('\\\\', '?'))
        /----?
        |    |
        |    |
        ?----/
        >>> print(TrackMap.from_map_text(
        ...     "/-----?\\n"
        ...     "|     |\\n"
        ...     "|  /--+--?\\n"
        ...     "|  |  |  |\\n"
        ...     "?--+--/  |\\n"
        ...     "   |     |\\n"
        ...     "   ?-----/\\n"
        ... .replace("?", "\\\\")).show().replace('\\\\', '?'))
        /-----?
        |     |
        |  /--+--?
        |  |  |  |
        ?--+--/  |
           |     |
           ?-----/
        >>> print(TrackMap.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\")).show().replace('\\\\', '?'))
        /->-?
        |   |  /----?
        | /-+--+-?  |
        | | |  | v  |
        ?-+-/  ?-+--/
          ?------/
        """
        if x_range is None:
            max_x = max(x for x, _ in self.track_offsets)
            x_range = range(max_x + 1)
        if y_range is None:
            max_y = max(y for _, y in self.track_offsets)
            y_range = range(max_y + 1)

        carts_by_position = self.get_carts_by_position()

        return "\n".join(
            "".join(
                (
                    carts_by_position[(x, y)][0].show()
                    if len(carts_by_position[(x, y)]) == 1 else
                    'X'
                )
                if (x, y) in carts_by_position else
                self.SHOW_MAP.get(self.track_offsets.get((x, y)), ' ')
                for x in x_range
            ).rstrip()
            for y in y_range
        )

    def get_crashed_positions(self):
        carts_by_position = self.get_carts_by_position()
        return (
            position
            for position, carts in carts_by_position.items()
            if len(carts) > 1
        )

    def get_carts_by_position(self):
        return {
            position: list(carts)
            for position, carts
            in itertools.groupby(sorted(
                self.carts, key=self.cart_by_position),
                key=self.cart_by_position)
        }

    def cart_by_position(self, cart):
        return cart.position


Challenge.main()
challenge = Challenge()
