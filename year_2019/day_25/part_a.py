#!/usr/bin/env python3
import doctest
import itertools
import sys
import time

from utils import get_current_directory
from year_2019.day_15.part_a import run_interactive_program
import year_2019.day_09.part_a


def solve(_input=None):
    """
    >>> solve()
    8401920
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    password = play_game(_input)
    if not password:
        raise Exception("Could not find password")

    return password


def play_game(program_text=None, interactive=False):
    if interactive:
        interactive_print = print
    else:
        interactive_print = lambda *args: None
    if program_text is None:
        program_text = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()

    ship = {
        "rooms": {},
        "items": set(),
        "picked_items": set(),
        "avoid_items": {
            "escape pod",
            "giant electromagnet",
            "photons",
            "infinite loop",
            "molten lava",
        },
        "too_light": set(),
        "too_heavy": set(),
    }

    program = run_interactive_program(program_text)
    last_room_name = None
    last_input_text = None
    _, output = program.send(None)
    suggestions_left = []
    do_all_suggestions = False
    while True:
        output_text = "".join(map(chr, output))
        try:
            last_room_name = handle_output(
                last_input_text, last_room_name, output_text, ship)
        except Exception:
            interactive_print(output_text)
            if "Oh, hello!" in output_text:
                password_line, = [
                    line
                    for line in output_text.splitlines()
                    if "Oh, hello!" in line
                ]
                password = int(password_line.split("typing ")[-1].split(" on")[0])
                return password
            raise
        doors_to_open = {
            door
            for door, next_room
            in ship['rooms'][last_room_name]['doors'].items()
            if not next_room
        }
        items_to_pick = {
            item
            for item in ship['rooms'][last_room_name]['items']
            if item not in ship['avoid_items']
        }
        # interactive_print(last_room_name, ship)
        # interactive_print("Rooms:")
        # for room in sorted(ship['rooms'].values(), key=lambda _room: _room['name']):
        #     if room['name'] == last_room_name:
        #         room_icon = '>'
        #     elif not all(room['doors'].values()):
        #         room_icon = '*'
        #     elif room['name'] in ship['rooms'][last_room_name]['doors'].values():
        #         room_icon = {
        #             destination: direction
        #             for direction, destination
        #             in ship['rooms'][last_room_name]['doors'].items()
        #         }[room['name']][0]
        #     else:
        #         room_icon = '.'
        #     interactive_print(
        #         f"{room_icon} "
        #         f"{room['name']}: "
        #         f"{room['description']}")
        if ship['picked_items']:
            interactive_print("Inventory:")
            for item in sorted(ship['picked_items']):
                interactive_print(f"  {item}")
            combination = tuple(sorted(ship['picked_items']))
            if combination in ship["too_light"]:
                interactive_print("Too light, pick some more")
            elif combination in ship["too_heavy"]:
                interactive_print("Too heavy, shed some more")
            else:
                interactive_print("Try to go to PSF!")
        # interactive_print(doors_to_open, items_to_pick)

        interactive_print(output_text)
        if suggestions_left:
            last_input_text, *suggestions_left = suggestions_left
            interactive_print(last_input_text)
        else:
            suggestions = get_suggestions(last_room_name, ship)
            interactive_print("Suggestions:", suggestions)

            while True:
                if do_all_suggestions:
                    if not suggestions:
                        interactive_print("No suggestions left")
                        do_all_suggestions = False
                        continue
                    last_input_text, *suggestions_left = suggestions
                    interactive_print(last_input_text)
                    break
                if interactive:
                    last_input_text = input("> ")
                else:
                    last_input_text = "all"
                if not last_input_text and suggestions:
                    last_input_text, *suggestions_left = suggestions
                    interactive_print(last_input_text)
                elif last_input_text == "all":
                    if not suggestions:
                        interactive_print("No suggestions left")
                        continue
                    last_input_text, *suggestions_left = suggestions
                    interactive_print(last_input_text)
                    do_all_suggestions = True
                elif last_input_text == "weight":
                    suggestions = get_weighting_suggestions(last_room_name, ship)
                    if not suggestions:
                        interactive_print("No suggestions left")
                        continue
                    last_input_text, *suggestions_left = suggestions
                    interactive_print(last_input_text)
                    do_all_suggestions = True
                elif last_input_text.startswith("goto ") or last_input_text == "psf":
                    target = last_input_text.replace("goto ", '')
                    if target == "psf":
                        target = "Pressure-Sensitive Floor"
                    target_room = ship["rooms"].get(target)
                    if not target_room:
                        interactive_print(f"Unknown room {target}")
                        continue
                    _, path = find_closest_room(ship, last_room_name, target)
                    if path is None:
                        interactive_print(f"Could not reach {target}")
                        continue
                    last_input_text, *suggestions_left = path
                    interactive_print(last_input_text)
                elif last_input_text.startswith("gowhere "):
                    target_item = last_input_text.replace("gowhere ", '')
                    room_by_item = {
                        item: room['name']
                        for room in ship["rooms"].values()
                        for item in room["items"]
                    }
                    target = room_by_item.get(target_item)
                    if not target:
                        interactive_print(f"Not known item {target_item}")
                        continue
                    _, path = find_closest_room(ship, last_room_name, target)
                    if path is None:
                        interactive_print(f"Could not reach {target}")
                        continue
                    last_input_text, *suggestions_left = path
                    interactive_print(last_input_text)

                break

        input_stream = list(map(ord, last_input_text + "\n"))
        _, output = program.send(input_stream)


def get_suggestions(last_room_name, ship):
    last_room = ship["rooms"].get(last_room_name)
    if not last_room:
        return []

    items_to_pick = last_room["items"] - ship["picked_items"] - ship["avoid_items"]
    if items_to_pick:
        return sorted(
            f"take {item}"
            for item in items_to_pick
        )

    doors_to_open = {
        door
        for door, destination
        in last_room["doors"].items()
        if not destination
    }
    if doors_to_open:
        return [sorted(doors_to_open)[0]]

    free_room_names = {
        room["name"]
        for room in ship["rooms"].values()
        if not all(room["doors"].values())
    }
    if free_room_names:
        if last_room_name in free_room_names:
            raise Exception(
                "Somehow there are no mystery doors in current room, but "
                "current room is one with mystery doors")
        _, path = find_closest_room(
            ship, last_room['name'], free_room_names)
        if path:
            return list(path)

    if last_room_name != "Security Checkpoint":
        _, path = find_closest_room(
            ship, last_room['name'], ["Security Checkpoint"])
        if path:
            return list(path)

    return get_weighting_suggestions(last_room_name, ship)


def get_weighting_suggestions(last_room_name, ship):
    if last_room_name != "Security Checkpoint":
        raise Exception("Can't get weighting suggestions if not in Security Checkpoint")
    if len(ship["picked_items"]) != 8:
        raise Exception("Need to have 8 items to get weighting suggestions")
    combination = next(iter(all_combinations(ship)))
    # print(combination, len(ship["too_heavy"]), "too heavy", len(ship["too_light"]), "too light")
    # time.sleep(0.25)
    suggestions = []
    for item in sorted(ship["picked_items"]):
        if item not in combination:
            suggestions.append(f"drop {item}")
            suggestions.append("south")
    suggestions.append("south")
    for item in sorted(ship["picked_items"]):
        if item not in combination:
            suggestions.append(f"take {item}")

    return suggestions


def all_combinations(ship):
    # Shortcut :wink:
    combination = ('fuel cell', 'jam', 'sand', 'spool of cat6')
    if combination not in (ship["too_light"] | ship["too_heavy"]):
        yield combination
    for length in range(9):
        combinations = itertools.combinations(sorted(ship["picked_items"]), length)
        for combination in combinations:
            if combination in (ship["too_light"] | ship["too_heavy"]):
                continue
            yield combination


def find_closest_room(ship, start, targets):
    if start in targets:
        return start, []
    visited = set()
    queue = [(start, ())]
    while queue:
        room, path = queue.pop(0)
        visited.add(room)
        next_steps = [
            (next_room, direction)
            for direction, next_room in ship["rooms"][room]["doors"].items()
            if next_room
            and next_room not in visited
        ]
        for next_room, direction in next_steps:
            next_path = path + (direction,)
            if next_room in targets:
                return next_room, next_path
            queue.append((next_room, next_path))

    return None, None


def handle_output(last_input_text, last_room_name, output, ship):
    lines = list(filter(None, map(str.strip, output.splitlines())))
    room_name_lines = [
        line
        for line in lines
        if line.startswith('==')
    ]
    last_room = ship['rooms'].get(last_room_name)
    if ship["rooms"] and not last_room_name:
        raise Exception("Don't know last position")
    if not room_name_lines:
        take_lines = [
            line
            for line in lines
            if line.startswith('You take the ')
        ]
        if len(take_lines) > 1:
            raise Exception(f"Got too many take lines: {len(take_lines)}")
        elif len(take_lines) == 1:
            take_line, = take_lines
            item = take_line.replace('You take the ', '').replace('.', '')
            if item not in ship["picked_items"]:
                ship["picked_items"].add(item)
        drop_lines = [
            line
            for line in lines
            if line.startswith('You drop the ')
        ]
        if len(drop_lines) > 1:
            raise Exception(f"Got too many drop lines: {len(drop_lines)}")
        elif len(drop_lines) == 1:
            drop_line, = drop_lines
            item = drop_line.replace('You drop the ', '').replace('.', '')
            if item in ship["picked_items"]:
                ship["picked_items"].remove(item)
        return last_room_name
    room_name_line = room_name_lines[0]
    room_name = room_name_line.replace('== ', '').replace(' ==', '')
    room_name_line_index = lines.index(room_name_line)
    description = lines[room_name_line_index + 1]
    door_lines_index = lines.index('Doors here lead:')
    door_lines = lines[door_lines_index + 1:door_lines_index + 5]
    door_lines = [
        line
        for index, line in enumerate(door_lines)
        if all(line_2.startswith('- ') for line_2 in door_lines[:index + 1])
    ]
    doors = {
        line.split('- ')[-1]
        for line in door_lines
    }
    if 'Items here:' in lines:
        item_lines_index = lines.index('Items here:')
        item_lines = lines[item_lines_index + 1:item_lines_index + 10]
        item_lines = [
            line
            for index, line in enumerate(item_lines)
            if all(line_2.startswith('- ') for line_2 in item_lines[:index + 1])
        ]
        items = sorted(
            line.split('- ')[-1]
            for line in item_lines
        )
    else:
        items = []

    if room_name not in ship['rooms']:
        ship['rooms'][room_name] = {
            "name": room_name,
            "description": description,
            "doors": {
                door: None
                for door in doors
            },
            "items": set(items),
        }
    room = ship['rooms'][room_name]

    weighting_lines = [
        line
        for line in lines
        if "Alert! Droids on this ship are " in line
    ]
    if weighting_lines:
        weighting_line, = weighting_lines
        if "Alert! Droids on this ship are lighter than the detected value!" in weighting_line:
            ship["too_heavy"].add(tuple(sorted(ship["picked_items"])))
        elif "Alert! Droids on this ship are heavier than the detected value!" in weighting_line:
            ship["too_light"].add(tuple(sorted(ship["picked_items"])))
        else:
            raise Exception(f"Unknown weighting line: {weighting_line}")
    elif room_name == "Pressure-Sensitive Floor":
        raise Exception("No weighting line found in PSF")

    if last_room_name and last_room_name != room_name and last_room_name not in room["doors"].values():
        if last_input_text not in OPPOSITE_DIRECTION:
            raise Exception(
                f"Moved rooms but last input was not a direction: "
                f"{last_input_text}")
        direction = last_input_text
        opposite_direction = OPPOSITE_DIRECTION[direction]
        if last_room["doors"][direction] is None:
            last_room["doors"][direction] = room_name
        elif last_room["doors"][direction] != room_name:
            raise Exception(
                f"Multiple rooms {direction} of {last_room_name}: {room_name} "
                f"or {last_room['doors'][direction]}")
        if room["doors"][opposite_direction] is None:
            room["doors"][opposite_direction] = last_room_name
        elif room["doors"][opposite_direction] != last_room_name:
            raise Exception(
                f"Multiple rooms {opposite_direction} of {room_name}: "
                f"{last_room_name} or {room['doors'][opposite_direction]}")

    if len(room_name_lines) > 1:
        second_room_line = room_name_lines[1]
        second_room_line_index = lines.index(second_room_line)
        rest_lines = lines[second_room_line_index:]
        rest_output = "\n".join(rest_lines)
        return handle_output(None, room_name, rest_output, ship)

    return room_name


OPPOSITE_DIRECTION = {
    'east': 'west',
    'west': 'east',
    'north': 'south',
    'south': 'north',
}


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1:] != ['play']:
            raise Exception(f"Only valid argument is 'play'")
        play_game(interactive=True)
    else:
        if doctest.testmod().failed:
            print("Tests failed")
        else:
            print("Tests passed")
        print("Solution:", solve())
