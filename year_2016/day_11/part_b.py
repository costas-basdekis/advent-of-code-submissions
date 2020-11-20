#!/usr/bin/env python3
from dataclasses import dataclass
from functools import total_ordering
from itertools import count, combinations, product
from typing import List, Tuple, Generic, Type, Set, Dict

from aox.utils import Timer
from utils import BaseChallenge, TV, get_type_argument_class, Cls, Self, \
    all_possible_combinations, int_to_bits
from utils.bitpacking import bits_to_int
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        55
        """
        building = part_a.Building.from_building_text(_input)
        building.floors[1].extend([
            part_a.Generator('elerium'), part_a.Microchip('elerium'),
            part_a.Generator('dilithium'), part_a.Microchip('dilithium'),
        ])
        if debug:
            print(building.show())
        return OptimisedBuildingSolver.from_building(building)\
            .get_smallest_solution_length(debug=debug)


OptimisedBuildingT = TV['OptimisedBuilding']


@dataclass
class OptimisedBuildingSolver(Generic[OptimisedBuildingT]):
    optimised_building: OptimisedBuildingT
    complete_optimised_building: OptimisedBuildingT
    floor_next_steps_map: Dict[
        Tuple[int, int],
        List[Tuple[Tuple[int, int], Tuple[int, int]]],
    ]
    next_floor_map: Dict[int, Set[int]]

    @classmethod
    def get_optimised_building_class(cls) -> Type[OptimisedBuildingT]:
        return get_type_argument_class(cls, OptimisedBuildingT)

    @classmethod
    def from_building(
            cls: Cls['OptimisedBuildingSolver'], building: part_a.Building,
    ) -> Self['OptimisedBuildingSolver']:
        optimised_building = cls.get_optimised_building_class()\
            .from_building(building)
        possible_objects = [
            bits_to_int(flags)
            for flags in all_possible_combinations(
                optimised_building.flag_by_type.values())
        ]
        possible_floors = product(possible_objects, possible_objects)
        all_floors = set(range(len(optimised_building.generators)))
        return cls(
            optimised_building=optimised_building,
            complete_optimised_building=optimised_building.get_complete(),
            floor_next_steps_map={
                floor: cls.get_next_floor_and_items_to_pick(*floor)
                for floor in possible_floors
            },
            next_floor_map={
                floor: {floor - 1, floor + 1} & all_floors
                for floor in all_floors
            },
        )

    def get_smallest_solution_length(self, debug: bool = False) -> int:
        return self.solve(debug=debug)

    def solve(self, debug: bool = False) -> int:
        if self.optimised_building.is_complete():
            return 0
        seen = {self.optimised_building}
        stack: List[Tuple[int, OptimisedBuildingT]] = [
            (0, self.optimised_building),
        ]
        if debug:
            timer = Timer()
        for step in count():
            if not stack:
                break
            distance, current_building = stack.pop(0)
            next_buildings = self.get_next_states(current_building)
            next_buildings -= seen
            next_distance = distance + 1
            for next_building in next_buildings:
                seen.add(next_building)
                if next_building.is_complete():
                    return next_distance
                stack.append((next_distance, next_building))

            if debug:
                if step % 5000 == 0:
                    # noinspection PyUnboundLocalVariable
                    print(
                        f"Step {step}, time: "
                        f"{timer.get_pretty_current_duration(0)}, stack: "
                        f"{len(stack)}, seen: {len(seen)}, distance: "
                        f"{distance}")

        raise Exception(f"Cannot find a solution")

    def double_solve(self, debug: bool = False) -> int:
        if self.optimised_building.is_complete():
            return 0
        distances_from_start = {self.optimised_building: 0}
        distances_from_end = {self.complete_optimised_building: 0}
        stack_from_start: List[Tuple[int, OptimisedBuildingT]] = [
            (0, self.optimised_building),
        ]
        stack_from_end: List[Tuple[int, OptimisedBuildingT]] = [
            (0, self.complete_optimised_building),
        ]
        searches = [
            (stack_from_start, distances_from_start, distances_from_end),
            (stack_from_end, distances_from_end, distances_from_start),
        ]
        if debug:
            timer = Timer()
        for step in count():
            if not stack_from_start or not stack_from_end:
                break
            for stack, distances, other_distances in searches:
                distance, current_building = stack.pop(0)
                next_buildings = self.get_next_states(current_building)
                next_buildings -= set(distances)
                next_distance = distance + 1
                for next_building in next_buildings:
                    if next_building in other_distances:
                        return (
                            next_distance + other_distances[next_building] - 1
                        )
                    distances[next_building] = next_distance
                    stack.append((next_distance, next_building))

            if debug:
                if step % 5000 == 0:
                    # noinspection PyUnboundLocalVariable
                    print(
                        f"Step {step}, time: "
                        f"{timer.get_pretty_current_duration(0)}, stack: "
                        f"{len(stack)}, seen: "
                        f"{len(distances_from_start) + len(distances_from_end)}"
                        f", distance: {distance}")

        raise Exception(f"Cannot find a solution")

    def get_next_states(self, optimised_building: OptimisedBuildingT
                        ) -> Set[OptimisedBuildingT]:
        """
        >>> def check(floors=None, position=1):
        ...     building = part_a.Building(floors or {}, position)
        ...     _optimised_building = OptimisedBuilding.from_building(building)
        ...     solver = OptimisedBuildingSolver.from_building(building)
        ...     # noinspection PyUnresolvedReferences
        ...     return sorted(
        ...         b.to_building().get_hash()
        ...         for b in solver.get_next_states(_optimised_building)
        ...     )
        >>> check()
        []
        >>> check({2: []})
        []
        >>> check({2: [part_a.Microchip('a')]})
        []
        >>> # noinspection PyUnresolvedReferences
        >>> check({1: [part_a.Microchip('a')], 2: []})
        ['e:2|1:|2:AM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [part_a.Microchip('a'), part_a.Microchip('b'),
        ...         part_a.Microchip('c')],
        ...     2: []
        ... })
        ['e:2|1:AM,BM|2:CM', 'e:2|1:AM,CM|2:BM', 'e:2|1:AM|2:BM,CM',
            'e:2|1:BM,CM|2:AM', 'e:2|1:BM|2:AM,CM',
            'e:2|1:CM|2:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [],
        ...     2: [part_a.Microchip('a'), part_a.Microchip('b'),
        ...         part_a.Microchip('c')]
        ... }, 2)
        ['e:1|1:AM,BM|2:CM', 'e:1|1:AM,CM|2:BM', 'e:1|1:AM|2:BM,CM',
            'e:1|1:BM,CM|2:AM', 'e:1|1:BM|2:AM,CM',
            'e:1|1:CM|2:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [],
        ...     2:[part_a.Microchip('a'), part_a.Microchip('b'),
        ...        part_a.Microchip('c')],
        ...     3: []
        ... }, 2)
        ['e:1|1:AM,BM|2:CM|3:', 'e:1|1:AM,CM|2:BM|3:', 'e:1|1:AM|2:BM,CM|3:',
            'e:1|1:BM,CM|2:AM|3:', 'e:1|1:BM|2:AM,CM|3:',
            'e:1|1:CM|2:AM,BM|3:',
            'e:3|1:|2:AM,BM|3:CM', 'e:3|1:|2:AM,CM|3:BM', 'e:3|1:|2:AM|3:BM,CM',
            'e:3|1:|2:BM,CM|3:AM', 'e:3|1:|2:BM|3:AM,CM',
            'e:3|1:|2:CM|3:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [part_a.Generator('a')],
        ...     2: [part_a.Microchip('a'), part_a.Microchip('b'),
        ...         part_a.Microchip('c')],
        ...     3: []
        ... }, 2)
        ['e:1|1:AG,AM|2:BM,CM|3:',
            'e:3|1:AG|2:AM,BM|3:CM', 'e:3|1:AG|2:AM,CM|3:BM',
            'e:3|1:AG|2:AM|3:BM,CM',
            'e:3|1:AG|2:BM,CM|3:AM', 'e:3|1:AG|2:BM|3:AM,CM',
            'e:3|1:AG|2:CM|3:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [part_a.Generator('a')],
        ...     2: [part_a.Microchip('a'), part_a.Microchip('b'),
        ...         part_a.Generator('b')],
        ...     3: []
        ... }, 2)
        ['e:1|1:AG,AM,BG|2:BM|3:', 'e:1|1:AG,AM|2:BG,BM|3:',
            'e:1|1:AG,BG,BM|2:AM|3:', 'e:1|1:AG,BG|2:AM,BM|3:',
            'e:3|1:AG|2:AM,BM|3:BG', 'e:3|1:AG|2:AM|3:BG,BM',
            'e:3|1:AG|2:BG,BM|3:AM', 'e:3|1:AG|2:BG|3:AM,BM']
        """
        if not (0 <= optimised_building.position
                < len(optimised_building.generators)):
            return set()
        generators = optimised_building.generators[optimised_building.position]
        microchips = optimised_building.microchips[optimised_building.position]
        if not generators and not microchips:
            return set()
        next_steps = self.floor_next_steps_map[(generators, microchips)]
        next_floors = self.next_floor_map[optimised_building.position]
        optimised_building_class = self.get_optimised_building_class()
        next_states = {
            optimised_building_class(tuple(
                (
                    generators | pick_generators
                    if floor == next_floor else
                    next_generators
                    if floor == optimised_building.position else
                    generators
                )
                for floor, generators in enumerate(optimised_building.generators)
            ), tuple(
                (
                    microchips | pick_microchips
                    if floor == next_floor else
                    next_microchips
                    if floor == optimised_building.position else
                    microchips
                )
                for floor, microchips in enumerate(optimised_building.microchips)
            ), next_floor, optimised_building.flag_by_type)
            for ((next_generators, next_microchips),
                 (pick_generators, pick_microchips)) in next_steps
            for next_floor in next_floors
        }
        return {
            state
            for state in next_states
            if state.is_valid()
        }

    @classmethod
    def get_next_floor_and_items_to_pick(
            cls, generators: int, microchips: int
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        >>> OptimisedBuildingSolver.get_next_floor_and_items_to_pick(0, 0)
        []
        >>> OptimisedBuildingSolver.get_next_floor_and_items_to_pick(1, 0)
        [((0, 0), (1, 0))]
        >>> OptimisedBuildingSolver.get_next_floor_and_items_to_pick(1, 0)
        [((0, 0), (1, 0))]
        >>> OptimisedBuildingSolver.get_next_floor_and_items_to_pick(7, 0)
        [((6, 0), (1, 0)), ((5, 0), (2, 0)), ((3, 0), (4, 0)), ((4, 0), (3, 0)),
            ((2, 0), (5, 0)), ((1, 0), (6, 0))]
        >>> OptimisedBuildingSolver.get_next_floor_and_items_to_pick(0, 7)
        [((0, 6), (0, 1)), ((0, 5), (0, 2)), ((0, 3), (0, 4)), ((0, 4), (0, 3)),
            ((0, 2), (0, 5)), ((0, 1), (0, 6))]
        >>> OptimisedBuildingSolver.get_next_floor_and_items_to_pick(3, 3)
        [((3, 2), (0, 1)), ((3, 1), (0, 2)), ((0, 3), (3, 0)), ((2, 2), (1, 1)),
            ((1, 1), (2, 2)), ((3, 0), (0, 3))]
        """
        a_building = cls.get_optimised_building_class()((), (), 0, {})
        items_to_pick = cls.get_items_to_pick(generators, microchips)
        return [
            ((next_generators, next_microchips),
             (pick_generators, pick_microchips))
            for ((next_generators, next_microchips),
                 (pick_generators, pick_microchips)) in (
                ((generators & ~pick_generators, microchips & ~pick_microchips),
                 (pick_generators, pick_microchips))
                for pick_generators, pick_microchips in items_to_pick
            )
            if a_building.is_floor_valid(next_generators, next_microchips)
        ]

    @classmethod
    def get_items_to_pick(cls, generators: int, microchips: int
                          ) -> List[Tuple[int, int]]:
        """
        >>> OptimisedBuildingSolver.get_items_to_pick(0, 0)
        []
        >>> OptimisedBuildingSolver.get_items_to_pick(1, 0)
        [(1, 0)]
        >>> OptimisedBuildingSolver.get_items_to_pick(1, 0)
        [(1, 0)]
        >>> OptimisedBuildingSolver.get_items_to_pick(7, 0)
        [(1, 0), (2, 0), (4, 0), (3, 0), (5, 0), (6, 0)]
        >>> OptimisedBuildingSolver.get_items_to_pick(0, 7)
        [(0, 1), (0, 2), (0, 4), (0, 3), (0, 5), (0, 6)]
        >>> OptimisedBuildingSolver.get_items_to_pick(3, 4)
        [(1, 0), (2, 0), (0, 4), (3, 0), (1, 4), (2, 4)]
        >>> OptimisedBuildingSolver.get_items_to_pick(3, 3)
        [(1, 0), (2, 0), (0, 1), (0, 2), (3, 0), (1, 1), (1, 2), (2, 1), (2, 2),
            (0, 3)]
        """
        items_list = cls.get_items_to_pick_from_list(
            [('G', item) for item in int_to_bits(generators)]
            + [('M', item) for item in int_to_bits(microchips)]
        )
        generator_items = [
            bits_to_int(
                item
                for _type, item in items
                if _type == 'G'
            )
            for items in items_list
        ]
        microchip_items = [
            bits_to_int(
                item
                for _type, item in items
                if _type == 'M'
            )
            for items in items_list
        ]
        return list(zip(generator_items, microchip_items))

    @classmethod
    def get_items_to_pick_from_list(cls, contents: List
                                    ) -> List[List]:
        """
        >>> OptimisedBuildingSolver.get_items_to_pick_from_list([])
        []
        >>> OptimisedBuildingSolver.get_items_to_pick_from_list([1])
        [[1]]
        >>> OptimisedBuildingSolver.get_items_to_pick_from_list([1, 2, 4])
        [[1], [2], [4], [1, 2], [1, 4], [2, 4]]
        """
        return [
            [_object]
            for _object in contents
        ] + [
            [first, second]
            for first, second in combinations(contents, 2)
        ]


