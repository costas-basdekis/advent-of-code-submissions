#!/usr/bin/env python3
import re
from abc import ABC
from dataclasses import dataclass, field
from enum import auto
from functools import reduce
from typing import Optional, Generic, List, Type, Dict, Set, Tuple

from aox.utils import StringEnum
from utils import BaseChallenge, Cls, PolymorphicParser, Self, TV, \
    get_type_argument_class, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        98
        """
        bot_set = InstructionSet.get_bot_set_from_instructions_text(_input)
        bot_set.resolve()
        bot = bot_set.find_bot(low_value=17, high_value=61)
        return bot.id


BotT = TV['Bot']


@dataclass
class BotSet(Generic[BotT]):
    bots: Dict[int, 'Bot'] = field(default_factory=dict)
    outputs: Dict[int, int] = field(default_factory=dict)

    def __getitem__(self, item: int) -> 'Bot':
        return self.bots.setdefault(item, Bot(item))

    def set_output(self: Self['BotSet'], _id: int,
                   value: int) -> Self['BotSet']:
        """
        >>> BotSet().set_output(1, 5)
        BotSet(bots={}, outputs={1: 5})
        >>> BotSet().set_output(1, 5).set_output(1, 5)
        Traceback (most recent call last):
        ...
        Exception: Tried to set output ...
        >>> BotSet(outputs={1: 5}).set_output(1, 5)
        Traceback (most recent call last):
        ...
        Exception: Tried to set output ...
        """
        if self.outputs.get(_id, None) is not None:
            raise Exception(
                f"Tried to set output {_id} to {value} but it already had a "
                f"value")
        self.outputs[_id] = value

        return self

    def find_bot(self, **kwargs) -> BotT:
        """
        >>> BotSet().find_bot(low_value=1)
        >>> BotSet(bots={1: Bot(1)}).find_bot(low_value=1)
        >>> BotSet(bots={1: Bot(1)}).find_bot(id=1)
        Bot(id=1, ...)
        """
        return next((
            bot
            for bot in self.bots.values()
            if all(
                getattr(bot, key) == value
                for key, value in kwargs.items()
            )
        ), None)

    def resolve(self: Self['BotSet']) -> Self['BotSet']:
        """
        >>> InstructionSet.get_bot_set_from_instructions_text(
        ...     "value 5 goes to bot 2\\n"
        ...     "bot 2 gives low to bot 1 and high to bot 0\\n"
        ...     "value 3 goes to bot 1\\n"
        ...     "bot 1 gives low to output 1 and high to bot 0\\n"
        ...     "bot 0 gives low to output 2 and high to output 0\\n"
        ...     "value 2 goes to bot 2\\n"
        ... ).resolve()
        BotSet(bots={2: Bot(id=2, low_value=2, high_value=5, ...),
            1: Bot(id=1, low_value=2, high_value=3, ...),
            0: Bot(id=0, low_value=3, high_value=5, ...)},
            outputs={1: 2, 2: 3, 0: 5})
        """
        self.resolve_between_bots()
        self.resolve_outputs()

        return self

    def resolve_outputs(self: Self['BotSet']) -> Self['BotSet']:
        """
        >>> BotSet().resolve_outputs()
        BotSet(bots={}, outputs={})
        >>> BotSet({1: Bot(1)}).resolve_outputs()
        BotSet(bots={...}, outputs={})
        >>> BotSet({
        ...     1: Bot(1, low_destination_type=Bot.DestinationType.Output,
        ...        low_destination=2),
        ... }).resolve_outputs()
        Traceback (most recent call last):
        ...
        Exception: ... it doesn't have one yet
        >>> BotSet({
        ...     1: Bot(1, 4, low_destination_type=Bot.DestinationType.Output,
        ...        low_destination=2),
        ... }).resolve_outputs()
        BotSet(bots={...}, outputs={2: 4})
        >>> BotSet({
        ...     1: Bot(1, 4, low_destination_type=Bot.DestinationType.Output,
        ...        low_destination=2),
        ...     2: Bot(2, 5, low_destination_type=Bot.DestinationType.Output,
        ...        low_destination=3),
        ... }).resolve_outputs()
        BotSet(bots={...}, outputs={2: 4, 3: 5})
        """
        for bot in self.bots.values():
            bot.set_outputs(self)

        return self

    def resolve_between_bots(self: Self['BotSet']) -> Self['BotSet']:
        """
        >>> BotSet().resolve_between_bots()
        BotSet(bots={}, outputs={})
        >>> BotSet({1: Bot(1)}).resolve_between_bots()
        Traceback (most recent call last):
        ...
        Exception: Could not resolve all bots: 1
        >>> BotSet({1: Bot(1), 2: Bot(2)}).resolve_between_bots()
        Traceback (most recent call last):
        ...
        Exception: Could not resolve all bots: 1, 2
        >>> BotSet({1: Bot(1, 4, 5), 2: Bot(2)}).resolve_between_bots()
        Traceback (most recent call last):
        ...
        Exception: Could not resolve all bots: 2
        >>> BotSet({
        ...     1: Bot(1, 4, 5, 2, 2, Bot.DestinationType.Bot,
        ...            Bot.DestinationType.Output),
        ...     2: Bot(2),
        ... }).resolve_between_bots()
        Traceback (most recent call last):
        ...
        Exception: Could not resolve all bots: 2
        >>> BotSet({
        ...     1: Bot(1, 4, 5, 2, 2, Bot.DestinationType.Bot,
        ...            Bot.DestinationType.Bot),
        ...     2: Bot(2),
        ... }).resolve_between_bots()
        BotSet(bots={1: Bot(id=1, low_value=4, high_value=5, ...),
            2: Bot(id=2, low_value=4, high_value=5, ...)}, outputs={})
        >>> BotSet({
        ...     1: Bot(1, 4, 5, 2, 2, Bot.DestinationType.Bot,
        ...            Bot.DestinationType.Bot),
        ...     2: Bot(2, None, None, 3, 3, Bot.DestinationType.Bot,
        ...            Bot.DestinationType.Bot),
        ...     3: Bot(3),
        ... }).resolve_between_bots()
        BotSet(bots={1: Bot(id=1, low_value=4, high_value=5, ...),
            2: Bot(id=2, low_value=4, high_value=5, ...),
            3: Bot(id=3, low_value=4, high_value=5, ...)}, outputs={})
        """
        if self.are_bots_resolved():
            return self
        dependency_map = self.get_dependency_map()
        dependency_order = self.get_dependency_order(dependency_map)
        resolution_order = self.get_resolution_order(
            dependency_map, dependency_order)
        for source_id, destination_id in resolution_order:
            source = self[source_id]
            destination = self[destination_id]
            source.give_to(destination)
        if not self.are_bots_resolved():
            raise Exception(
                f"Could not resolve all bots: "
                f"{', '.join(map(str, sorted(self.get_unresolved_bot_ids())))}")
        return self

    def get_resolution_order(self, dependency_map: Dict[int, Set[int]],
                             dependency_order: List[int],
                             ) -> List[Tuple[int, int]]:
        """
        >>> BotSet().get_resolution_order({}, [])
        []
        >>> BotSet().get_resolution_order({1: {2}}, [1])
        [(2, 1)]
        >>> BotSet().get_resolution_order(
        ...     {1: {2}, 2: {3}, 3: {4, 5}}, [3, 2, 1])
        [(4, 3), (5, 3), (3, 2), (2, 1)]
        >>> BotSet().get_resolution_order(
        ...     {1: {3}, 2: {3}, 3: {4, 5}}, [3, 1, 2])
        [(4, 3), (5, 3), (3, 1), (3, 2)]
        >>> BotSet().get_resolution_order(
        ...     {2: {3}, 1: {3}, 3: {4, 5}}, [3, 1, 2])
        [(4, 3), (5, 3), (3, 1), (3, 2)]
        >>> BotSet().get_resolution_order({2: {1}}, [2])
        [(1, 2)]
        """
        return [
            (dependency_id, bot_id)
            for bot_id in dependency_order
            for dependency_id in sorted(dependency_map[bot_id])
        ]

    def get_dependency_order(self, dependency_map: Dict[int, Set[int]]
                             ) -> List[int]:
        """
        >>> BotSet().get_dependency_order({})
        []
        >>> BotSet().get_dependency_order({1: {2}})
        [1]
        >>> BotSet().get_dependency_order({1: {2}, 2: {3}, 3: {4, 5}})
        [3, 2, 1]
        >>> BotSet().get_dependency_order({1: {3}, 2: {3}, 3: {4, 5}})
        [3, 1, 2]
        >>> BotSet().get_dependency_order({2: {3}, 1: {3}, 3: {4, 5}})
        [3, 1, 2]
        >>> BotSet().get_dependency_order({2: {1}})
        [2]
        """
        if not dependency_map:
            return []
        dependencies = reduce(set.__or__, dependency_map.values())
        remaining = set(dependency_map)
        resolved = dependencies - remaining
        dependency_order = []
        while remaining:
            newly_resolved = {
                bot_id
                for bot_id, bot_dependencies in dependency_map.items()
                if not bot_dependencies - resolved
            } - resolved
            if not newly_resolved:
                raise Exception(
                    f"Could not continue resolution after {dependency_order}: "
                    f"{sorted(remaining)} remaining")
            dependency_order += sorted(newly_resolved)
            remaining -= newly_resolved
            resolved |= newly_resolved

        return dependency_order

    def get_dependency_map(self) -> Dict[int, Set[int]]:
        """
        >>> BotSet().get_dependency_map()
        {}
        >>> BotSet({1: Bot(1, 4, 5)}).get_dependency_map()
        {}
        >>> BotSet({1: Bot(1, 4)}).get_dependency_map()
        {}
        >>> BotSet({
        ...     1: Bot(1, 4),
        ...     2: Bot(2, low_destination=1,
        ...            low_destination_type=Bot.DestinationType.Bot),
        ... }).get_dependency_map()
        {1: {2}}
        >>> BotSet({
        ...     1: Bot(1, 4, 5, 2, 2, Bot.DestinationType.Bot,
        ...            Bot.DestinationType.Bot),
        ...     2: Bot(2),
        ... }).get_dependency_map()
        {2: {1}}
        """
        unresolved_bot_ids = self.get_unresolved_bot_ids()
        if not unresolved_bot_ids:
            return {}
        return helper.group_by((
            (destination, bot.id)
            for bot in self.bots.values()
            for destination_type, destination in (
                (bot.low_destination_type, bot.low_destination),
                (bot.high_destination_type, bot.high_destination),
            )
            if destination_type == Bot.DestinationType.Bot
            and destination in unresolved_bot_ids
        ), key=lambda pair: pair[0], value="auto", values_container=set)

    def get_unresolved_bot_ids(self):
        """
        >>> sorted(BotSet().get_unresolved_bot_ids())
        []
        >>> sorted(BotSet({1: Bot(1)}).get_unresolved_bot_ids())
        [1]
        >>> sorted(BotSet({1: Bot(1, 6, 7)}).get_unresolved_bot_ids())
        []
        >>> sorted(BotSet({
        ...     1: Bot(1), 2: Bot(2, 4, 5)}).get_unresolved_bot_ids())
        [1]
        >>> sorted(BotSet({
        ...     1: Bot(1, 6, 7), 2: Bot(2, 4, 5)}).get_unresolved_bot_ids())
        []
        """
        return {
            bot.id
            for bot in self.bots.values()
            if not bot.is_resolved()
        }

    def are_bots_resolved(self) -> bool:
        """
        >>> BotSet().are_bots_resolved()
        True
        >>> BotSet({1: Bot(1)}).are_bots_resolved()
        False
        >>> BotSet({1: Bot(1, 6, 7)}).are_bots_resolved()
        True
        >>> BotSet({1: Bot(1), 2: Bot(2, 4, 5)}).are_bots_resolved()
        False
        >>> BotSet({1: Bot(1, 6, 7), 2: Bot(2, 4, 5)}).are_bots_resolved()
        True
        """
        return all(
            bot.is_resolved()
            for bot in self.bots.values()
        )


@dataclass
class Bot:
    class DestinationType(StringEnum):
        Bot = auto()
        Output = auto()

        def __repr__(self):
            return f"{type(self).__name__}.{self.name}"

    id: int
    low_value: Optional[int] = None
    high_value: Optional[int] = None
    low_destination: Optional[int] = None
    high_destination: Optional[int] = None
    low_destination_type: Optional[DestinationType] = None
    high_destination_type: Optional[DestinationType] = None

    def take(self: Self['Bot'], value: int) -> Self['Bot']:
        """
        >>> Bot(1).take(1)
        Bot(id=1, low_value=1, high_value=None, low_destination=None,
            high_destination=None, low_destination_type=None,
            high_destination_type=None)
        >>> Bot(1).take(1).take(2)
        Bot(id=1, low_value=1, high_value=2, low_destination=None,
            high_destination=None, low_destination_type=None,
            high_destination_type=None)
        >>> Bot(1).take(1).take(0)
        Bot(id=1, low_value=0, high_value=1, low_destination=None,
            high_destination=None, low_destination_type=None,
            high_destination_type=None)
        >>> Bot(1).take(1).take(2).take(3)
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        if self.low_value is None:
            self.low_value = value
        elif self.high_value is None:
            self.high_value = value
            self.low_value, self.high_value = \
                sorted([self.low_value, self.high_value])
        else:
            raise Exception(
                f"Tried to give new value {value} to bot {self}, but it "
                f"already had 2 values")

        return self

    def set_low_destination(self: Self['Bot'], destination: int,
                            _type: DestinationType) -> Self['Bot']:
        """
        >>> Bot(1).set_low_destination(2, Bot.DestinationType.Bot)
        Bot(id=1, low_value=None, high_value=None, low_destination=2,
            high_destination=None, low_destination_type=DestinationType.Bot,
            high_destination_type=None)
        >>> Bot(1, high_destination=3,
        ...     high_destination_type=Bot.DestinationType.Bot)\\
        ...         .set_low_destination(2, Bot.DestinationType.Bot)
        Bot(id=1, low_value=None, high_value=None, low_destination=2,
            high_destination=3, low_destination_type=DestinationType.Bot,
            high_destination_type=DestinationType.Bot)
        >>> Bot(1).set_low_destination(2, Bot.DestinationType.Bot)\\
        ...     .set_low_destination(2, Bot.DestinationType.Bot)
        Traceback (most recent call last):
        ...
        Exception: ...
        >>> Bot(1).set_low_destination(2, Bot.DestinationType.Bot)\\
        ...     .set_low_destination(4, Bot.DestinationType.Output)
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        if self.low_destination is not None \
                or self.low_destination_type is not None:
            raise Exception(
                f"Tried to set new low destination {destination}/{_type} for "
                f"bot {self}, but it already had one")
        self.low_destination = destination
        self.low_destination_type = _type

        return self

    def set_high_destination(self: Self['Bot'], destination: int,
                             _type: DestinationType) -> Self['Bot']:
        """
        >>> Bot(1).set_high_destination(3, Bot.DestinationType.Bot)
        Bot(id=1, low_value=None, high_value=None, low_destination=None,
            high_destination=3, low_destination_type=None,
            high_destination_type=DestinationType.Bot)
        >>> Bot(1, low_destination=2,
        ...     low_destination_type=Bot.DestinationType.Bot)\\
        ...         .set_high_destination(3, Bot.DestinationType.Bot)
        Bot(id=1, low_value=None, high_value=None, low_destination=2,
            high_destination=3, low_destination_type=DestinationType.Bot,
            high_destination_type=DestinationType.Bot)
        >>> Bot(1).set_high_destination(2, Bot.DestinationType.Bot)\\
        ...     .set_high_destination(2, Bot.DestinationType.Bot)
        Traceback (most recent call last):
        ...
        Exception: ...
        >>> Bot(1).set_high_destination(2, Bot.DestinationType.Bot)\\
        ...     .set_high_destination(4, Bot.DestinationType.Output)
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        if self.high_destination is not None \
                or self.high_destination_type is not None:
            raise Exception(
                f"Tried to set new high destination {destination}/{_type} for "
                f"bot {self}, but it already had one")
        self.high_destination = destination
        self.high_destination_type = _type

        return self

    def give_to(self: Self['Bot'], bot: Self['Bot']) -> Self['Bot']:
        """
        >>> Bot(1).give_to(Bot(2))
        Traceback (most recent call last):
        ...
        Exception: ... does not have anything to give to ...
        >>> Bot(1, low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2).give_to(Bot(2))
        Traceback (most recent call last):
        ...
        Exception: ... does not have anything to give to ...
        >>> Bot(1, low_destination_type=Bot.DestinationType.Bot,
        ...     low_destination=2).give_to(Bot(2))
        Traceback (most recent call last):
        ...
        Exception: ... it doesn't have one yet
        >>> Bot(1, low_value=5, low_destination_type=Bot.DestinationType.Bot,
        ...     low_destination=2).give_to(Bot(2))
        Bot(id=2, low_value=5, high_value=None, ...)
        >>> Bot(1, low_value=5, low_destination_type=Bot.DestinationType.Bot,
        ...     low_destination=2).give_to(Bot(2, 6, 7))
        Traceback (most recent call last):
        ...
        Exception: ... already had 2 values
        >>> Bot(1, low_value=5, high_value=6,
        ...     low_destination_type=Bot.DestinationType.Bot,
        ...     low_destination=2,
        ...     high_destination_type=Bot.DestinationType.Bot,
        ...     high_destination=2).give_to(Bot(2))
        Bot(id=2, low_value=5, high_value=6, ...)
        >>> Bot(1, low_value=5, high_value=6,
        ...     low_destination_type=Bot.DestinationType.Bot,
        ...     low_destination=2,
        ...     high_destination_type=Bot.DestinationType.Bot,
        ...     high_destination=2).give_to(Bot(2, 7))
        Traceback (most recent call last):
        ...
        Exception: ... already had 2 values
        """
        gave = False
        if self.low_destination_type == self.DestinationType.Bot \
                and self.low_destination == bot.id:
            if self.low_value is None:
                raise Exception(
                    f"Bot {self} cannot give low value to {bot}: it doesn't "
                    f"have one yet")
            bot.take(self.low_value)
            gave = True
        if self.high_destination_type == self.DestinationType.Bot \
                and self.high_destination == bot.id:
            if self.high_value is None:
                raise Exception(
                    f"Bot {self} cannot give high value to {bot}: it doesn't "
                    f"have one yet")
            bot.take(self.high_value)
            gave = True
        if not gave:
            raise Exception(
                f"Bot {self} does not have anything to give to {bot}")

        return bot

    def set_outputs(self, bot_set: BotSet) -> BotSet:
        """
        >>> Bot(1).set_outputs(BotSet())
        BotSet(bots={}, outputs={})
        >>> Bot(1, low_destination_type=Bot.DestinationType.Bot,
        ...     low_destination=2).set_outputs(BotSet())
        BotSet(bots={}, outputs={})
        >>> Bot(1, low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2).set_outputs(BotSet())
        Traceback (most recent call last):
        ...
        Exception: ... it doesn't have one yet
        >>> Bot(1, low_value=5, low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2).set_outputs(BotSet())
        BotSet(bots={}, outputs={2: 5})
        >>> Bot(1, low_value=5, low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2).set_outputs(BotSet(outputs={2: 5}))
        Traceback (most recent call last):
        ...
        Exception: Tried to set output ...
        >>> Bot(1, low_value=5, high_value=6,
        ...     low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2,
        ...     high_destination_type=Bot.DestinationType.Output,
        ...     high_destination=3).set_outputs(BotSet())
        BotSet(bots={}, outputs={2: 5, 3: 6})
        >>> Bot(1, low_value=5, high_value=6,
        ...     low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2,
        ...     high_destination_type=Bot.DestinationType.Bot,
        ...     high_destination=3).set_outputs(BotSet())
        BotSet(bots={}, outputs={2: 5})
        >>> Bot(1, low_value=5, high_value=6,
        ...     low_destination_type=Bot.DestinationType.Output,
        ...     low_destination=2,
        ...     high_destination_type=Bot.DestinationType.Output,
        ...     high_destination=2).set_outputs(BotSet())
        Traceback (most recent call last):
        ...
        Exception: Tried to set output ...
        """
        if self.low_destination_type == self.DestinationType.Output:
            if self.low_value is None:
                raise Exception(
                    f"Bot {self} cannot give set low value as output: it "
                    f"doesn't have one yet")
            bot_set.set_output(self.low_destination, self.low_value)
        if self.high_destination_type == self.DestinationType.Output:
            if self.high_value is None:
                raise Exception(
                    f"Bot {self} cannot give set high value as output: it "
                    f"doesn't have one yet")
            bot_set.set_output(self.high_destination, self.high_value)

        return bot_set

    def is_resolved(self) -> bool:
        """
        >>> Bot(1).is_resolved()
        False
        >>> Bot(1, 2).is_resolved()
        False
        >>> Bot(1, None, 3).is_resolved()
        False
        >>> Bot(1, 2, 3).is_resolved()
        True
        """
        return (
            self.low_value is not None
            and self.high_value is not None
        )


