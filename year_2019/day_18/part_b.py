#!/usr/bin/env python3
from string import ascii_letters, ascii_lowercase

import utils

from year_2019.day_18.part_a import get_all_items_distance_and_blockers,\
    parse_map


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2082
        """
        contents, start_positions = parse_map(_input)
        contents, start_positions = replace_single_vault_with_four(
            contents, start_positions)
        minimum_distance, _ = get_minimum_collection_multiple(
            contents, start_positions)

        return minimum_distance


def get_minimum_collection_multiple(contents, start_positions):
    """
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "######\\n"
    ...     "#A.@a#\\n"
    ...     "######\\n"
    ... ))[0]
    1
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "#########\\n"
    ...     "#b.A.@.a#\\n"
    ...     "#########\\n"
    ... ))[0]
    8
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "########################\\n"
    ...     "#f.D.E.e.C.b.A.@.a.B.c.#\\n"
    ...     "######################.#\\n"
    ...     "#d.....................#\\n"
    ...     "########################\\n"
    ... ))[0]
    86
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "########################\\n"
    ...     "#@..............ac.GI.b#\\n"
    ...     "###d#e#f################\\n"
    ...     "###A#B#C################\\n"
    ...     "###g#h#i################\\n"
    ... ))[0]
    81
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "########################\\n"
    ...     "#...............b.C.D.f#\\n"
    ...     "#.######################\\n"
    ...     "#.....@.a.B.c.d.A.e.F.g#\\n"
    ...     "########################\\n"
    ... ))[0]
    132
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "#######\\n"
    ...     "#a.#Cd#\\n"
    ...     "##@#@##\\n"
    ...     "#######\\n"
    ...     "##@#@##\\n"
    ...     "#cB#Ab#\\n"
    ...     "#######\\n"
    ... ))[0]
    8
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "#######\\n"
    ...     "#a.#Cd#\\n"
    ...     "##@.@##\\n"
    ...     "#######\\n"
    ...     "##@#@##\\n"
    ...     "#cB#Ab#\\n"
    ...     "#######\\n"
    ... ))[0]
    Traceback (most recent call last):
    ...
    Exception: Keys are shared in vaults
    >>> get_minimum_collection_multiple(
    ...     *replace_single_vault_with_four(*parse_map(
    ...         "#######\\n"
    ...         "#a.#Cd#\\n"
    ...         "##...##\\n"
    ...         "##.@.##\\n"
    ...         "##...##\\n"
    ...         "#cB#Ab#\\n"
    ...         "#######\\n"
    ...     )))[0]
    8
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "###############\\n"
    ...     "#d.ABC.#.....a#\\n"
    ...     "######@#@######\\n"
    ...     "###############\\n"
    ...     "######@#@######\\n"
    ...     "#b.....#.....c#\\n"
    ...     "###############\\n"
    ... ))[0]
    24
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "#############\\n"
    ...     "#DcBa.#.GhKl#\\n"
    ...     "#.###@#@#I###\\n"
    ...     "#e#d#####j#k#\\n"
    ...     "###C#@#@###J#\\n"
    ...     "#fEbA.#.FgHi#\\n"
    ...     "#############\\n"
    ... ))[0]
    32
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "#############\\n"
    ...     "#g#f.D#..h#l#\\n"
    ...     "#F###e#E###.#\\n"
    ...     "#dCba@#@BcIJ#\\n"
    ...     "#############\\n"
    ...     "#nK.L@#@G...#\\n"
    ...     "#M###N#H###.#\\n"
    ...     "#o#m..#i#jk.#\\n"
    ...     "#############\\n"
    ... ))[0]
    72
    >>> get_minimum_collection_multiple(*parse_map(
    ...     "#################\\n"
    ...     "#i.G..c...e..H.p#\\n"
    ...     "########.########\\n"
    ...     "#j.A..b...f..D.o#\\n"
    ...     "########@########\\n"
    ...     "#k.E..a...g..B.n#\\n"
    ...     "########.########\\n"
    ...     "#l.F..d...h..C.m#\\n"
    ...     "#################\\n"
    ... ))[0]
    136
    """
    items_positions = {
        item: position
        for position, item in contents.items()
        if item in ascii_letters
    }
    keys = [
        item
        for item in items_positions
        if item in ascii_lowercase
    ]
    vaults = list(range(len(start_positions)))
    # print("Contents", contents, start_positions)
    initial_distance_and_blockers_by_vault = [
        get_all_items_distance_and_blockers(contents, start_position)
        for start_position in start_positions
    ]
    # print("Initial", initial_distance_and_blockers_by_vault)
    keys_by_vault = [
        set(keys) & set(initial_distance_and_blockers_by_vault[vault])
        for vault in vaults
    ]
    if len(keys) != len(sum(map(list, keys_by_vault), [])):
        raise Exception("Keys are shared in vaults")
    distances_and_blockers_by_key = {
        key: get_all_items_distance_and_blockers(
            contents, items_positions[key])
        for key in keys
    }

    minimum_collection = None
    stack = [((), tuple(
        ()
        for _ in vaults
    ), tuple(
        tuple(sorted(
            key
            for key in vault_keys
            if not initial_distance_and_blockers_by_vault[vault][key][1]
        ))
        for vault, vault_keys in enumerate(keys_by_vault)
    ), start_positions, 0)]
    minimum_distance_by_hash = {}
    while stack:
        current_path, current_vault_paths, vaults_current_keys_left, \
            current_positions, current_distance = stack[-1]
        # print("Get", stack[-1])
        if not any(vaults_current_keys_left):
            stack.pop()
            # print("No left", current_path, current_distance)
            if len(current_path) == len(keys):
                if minimum_collection is None:
                    minimum_collection = (current_distance, current_path)
                    print("Solution", minimum_collection)
                else:
                    minimum_distance, _ = minimum_collection
                    if current_distance < minimum_distance:
                        minimum_collection = current_distance, current_path
                        print("Solution", minimum_collection)
            continue
        for vault, vault_current_keys_left \
                in enumerate(vaults_current_keys_left):
            if not vault_current_keys_left:
                continue
            next_vault = vault
            break
        else:
            raise Exception("Could not find next key")
        next_key = vaults_current_keys_left[vault][0]
        # print("Next vault and key", next_vault, next_key)
        vaults_new_keys_left = [
            vault_current_keys_left[1:]
            if vault == next_vault else
            vault_current_keys_left
            for vault, vault_current_keys_left
            in enumerate(vaults_current_keys_left)
        ]
        if next_key in current_path:
            raise Exception(f"Next key {next_key} is in path {current_path}")
        next_path = current_path + (next_key,)
        next_vault_paths = tuple(
            current_vault_path + (next_key,)
            if vault == next_vault else
            current_vault_path
            for vault, current_vault_path in enumerate(current_vault_paths)
        )
        stack[-1] = \
            current_path, current_vault_paths, vaults_new_keys_left, \
            current_positions, current_distance
        next_positions = [
            items_positions[next_key]
            if vault == next_vault else
            current_position
            for vault, current_position in enumerate(current_positions)
        ]
        current_vault_path = current_vault_paths[next_vault]
        if current_vault_path:
            next_key_distance, _ = distances_and_blockers_by_key[
                current_vault_path[-1]][next_key]
        else:
            next_key_distance, _ = \
                initial_distance_and_blockers_by_vault[next_vault][next_key]
        if not next_key_distance:
            raise Exception(
                f"Got 0 next key distance for vault {next_vault} from "
                f"{current_vault_path[-1] if current_vault_path else start_positions[next_vault]} "
                f"to {next_key}")
        next_distance = current_distance + next_key_distance
        next_hash = get_position_hash_multiple(next_path, next_positions)
        if next_hash not in minimum_distance_by_hash:
            minimum_distance_by_hash[next_hash] = next_distance
        else:
            if minimum_distance_by_hash[next_hash] < next_distance:
                continue
            if next_distance < minimum_distance_by_hash[next_hash]:
                minimum_distance_by_hash[next_hash] = next_distance
        if minimum_collection:
            minimum_distance, _ = minimum_collection
            if next_distance >= minimum_distance:
                # print("Too long", next_path, next_distance, minimum_distance)
                continue
        next_keys_left = tuple(
            tuple(sorted(
                key
                for key in vault_keys
                if key not in next_path
                and not (
                    set((
                        distances_and_blockers_by_key[contents[next_position]]
                        if contents[next_position] != 'space' else
                        initial_distance_and_blockers_by_vault[vault]
                    )[key][1])
                    - set(next_path)
                )
            ))
            for (vault, vault_keys), next_position in
            zip(enumerate(keys_by_vault), next_positions)
        )
        if set(next_path) & set(next_keys_left):
            raise Exception(
                f"Next path {next_path} intersects with keys left "
                f"{next_keys_left}")
        stack.append(
            (next_path, next_vault_paths, next_keys_left, next_positions,
             next_distance))
        # print("Add", stack[-1], minimum_collection)

    return minimum_collection


def get_position_hash_multiple(path, positions):
    return f"{','.join(sorted(path))}|{'/'.join(map(str, positions))}"


REPLACE_NEIGHBOUR_MAP = {
    (-1, -1): 'space',
    (1, -1): 'space',
    (1, 1): 'space',
    (-1, 1): 'space',
    (0, -1): None,
    (0, 1): None,
    (-1, 0): None,
    (1, 0): None,
    (0, 0): None,
}


def replace_single_vault_with_four(contents, start_positions):
    """
    >>> print(show_map(*replace_single_vault_with_four(*parse_map(
    ...     "...\\n"
    ...     ".@.\\n"
    ...     "...\\n"
    ... ))))
    @#@
    ###
    @#@
    >>> print(show_map(*replace_single_vault_with_four(*parse_map(
    ...     "#######\\n"
    ...     "#a.#Cd#\\n"
    ...     "##...##\\n"
    ...     "##.@.##\\n"
    ...     "##...##\\n"
    ...     "#cB#Ab#\\n"
    ...     "#######\\n"
    ... ))))
    a.#Cd
    #@#@#
    #####
    #@#@#
    cB#Ab
    """
    if len(start_positions) != 1:
        raise Exception(
            f"Expected a single start position but got {len(start_positions)}")
    start_position, = start_positions
    start_x, start_y = start_position
    neighbours = {
        (start_x + offset_x, start_y + offset_y)
        for offset_x, offset_y in REPLACE_NEIGHBOUR_MAP
    }
    non_empty_neighbours = {
        neighbour: contents[neighbour]
        for neighbour in neighbours
        if contents[neighbour] not in ['space', 'wall']
    }
    if non_empty_neighbours:
        raise Exception(
            f"Some neighbours were not walls or empty: {non_empty_neighbours}")
    new_contents = {
        **contents,
        **{
            (start_x + offset_x, start_y + offset_y): replacement
            for (offset_x, offset_y), replacement
            in REPLACE_NEIGHBOUR_MAP.items()
        }
    }
    new_contents = {
        position: content
        for position, content in new_contents.items()
        if content
    }
    new_start_positions = [
        (start_x + offset_x, start_y + offset_y)
        for (offset_x, offset_y), replacement
        in REPLACE_NEIGHBOUR_MAP.items()
        if replacement == 'space'
    ]

    return new_contents, new_start_positions


SHOW_MAP = {
    'space': '.',
    None: '#',
}


def show_map(contents, start_positions):
    """
    >>> print(":", show_map(*parse_map(
    ...     "...\\n"
    ...     ".@.\\n"
    ...     "...\\n"
    ... )))
    : ...
    .@.
    ...
    >>> print(show_map(*parse_map(
    ...     "@#@\\n"
    ...     "###\\n"
    ...     "@#@\\n"
    ... )))
    @#@
    ###
    @#@
    >>> print(show_map(*parse_map(
    ...     "@#@a\\n"
    ...     "###A\\n"
    ...     "@#@.\\n"
    ... )))
    @#@a
    ###A
    @#@.
    """
    xs = [x for x, _ in contents]
    min_x, max_x = min(xs), max(xs)
    ys = [y for _, y in contents]
    min_y, max_y = min(ys), max(ys)

    return "\n".join(
        "".join(
            SHOW_MAP.get(contents.get((x, y)), contents.get((x, y)))
            if (x, y) not in start_positions else
            '@'
            for x in range(min_x, max_x + 1)
        )
        for y in range(min_y, max_y + 1)
    )


Challenge.main()
challenge = Challenge()