@total_ordering
@dataclass(eq=True, frozen=True)
class OptimisedBuilding:
    generators: Tuple[int]
    microchips: Tuple[int]
    position: int
    flag_by_type: Dict[str, int]

    @classmethod
    def from_building(cls: Cls['OptimisedBuilding'], building: part_a.Building
                      ) -> Self['OptimisedBuilding']:
        """
        >>> def check(*args):
        ...     return OptimisedBuilding\\
        ...         .from_building(part_a.Building(*args))\\
        ...         .get_hash()
        >>> check()
        (0, (), ())
        >>> check({1: []})
        (0, (0,), (0,))
        >>> check({1: [part_a.Microchip('a')]})
        (0, (0,), (1,))
        >>> check({1: [part_a.Microchip('a')], 2: []})
        (0, (0, 0), (1, 0))
        >>> check({
        ...     1: [part_a.Microchip('a')],
        ...     2: [part_a.Generator('a')],
        ...     3: [part_a.Generator('b'), part_a.Microchip('b'),
        ...         part_a.Generator('c'), part_a.Microchip('d')]
        ... })
        (0, (0, 1, 6), (1, 0, 10))
        """
        if building.floors:
            min_floor = min(building.floors)
            max_floor = max(building.floors)
        else:
            min_floor = 1
            max_floor = 0
        position = building.position - min_floor
        floors_contents = [
            building.floors[floor]
            for floor in range(min_floor, max_floor + 1)
        ]
        all_types = {
            _object.type
            for contents in floors_contents
            for _object in contents
            if isinstance(_object, (part_a.Generator, part_a.Microchip))
        }
        flag_by_type = {
            _type: 2 ** index
            for index, _type in enumerate(sorted(all_types))
        }
        return cls(
            generators=tuple(
                bits_to_int(
                    flag_by_type[_object.type]
                    for _object in contents
                    if isinstance(_object, part_a.Generator)
                )
                for contents in floors_contents
            ),
            microchips=tuple(
                bits_to_int(
                    flag_by_type[_object.type]
                    for _object in contents
                    if isinstance(_object, part_a.Microchip)
                )
                for contents in floors_contents
            ),
            position=position,
            flag_by_type=flag_by_type,
        )

    def to_building(self) -> part_a.Building:
        """
        >>> def check(*args):
        ...     return OptimisedBuilding\\
        ...         .from_building(part_a.Building(*args))\\
        ...         .to_building()\\
        ...         .get_hash()
        >>> check()
        'e:1|'
        >>> check({1: []})
        'e:1|1:'
        >>> check({1: [part_a.Microchip('a')], 2: []})
        'e:1|1:AM|2:'
        """
        type_by_flag = {
            flag: _type
            for _type, flag in self.flag_by_type.items()
        }
        return part_a.Building(
            floors={
                floor + 1: [
                    part_a.Generator(type_by_flag[flag])
                    for flag in int_to_bits(generators)
                ] + [
                    part_a.Microchip(type_by_flag[flag])
                    for flag in int_to_bits(microchips)
                ]
                for floor, (generators, microchips)
                in enumerate(zip(self.generators, self.microchips))
            },
            position=self.position + 1,
        )

    def __lt__(self, other: 'OptimisedBuilding') -> bool:
        return self.get_hash() < other.get_hash()

    def __hash__(self):
        return hash(self.get_hash())

    def get_hash(self) -> Tuple[int, Tuple[int, ...], Tuple[int, ...]]:
        return self.position, self.generators, self.microchips

    def get_complete(self: Self['OptimisedBuilding']
                     ) -> Self['OptimisedBuilding']:
        cls: Cls['OptimisedBuilding'] = type(self)
        top_floor = min(0, len(self.generators) - 1)
        # noinspection PyArgumentList
        return cls(
            generators=tuple(
                bits_to_int(self.generators)
                if floor == top_floor else
                0
                for floor in range(len(self.generators))
            ),
            microchips=tuple(
                bits_to_int(self.microchips)
                if floor == top_floor else
                0
                for floor in range(len(self.microchips))
            ),
            position=top_floor,
            flag_by_type=self.flag_by_type,
        )

    def is_valid(self) -> bool:
        return all(
            self.is_floor_valid(generators, microchips)
            for generators, microchips in zip(self.generators, self.microchips)
        )

    def is_complete(self) -> bool:
        return (
            not any(self.generators[:-1])
            and not any(self.microchips[:-1])
        )

    def is_floor_valid(self, generators: int, microchips: int) -> bool:
        return not generators or not (microchips & ~generators)


Challenge.main()
challenge = Challenge()