InstructionT = TV['Instruction']
BotSetT = TV[BotSet]


@dataclass
class InstructionSet(Generic[InstructionT, BotSetT]):
    instructions: List[InstructionT]

    @classmethod
    def get_instruction_class(cls) -> Type[InstructionT]:
        return get_type_argument_class(cls, InstructionT)

    @classmethod
    def get_bot_set_class(cls) -> Type[BotSetT]:
        return get_type_argument_class(cls, BotSetT)

    @classmethod
    def get_bot_set_from_instructions_text(
            cls, instructions_text: str) -> BotSetT:
        """
        >>> InstructionSet.get_bot_set_from_instructions_text(
        ...     "value 5 goes to bot 2\\n"
        ...     "bot 2 gives low to bot 1 and high to bot 0\\n"
        ...     "value 3 goes to bot 1\\n"
        ...     "bot 1 gives low to output 1 and high to bot 0\\n"
        ...     "bot 0 gives low to output 2 and high to output 0\\n"
        ...     "value 2 goes to bot 2\\n"
        ... )
        BotSet(bots={2:
            Bot(id=2, low_value=2, high_value=5, low_destination=1,
                high_destination=0, low_destination_type=DestinationType.Bot,
                high_destination_type=DestinationType.Bot),
            1: Bot(id=1, low_value=3, high_value=None, low_destination=1,
                high_destination=0, low_destination_type=DestinationType.Output,
                high_destination_type=DestinationType.Bot),
            0: Bot(id=0, low_value=None, high_value=None, low_destination=2,
                high_destination=0, low_destination_type=DestinationType.Output,
                high_destination_type=DestinationType.Output)},
            outputs={})
        """
        instruction_set = cls.from_instructions_text(instructions_text)
        return instruction_set.apply(cls.get_bot_set_class()())

    @classmethod
    def from_instructions_text(
            cls: Cls['InstructionSet'], instructions_text: str
    ) -> Self['InstructionSet']:
        """
        >>> InstructionSet.from_instructions_text(
        ...     "value 5 goes to bot 2\\n"
        ...     "bot 2 gives low to bot 1 and high to bot 0\\n"
        ... )
        InstructionSet(instructions=[InitialInstruction(value=5, destination=2),
            GiveInstruction(source=2, low_destination=1, high_destination=0,
                low_destination_type=DestinationType.Bot,
                high_destination_type=DestinationType.Bot)])
        """
        instruction_class = cls.get_instruction_class()
        return cls(list(map(
            instruction_class.parse, instructions_text.splitlines())))

    def apply(self, bot_set: BotSetT) -> BotSetT:
        for instruction in self.instructions:
            instruction.apply(bot_set)

        return bot_set


