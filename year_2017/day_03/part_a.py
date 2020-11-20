#!/usr/bin/env python3
import math

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve() > 295
        True
        >>> Challenge().default_solve()
        480
        """
        return Grid().get_point_for_index(int(_input.strip()))\
            .manhattan_length()


class Grid:
    def get_point_for_index(self, index):
        """
        >>> Grid().get_point_for_index(1)
        Point2D(x=0, y=0)
        >>> Grid().get_point_for_index(2)
        Point2D(x=1, y=0)
        >>> Grid().get_point_for_index(9)
        Point2D(x=1, y=1)
        """
        ring = self.get_ring_for_index(index)
        if ring == 0:
            return utils.Point2D.ZERO_POINT
        side_index, side_offset = self.get_side_index_and_offset(ring, index)
        if side_index == 0:
            return utils.Point2D(ring, ring).offset((0, -(side_offset + 1)))
        elif side_index == 1:
            return utils.Point2D(ring, -ring).offset((-(side_offset + 1), 0))
        elif side_index == 2:
            return utils.Point2D(-ring, -ring).offset((0, side_offset + 1))
        elif side_index == 3:
            return utils.Point2D(-ring, ring).offset(((side_offset + 1), 0))

        raise Exception(f"Mis-calculated side for {index}")

    def get_side_index_and_offset(self, ring, index):
        """
        >>> Grid().get_side_index_and_offset(1, 2)
        (0, 0)
        >>> Grid().get_side_index_and_offset(1, 9)
        (3, 1)
        """
        previous_square = (ring * 2 - 1) ** 2
        side_length = ring * 2
        side_index = (index - previous_square - 1) // side_length
        side_offset = (index - previous_square - 1) % side_length

        return side_index, side_offset

    def get_ring_for_index(self, index):
        """
        >>> Grid().get_ring_for_index(1)
        0
        >>> Grid().get_ring_for_index(2)
        1
        >>> Grid().get_ring_for_index(9)
        1
        >>> {Grid().get_ring_for_index(_index) for _index in range(2, 10)}
        {1}
        >>> Grid().get_ring_for_index(10)
        2
        >>> Grid().get_ring_for_index(25)
        2
        >>> {Grid().get_ring_for_index(_index) for _index in range(10, 26)}
        {2}
        >>> {Grid().get_ring_for_index(_index) for _index in range(26, 50)}
        {3}
        """
        if index < 1:
            raise Exception(f"Index must be at least 1")
        return math.floor(math.sqrt(index - 1) + 1) // 2


challenge = Challenge()
challenge.main()
