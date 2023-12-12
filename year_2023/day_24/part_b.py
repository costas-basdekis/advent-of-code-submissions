#!/usr/bin/env python3
from itertools import count, combinations
from typing import Iterable, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, Point3D
from year_2023.day_24 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        pass
        """
        >>> Challenge().default_solve()
        42
        """
        hailstone = CloudExtended\
            .from_text(_input)\
            .get_colliding_hailstone()
        return int(hailstone.position.x + hailstone.position.y + hailstone.position.z)


class CloudExtended(part_a.Cloud):
    def get_colliding_hailstone(self) -> part_a.Hailstone:
        """
        >>> print(CloudExtended.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').get_colliding_hailstone())
        24.0, 13.0, 10.0 @ -3.0, 1.0, 2.0
        """

        """
        https://www.reddit.com/r/adventofcode/comments/18pnycy/comment/kxqjg33/
        A little linear algebra makes part 2 very straightforward. You don't even need to solve a system of equations. It helps to view everything relative to hailstone 0. Let position_x and velocity_x be the position and velocity of hailstone x.

        Stones 1 and 2, relative to stone 0:
        p1 = position_1 - position_0
        v1 = velocity_1 - velocity_0
        p2 = position_2 - position_0
        v2 = velocity_2 - velocity_0
        
        Let t1 and t2 be the times that the rock collides with hailstones 1 and 2 respectively.
        
        Viewed from hailstone 0, the two collisions are thus at
        p1 + t1 * v1
        p2 + t2 * v2
        
        Hailstone 0 is always at the origin, thus its collision is at 0. Since all three collisions must form a straight line, the above two collision vectors must be collinear, and their cross product will be 0:
        
        (p1 + t1 * v1) x (p2 + t2 * v2) = 0
        
        Cross product is distributive with vector addition and compatible with scalar multiplication, so the above can be expanded:
        
        (p1 x p2) + t1 * (v1 x p2) + t2 * (p1 x v2) + t1 * t2 * (v1 x v2) = 0
        
        This is starting to look like a useful linear equation, except for that t1 * t2 term. Let's try to get rid of it. Dot product and cross product interact in a useful way. For arbitrary vectors a and b:
        
        (a x b) * a = (a x b) * b = 0.
        
        We can use this property to get rid of the t1 * t2 term. Let's take the dot product with v2. Note that dot product is also distributive with vector addition and compatible with scalar multiplication. The dot product zeros out both the t2 and t1*t2 terms, leaving a simple linear equation for t1:
        
        (p1 x p2) * v2 + t1 * (v1 x p2) * v2 = 0
        
        t1 = -((p1 x p2) * v2) / ((v1 x p2) * v2)
        
        If we use v1 instead of v2 for the dot product, we get this instead:
        
        (p1 x p2) * v1 + t2 * (p1 x v2) * v1 = 0
        
        t2 = -((p1 x p2) * v1) / ((p1 x v2) * v1)
        
        Once we have t1 and t2 we can compute the locations (in absolute coordinates) of the two collisions and work backwards to find the velocity and initial position of the rock.
        
        c1 = position_1 + t1 * velocity_1
        c2 = position_2 + t2 * velocity_2
        v = (c2 - c1) / (t2 - t1)
        p = c1 - t1 * v
        """

        h0 = self.hailstones[0]
        h1 = self.hailstones[1]
        h2 = self.hailstones[2]
        p1 = h1.position.difference(h0.position)
        v1 = h1.velocity.difference(h0.velocity)
        p2 = h2.position.difference(h0.position)
        v2 = h2.velocity.difference(h0.velocity)
        cross = p1.cross(p2)
        t1 = -cross.inner(v2) / (v1.cross(p2).inner(v2))
        t2 = -cross.inner(v1) / (p1.cross(v2).inner(v1))
        c1 = h1.position.offset(h1.velocity, factor=t1)
        c2 = h2.position.offset(h2.velocity, factor=t2)
        velocity = c2.difference(c1).resize(1 / (t2 - t1))
        position = c1.difference(velocity.resize(t1))
        hailstone = part_a.Hailstone(position, velocity)
        return hailstone

    def find_collision_timely_line(self, initial_first_time: int = 0, initial_second_time: int = 1, debugger: Debugger = Debugger(enabled=False)) -> part_a.Hailstone:
        """
        >>> print(CloudExtended.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').find_collision_timely_line())
        24.0, 13.0, 10.0 @ -3.0, 1.0, 2.0
        """
        indexes = list(range(len(self.hailstones)))
        non_integer_count = 0
        for second_time in count(initial_second_time):
            for first_time in range(initial_first_time, second_time):
                for index_a, index_b in combinations(indexes, 2):
                    for first_index, second_index in [(index_a, index_b), (index_b, index_a)]:
                        debugger.step()
                        hailstone, is_integer, collides_with_everything = self.test_timely_collision(first_index, second_index, first_time, second_time)
                        if not is_integer:
                            non_integer_count += 1
                        if collides_with_everything:
                            return hailstone
                        if debugger.should_report() or collides_with_everything:
                            debugger.default_report_if(
                                f"Looking at t={first_time}-{second_time} "
                                f"(last check for indexes #{first_index} and #{second_index}), "
                                f"skipped {non_integer_count} non-integers, "
                                f"hailstone {hailstone}",
                            )
            initial_first_time = 0
        raise Exception("No collision found")

    def test_timely_collision(self, first_index: int, second_index: int, first_time: float, second_time: float) -> Tuple[part_a.Hailstone, bool, bool]:
        """
        >>> CloudExtended.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').test_timely_collision(4, 1, 1, 3)
        (Hailstone(position=Point3D(x=24.0, y=13.0, z=10.0), velocity=Point3D(x=-3.0, y=1.0, z=2.0)), True, True)
        """
        first = self.hailstones[first_index]
        second = self.hailstones[second_index]
        first_point: Point3D = first.position.offset(first.velocity, factor=first_time)
        second_point: Point3D = second.position.offset(second.velocity, factor=second_time)
        velocity = second_point.difference(first_point).resize(1 / (second_time - first_time))
        position = first_point.offset(velocity, factor=-first_time)
        hailstone = part_a.Hailstone(position, velocity)
        is_integer = all(
            int(value) == value
            for values in [position, velocity]
            for value in values
        )
        if not is_integer:
            return hailstone, is_integer, False
        collides_with_everything = all(
            position is not None
            and time1 == time2
            and int(time1) == time1
            for _, time1, time2, position
            in self.get_collision_points_with(hailstone)
        )
        return hailstone, is_integer, collides_with_everything

    def find_collision_line(self, initial_first_time: int = 0, initial_second_time: int = 1, debugger: Debugger = Debugger(enabled=False)) -> part_a.Hailstone:
        """
        >>> print(CloudExtended.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').find_collision_timely_line())
        24.0, 13.0, 10.0 @ -3.0, 1.0, 2.0
        """
        first_index, second_index = 0, 1
        for time_b in count(initial_second_time):
            for time_a in range(initial_first_time, time_b):
                for first_time, second_time in [(time_a, time_b), (time_b, time_a)]:
                    debugger.step()
                    hailstone, collides_with_everything = self.test_collision(first_index, second_index, first_time, second_time)
                    if collides_with_everything:
                        return hailstone
                    if debugger.should_report() or collides_with_everything:
                        debugger.default_report_if(
                            f"Looking at t={first_time} & {second_time}"
                        )
            initial_first_time = 0
        raise Exception("No collision found")

    def test_collision(self, first_index: int, second_index: int, first_time: float, second_time: float) -> Tuple[part_a.Hailstone, bool]:
        """
        >>> CloudExtended.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''').test_timely_collision(4, 1, 1, 3)
        (Hailstone(position=Point3D(x=24.0, y=13.0, z=10.0), velocity=Point3D(x=-3.0, y=1.0, z=2.0)), True, True)
        """
        first = self.hailstones[first_index]
        second = self.hailstones[second_index]
        first_point: Point3D = first.position.offset(first.velocity, factor=first_time)
        second_point: Point3D = second.position.offset(second.velocity, factor=second_time)
        velocity = second_point.difference(first_point).resize(1 / (second_time - first_time))
        hailstone = part_a.Hailstone(first_point, velocity)
        collides_with_everything = all(
            position is not None
            and time1 is not None
            and time2 is not None
            for _, time1, time2, position
            in self.get_collision_points_with(hailstone)
        )
        return hailstone, collides_with_everything

    def get_collision_points_with(self, hailstone: part_a.Hailstone) -> Iterable[Tuple[part_a.Hailstone, Optional[float], Optional[float], Optional[Point3D]]]:
        """
        >>> def check(c: CloudExtended, _hailstone: part_a.Hailstone):
        ...     print("\\n\\n".join(
        ...         (
        ...             f"Hailstone: {result}\\nCollision time: {time1}\\nCollision position: {position.x}, {position.y}, {position.z}"
        ...             if time1 == time2 else
        ...             f"Hailstone: {result}\\nCollision times: {time1} != {time2}\\nCollision position: {position.x}, {position.y}, {position.z}"
        ...         )
        ...         if position is not None else
        ...         f"Hailstone: {result}\\nNo collision"
        ...         for result, time1, time2, position in c.get_collision_points_with(_hailstone)
        ...     ))
        >>> _cloud = CloudExtended.from_text('''
        ...     19, 13, 30 @ -2,  1, -2
        ...     18, 19, 22 @ -1, -1, -2
        ...     20, 25, 34 @ -2, -2, -4
        ...     12, 31, 28 @ -1, -2, -1
        ...     20, 19, 15 @  1, -5, -3
        ... ''')
        >>> check(_cloud, part_a.Hailstone.from_text("24, 13, 10 @ -3, 1, 2"))
        Hailstone: 19, 13, 30 @ -2, 1, -2
        Collision time: 5.0
        Collision position: 9.0, 18.0, 20.0
        <BLANKLINE>
        Hailstone: 18, 19, 22 @ -1, -1, -2
        Collision time: 3.0
        Collision position: 15.0, 16.0, 16.0
        <BLANKLINE>
        Hailstone: 20, 25, 34 @ -2, -2, -4
        Collision time: 4.0
        Collision position: 12.0, 17.0, 18.0
        <BLANKLINE>
        Hailstone: 12, 31, 28 @ -1, -2, -1
        Collision time: 6.0
        Collision position: 6.0, 19.0, 22.0
        <BLANKLINE>
        Hailstone: 20, 19, 15 @ 1, -5, -3
        Collision time: 1.0
        Collision position: 21.0, 14.0, 12.0
        >>> check(_cloud, part_a.Hailstone.from_text("9, 18, 20 @ 12, -4, -8"))
        Hailstone: 19, 13, 30 @ -2, 1, -2
        Collision times: 5.0 != 0.0
        Collision position: 9, 18, 20
        <BLANKLINE>
        Hailstone: 18, 19, 22 @ -1, -1, -2
        Collision times: 3.0 != 0.5
        Collision position: 15.0, 16.0, 16.0
        <BLANKLINE>
        Hailstone: 20, 25, 34 @ -2, -2, -4
        Collision times: 4.0 != 0.25
        Collision position: 12.0, 17.0, 18.0
        <BLANKLINE>
        Hailstone: 12, 31, 28 @ -1, -2, -1
        Collision times: 6.0 != -0.25
        Collision position: 6.0, 19.0, 22.0
        <BLANKLINE>
        Hailstone: 20, 19, 15 @ 1, -5, -3
        Collision time: 1.0
        Collision position: 21.0, 14.0, 12.0
        """
        return (
            (
                own,
                own.get_intersection_time(hailstone)[0],
                hailstone.get_intersection_time(own)[0],
                intersection[0],
            )
            for own in self.hailstones
            for intersection in [own.get_intersection_position(hailstone)]
        )


Challenge.main()
challenge = Challenge()