class Instruction(PolymorphicParser, ABC, root=True):
    """
    >>> Instruction.parse('value 5 goes to bot 2')
    InitialInstruction(value=5, destination=2)
    >>> Instruction.parse(
    ...     'bot 2 gives low to bot 1 and high to bot 0')
    GiveInstruction(source=2, low_destination=1, high_destination=0,
        low_destination_type=DestinationType.Bot,
        high_destination_type=DestinationType.Bot)
    >>> Instruction.parse(
    ...     'bot 2 gives low to bot 1 and high to output 0')
    GiveInstruction(source=2, low_destination=1, high_destination=0,
        low_destination_type=DestinationType.Bot,
        high_destination_type=DestinationType.Output)
    >>> Instruction.parse(
    ...     'bot 2 gives low to output 1 and high to bot 0')
    GiveInstruction(source=2, low_destination=1, high_destination=0,
        low_destination_type=DestinationType.Output,
        high_destination_type=DestinationType.Bot)
    >>> Instruction.parse(
    ...     'bot 2 gives low to output 1 and high to output 0')
    GiveInstruction(source=2, low_destination=1, high_destination=0,
        low_destination_type=DestinationType.Output,
        high_destination_type=DestinationType.Output)
    """

    def apply(self, bot_set: BotSet) -> BotSet:
        raise NotImplementedError()


