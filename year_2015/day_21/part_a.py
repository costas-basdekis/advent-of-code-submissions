#!/usr/bin/env python3
import re
from dataclasses import dataclass, field
from itertools import product, combinations
from typing import List, Dict, Generic, Type, Iterable, Tuple

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        78
        """
        item_set = ItemSet.get_default_item_set()
        character = Character(100, 0, 0)
        enemy = Character.from_character_text(_input)
        return Squire().get_min_cost_that_gives_victory(
            item_set, character, enemy)


class Squire:
    ITEM_COUNT_RANGES_BY_TYPE = {
        "Weapons": [1],
        "Armor": [0, 1],
        "Rings": [0, 1, 2],
    }

    def get_min_cost_that_gives_victory(
            self, item_set: 'ItemSet', character: 'Character',
            enemy: 'Character') -> int:
        return min(
            Item.get_items_cost(list(items))
            for items in self.get_equipment_sets_that_give_victory(
                item_set, character, enemy)
        )

    def get_equipment_sets_that_give_victory(
            self, item_set: 'ItemSet', character: 'Character',
            enemy: 'Character') -> Iterable[Tuple['Item', ...]]:
        for items in self.get_all_equipment_sets(item_set):
            equipped_character = character.equip(list(items))
            if equipped_character.can_defeat(enemy):
                yield items

    def get_all_equipment_sets(self, item_set: 'ItemSet',
                               ) -> Iterable[Tuple['Item', ...]]:
        """
        >>> # noinspection PyUnresolvedReferences
        >>> sorted(x[-1:] + x[:-1] for x in Squire().get_all_equipment_sets(
        ...     ItemSet({
        ...         "Weapons": ["w1", "w2"], "Armor": ["a1", "a2"],
        ...         "Rings": ["r1", "r2", "r3"]})))
        [('w1',),
            ('w1', 'a1'),
                ('w1', 'a1', 'r1'),
                    ('w1', 'a1', 'r1', 'r2'),
                    ('w1', 'a1', 'r1', 'r3'),
                ('w1', 'a1', 'r2'),
                    ('w1', 'a1', 'r2', 'r3'),
                ('w1', 'a1', 'r3'),
            ('w1', 'a2'),
                ('w1', 'a2', 'r1'),
                    ('w1', 'a2', 'r1', 'r2'),
                    ('w1', 'a2', 'r1', 'r3'),
                ('w1', 'a2', 'r2'),
                    ('w1', 'a2', 'r2', 'r3'),
                ('w1', 'a2', 'r3'),
            ('w1', 'r1'),
                ('w1', 'r1', 'r2'),
                ('w1', 'r1', 'r3'),
            ('w1', 'r2'),
                ('w1', 'r2', 'r3'),
            ('w1', 'r3'),
        ('w2',),
            ('w2', 'a1'),
                ('w2', 'a1', 'r1'),
                    ('w2', 'a1', 'r1', 'r2'),
                    ('w2', 'a1', 'r1', 'r3'),
                ('w2', 'a1', 'r2'),
                    ('w2', 'a1', 'r2', 'r3'),
                ('w2', 'a1', 'r3'),
            ('w2', 'a2'),
                ('w2', 'a2', 'r1'),
                    ('w2', 'a2', 'r1', 'r2'),
                    ('w2', 'a2', 'r1', 'r3'),
                ('w2', 'a2', 'r2'),
                    ('w2', 'a2', 'r2', 'r3'),
                ('w2', 'a2', 'r3'),
            ('w2', 'r1'),
                ('w2', 'r1', 'r2'),
                ('w2', 'r1', 'r3'),
            ('w2', 'r2'),
                ('w2', 'r2', 'r3'),
            ('w2', 'r3')]
        """
        type_and_count_sets = self.get_all_possible_type_and_count_sets()
        for type_and_count_set in type_and_count_sets:
            for item_tuples in product(*(
                tuple(combinations(item_set.items_by_type[_type], count))
                for _type, count in type_and_count_set
            )):
                yield sum(item_tuples, ())

    def get_all_possible_type_and_count_sets(
            self) -> Iterable[Tuple[Tuple[str, int]]]:
        """
        >>> list(Squire().get_all_possible_type_and_count_sets())
        [(('Armor', 0), ('Rings', 0), ('Weapons', 1)),
            (('Armor', 0), ('Rings', 1), ('Weapons', 1)),
            (('Armor', 0), ('Rings', 2), ('Weapons', 1)),
        (('Armor', 1), ('Rings', 0), ('Weapons', 1)),
            (('Armor', 1), ('Rings', 1), ('Weapons', 1)),
            (('Armor', 1), ('Rings', 2), ('Weapons', 1))]
        """
        types_and_count_ranges = sorted(self.ITEM_COUNT_RANGES_BY_TYPE.items())
        types = [_type for _type, _ in types_and_count_ranges]
        count_ranges = [
            count_range
            for _, count_range in types_and_count_ranges
        ]
        count_sets = product(*count_ranges)
        for count_set in count_sets:
            yield tuple(zip(types, count_set))


ItemT = TV['Item']


@dataclass
class ItemSet(Generic[ItemT]):
    items_by_type: Dict[str, List[ItemT]]

    re_header = re.compile(r"^(\w+):\s+Cost\s+Damage\s+Armor$")

    @classmethod
    def get_item_class(cls) -> Type[ItemT]:
        return get_type_argument_class(cls, ItemT)

    @classmethod
    def get_default_item_set(cls):
        return ItemSet.from_items_text(
            "Weapons:    Cost  Damage  Armor\n"
            "Dagger        8     4       0\n"
            "Shortsword   10     5       0\n"
            "Warhammer    25     6       0\n"
            "Longsword    40     7       0\n"
            "Greataxe     74     8       0\n"
            "\n"
            "Armor:      Cost  Damage  Armor\n"
            "Leather      13     0       1\n"
            "Chainmail    31     0       2\n"
            "Splintmail   53     0       3\n"
            "Bandedmail   75     0       4\n"
            "Platemail   102     0       5\n"
            "\n"
            "Rings:      Cost  Damage  Armor\n"
            "Damage +1    25     1       0\n"
            "Damage +2    50     2       0\n"
            "Damage +3   100     3       0\n"
            "Defense +1   20     0       1\n"
            "Defense +2   40     0       2\n"
            "Defense +3   80     0       3\n"
        )

    @classmethod
    def from_items_text(cls, items_text: str):
        """
        >>> ItemSet.get_default_item_set()
        ItemSet(items_by_type={'Weapons': [Item(type='Weapons', name='Dagger',
            cost=8, damage=4, armor=0),
            Item(type='Weapons', name='Shortsword', cost=10, damage=5, armor=0),
            ...],
            'Armor': [...],
            'Rings': [...]})
        """
        type_blocks = items_text.strip().split("\n\n")
        items_by_type = {}
        for type_block in type_blocks:
            header_text, *type_item_texts = type_block.splitlines()
            header_match = cls.re_header.match(header_text)
            if not header_match:
                raise Exception(f"Could not parse header {repr(header_text)}")
            _type, = header_match.groups()
            item_class = cls.get_item_class()
            items = [
                item_class.from_item_text(item_text, _type)
                for item_text in type_item_texts
            ]
            items_by_type[_type] = items

        return cls(items_by_type)


@dataclass
class Item:
    type: str
    name: str
    cost: int
    damage: int
    armor: int

    re_item = re.compile(r"^((?:[\w+]| [\w+])+)\s+(\d+)\s+(\d+)\s+(\d+)$")

    @classmethod
    def from_item_text(cls, item_text: str, _type: str):
        """
        >>> Item.from_item_text("Dagger        8     4       0", "Weapons")
        Item(type='Weapons', name='Dagger', cost=8, damage=4, armor=0)
        """
        match = cls.re_item.match(item_text)
        if not match:
            raise Exception(f"Could not parse {repr(item_text)}")
        name, cost_str, damage_str, armor_str = match.groups()
        return cls(_type, name, int(cost_str), int(damage_str), int(armor_str))

    @classmethod
    def get_items_cost(cls, items: List['Item']) -> int:
        return sum(item.cost for item in items)


@dataclass
class Character:
    hit_points: int
    damage: int
    armor: int
    items: List[Item] = field(default_factory=list)
    items_cost: int = 0

    re_character = re.compile(
        r"^Hit Points: (\d+)\s+Damage: (\d+)\s+Armor: (\d+)$")

    @classmethod
    def from_character_text(cls, character_text: str):
        """
        >>> Character.from_character_text(
        ... "Hit Points: 104\\n"
        ... "Damage: 8\\n"
        ... "Armor: 1\\n"
        ... )
        Character(hit_points=104, damage=8, armor=1, items=[], items_cost=0)
        """
        hit_points_str, damage_str, armor_str = \
            cls.re_character.match(character_text.strip()).groups()

        return cls(int(hit_points_str), int(damage_str), int(armor_str))

    def copy(self) -> 'Character':
        return self.equip([])

    def equip(self, items: List[Item]) -> 'Character':
        """
        >>> Character(104, 8, 1, []).equip([])
        Character(hit_points=104, damage=8, armor=1, items=[], items_cost=0)
        >>> Character(104, 8, 1, []).equip([Item("Weapons", "Dagger", 8, 4, 0)])
        Character(hit_points=104, damage=12, armor=1, items=[...], items_cost=8)
        """
        new_items = self.items + items
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            hit_points=self.hit_points,
            damage=self.damage + sum(item.damage for item in items),
            armor=self.armor + sum(item.armor for item in items),
            items=new_items,
            items_cost=self.items_cost + Item.get_items_cost(items),
        )

    def can_defeat(self, enemy: 'Character') -> bool:
        """
        >>> Character(8, 5, 5).can_defeat(Character(12, 7, 2))
        True
        """
        me = self.copy()
        enemy = enemy.copy()
        opponents: Tuple[Character, Character] = (me, enemy)
        if not any(opponent.is_alive() for opponent in opponents):
            raise Exception(f"Can't start with two dead opponents")
        while all(opponent.is_alive() for opponent in opponents):
            attacker, defender = opponents
            attacker.attack(defender)
            opponents = (defender, attacker)
        return me.is_alive()

    def is_alive(self) -> bool:
        return self.hit_points > 0

    def attack(self, enemy: 'Character'):
        enemy.hit_points -= self.get_attack_value(enemy)

    def get_attack_value(self, enemy: 'Character') -> int:
        """
        >>> Character(100, 8, 0).get_attack_value(Character(10, 0, 3))
        5
        >>> Character(100, 8, 0).get_attack_value(Character(10, 0, 300))
        1
        """
        return max(1, self.damage - enemy.armor)


Challenge.main()
challenge = Challenge()
