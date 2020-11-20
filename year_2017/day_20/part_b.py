#!/usr/bin/env python3
import functools
import itertools
import math

import utils
from year_2017.day_20 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        448
        """
        return ParticleSetExtended.from_particles_text(_input)\
            .get_non_colliding_particles_count()


class ParticleSetExtended(part_a.ParticleSet):
    def get_non_colliding_particles_count(self):
        return len(self.get_non_colliding_particles())

    def get_non_colliding_particles(self):
        """
        >>> ParticleSetExtended.from_particles_text(
        ...     "p=<-6,0,0>, v=< 3,0,0>, a=< 0,0,0>\\n"
        ...     "p=<-4,0,0>, v=< 2,0,0>, a=< 0,0,0>\\n"
        ...     "p=<-2,0,0>, v=< 1,0,0>, a=< 0,0,0>\\n"
        ...     "p=< 3,0,0>, v=<-1,0,0>, a=< 0,0,0>\\n"
        ... ).get_non_colliding_particles()
        {ParticleExtended(position=Point3D(x=3, y=0, z=0),
            velocity=Point3D(x=-1, y=0, z=0),
            acceleration=Point3D(x=0, y=0, z=0))}
        """
        collision_map = self.get_collision_map()
        pairs_by_collision_time = utils.helper.reverse_dict(collision_map, set)
        collision_times = sorted(pairs_by_collision_time)
        remaining_particles = set(self.particles)
        for time in collision_times:
            collided_particles = {
                particle
                for pair in pairs_by_collision_time[time]
                if remaining_particles.issuperset(pair)
                for particle in pair
            }
            remaining_particles -= collided_particles

        return remaining_particles

    def get_collision_map(self):
        return {
            pair: step
            for pair, step in (
                ((first, second), first.get_steps_until_collision(second))
                for first, second in itertools.combinations(self.particles, 2)
            )
            if step is not None
        }


class ParticleExtended(part_a.Particle):
    def get_steps_until_collision(self, other):
        quadratic_factors = self.get_collision_quadratic_factors(other)
        axis_solutions = tuple(
            solution
            for solution
            in map(self.solve_quadratic_equation, quadratic_factors)
            if solution is not None
        )
        if set() in axis_solutions:
            return None
        if not axis_solutions:
            return 0

        solutions = functools.reduce(set.__and__, axis_solutions)
        if not solutions:
            return None

        return min(solutions)

    def solve_quadratic_equation(self, factors):
        a, b, c = factors
        if a == 0:
            if b == 0:
                if c == 0:
                    return None
                return set()
            return self.filter_positive_integer_solutions({-c / b})
        discriminate = b ** 2 - 4 * a * c
        if discriminate < 0:
            return set()
        return self.filter_positive_integer_solutions({
            (-b + math.sqrt(discriminate)) / (2 * a),
            (-b - math.sqrt(discriminate)) / (2 * a),
        })

    def filter_positive_integer_solutions(self, solutions):
        return set(map(int, filter(self.is_positive_integer, solutions)))

    def is_positive_integer(self, number):
        if number < 0:
            return False
        return int(number) == number

    def get_collision_quadratic_factors(self, other):
        my_quadratic_factors = self.get_position_quadratic_factors()
        other_quadratic_factors = other.get_position_quadratic_factors()
        quadratic_vectors = tuple(
            my_factor.difference(other_factor)
            for my_factor, other_factor
            in zip(my_quadratic_factors, other_quadratic_factors)
        )

        return tuple(
            tuple(
                getattr(quadratic_vector, axis)
                for quadratic_vector in quadratic_vectors
            )
            for axis in ["x", "y", "z"]
        )

    def get_position_quadratic_factors(self):
        return (
            self.acceleration.resize(0.5),
            self.velocity.offset(self.acceleration.resize(0.5)),
            self.position,
        )


ParticleSetExtended.particle_class = ParticleExtended


challenge = Challenge()
challenge.main()
