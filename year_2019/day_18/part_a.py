#!/usr/bin/env python3
from string import ascii_lowercase, ascii_letters

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        5288
        """
        contents, (start_position,) = parse_map(_input)
        minimum_distance, _ = get_minimum_collection(
            contents, start_position)

        return minimum_distance


def get_minimum_collection(contents, start_position):
    """
    >>> contents_a, start_position_a = parse_map(
    ...     "######\\n"
    ...     "#A.@a#\\n"
    ...     "######\\n"
    ... )
    >>> get_minimum_collection(contents_a, start_position_a[0])[0]
    1
    >>> contents_b, start_position_b = parse_map(
    ...     "#########\\n"
    ...     "#b.A.@.a#\\n"
    ...     "#########\\n"
    ... )
    >>> get_minimum_collection(contents_b, start_position_b[0])[0]
    8
    >>> contents_c, start_position_c = parse_map(
    ...     "########################\\n"
    ...     "#f.D.E.e.C.b.A.@.a.B.c.#\\n"
    ...     "######################.#\\n"
    ...     "#d.....................#\\n"
    ...     "########################\\n"
    ... )
    >>> get_minimum_collection(contents_c, start_position_c[0])[0]
    86
    >>> contents_d, start_position_d = parse_map(
    ...     "########################\\n"
    ...     "#@..............ac.GI.b#\\n"
    ...     "###d#e#f################\\n"
    ...     "###A#B#C################\\n"
    ...     "###g#h#i################\\n"
    ... )
    >>> get_minimum_collection(contents_d, start_position_d[0])[0]
    81
    >>> contents_e, start_position_e = parse_map(
    ...     "########################\\n"
    ...     "#...............b.C.D.f#\\n"
    ...     "#.######################\\n"
    ...     "#.....@.a.B.c.d.A.e.F.g#\\n"
    ...     "########################\\n"
    ... )
    >>> get_minimum_collection(contents_e, start_position_e[0])[0]
    132
    """
    """
    >>> contents_e, start_position_e = parse_map(
    ...     "#################\\n"
    ...     "#i.G..c...e..H.p#\\n"
    ...     "########.########\\n"
    ...     "#j.A..b...f..D.o#\\n"
    ...     "########@########\\n"
    ...     "#k.E..a...g..B.n#\\n"
    ...     "########.########\\n"
    ...     "#l.F..d...h..C.m#\\n"
    ...     "#################\\n"
    ... )
    >>> get_minimum_collection(contents_e, start_position_e[0])[0]
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
    initial_distance_and_blockers = get_all_items_distance_and_blockers(
        contents, start_position)
    distances_and_blockers_by_key = {
        key: get_all_items_distance_and_blockers(
            contents, items_positions[key])
        for key in keys
    }

    minimum_collection = None
    stack = [((), tuple(sorted(
        key
        for key in keys
        if not initial_distance_and_blockers[key][1]
    )), start_position, 0)]
    minimum_distance_by_hash = {}
    while stack:
        current_path, current_keys_left, current_position, current_distance = \
            stack[-1]
        if not current_keys_left:
            stack.pop()
            # print("No left", current_path, current_distance)
            if len(current_path) == len(keys):
                if minimum_collection is None:
                    minimum_collection = (current_distance, current_path)
                    # print(minimum_collection)
                else:
                    minimum_distance, _ = minimum_collection
                    if current_distance < minimum_distance:
                        minimum_collection = current_distance, current_path
                        # print(minimum_collection)
            continue
        next_key, new_keys_left = \
            current_keys_left[0], current_keys_left[1:]
        if next_key in current_path:
            raise Exception(f"Next key {next_key} is in path {current_path}")
        next_path = current_path + (next_key,)
        stack[-1] = \
            current_path, new_keys_left, current_position, current_distance
        next_position = items_positions[next_key]
        if current_path:
            next_key_distance, _ = distances_and_blockers_by_key[
                current_path[-1]][next_key]
        else:
            next_key_distance, _ = initial_distance_and_blockers[next_key]
        next_distance = current_distance + next_key_distance
        next_hash = get_position_hash(next_path, next_position)
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
        next_keys_left = tuple(sorted(
            key
            for key in keys
            if key not in next_path
            and not (
                set(distances_and_blockers_by_key[next_key][key][1])
                - set(next_path)
            )
        ))
        if set(next_path) & set(next_keys_left):
            raise Exception(
                f"Next path {next_path} intersects with keys left "
                f"{next_keys_left}")
        stack.append((next_path, next_keys_left, next_position, next_distance))
        # print(stack[-1], minimum_collection)

    return minimum_collection


