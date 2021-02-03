#!/usr/bin/env python3
import re
from dataclasses import dataclass

import utils
from utils import Point3D


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        737
        """
        robot_set = RobotSet.from_robots_text(_input)
        return robot_set \
            .get_loudest_robot()\
            .get_robot_count_in_reach(robot_set.robots)


class RobotSet:
    robot_class = NotImplemented

    @classmethod
    def from_robots_text(cls, robots_text):
        """
        >>> robot_set_a = RobotSet.from_robots_text(
        ...     "pos=<0,0,0>, r=4\\n"
        ...     "pos=<1,0,0>, r=1\\n"
        ...     "pos=<4,0,0>, r=3\\n"
        ...     "pos=<0,2,0>, r=1\\n"
        ...     "pos=<0,5,0>, r=3\\n"
        ...     "pos=<0,0,3>, r=1\\n"
        ...     "pos=<1,1,1>, r=1\\n"
        ...     "pos=<1,1,2>, r=1\\n"
        ...     "pos=<1,3,1>, r=1\\n"
        ... )
        >>> len(robot_set_a.robots)
        9
        >>> robot_set_a.robots[2]
        Robot(position=Point3D(x=4, y=0, z=0), radius=3)
        """
        non_empty_lines = filter(None, robots_text.splitlines())
        return cls(list(map(cls.robot_class.from_robot_text, non_empty_lines)))

    def __init__(self, robots):
        self.robots = robots

    def get_loudest_robot(self):
        """
        >>> RobotSet.from_robots_text(
        ...     "pos=<0,0,0>, r=4\\n"
        ...     "pos=<1,0,0>, r=1\\n"
        ...     "pos=<4,0,0>, r=3\\n"
        ...     "pos=<0,2,0>, r=1\\n"
        ...     "pos=<0,5,0>, r=3\\n"
        ...     "pos=<0,0,3>, r=1\\n"
        ...     "pos=<1,1,1>, r=1\\n"
        ...     "pos=<1,1,2>, r=1\\n"
        ...     "pos=<1,3,1>, r=1\\n"
        ... ).get_loudest_robot()
        Robot(position=Point3D(x=0, y=0, z=0), radius=4)
        """
        return max(self.robots, key=lambda robot: robot.radius, default=None)


@dataclass(frozen=True, eq=True, order=True)
class Robot:
    position: Point3D
    radius: int

    re_robot = re.compile(r"^pos=<(-?\d+),(-?\d+),(-?\d+)>, r=(\d+)$")

    @classmethod
    def from_robot_text(cls, robot_text):
        """
        >>> Robot.from_robot_text("pos=<0,0,0>, r=4")
        Robot(position=Point3D(x=0, y=0, z=0), radius=4)
        """
        x_str, y_str, z_str, radius_str = \
            cls.re_robot.match(robot_text).groups()
        position = Point3D.from_int_texts(x_str, y_str, z_str)
        radius = int(radius_str)

        return cls(position, radius)

    def get_robot_count_in_reach(self, robots):
        """
        >>> robot_set_a = RobotSet.from_robots_text(
        ...     "pos=<0,0,0>, r=4\\n"
        ...     "pos=<1,0,0>, r=1\\n"
        ...     "pos=<4,0,0>, r=3\\n"
        ...     "pos=<0,2,0>, r=1\\n"
        ...     "pos=<0,5,0>, r=3\\n"
        ...     "pos=<0,0,3>, r=1\\n"
        ...     "pos=<1,1,1>, r=1\\n"
        ...     "pos=<1,1,2>, r=1\\n"
        ...     "pos=<1,3,1>, r=1\\n"
        ... )
        >>> robot_set_a.robots[0].get_robot_count_in_reach(robot_set_a.robots)
        7
        """
        return utils.helper.iterable_length(self.filter_robots_in_reach(robots))

    def filter_robots_in_reach(self, robots):
        return filter(self.can_reach, robots)

    def can_reach(self, other):
        """
        >>> Robot(Point3D(0, 0, 0), radius=4)\\
        ...     .can_reach(Robot(Point3D(0, 0, 0), radius=0))
        True
        >>> Robot(Point3D(0, 0, 0), radius=4)\\
        ...     .can_reach(Robot(Point3D(2, 3, -4), radius=0))
        False
        >>> Robot(Point3D(0, 0, 0), radius=9)\\
        ...     .can_reach(Robot(Point3D(2, 3, -4), radius=0))
        True
        """
        return self.position.manhattan_distance(other.position) <= self.radius


RobotSet.robot_class = Robot


Challenge.main()
challenge = Challenge()
