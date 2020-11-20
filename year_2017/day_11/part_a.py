#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        794
        """
        directions = DirectionsRotator()\
            .rotate_directions(_input.strip().split(','))
        return utils.PointHex(0, 0).move_many(directions)\
            .step_distance(utils.PointHex(0, 0))


class DirectionsRotator:
    ROTATION_MAP = {
        'n': utils.PointHex.E,
        'nw': utils.PointHex.NE,
        'sw': utils.PointHex.NW,
        's': utils.PointHex.W,
        'se': utils.PointHex.SW,
        'ne': utils.PointHex.SE,
    }

    def rotate_directions(self, directions):
        return [
            self.ROTATION_MAP[direction]
            for direction in directions
        ]


challenge = Challenge()
challenge.main()
