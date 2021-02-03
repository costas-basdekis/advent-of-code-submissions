#!/usr/bin/env python3
import itertools
import string

import click

import utils
from year_2018.day_23 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        123356173
        """
        robot_set = RobotSetExtended.from_robots_text(_input)
        if debug:
            most_popular_robot = robot_set.get_most_popular_robot()
            print(robot_set.show(100, 'z', highlight_robot=most_popular_robot))
            print(robot_set.show(100, 'y', highlight_robot=most_popular_robot))
            print(robot_set.show(100, 'x', highlight_robot=most_popular_robot))

        overlaps = robot_set.get_overlaps()

        most_popular_robot = robot_set.get_most_popular_robot()
        minimum_reach_count = most_popular_robot\
            .get_robot_count_that_can_be_reached_by(robot_set.robots)

        overlaps_with_minimum_reach_count = {
            robot: overlaps
            for robot, overlaps in overlaps.items()
            if len(overlaps) >= minimum_reach_count
        }

        marginal_pairs = [
            (lhs, rhs)
            for lhs, rhs
            in itertools.combinations(overlaps_with_minimum_reach_count, 2)
            if lhs.overlap_slack(rhs) == 0
        ]
        if not marginal_pairs:
            raise Exception(
                f"Expected pairs with >= {minimum_reach_count} overlaps to "
                f"have marginal pairs")

        marginal_robots = set(sum(marginal_pairs, ()))

        marginal_robots_with_multiple_partners = sorted(
            robot
            for robot, count in (
                (robot, utils.helper.iterable_length(items))
                for robot, items in itertools.groupby(sorted(
                    sum(marginal_pairs, ())))
            )
            if count > 1
        )

        pair_a_robot_a = marginal_robots_with_multiple_partners[0]

        pair_a_robot_a_counterparts = sorted(
            next(iter(set(pair) - {pair_a_robot_a}))
            for pair in marginal_pairs
            if pair_a_robot_a in pair
        )

        pair_a_robot_b = pair_a_robot_a_counterparts[0]
        pair_a_mid_point = pair_a_robot_a.get_mid_point(pair_a_robot_b)

        non_satisfied_robots = [
            robot
            for robot in marginal_robots
            if not robot.can_reach_position(pair_a_mid_point)
        ]

        if len(non_satisfied_robots) != 2:
            raise Exception(
                f"Expect to have 2 non-satisfied robots, not "
                f"{len(non_satisfied_robots)}")

        pair_b_robot_a, pair_b_robot_b = non_satisfied_robots

        pair_b_mid_point = pair_b_robot_a.get_mid_point(pair_b_robot_b)

        # Solution should be on the common line between the pair a plane
        # through pair a mid point, and the pair b plane through
        # pair b mid point.
        # Since the intersection will be either on the pair a plane or on the
        # pair b plane, the distance to 0 will be either that of
        # pair a mid point or pair b mid point.
        # But which? It logically follows that the intersection will be on the
        # plane of the pair whose mid-point is furthest from 0, but actually
        # it's the other way around

        return min(
            pair_a_mid_point.manhattan_length(),
            pair_b_mid_point.manhattan_length(),
        )


class RobotSetExtended(part_a.RobotSet):
    def get_overlaps(self):
        overlaps = set()
        for lhs, rhs in itertools.combinations(self.robots, 2):
            if not lhs.overlaps(rhs):
                continue
            overlaps.add((lhs, rhs))
            overlaps.add((rhs, lhs))

        return {
            robot: {
                other
                for other in self.robots
                if (robot, other) in overlaps
            }
            for robot in self.robots
        }

    def iterate_popular_positions(self, popular_robots):
        return {
            approach
            for popular_robot in popular_robots
            for max_distance_can_move, target
            in self.get_robots_to_approach(popular_robot)
            if max_distance_can_move
            for approach in self.get_robot_approaches(
                popular_robot, target, max_distance_can_move)
        }

    def get_robot_approaches(self, start, target, max_distance_can_move):
        delta = target.position.difference(start.position)

        sign_x = delta.x // (abs(delta.x) or 1)
        sign_y = delta.y // (abs(delta.y) or 1)
        sign_z = delta.z // (abs(delta.z) or 1)

        x, y, z = start.position

        return (
            RobotExtended(position=utils.Point3D(
                x=x + d_x * sign_x,
                y=y + d_y * sign_y,
                z=z + d_z * sign_z,
            ), radius=0)
            for d_x in range(
                min(abs(delta.x), max_distance_can_move) + 1)
            for d_y in range(
                min(abs(delta.y), max_distance_can_move - d_x) + 1)
            for d_z in (max_distance_can_move - d_x - d_y,)
            if 0 <= d_z <= abs(delta.z)
        )

    def get_robots_to_approach(self, popular_robot):
        max_distance_can_move = min((
            robot.radius - robot.manhattan_distance(popular_robot)
            for robot in self.robots
            if popular_robot.can_be_reached_by(robot)
        ), default=None)
        if not max_distance_can_move:
            return []

        return [
            (robot.manhattan_distance(popular_robot) - robot.radius, robot)
            for robot in self.robots
            if 0 <= (robot.manhattan_distance(popular_robot) - robot.radius)
            <= max_distance_can_move
        ]

    def get_most_popular_initial_position(self):
        most_popular_robot = self.get_most_popular_robot()
        return RobotExtended(position=most_popular_robot.position, radius=0)

    def get_most_popular_robot(self):
        return max(
            self.robots,
            key=self.sort_key_robot_count_that_can_can_be_reached_by)

    def sort_key_robot_count_that_can_can_be_reached_by(self, robot):
        return robot.get_robot_count_that_can_be_reached_by(self.robots)

    def get_most_overlapping_robot(self):
        return max(self.robots, key=self.sort_key_robot_count_that_overlap)

    def sort_key_robot_count_that_overlap(self, robot):
        return robot.get_robot_count_that_overlap(self.robots)

    def show(self, size, axis, highlight_robot=None):
        min_x = min(robot.position.x for robot in self.robots)
        max_x = max(robot.position.x for robot in self.robots)
        min_y = min(robot.position.y for robot in self.robots)
        max_y = max(robot.position.y for robot in self.robots)
        min_z = min(robot.position.z for robot in self.robots)
        max_z = max(robot.position.z for robot in self.robots)

        size_x = max_x - min_x + 1
        size_y = max_y - min_y + 1
        size_z = max_z - min_z + 1

        axis_x = 'x', min_x, max_x, size_x
        axis_y = 'y', min_y, max_y, size_y
        axis_z = 'z', min_z, max_z, size_z

        if axis == 'z':
            first_axis, second_axis = axis_x, axis_y
        elif axis == 'y':
            first_axis, second_axis = axis_x, axis_z
        elif axis == 'x':
            first_axis, second_axis = axis_y, axis_z
        else:
            raise Exception(f"Unknown axis '{axis}'")
        name_first, min_first, max_first, size_first = first_axis
        name_second, min_second, max_second, size_second = second_axis

        bins = {}
        for robot in self.robots:
            first_index = (
                (getattr(robot.position, name_first) - min_first)
                * size // size_first
            )
            second_index = (
                (getattr(robot.position, name_second) - min_second)
                * size // size_second
            )
            bins.setdefault((first_index, second_index), set()).add(robot)

        return "\n".join(
            "".join(
                self.show_set(
                    bins.get((first_index, second_index), set()),
                    highlight_robot)
                for first_index in range(size)
            )
            for second_index in range(size)
        )

    def show_set(self, robots, highlight_robot):
        text = self.show_count(len(robots))
        if highlight_robot:
            if highlight_robot in robots:
                text = click.style(text, bg='red')
            elif robots and all(map(highlight_robot.can_be_reached_by, robots)):
                text = click.style(text, fg='black', bg='green')
            elif any(map(highlight_robot.can_be_reached_by, robots)):
                text = click.style(text, fg='green')

        return text

    def show_count(self, count):
        if not count:
            return ' '
        if count < 10:
            return str(count)
        if count < 100:
            return string.ascii_lowercase[:10][(count - 10) // 10]
        if count < 1000:
            return string.ascii_uppercase[:10][(count - 10) // 10]

        raise Exception(f"Count was too high {count}")


class RobotExtended(part_a.Robot):
    def manhattan_distance(self, other):
        return self.position.manhattan_distance(other.position)

    def get_robot_count_that_can_be_reached_by(self, robots):
        return utils.helper.iterable_length(
            self.filter_robots_that_can_be_reached_by(robots))

    def filter_robots_that_can_be_reached_by(self, robots):
        return filter(self.can_be_reached_by, robots)

    def can_be_reached_by(self, other):
        return other.can_reach(self)

    def can_reach_position(self, position):
        return self.position.manhattan_distance(position) <= self.radius

    def get_robot_count_that_overlap(self, robots):
        return utils.helper.iterable_length(
            self.filter_overlapping_robots(robots))

    def filter_overlapping_robots(self, robots):
        return filter(self.overlaps, robots)

    def overlaps(self, other):
        return self.overlap_slack(other) >= 0

    def overlap_slack(self, other):
        return self.radius + other.radius - self.manhattan_distance(other)

    def get_mid_point(self, other):
        sign = other.position.difference_sign(self.position)

        split_radius = self.radius // 3
        split_radius_remnant = self.radius % 3
        return self.position.offset((
            sign.x * (split_radius + (1 if split_radius_remnant > 0 else 0)),
            sign.y * (split_radius + (1 if split_radius_remnant > 1 else 0)),
            sign.z * (split_radius + (1 if split_radius_remnant > 2 else 0)),
        ))


RobotSetExtended.robot_class = RobotExtended


Challenge.main()
challenge = Challenge()
