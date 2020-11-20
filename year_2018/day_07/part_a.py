#!/usr/bin/env python3
import doctest
import itertools
import re
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    'GKCNPTVHIRYDUJMSXFBQLOAEWZ'
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    order = Resolver.from_requirements_text(_input).get_resolution_order()

    return "".join(order)


class Resolver:
    @classmethod
    def from_requirements_text(cls, requirements_text):
        """
        >>> list(map(tuple, Resolver.from_requirements_text(
        ...     "Step C must be finished before step A can begin.\\n"
        ...     "Step C must be finished before step F can begin.\\n"
        ...     "Step A must be finished before step B can begin.\\n"
        ...     "Step A must be finished before step D can begin.\\n"
        ...     "Step B must be finished before step E can begin.\\n"
        ...     "Step D must be finished before step E can begin.\\n"
        ...     "Step F must be finished before step E can begin.\\n"
        ... ).requirements))
        [('A', 'C'), ('F', 'C'), ('B', 'A'), ('D', 'A'), ('E', 'B'), ('E', 'D'), ('E', 'F')]
        """
        lines = requirements_text.splitlines()
        non_empty_lines = filter(None, lines)
        return cls(list(map(
            Requirement.from_requirement_text, non_empty_lines)))

    @classmethod
    def from_tuples(cls, tuples):
        return cls(list(Requirement(*_tuple) for _tuple in tuples))

    def __init__(self, requirements):
        self.requirements = requirements

    def get_requirements_map(self):
        """
        >>> sorted(Resolver.from_tuples([
        ...     ('A', 'C'), ('F', 'C'), ('B', 'A'), ('D', 'A'), ('E', 'B'),
        ...     ('E', 'D'), ('E', 'F')]).get_requirements_map().items())
        [('A', ('C',)), ('B', ('A',)), ('C', ()), ('D', ('A',)), ('E', ('B', 'D', 'F')), ('F', ('C',))]
        """
        all_steps = {
            requirement.step
            for requirement in self.requirements
        } | {
            requirement.prerequisite
            for requirement in self.requirements
        }
        return {
            **{
                step: ()
                for step in all_steps
            },
            ** {
                step: tuple(sorted(
                    requirement.prerequisite
                    for requirement in requirements
                ))
                for step, requirements
                in itertools.groupby(sorted(
                    self.requirements, key=lambda requirement: requirement.step),
                    key=lambda requirement: requirement.step)
            },
        }

    def get_resolution_order(self):
        """
        >>> Resolver.from_tuples([
        ...     ('A', 'C'), ('F', 'C'), ('B', 'A'), ('D', 'A'), ('E', 'B'),
        ...     ('E', 'D'), ('E', 'F')]).get_resolution_order()
        ['C', 'A', 'B', 'D', 'F', 'E']
        """
        requirements_map = self.get_requirements_map()
        order = []
        remaining = set(requirements_map)
        while remaining:
            free_steps = sorted(
                step
                for step in remaining
                if all(
                    prerequisite in order
                    for prerequisite in requirements_map[step]
                )
            )
            if not free_steps:
                raise Exception("No free steps remaining but other steps are")
            next_step = free_steps[0]
            order.append(next_step)
            remaining.remove(next_step)

        return order


class Requirement(namedtuple("Step", ("step", "prerequisite"))):
    re_requirement = re.compile(
        r"Step (\w+) must be finished before step (\w+) can begin.")

    @classmethod
    def from_requirement_text(cls, requirement_text):
        """
        >>> Requirement.from_requirement_text(
        ...     "Step C must be finished before step A can begin.")
        Requirement(step='A', prerequisite='C')
        """
        prerequisite, step = cls.re_requirement\
            .match(requirement_text)\
            .groups()

        return cls(step, prerequisite)


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
