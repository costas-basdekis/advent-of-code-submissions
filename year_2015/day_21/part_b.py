#!/usr/bin/env python3
from collections import Iterable
from typing import Tuple

from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        148
        """
        item_set = part_a.ItemSet.get_default_item_set()
        character = part_a.Character(100, 0, 0)
        enemy = part_a.Character.from_character_text(_input)
        return SquireExtended().get_max_cost_that_does_not_give_victory(
            item_set, character, enemy)


class SquireExtended(part_a.Squire):
    def get_max_cost_that_does_not_give_victory(
            self, item_set: part_a.ItemSet, character: part_a.Character,
            enemy: part_a.Character) -> int:
        return max(
            part_a.Item.get_items_cost(list(items))
            for items in self.get_equipment_sets_that_do_not_give_victory(
                item_set, character, enemy)
        )

    def get_equipment_sets_that_do_not_give_victory(
            self, item_set: part_a.ItemSet, character: part_a.Character,
            enemy: part_a.Character) -> Iterable[Tuple[part_a.Item, ...]]:
        for items in self.get_all_equipment_sets(item_set):
            equipped_character = character.equip(list(items))
            if not equipped_character.can_defeat(enemy):
                yield items


Challenge.main()
challenge = Challenge()
