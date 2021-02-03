#!/usr/bin/env python3
import utils

from year_2019.day_06.part_a import create_orbit_mapping, parse_orbits,\
    get_orbit_path


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        562
        """
        return get_transfer_count(
            'YOU', 'SAN', create_orbit_mapping(parse_orbits(_input))) - 2


def get_transfer_count(source, target, mapping):
    """
    >>> get_transfer_count("YOU", "SAN", create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L\\n"\
        "K)YOU\\nI)SAN")))
    6
    """
    return len(get_transfers(source, target, mapping)) - 1


def get_transfers(source, target, mapping):
    """
    >>> get_transfers("YOU", "SAN", create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L\\n"\
        "K)YOU\\nI)SAN")))
    ['YOU', 'K', 'J', 'E', 'D', 'I', 'SAN']
    >>> get_transfers("YOU", "COM", create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L\\n"\
        "K)YOU\\nI)SAN")))
    ['YOU', 'K', 'J', 'E', 'D', 'C', 'B', 'COM']
    >>> get_transfers("YOU", "L", create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L\\n"\
        "K)YOU\\nI)SAN")))
    ['YOU', 'K', 'L']
    >>> get_transfers("YOU", "J", create_orbit_mapping(parse_orbits(\
        "COM)B\\nB)C\\nC)D\\nD)E\\nE)F\\nB)G\\nG)H\\nD)I\\nE)J\\nJ)K\\nK)L\\n"\
        "K)YOU\\nI)SAN")))
    ['YOU', 'K', 'J']
    """
    from_source = get_orbit_path(source, mapping)
    from_target = get_orbit_path(target, mapping)
    common_ancestor = get_common_ancestor(from_source, from_target)
    common_ancestor_index_from_source = from_source.index(common_ancestor)
    common_ancestor_index_from_target = from_target.index(common_ancestor)

    return (
        from_source[:common_ancestor_index_from_source + 1]
        + list(reversed(from_target[:common_ancestor_index_from_target]))
    )


def get_common_ancestor(path_a, path_b):
    """
    >>> get_common_ancestor(['COM'], ['COM'])
    'COM'
    >>> get_common_ancestor(['B', 'A', 'COM'], ['D', 'C', 'COM'])
    'COM'
    >>> get_common_ancestor(['B', 'A', 'D', 'C', 'COM'], ['D', 'C', 'COM'])
    'D'
    >>> get_common_ancestor(['B', 'A', 'C', 'COM'], ['D', 'C', 'COM'])
    'C'
    """
    for position in path_a:
        if position in path_b:
            return position

    raise Exception("Could not find common ancestor")


Challenge.main()
challenge = Challenge()