def get_all_items_distance_and_blockers(contents, start_position):
    """
    >>> contents_a, start_positions_a = parse_map(
    ...     "######\\n"
    ...     "#A.@a#\\n"
    ...     "######\\n"
    ... )
    >>> get_all_items_distance_and_blockers(contents_a, start_positions_a[0])
    {'a': (1, ()), 'A': (2, ())}
    >>> contents_b, start_positions_b = parse_map(
    ...     "#########\\n"
    ...     "#b.A.@.a#\\n"
    ...     "#########\\n"
    ... )
    >>> get_all_items_distance_and_blockers(contents_b, start_positions_b[0])
    {'a': (2, ()), 'A': (2, ()), 'b': (4, ('a',))}
    >>> contents_c, start_positions_c = parse_map(
    ...     "#########\\n"
    ...     "#b.A.@.a#\\n"
    ...     "#########\\n"
    ...     "#d.B.@.c#\\n"
    ...     "#########\\n"
    ... )
    >>> get_all_items_distance_and_blockers(contents_c, start_positions_c[0])
    {'a': (2, ()), 'A': (2, ()), 'b': (4, ('a',))}
    >>> get_all_items_distance_and_blockers(contents_c, start_positions_c[1])
    {'c': (2, ()), 'B': (2, ()), 'd': (4, ('b',))}
    """
    stack = [(start_position, 0, ())]
    visited = set(start_position)
    items = {}
    while stack:
        position, distance, blockers = stack.pop(0)

        content = contents.get(position)
        if not content:
            continue

        if position in visited:
            continue
        visited.add(position)

        is_blocker = content in ascii_letters
        if is_blocker:
            items[content] = \
                (distance, tuple(sorted(set(map(str.lower, blockers)))))

        new_distance = distance + 1
        if is_blocker:
            new_blockers = blockers + (content,)
        else:
            new_blockers = blockers
        neighbours = get_neighbour_positions(position)
        stack.extend(
            (neighbour, new_distance, new_blockers)
            for neighbour in neighbours
        )

    return items


def get_position_hash(path, position):
    return f"{','.join(sorted(path))}|{position}"


def collect_key(contents, key, distance, distance_so_far):
    """
    >>> collect_key({
    ...     (1, 1): 'A', (2, 1): 'space', (3, 1): 'space', (4, 1): 'a',
    ... }, 'a', 1, 0)
    ({(1, 1): 'space', (2, 1): 'space', (3, 1): 'space', (4, 1): 'space'}, (4, 1), 1)
    >>> collect_key({
    ...     (1, 1): 'space', (2, 1): 'space', (3, 1): 'space', (4, 1): 'a',
    ... }, 'a', 1, 0)
    ({(1, 1): 'space', (2, 1): 'space', (3, 1): 'space', (4, 1): 'space'}, (4, 1), 1)
    """
    reverse_contents = {
        content: position
        for position, content in contents.items()
    }
    new_contents = {
        **contents,
        reverse_contents[key]: 'space',
    }
    door_position = reverse_contents.get(key.upper())
    if door_position:
        new_contents[door_position] = 'space'

    return new_contents, reverse_contents[key], distance + distance_so_far


def parse_map(map_text):
    """
    >>> parse_map(
    ...     "######\\n"
    ...     "#A.@a#\\n"
    ...     "######\\n"
    ... )
    ({(1, 1): 'A', (2, 1): 'space', (3, 1): 'space', (4, 1): 'a'}, [(3, 1)])
    >>> parse_map(
    ...     "######\\n"
    ...     "#@.@a#\\n"
    ...     "######\\n"
    ... )
    ({(1, 1): 'space', (2, 1): 'space', (3, 1): 'space', (4, 1): 'a'}, [(1, 1), (3, 1)])
    """
    lines = map_text.splitlines()
    non_empty_lines = list(filter(None, map(str.strip, lines)))
    start_positions = [
        (x, y)
        for y, line in enumerate(non_empty_lines)
        for x, content in enumerate(line)
        if content == '@'
    ]
    contents = {
        (x, y): (
            'space'
            if content in ['.', '@'] else
            content
        )
        for y, line in enumerate(non_empty_lines)
        for x, content in enumerate(line)
        if content != '#'
    }

    return contents, start_positions


OFFSETS = [
    (0, -1),
    (0, 1),
    (1, 0),
    (-1, 0),
]


def get_neighbour_positions(position):
    """
    >>> get_neighbour_positions((0, 0))
    [(0, -1), (0, 1), (1, 0), (-1, 0)]
    >>> get_neighbour_positions((-3, 4))
    [(-3, 3), (-3, 5), (-2, 4), (-4, 4)]
    """
    x, y = position
    return [
        (x + offset_x, y + offset_y)
        for offset_x, offset_y in OFFSETS
    ]


Challenge.main()
challenge = Challenge()
