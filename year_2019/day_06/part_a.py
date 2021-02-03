#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        453028
        """
        return get_total_orbit_count(create_orbit_mapping(parse_orbits(_input)))


UNIVERSAL_CENTER_OF_MASS = 'COM'


def get_total_orbit_count(mapping):
    """
    >>> get_total_orbit_count({})
    0
    >>> get_total_orbit_count({'A': 'COM'})
    1
    >>> get_total_orbit_count({'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    9
    >>> get_total_orbit_count(create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    42
    """
    return sum(
        get_orbit_count(orbiter, mapping)
        for orbiter in mapping
    )


def get_orbit_count(start, mapping):
    """
    >>> get_orbit_count('COM', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    0
    >>> get_orbit_count('A', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    1
    >>> get_orbit_count('B', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    2
    >>> get_orbit_count('C', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    3
    >>> get_orbit_count('D', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    3
    >>> get_orbit_count('D', create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    3
    >>> get_orbit_count('L', create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    7
    >>> get_orbit_count('COM', create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    0
    """
    path = get_orbit_path(start, mapping)

    return len(path) - 1


def get_orbit_path(start, mapping):
    """
    >>> get_orbit_path('COM', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    ['COM']
    >>> get_orbit_path('A', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    ['A', 'COM']
    >>> get_orbit_path('B', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    ['B', 'A', 'COM']
    >>> get_orbit_path('C', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    ['C', 'B', 'A', 'COM']
    >>> get_orbit_path('D', {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'})
    ['D', 'B', 'A', 'COM']
    >>> get_orbit_path('D', create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    ['D', 'C', 'B', 'COM']
    >>> get_orbit_path('L', create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    ['L', 'K', 'J', 'E', 'D', 'C', 'B', 'COM']
    >>> get_orbit_path('COM', create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")))
    ['COM']
    """
    path = [start]
    position = start
    while position != UNIVERSAL_CENTER_OF_MASS:
        position = mapping[position]
        path.append(position)

    return path


def create_orbit_mapping(orbits):
    """
    >>> create_orbit_mapping([('COM', 'A'), ('A', 'B'), ('B', 'C'), ('B', 'D')])
    {'A': 'COM', 'B': 'A', 'C': 'B', 'D': 'B'}
    >>> create_orbit_mapping(parse_orbits("COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L"))
    {'B': 'COM', 'C': 'B', 'D': 'C', 'E': 'D', 'F': 'E', 'G': 'B', 'H': 'G', 'I': 'D', 'J': 'E', 'K': 'J', 'L': 'K'}
    """
    return {
        orbiter: center
        for center, orbiter in orbits
    }


def parse_orbits(_input):
    """
    >>> parse_orbits("COM)A\\nA)B\\nB)C\\nB)D\\n")
    [('COM', 'A'), ('A', 'B'), ('B', 'C'), ('B', 'D')]
    >>> parse_orbits("COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L")
    [('COM', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E'), ('E', 'F'), ('B', 'G'), ('G', 'H'), ('D', 'I'), ('E', 'J'), ('J', 'K'), ('K', 'L')]
    """
    lines = _input.splitlines()
    non_empty_lines = filter(None, lines)
    pairs = [tuple(line.split(')')) for line in non_empty_lines]

    return pairs


Challenge.main()
challenge = Challenge()
