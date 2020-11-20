#!/usr/bin/env python3
import itertools

import utils
from year_2018.day_22 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        982
        """
        return CaveExtended.from_cave_description(_input)\
            .get_shortest_time()


class CaveExtended(part_a.Cave):
    TOOL_TORCH = 'torch'
    TOOL_GEAR = 'gear'
    TOOL_NEITHER = 'neither'

    TOOLS_BY_TYPE = {
        part_a.Cave.TYPE_ROCKY: {TOOL_TORCH, TOOL_GEAR},
        part_a.Cave.TYPE_WET: {TOOL_GEAR, TOOL_NEITHER},
        part_a.Cave.TYPE_NARROW: {TOOL_NEITHER, TOOL_TORCH},
    }

    TYPES_BY_TOOL = {
        tool: set(_type for _, _type in items)
        for tool, items in itertools.groupby(sorted(
            (tool, _type)
            for tool, types in TOOLS_BY_TYPE.items()
            for _type in types
        ), key=lambda item: item[0])
    }

    def get_shortest_time(self, start=(0, 0), start_tool=TOOL_TORCH, end=None,
                          debug=False, report_count=500000):
        """
        >>> CaveExtended(510, (10, 10)).get_shortest_time()
        45
        """
        if end is None:
            end = self.target

        distances = {(start, start_tool): 0}
        stack = [(start, start_tool, 0, 0)]
        if debug:
            count = 0
        while stack and (end, self.TOOL_TORCH) not in distances:
            if debug:
                count += 1
                if count % report_count == 0:
                    print(count, len(distances), len(stack))
            position, tool, distance, wait_time = stack.pop(0)
            if wait_time:
                if (position, tool) in distances:
                    continue
                if wait_time == 1:
                    distances[(position, tool)] = distance
                stack.append((position, tool, distance, wait_time - 1))
                continue
            _type = self.get_type(position)
            next_states = [
                ((position, next_tool), distance + 7, 6)
                for next_tool in self.TOOLS_BY_TYPE[_type] - {tool}
            ] + [
                ((next_position, tool), distance + 1, 0)
                for next_position in self.get_neighbours(position, tool)
            ]
            for item, next_distance, wait_time in next_states:
                if item in distances:
                    continue
                if wait_time == 0:
                    distances[item] = next_distance
                stack.append(item + (next_distance, wait_time))

        target_time = distances.get((end, self.TOOL_TORCH))
        if target_time is None:
            raise Exception(f"Could not find target")

        return target_time

    def get_neighbours(self, position, tool):
        return [
            (x, y)
            for x, y in utils.helper.get_manhattan_neighbours(position)
            if x >= 0 and y >= 0
            and tool in self.TOOLS_BY_TYPE[self.get_type((x, y))]
        ]


challenge = Challenge()
challenge.main()
