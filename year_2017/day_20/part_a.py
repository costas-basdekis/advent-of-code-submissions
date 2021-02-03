#!/usr/bin/env python3
import re
from copy import copy
from dataclasses import dataclass

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        457
        """
        return ParticleSet.from_particles_text(_input)\
            .get_particle_index_closest_to_origin_in_the_long_run()


class ParticleSet:
    particle_class = NotImplemented

    @classmethod
    def from_particles_text(cls, particles_text):
        lines = particles_text.strip().splitlines()
        return cls(list(map(cls.particle_class.from_particle_text, lines)))

    def __init__(self, particles):
        self.particles = particles

    def get_particle_index_closest_to_origin_in_the_long_run(self):
        """
        >>> ParticleSet.from_particles_text(
        ...     "p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>\\n"
        ...     "p=< 4,0,0>, v=< 0,0,0>, a=<-2,0,0>\\n"
        ... ).get_particle_index_closest_to_origin_in_the_long_run()
        0
        """
        return self.particles.index(
            self.get_particle_closest_to_origin_in_the_long_run())

    def get_particle_closest_to_origin_in_the_long_run(self):
        return min(
            self.particles,
            key=self.particle_class.get_distance_in_the_long_run)


@dataclass(eq=True, unsafe_hash=True)
class Particle:
    position: utils.Point3D
    velocity: utils.Point3D
    acceleration: utils.Point3D

    re_particle = re.compile(r"^p=<([^>]+)>,\s+v=<([^>]+)>,\s+a=<([^>]+)>$")

    re_coordinates = re.compile(r"^\s*(-?\d+),(-?\d+),(-?\d+)$")

    @classmethod
    def from_particle_text(cls, particle_text):
        """
        >>> Particle.from_particle_text('p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>')
        Particle(position=Point3D(x=3, y=0, z=0),
            velocity=Point3D(x=2, y=0, z=0),
            acceleration=Point3D(x=-1, y=0, z=0))
        """
        position_str, velocity_str, acceleration_str = \
            cls.re_particle.match(particle_text).groups()

        return cls(
            cls.parse_vector(position_str),
            cls.parse_vector(velocity_str),
            cls.parse_vector(acceleration_str),
        )

    @classmethod
    def parse_vector(cls, vector_text):
        x_str, y_str, z_str = cls.re_coordinates.match(vector_text).groups()

        return utils.Point3D(int(x_str), int(y_str), int(z_str))

    def get_shortest_distance_to_origin(self):
        """
        >>> Particle.from_particle_text('p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>')\\
        ...     .get_shortest_distance_to_origin()
        1
        """
        shortest_distance = self.distance_to_origin()
        while not self.will_distance_to_origin_increase():
            self.step()
            shortest_distance = \
                min(shortest_distance, self.distance_to_origin())

        return shortest_distance

    def get_distance_in_the_long_run(self, count=1 * 1000 * 1000 * 1000):
        return copy(self).step_many(count).distance_to_origin()

    def step_many(self, count):
        """
        >>> Particle.from_particle_text('p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>')\\
        ...     .step_many(5)
        Particle(position=Point3D(x=-2, y=0, z=0),
            velocity=Point3D(x=-3, y=0, z=0),
            acceleration=Point3D(x=-1, y=0, z=0))
        """
        self.position = self.position\
            .offset(self.velocity, count)\
            .offset(self.acceleration, count * (count + 1) // 2)
        self.velocity = self.velocity\
            .offset(self.acceleration, count)

        return self

    def step(self):
        """
        >>> Particle.from_particle_text(
        ...     'p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>').step()
        Particle(position=Point3D(x=4, y=0, z=0),
            velocity=Point3D(x=1, y=0, z=0),
            acceleration=Point3D(x=-1, y=0, z=0))
        >>> Particle.from_particle_text('p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>')\\
        ...     .step().step().step().step().step()
        Particle(position=Point3D(x=-2, y=0, z=0),
            velocity=Point3D(x=-3, y=0, z=0),
            acceleration=Point3D(x=-1, y=0, z=0))
        """
        self.velocity = self.velocity.offset(self.acceleration)
        self.position = self.position.offset(self.velocity)

        return self

    def will_distance_to_origin_increase(self):
        return (
            self.acceleration.sign()
            == self.velocity.sign()
            == self.position.sign()
        )

    def distance_to_origin(self):
        """
        >>> particle = Particle.from_particle_text(
        ...     'p=< 3,0,0>, v=< 2,0,0>, a=<-1,0,0>')
        >>> particle.distance_to_origin()
        3
        >>> particle.step().distance_to_origin()
        4
        """
        return self.position.manhattan_length()


ParticleSet.particle_class = Particle


Challenge.main()
challenge = Challenge()
