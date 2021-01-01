#!/usr/bin/env python3
import utils

from year_2018.day_13 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        '67,74'
        """

        track_map = TrackMapExtended.from_map_text(_input)
        x, y = track_map.tick_until_single_cart_left()
        # print(track_map.show(range(50, 60), range(100, 110)))

        return f'{x},{y}'


class TrackMapExtended(part_a.TrackMap):
    def tick_until_single_cart_left(self):
        """
        >>> track_map_a = TrackMapExtended.from_map_text(
        ...     "/>-<?\\n"
        ...     "|   |\\n"
        ...     "| /<+-?\\n"
        ...     "| | | v\\n"
        ...     "?>+</ |\\n"
        ...     "  |   ^\\n"
        ...     "  ?<->/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_a.tick_until_single_cart_left()
        (6, 4)
        >>> print(track_map_a.show().replace('\\\\', '?'))
        /---?
        |   |
        | /-+-?
        | | | |
        ?-+-/ ^
          |   |
          ?---/
        """
        self.remove_crashes()
        if len(self.carts) % 2 != 1:
            raise Exception(
                f"Odd number of carts are required, not {len(self.carts)}")
        start_position = None
        while len(self.carts) > 1:
            crash_position, start_position = self.tick_until_crash(
                return_start_position=True, min_start_position=start_position)
            cart_count_before_removal = len(self.carts)
            cart_positions_before_removal = \
                [cart.position for cart in self.carts]
            self.remove_crashes({crash_position})
            if len(self.carts) % 2 != 1:
                raise Exception(
                    f"Expected to end up with odd number of carts after a "
                    f"crash at {crash_position}, but got {len(self.carts)}: "
                    f"{[cart.position for cart in self.carts]} "
                    f"({cart_count_before_removal} before removal: "
                    f"{cart_positions_before_removal})")

        if len(self.carts) != 1:
            raise Exception(
                f"Expected to result with 1 cart, but had {len(self.carts)}")
        cart, = self.carts

        return cart.position

    def remove_crashes(self, crashed_positions=None):
        """
        >>> track_map_a = TrackMapExtended.from_map_text(
        ...     "/->-?\\n"
        ...     "|   |  /----?\\n"
        ...     "| /-+--+-?  |\\n"
        ...     "| | |  | v  |\\n"
        ...     "?-+-/  ?-+--/\\n"
        ...     "  ?------/\\n"
        ... .replace("?", "\\\\"))
        >>> track_map_a.tick_until_crash(14) and None
        >>> track_map_a.remove_crashes()
        >>> print(track_map_a.show().replace('\\\\', '?'))
        /---?
        |   |  /----?
        | /-+--+-?  |
        | | |  | |  |
        ?-+-/  ?-+--/
          ?------/
        """
        if crashed_positions is None:
            crashed_positions = set(self.get_crashed_positions())

        self.carts = [
            cart
            for cart in self.carts
            if cart.position not in crashed_positions
        ]


challenge = Challenge()
challenge.main()
