#!/usr/bin/env python3
import functools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        390
        """
        return len(PointList.from_points_text(_input).get_constellations())


class PointList:
    @classmethod
    def from_points_text(cls, points_text):
        """
        >>> point_list_a = PointList.from_points_text(
        ...     " 0,0,0,0\\n"
        ...     " 3,0,0,0\\n"
        ...     " 0,3,0,0\\n"
        ...     " 0,0,3,0\\n"
        ...     " 0,0,0,3\\n"
        ...     " 0,0,0,6\\n"
        ...     " 9,0,0,0\\n"
        ...     "12,0,0,0\\n"
        ... )
        >>> len(point_list_a.points)
        8
        >>> point_list_a.points[-1]
        Point(x=12, y=0, z=0, t=0)
        """
        non_empty_lines = filter(None, points_text.splitlines())
        return cls(list(map(Point.from_comma_delimited_text, non_empty_lines)))

    def __init__(self, points):
        """
        >>> len(PointList.from_points_text(
        ...     "1,-1,-1,-2\\n"
        ...     "-2,-2,0,1\\n"
        ...     "0,2,1,3\\n"
        ...     "-2,3,-2,1\\n"
        ...     "0,2,3,-2\\n"
        ...     "-1,-1,1,-2\\n"
        ...     "0,-2,-1,0\\n"
        ...     "-2,2,3,-1\\n"
        ...     "1,2,2,0\\n"
        ...     "-1,-2,0,-2\\n"
        ... ).get_constellations())
        8
        """
        self.points = points

    def get_constellations(self):
        """
        >>> point_list_a = PointList.from_points_text(
        ...     " 0,0,0,0\\n"
        ...     " 3,0,0,0\\n"
        ...     " 0,3,0,0\\n"
        ...     " 0,0,3,0\\n"
        ...     " 0,0,0,3\\n"
        ...     " 0,0,0,6\\n"
        ...     " 9,0,0,0\\n"
        ...     "12,0,0,0\\n"
        ... )
        >>> constellations_a = point_list_a.get_constellations()
        >>> tuple(
        ...     len(_constellation.points)
        ...     for _constellation in constellations_a
        ... )
        (6, 2)
        >>> Point(x=12, y=0, z=0, t=0) in constellations_a[1].points
        True
        >>> point_list_b = PointList.from_points_text(
        ...     " 0,0,0,0\\n"
        ...     " 3,0,0,0\\n"
        ...     " 0,3,0,0\\n"
        ...     " 0,0,3,0\\n"
        ...     " 0,0,0,3\\n"
        ...     " 0,0,0,6\\n"
        ...     " 9,0,0,0\\n"
        ...     "12,0,0,0\\n"
        ...     "6,0,0,0\\n"
        ... )
        >>> constellations_b = point_list_b.get_constellations()
        >>> tuple(
        ...     len(_constellation.points)
        ...     for _constellation in constellations_b
        ... )
        (9,)
        >>> len(PointList.from_points_text(
        ...     "-1,2,2,0\\n"
        ...     "0,0,2,-2\\n"
        ...     "0,0,0,-2\\n"
        ...     "-1,2,0,0\\n"
        ...     "-2,-2,-2,2\\n"
        ...     "3,0,2,-1\\n"
        ...     "-1,3,2,2\\n"
        ...     "-1,0,-1,0\\n"
        ...     "0,2,1,-2\\n"
        ...     "3,0,0,0\\n"
        ... ).get_constellations())
        4
        >>> len(PointList.from_points_text(
        ...     "1,-1,0,1\\n"
        ...     "2,0,-1,0\\n"
        ...     "3,2,-1,0\\n"
        ...     "0,0,3,1\\n"
        ...     "0,0,-1,-1\\n"
        ...     "2,3,-2,0\\n"
        ...     "-2,2,0,0\\n"
        ...     "2,-2,0,-1\\n"
        ...     "1,-1,0,-1\\n"
        ...     "3,2,0,2\\n"
        ... ).get_constellations())
        3
        >>> len(PointList.from_points_text(
        ...     "1,-1,-1,-2\\n"
        ...     "-2,-2,0,1\\n"
        ...     "0,2,1,3\\n"
        ...     "-2,3,-2,1\\n"
        ...     "0,2,3,-2\\n"
        ...     "-1,-1,1,-2\\n"
        ...     "0,-2,-1,0\\n"
        ...     "-2,2,3,-1\\n"
        ...     "1,2,2,0\\n"
        ...     "-1,-2,0,-2\\n"
        ... ).get_constellations())
        8
        """
        constellations = []
        for point in self.points:
            matching_constellations = [
                constellation
                for constellation in constellations
                if constellation.can_add(point)
            ]
            if not matching_constellations:
                constellation = Constellation((point,))
                constellations.append(constellation)
            elif len(matching_constellations) == 1:
                constellation, = matching_constellations
                constellation.add(point)
            else:
                first_constellation, *rest = matching_constellations
                first_constellation.add(point)
                for other in rest:
                    first_constellation.absorb(other)
                    constellations.remove(other)

        return constellations


class Constellation:
    def __init__(self, points=None):
        if points:
            self.points = set(points)
        else:
            self.points = set()
        self.neighbourhood = functools.reduce(set.__or__, (
            set(point.get_stellar_neighbourhood())
            for point in self.points
        ), set())

    def can_add(self, point):
        """
        >>> Constellation().can_add(Point(0, 0, 0, 0))
        True
        >>> Constellation((Point(0, 0, 0, 0),)).can_add(Point(0, 0, 0, 0))
        True
        """
        return (not self.points) or (point in self.neighbourhood)

    def add(self, point):
        self.points.add(point)
        self.neighbourhood.update(point.get_stellar_neighbourhood())

    def absorb(self, other):
        self.points.update(other.points)
        self.neighbourhood.update(other.neighbourhood)


class Point(utils.Point4D):
    def get_stellar_neighbourhood(self):
        """
        >>> Point(0, 0, 0, 0) in {Point(0, 0, 0, 0)}
        True
        >>> Point(0, 0, 0, 0) \\
        ...     in set(Point(0, 0, 0, 0).get_stellar_neighbourhood())
        True
        """
        return self.get_manhattan_neighbourhood(3)


challenge = Challenge()
challenge.main()