@Instruction.register
@dataclass
class InitialInstruction(Instruction):
    name = 'initial'

    value: int
    destination: int

    re_initial_instruction = re.compile(r"^value (\d+) goes to bot (\d+)$")

    @classmethod
    def try_parse(cls: Cls['InitialInstruction'], text: str
                  ) -> Optional[Self['InitialInstruction']]:
        """
        >>> InitialInstruction.try_parse('value 5 goes to bot 2')
        InitialInstruction(value=5, destination=2)
        >>> InitialInstruction.try_parse(
        ...     'bot 2 gives low to bot 1 and high to bot 0')
        >>> InitialInstruction.try_parse(
        ...     'bot 2 gives low to bot 1 and high to output 0')
        >>> InitialInstruction.try_parse(
        ...     'bot 2 gives low to output 1 and high to bot 0')
        >>> InitialInstruction.try_parse(
        ...     'bot 2 gives low to output 1 and high to output 0')
        """
        match = cls.re_initial_instruction.match(text)
        if not match:
            return None

        value_str, destination_str = match.groups()
        return cls(int(value_str), int(destination_str))

    def apply(self, bot_set: BotSet) -> BotSet:
        """
        >>> _bot_set = BotSet()
        >>> InitialInstruction(5, 1).apply(_bot_set)
        BotSet(bots={1: Bot(id=1, low_value=5, high_value=None,
            low_destination=None, high_destination=None,
            low_destination_type=None, high_destination_type=None)},
            outputs={})
        >>> InitialInstruction(6, 1).apply(_bot_set)
        BotSet(bots={1: Bot(id=1, low_value=5, high_value=6,
            low_destination=None, high_destination=None,
            low_destination_type=None, high_destination_type=None)}, outputs={})
        >>> InitialInstruction(5, 2).apply(_bot_set)
        BotSet(bots={1: Bot(id=1, low_value=5, high_value=6,
            low_destination=None, high_destination=None,
            low_destination_type=None, high_destination_type=None),
            2: Bot(id=2, low_value=5, high_value=None,
                low_destination=None, high_destination=None,
            low_destination_type=None, high_destination_type=None)}, outputs={})
        >>> InitialInstruction(4, 2).apply(_bot_set)
        BotSet(bots={1: Bot(id=1, low_value=5, high_value=6,
            low_destination=None, high_destination=None,
            low_destination_type=None, high_destination_type=None),
            2: Bot(id=2, low_value=4, high_value=5,
                low_destination=None, high_destination=None,
                low_destination_type=None, high_destination_type=None)},
            outputs={})
        >>> InitialInstruction(4, 1).apply(_bot_set)
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        bot_set[self.destination].take(self.value)

        return bot_set


@Instruction.register
@dataclass
class GiveInstruction(Instruction):
    name = 'give'

    source: int
    low_destination: int
    high_destination: int
    low_destination_type: Bot.DestinationType
    high_destination_type: Bot.DestinationType

    re_give_instruction = re.compile(
        r"^bot (\d+) gives low to (bot|output) (\d+) "
        r"and high to (bot|output) (\d+)$")

    @classmethod
    def try_parse(cls: Cls['GiveInstruction'], text: str
                  ) -> Optional[Self['GiveInstruction']]:
        """
        >>> GiveInstruction.try_parse('value 5 goes to bot 2')
        >>> GiveInstruction.try_parse(
        ...     'bot 2 gives low to bot 1 and high to bot 0')
        GiveInstruction(source=2, low_destination=1, high_destination=0,
            low_destination_type=DestinationType.Bot,
            high_destination_type=DestinationType.Bot)
        >>> GiveInstruction.try_parse(
        ...     'bot 2 gives low to bot 1 and high to output 0')
        GiveInstruction(source=2, low_destination=1, high_destination=0,
            low_destination_type=DestinationType.Bot,
            high_destination_type=DestinationType.Output)
        >>> GiveInstruction.try_parse(
        ...     'bot 2 gives low to output 1 and high to bot 0')
        GiveInstruction(source=2, low_destination=1, high_destination=0,
            low_destination_type=DestinationType.Output,
            high_destination_type=DestinationType.Bot)
        >>> GiveInstruction.try_parse(
        ...     'bot 2 gives low to output 1 and high to output 0')
        GiveInstruction(source=2, low_destination=1, high_destination=0,
            low_destination_type=DestinationType.Output,
            high_destination_type=DestinationType.Output)
        """
        match = cls.re_give_instruction.match(text)
        if not match:
            return None

        source_str, low_destination_type_str, low_destination_str, \
            high_destination_type_str, high_destination_str = match.groups()
        return cls(
            int(source_str), int(low_destination_str),
            int(high_destination_str),
            Bot.DestinationType(low_destination_type_str),
            Bot.DestinationType(high_destination_type_str),
        )

    def apply(self, bot_set: BotSet) -> BotSet:
        """
        >>> _bot_set = BotSet()
        >>> GiveInstruction(
        ...     1, 2, 3, Bot.DestinationType.Bot,
        ...     Bot.DestinationType.Bot).apply(_bot_set)
        BotSet(bots={1: Bot(id=1, low_value=None, high_value=None,
            low_destination=2, high_destination=3,
            low_destination_type=DestinationType.Bot,
            high_destination_type=DestinationType.Bot)}, outputs={})
        >>> GiveInstruction(2, 4, 5, Bot.DestinationType.Bot,
        ...     Bot.DestinationType.Bot).apply(_bot_set)
        BotSet(bots={1: Bot(id=1, low_value=None, high_value=None,
            low_destination=2, high_destination=3,
            low_destination_type=DestinationType.Bot,
            high_destination_type=DestinationType.Bot),
            2: Bot(id=2, low_value=None, high_value=None,
                low_destination=4, high_destination=5,
                low_destination_type=DestinationType.Bot,
                high_destination_type=DestinationType.Bot)}, outputs={})
        >>> GiveInstruction(1, 2, 3, Bot.DestinationType.Bot,
        ...     Bot.DestinationType.Bot).apply(_bot_set)
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        bot = bot_set[self.source]
        bot.set_low_destination(self.low_destination, self.low_destination_type)
        bot.set_high_destination(
            self.high_destination, self.high_destination_type)

        return bot_set


Challenge.main()
challenge = Challenge()
