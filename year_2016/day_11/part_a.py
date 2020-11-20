#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from functools import total_ordering
from itertools import count, combinations
from typing import Dict, Optional, Generic, List, Tuple, Type, Set

from aox.utils import Timer
from utils import BaseChallenge, PolymorphicParser, Self, Cls, TV, \
    get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        """
        """
        >>> Challenge().default_solve()
        31
        """
        building = Building.from_building_text(_input)
        if debug:
            print(building.show())
        return building.get_smallest_solution_length(debug=debug)


BuildingT = TV['Building']


class BuildingSolver(Generic[BuildingT]):
    @classmethod
    def get_building_class(cls) -> Type[BuildingT]:
        return get_type_argument_class(cls, BuildingT)

    def get_smallest_solution_length(
            self, building: BuildingT, debug: bool = False) -> int:
        """
        >>> Building.from_building_text(
        ...     "The first floor contains a hydrogen-compatible microchip and "
        ...     "a lithium-compatible microchip.\\n"
        ...     "The second floor contains a hydrogen generator.\\n"
        ...     "The third floor contains a lithium generator.\\n"
        ...     "The fourth floor contains nothing relevant.\\n"
        ... ).get_smallest_solution_length()
        11
        """
        return len(self.solve(building, debug=debug))

    def solve(self, building: BuildingT, debug: bool = False
              ) -> List[BuildingT]:
        if building.is_complete():
            return []
        previous_map: Dict[BuildingT, BuildingT] = {building: None}
        stack: List[Tuple[int, BuildingT]] = [(0, building)]
        if debug:
            timer = Timer()
        for step in count():
            if not stack:
                break
            distance, current_building = stack.pop(0)
            next_buildings = self.get_next_states(current_building)
            next_buildings -= set(previous_map)
            next_distance = distance + 1
            for next_building in next_buildings:
                previous_map[next_building] = current_building
                if next_building.is_complete():
                    return self.map_solution(previous_map, next_building)
                stack.append((next_distance, next_building))

            if debug:
                if step % 5000 == 0:
                    # noinspection PyUnboundLocalVariable
                    print(
                        f"Step {step}, time: "
                        f"{timer.get_pretty_current_duration(0)}s, stack: "
                        f"{len(stack)}, seen: {len(previous_map)}, "
                        f"distance: {distance}")

        raise Exception(f"Cannot find a solution")

    def map_solution(self, previous_map: Dict[BuildingT, BuildingT],
                     last_building: BuildingT) -> [BuildingT]:
        """
        >>> BuildingSolver().map_solution({1: None},1)
        []
        >>> BuildingSolver().map_solution({1: 2, 2: None},1)
        [2]
        >>> BuildingSolver().map_solution({1: 2, 2: None, 3: 4, 4: None},1)
        [2]
        >>> BuildingSolver().map_solution({1: 2, 2: 3, 3: 4, 4: None},1)
        [4, 3, 2]
        >>> BuildingSolver().map_solution({1: 2, 2: 3, 3: 4, 4: 1},1)
        Traceback (most recent call last):
        ...
        Exception: Got cycle when trying to find solution
        """
        solution = []
        current_building = last_building
        while True:
            previous_building = previous_map[current_building]
            if previous_building is None:
                break
            if previous_building in solution:
                raise Exception(
                    f"Got cycle when trying to find solution")
            solution.insert(0, previous_building)
            current_building = previous_building

        return solution

    def get_next_states(self, building: BuildingT) -> Set[BuildingT]:
        """
        >>> def check(floors=None, position=1):
        ...     # noinspection PyUnresolvedReferences
        ...     return sorted(
        ...         b.get_hash()
        ...         for b in BuildingSolver().get_next_states(
        ...             Building(floors or {}, position))
        ...     )
        >>> check()
        []
        >>> check({2: []})
        []
        >>> check({2: [Microchip('a')]})
        []
        >>> # noinspection PyUnresolvedReferences
        >>> check({1: [Microchip('a')], 2: []})
        ['e:2|1:|2:AM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({1: [Microchip('a'), Microchip('b'), Microchip('c')], 2: []})
        ['e:2|1:AM,BM|2:CM', 'e:2|1:AM,CM|2:BM', 'e:2|1:AM|2:BM,CM',
            'e:2|1:BM,CM|2:AM', 'e:2|1:BM|2:AM,CM',
            'e:2|1:CM|2:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [], 2: [Microchip('a'), Microchip('b'), Microchip('c')]}, 2)
        ['e:1|1:AM,BM|2:CM', 'e:1|1:AM,CM|2:BM', 'e:1|1:AM|2:BM,CM',
            'e:1|1:BM,CM|2:AM', 'e:1|1:BM|2:AM,CM',
            'e:1|1:CM|2:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [], 2:[Microchip('a'), Microchip('b'), Microchip('c')],
        ...     3: []}, 2)
        ['e:1|1:AM,BM|2:CM|3:', 'e:1|1:AM,CM|2:BM|3:', 'e:1|1:AM|2:BM,CM|3:',
            'e:1|1:BM,CM|2:AM|3:', 'e:1|1:BM|2:AM,CM|3:',
            'e:1|1:CM|2:AM,BM|3:',
            'e:3|1:|2:AM,BM|3:CM', 'e:3|1:|2:AM,CM|3:BM', 'e:3|1:|2:AM|3:BM,CM',
            'e:3|1:|2:BM,CM|3:AM', 'e:3|1:|2:BM|3:AM,CM',
            'e:3|1:|2:CM|3:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [Generator('a')],
        ...     2: [Microchip('a'), Microchip('b'), Microchip('c')],
        ...     3: []}, 2)
        ['e:1|1:AG,AM|2:BM,CM|3:',
            'e:3|1:AG|2:AM,BM|3:CM', 'e:3|1:AG|2:AM,CM|3:BM',
            'e:3|1:AG|2:AM|3:BM,CM',
            'e:3|1:AG|2:BM,CM|3:AM', 'e:3|1:AG|2:BM|3:AM,CM',
            'e:3|1:AG|2:CM|3:AM,BM']
        >>> # noinspection PyUnresolvedReferences
        >>> check({
        ...     1: [Generator('a')],
        ...     2: [Microchip('a'), Microchip('b'), Generator('b')],
        ...     3: []}, 2)
        ['e:1|1:AG,AM,BG|2:BM|3:', 'e:1|1:AG,AM|2:BG,BM|3:',
            'e:1|1:AG,BG,BM|2:AM|3:', 'e:1|1:AG,BG|2:AM,BM|3:',
            'e:3|1:AG|2:AM,BM|3:BG', 'e:3|1:AG|2:AM|3:BG,BM',
            'e:3|1:AG|2:BG,BM|3:AM', 'e:3|1:AG|2:BG|3:AM,BM']
        """
        floor_contents = building.floors.get(building.position, [])
        if not floor_contents:
            return set()
        items_list = self.get_items_to_pick(floor_contents)
        next_floors = sorted({
            building.position + offset
            for offset in (1, -1)
        } & set(building.floors))
        building_class = self.get_building_class()
        next_states = {
            building_class({
                **building.floors,
                building.position: sorted(set(floor_contents) - set(items)),
                next_floor: sorted(
                    set(building.floors[next_floor])
                    | set(items)
                ),
            }, next_floor)
            for next_floor in next_floors
            for items in items_list
        }
        return {
            state
            for state in next_states
            if state.is_valid()
        }

    def get_items_to_pick(self, contents: List['ObjectT']
                          ) -> List[Tuple['ObjectT', ...]]:
        """
        >>> BuildingSolver().get_items_to_pick([])
        []
        >>> BuildingSolver().get_items_to_pick([1])
        [(1,)]
        >>> BuildingSolver().get_items_to_pick([1, 2, 3])
        [(1,), (2,), (3,), (1, 2), (1, 3), (2, 3)]
        """
        return [
            (_object,)
            for _object in contents
        ] + list(combinations(contents, 2))


ObjectT = TV['Object']


@total_ordering
@dataclass(eq=True, frozen=True)
class Building(Generic[ObjectT]):
    floors: Dict[int, List[ObjectT]] = field(default_factory=dict)
    position: int = 1

    @classmethod
    def get_object_class(cls) -> Type[ObjectT]:
        return get_type_argument_class(cls, ObjectT)

    @classmethod
    def from_building_text(cls: Cls['Building'], building_text: str
                           ) -> Self['Building']:
        """
        >>> Building.from_building_text(
        ...     "The first floor contains a hydrogen-compatible microchip and "
        ...     "a lithium-compatible microchip.\\n"
        ...     "The second floor contains a hydrogen generator.\\n"
        ...     "The third floor contains a lithium generator.\\n"
        ...     "The fourth floor contains nothing relevant.\\n"
        ... )
        Building(floors={1:
            [Microchip(type='hydrogen'), Microchip(type='lithium')],
            2: [Generator(type='hydrogen')], 3: [Generator(type='lithium')],
            4: []}, position=1)
        """
        return cls(dict(map(
            cls.floor_from_floor_text, building_text.splitlines())))

    FLOOR_NAME_MAP = {
        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
    }

    re_floor = re.compile(
        r"^The (\w+) floor contains (?:nothing relevant|(.*))\.$")

    @classmethod
    def floor_from_floor_text(cls, floor_text: str
                              ) -> Tuple[int, List[ObjectT]]:
        """
        >>> Building.floor_from_floor_text(
        ...     "The first floor contains a hydrogen-compatible microchip and "
        ...     "a lithium-compatible microchip.\\n")
        (1, [Microchip(type='hydrogen'), Microchip(type='lithium')])
        >>> Building.floor_from_floor_text(
        ...     "The fourth floor contains nothing relevant.\\n")
        (4, [])
        """
        floor_name, contents_str = cls.re_floor.match(floor_text).groups()
        floor = cls.FLOOR_NAME_MAP[floor_name]
        if contents_str is None:
            contents = []
        else:
            contents = cls.contents_from_content_text(contents_str)

        return floor, contents

    re_contents_separator = re.compile(r"(?:, and |, | and )")

    @classmethod
    def contents_from_content_text(cls, contents_text: str) -> List[ObjectT]:
        """
        >>> Building.contents_from_content_text(
        ...     "a hydrogen-compatible microchip")
        [Microchip(type='hydrogen')]
        >>> Building.contents_from_content_text(
        ...     "a hydrogen-compatible microchip and a lithium-compatible "
        ...     "microchip")
        [Microchip(type='hydrogen'), Microchip(type='lithium')]
        >>> Building.contents_from_content_text(
        ...     "a thulium generator, a thulium-compatible microchip, a "
        ...     "plutonium generator, and a strontium generator")
        [Generator(type='thulium'), Microchip(type='thulium'),
            Generator(type='plutonium'), Generator(type='strontium')]
        """
        content_texts = cls.re_contents_separator.split(contents_text)
        object_class = cls.get_object_class()
        return list(map(object_class.parse, content_texts))

    def __lt__(self: Self['Building'], other: Self['Building']) -> bool:
        return self.get_hash() < other.get_hash()

    def __hash__(self):
        return hash(self.get_hash())

    def get_smallest_solution_length(
            self, solver_class: Type[BuildingSolver] = BuildingSolver,
            debug: bool = False) -> int:
        return solver_class().get_smallest_solution_length(self, debug=debug)

    def is_complete(self) -> bool:
        """
        >>> Building({}).is_complete()
        True
        >>> Building({1: []}).is_complete()
        True
        >>> Building({1: [], 2: [], 3: []}).is_complete()
        True
        >>> Building({1: [], 2: [], 3: [Generator('a')]}).is_complete()
        True
        >>> Building({
        ...     1: [], 2: [Microchip('a')], 3: [Generator('a')]}).is_complete()
        False
        """
        if not self.floors:
            return True
        top_floor = max(self.floors)
        return not any(
            contents
            for floor, contents in self.floors.items()
            if floor != top_floor
        )

    def is_valid(self) -> bool:
        """
        >>> Building({}).is_valid()
        True
        >>> Building({1: [], 2: []}).is_valid()
        True
        >>> Building({1: [Microchip('a')], 2: [Generator('a')]}).is_valid()
        True
        >>> Building({1: [Microchip('a')], 2: [Generator('b')]}).is_valid()
        True
        >>> Building({
        ...     1: [Microchip('a')], 2: [Microchip('c'), Generator('b')]})\\
        ...     .is_valid()
        False
        >>> Building({
        ...     1: [Microchip('a')], 2: [Microchip('c'), Generator('c')]})\\
        ...     .is_valid()
        True
        """
        return self.are_floors_valid(self.floors)

    def are_floors_valid(self, floors: Dict[int, List[ObjectT]]) -> bool:
        """
        >>> Building().are_floors_valid({})
        True
        >>> Building().are_floors_valid({1: [], 2: []})
        True
        >>> Building().are_floors_valid({
        ...     1: [Microchip('a')], 2: [Generator('a')]})
        True
        >>> Building().are_floors_valid({
        ...     1: [Microchip('a')], 2: [Generator('b')]})
        True
        >>> Building().are_floors_valid({
        ...     1: [Microchip('a')], 2: [Microchip('c'), Generator('b')]})
        False
        >>> Building().are_floors_valid({
        ...     1: [Microchip('a')], 2: [Microchip('c'), Generator('c')]})
        True
        """
        return all(
            self.is_floor_valid(contents)
            for contents in floors.values()
        )

    def is_floor_valid(self, contents: List[ObjectT]) -> bool:
        """
        >>> Building().is_floor_valid([])
        True
        >>> Building().is_floor_valid([Microchip('a')])
        True
        >>> Building().is_floor_valid([
        ...     Microchip('a'), Microchip('b'), Microchip('c')])
        True
        >>> Building().is_floor_valid([
        ...     Microchip('a'), Microchip('b'), Microchip('c'),
        ...     Generator('d')])
        False
        >>> Building().is_floor_valid([
        ...     Microchip('a'), Microchip('b'), Microchip('c'),
        ...     Generator('a'), Generator('b'), Generator('d')])
        False
        >>> Building().is_floor_valid([
        ...     Microchip('a'), Microchip('b'), Microchip('c'),
        ...     Generator('a'), Generator('b'), Generator('c'), Generator('d')])
        True
        """
        return (
                not self.floor_contains_generators(contents)
                or self.are_all_microchips_with_their_generators(contents)
        )

    def floor_contains_generators(self, contents: List[ObjectT]) -> bool:
        """
        >>> Building().floor_contains_generators([])
        False
        >>> Building().floor_contains_generators([Microchip('a')])
        False
        >>> Building().floor_contains_generators([Generator('a')])
        True
        >>> Building().floor_contains_generators([
        ...     Generator('a'), Microchip('a'), Microchip('b')])
        True
        """
        return any(
            isinstance(_object, Generator)
            for _object in contents
        )

    def are_all_microchips_with_their_generators(
            self, contents: List[ObjectT]) -> bool:
        """
        >>> Building().are_all_microchips_with_their_generators([])
        True
        >>> Building().are_all_microchips_with_their_generators([
        ...     Generator('a')])
        True
        >>> Building().are_all_microchips_with_their_generators([
        ...     Generator('a'), Microchip('a')])
        True
        >>> Building().are_all_microchips_with_their_generators([
        ...     Generator('b'), Microchip('a')])
        False
        >>> Building().are_all_microchips_with_their_generators([
        ...     Generator('b'), Microchip('a'), Generator('a')])
        True
        """
        return all(
            microchip.get_generator() in contents
            for microchip in contents
            if isinstance(microchip, Microchip)
        )

    def get_hash(self) -> str:
        """
        >>> Building().get_hash()
        'e:1|'
        >>> Building({1:[]}).get_hash()
        'e:1|1:'
        >>> Building({
        ...     1:[Microchip('a')], 2: [], 3: [Generator('a'),
        ...         Microchip('bab'), Microchip('bcb')]}).get_hash()
        'e:1|1:AM|2:|3:AG,BabM,BcbM'
        >>> Building({
        ...     1:[Microchip('a')], 2: [], 3: [Generator('a'),
        ...         Microchip('bcb'), Microchip('bab')]}).get_hash()
        'e:1|1:AM|2:|3:AG,BabM,BcbM'
        """
        return "e:{}|{}".format(
            self.position,
            "|".join(
                "{}:{}".format(
                    floor,
                    ",".join(sorted(_object.show(None) for _object in contents))
                )
                for floor, contents in sorted(self.floors.items())
            )
        )

    def show(self, length: Optional[int] = None) -> str:
        """
        >>> building = Building.from_building_text(
        ...     "The first floor contains a hydrogen-compatible microchip and "
        ...     "a lithium-compatible microchip.\\n"
        ...     "The second floor contains a hydrogen generator.\\n"
        ...     "The third floor contains a lithium generator.\\n"
        ...     "The fourth floor contains nothing relevant.\\n"
        ... )
        >>> print(building.show())
        F4 .  .  .  .  .
        F3 .  .  .  LG .
        F2 .  HG .  .  .
        F1 E  .  HM .  LM
        >>> print(building.show(2))
        F4 .   .   .   .   .
        F3 .   .   .   LiG .
        F2 .   HyG .   .   .
        F1 E   .   HyM .   LiM
        """
        objects = sum(self.floors.values(), [])
        if length is None:
            length = self.get_minimum_object_show_length(objects)
        objects_in_order = sorted(
            objects, key=lambda _object: _object.show(length=length))
        line_template = f"F{{}} {{: <{length + 1}}} {{}}"
        dot_template = f"{{: <{length + 1}}}"
        dot = dot_template.format(".")
        return "\n".join(
            line_template.format(
                floor,
                "E" if floor == self.position else ".",
                " ".join(
                    _object.show(length=length)
                    if _object in contents else
                    dot
                    for _object in objects_in_order
                ),
            ).rstrip()
            for floor, contents in sorted(self.floors.items(), reverse=True)
        )

    def get_minimum_object_show_length(self, objects: List[ObjectT]) -> int:
        """
        >>> Building().get_minimum_object_show_length([])
        1
        >>> Building().get_minimum_object_show_length([
        ...     Generator(type='thulium'), Microchip(type='thulium'),
        ...     Generator(type='plutonium'), Microchip(type='plutonium')])
        1
        >>> Building().get_minimum_object_show_length([
        ...     Generator(type='thulium'), Microchip(type='thulium'),
        ...     Generator(type='pyrite'), Microchip(type='pyrite'),
        ...     Generator(type='plutonium'), Microchip(type='plutonium')])
        2
        >>> Building().get_minimum_object_show_length([
        ...     Generator(type='thulium'), Microchip(type='thulium'),
        ...     Generator(type='thorium'), Microchip(type='thorium'),
        ...     Generator(type='plutonium'), Microchip(type='plutonium')])
        3
        >>> Building().get_minimum_object_show_length([
        ...     Generator(type='thulium'), Microchip(type='thulium'),
        ...     Generator(type='thulium'), Microchip(type='thulium')])
        7
        """
        previous_names = None
        for length in count(1):
            names = {
                _object.show(length=length)
                for _object in objects
            }
            if len(names) == len(objects):
                return length
            if names == previous_names:
                return length - 1
            previous_names = names

        return 1


@total_ordering
class Object(PolymorphicParser, ABC, root=True):
    """
    >>> Object.parse('a thulium generator')
    Generator(type='thulium')
    >>> Object.parse('a thulium-compatible microchip')
    Microchip(type='thulium')
    """

    def show(self, length: int = 1) -> str:
        raise NotImplementedError()

    def __lt__(self, other: 'Object') -> bool:
        if isinstance(other, type(self)):
            return self.same_type_lt(other)
        if not isinstance(other, Object):
            raise TypeError(
                f"'<' not supported between instances of "
                f"'{type(self).__name__}' and '{type(other).__name__}'")
        return type(self).__name__ < type(other).__name__

    def same_type_lt(self, other: 'Object') -> bool:
        raise NotImplementedError()


@Object.register
@dataclass(eq=True, frozen=True)
class Generator(Object):
    """
    >>> Generator('a') == Generator('a')
    True
    >>> Generator('a') is Generator('a')
    False
    >>> Generator('a') == Microchip('a')
    False
    """
    name = 'generator'
    type: str

    re_generator = re.compile(r"^a (\w+) generator$")

    @classmethod
    def try_parse(cls: Cls['Generator'], text: str
                  ) -> Optional[Self['Generator']]:
        """
        >>> Generator.try_parse('a thulium generator')
        Generator(type='thulium')
        >>> Generator.try_parse('a thulium-compatible microchip')
        """
        match = cls.re_generator.match(text)
        if not match:
            return None

        _type, = match.groups()

        return cls(_type)

    def same_type_lt(self, other: 'Generator') -> bool:
        return self.type < other.type

    def show(self, length: int = 1) -> str:
        if length is None:
            abbreviation = self.type
        else:
            abbreviation = self.type[:length]
        return f"{abbreviation.title()}G"


@Object.register
@dataclass(eq=True, frozen=True, order=True)
class Microchip(Object):
    """
    >>> Microchip('a') == Microchip('a')
    True
    >>> Microchip('a') is Microchip('a')
    False
    >>> Microchip('a') == Generator('a')
    False
    """
    name = 'microchip'
    type: str

    re_microchip = re.compile(r"^a (\w+)-compatible microchip$")

    @classmethod
    def try_parse(cls: Cls['Microchip'], text: str
                  ) -> Optional[Self['Microchip']]:
        """
        >>> Microchip.try_parse('a thulium generator')
        >>> Microchip.try_parse('a thulium-compatible microchip')
        Microchip(type='thulium')
        """
        match = cls.re_microchip.match(text)
        if not match:
            return None

        _type, = match.groups()

        return cls(_type)

    def same_type_lt(self, other: 'Generator') -> bool:
        return self.type < other.type

    def show(self, length: int = 1) -> str:
        if length is None:
            abbreviation = self.type
        else:
            abbreviation = self.type[:length]
        return f"{abbreviation.title()}M"

    def get_generator(self) -> 'Object':
        """
        >>> Microchip('a').get_generator()
        Generator(type='a')
        >>> Microchip('a').get_generator() in [Generator('a')]
        True
        """
        return Generator(self.type)


Challenge.main()
challenge = Challenge()
