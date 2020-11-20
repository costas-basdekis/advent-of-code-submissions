#!/usr/bin/env python3
import itertools
import re
from dataclasses import dataclass
from typing import Tuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        23385
        """
        group_set = GroupSet.from_groups_text(_input)
        group_set.step_many()
        return group_set.get_unit_count()


class GroupSet:
    group_class = NotImplemented
    re_faction_name = re.compile(r"^(.+):$")

    @classmethod
    def from_groups_text(cls, groups_text):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> len(group_set_a.groups)
        4
        >>> [group.faction for group in group_set_a.groups]
        ['Immune System', 'Immune System', 'Infection', 'Infection']
        >>> [group.initiative for group in group_set_a.groups]
        [2, 3, 1, 4]
        >>> [group.weaknesses for group in group_set_a.groups]
        [('radiation', 'bludgeoning'), ('bludgeoning', 'slashing'),
            ('radiation',), ('fire', 'cold')]
        """
        faction_strs = groups_text.strip().split("\n\n")
        groups = []
        for faction_str in faction_strs:
            non_empty_lines = list(filter(None, faction_str.splitlines()))
            name_str, group_strs = non_empty_lines[0], non_empty_lines[1:]
            faction_name, = cls.re_faction_name.match(name_str).groups()
            groups.extend(
                cls.group_class.from_group_text(faction_name, group_str)
                for group_str in group_strs
            )

        initiatives = [group.initiative for group in groups]
        if len(initiatives) != len(set(initiatives)):
            raise Exception(
                f"Got {len(initiatives) - len(set(initiatives))} "
                f"duplicate initiatives")

        return cls(groups)

    def __init__(self, groups):
        self.groups = groups

    def get_unit_count(self):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.get_unit_count()
        6292
        >>> group_set_a.step_many()
        True
        >>> group_set_a.get_unit_count()
        5216
        """
        return sum(
            group.size
            for group in self.groups
        )

    def step_many(self, count=None, debug=False, report_count=100000):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.step_many(3)
        False
        >>> [(group.initiative, group.size) for group in group_set_a.groups]
        [(3, 618), (1, 789), (4, 4434)]
        >>> group_set_a.step_many(4)
        False
        >>> [(group.initiative, group.size) for group in group_set_a.groups]
        [(3, 49), (1, 782), (4, 4434)]
        >>> group_set_a.step_many()
        True
        >>> [(group.initiative, group.size) for group in group_set_a.groups]
        [(1, 782), (4, 4434)]
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.step_many()
        True
        >>> [(group.initiative, group.size) for group in group_set_a.groups]
        [(1, 782), (4, 4434)]
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        finished = False
        for step in steps:
            finished = self.step()
            if finished:
                break
            if debug and step % report_count == 0:
                print(
                    f"Step {step} with {self.get_unit_count()} units in "
                    f"{len(self.groups)} groups")

        return finished

    def step(self):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.step()
        False
        >>> [(group.initiative, group.size) for group in group_set_a.groups]
        [(3, 905), (1, 797), (4, 4434)]
        """
        attacking_pairs = self.get_attacking_pairs()
        if not attacking_pairs:
            return True
        unit_count_before = self.get_unit_count()
        for attacker, defender in attacking_pairs:
            if attacker.size <= 0:
                continue
            units_killed = attacker.get_units_killed(defender)
            defender.size -= units_killed

        self.groups = [group for group in self.groups if group.size > 0]

        unit_count_after = self.get_unit_count()
        if unit_count_after == unit_count_before:
            return True

        return False

    def get_attacking_pairs(self):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> [
        ...     (attacker.initiative, defender.initiative)
        ...     for attacker, defender in group_set_a.get_attacking_pairs()
        ... ]
        [(4, 3), (3, 1), (2, 4), (1, 2)]
        """
        targeted_pairs = self.get_targeted_pairs()
        return sorted(targeted_pairs, key=self.attack_sort_key, reverse=True)

    def attack_sort_key(self, pair):
        attacker, _ = pair
        return attacker.initiative

    def get_targeted_pairs(self):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> [
        ...     (attacker.initiative, defender.initiative)
        ...     for attacker, defender in group_set_a.get_targeted_pairs()
        ... ] # [1, 2, 4, 3]
        [(1, 2), (2, 4), (4, 3), (3, 1)]
        """
        pairs = []
        sorted_groups_for_selection = self.sort_groups_for_selection()
        unopposed_groups = set(self.groups)
        for group in sorted_groups_for_selection:
            chosen_enemy = self.choose_enemy(group, unopposed_groups)
            if not chosen_enemy:
                continue
            unopposed_groups.remove(chosen_enemy)
            pairs.append((group, chosen_enemy))

        return pairs

    def choose_enemy(self, group, unopposed_groups):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.choose_enemy(
        ...     group_set_a.groups[0],
        ...     {group_set_a.groups[2], group_set_a.groups[3]})
        Group(..., initiative=4, ...)
        """
        enemies = group.filter_enemies(unopposed_groups)
        chosen_enemy = max(
            enemies, key=self.get_group_enemy_sort_key(group), default=None)
        return chosen_enemy

    def get_group_enemy_sort_key(self, group):
        def group_enemy_sort_key(enemy):
            return (
                group.get_potential_attack(enemy),
                enemy.effective_power,
                enemy.initiative,
            )

        return group_enemy_sort_key

    def sort_groups_for_selection(self):
        """
        >>> def get_sorted_order(groups_attributes):
        ...     group_set = GroupSet([
        ...         Group(**{
        ...             "faction": 'a', "hit_points": 1,
        ...             "attack_type": 'r', "weaknesses": (), "immunities": (),
        ...             **group_attributes,
        ...         })
        ...         for group_attributes in groups_attributes
        ...     ])
        ...     sorted_groups = group_set.sort_groups_for_selection()
        ...     return [
        ...         group.initiative
        ...         for group in sorted_groups
        ...     ]
        >>> get_sorted_order([
        ...     {"size": 1, "attack": 1, "initiative": 0},
        ...     {"size": 1, "attack": 2, "initiative": 1},
        ... ])
        [1, 0]
        >>> get_sorted_order([
        ...     {"size": 1, "attack": 2, "initiative": 0},
        ...     {"size": 1, "attack": 2, "initiative": 1},
        ... ])
        [1, 0]
        >>> get_sorted_order([
        ...     {"size": 1, "attack": 2, "initiative": 2},
        ...     {"size": 1, "attack": 2, "initiative": 1},
        ... ])
        [2, 1]
        >>> get_sorted_order([
        ...     {"size": 1, "attack": 3, "initiative": 2},
        ...     {"size": 1, "attack": 2, "initiative": 1},
        ... ])
        [2, 1]
        >>> get_sorted_order([
        ...     {"size": 1, "attack": 3, "initiative": 0},
        ...     {"size": 1, "attack": 2, "initiative": 1},
        ... ])
        [0, 1]
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> [
        ...     group.initiative
        ...     for group in group_set_a.sort_groups_for_selection()
        ... ] # {1: 92916, 2: 76619, 4: 53820, 3: 24725}
        [1, 2, 4, 3]
        """
        return sorted(
            self.groups, key=self.group_selection_sort_key, reverse=True)

    def group_selection_sort_key(self, group):
        return group.effective_power, group.initiative


@dataclass
class Group:
    faction: str
    size: int
    hit_points: int
    initiative: int
    attack: int
    attack_type: str
    weaknesses: Tuple[str, ...]
    immunities: Tuple[str, ...]

    re_group = re.compile(
        r"(\d+) units each with (\d+) hit points "
        r"(?:\((?:(weak|immune) to ([^;)]+))?"
        r"(?:; )?"
        r"(?:(weak|immune) to ([^;)]+))?\) )?"
        r"with an attack that does (\d+) (\w+) damage at initiative (\d+)")

    @classmethod
    def from_group_text(cls, faction, group_text):
        """
        >>> Group.from_group_text("Immune System",
        ...     "18 units each with 729 hit points "
        ...     "(weak to fire, radiation; immune to cold, slashing) "
        ...     "with an attack that does 23 radiation damage at initiative 10")
        Group(faction='Immune System', size=18, hit_points=729, initiative=10,
            attack=23, attack_type='radiation',
            weaknesses=('fire', 'radiation'), immunities=('cold', 'slashing'))
        >>> Group.from_group_text("Immune System",
        ...     "2 units each with 2 hit points "
        ...     "(weak to fire; immune to cold) "
        ...     "with an attack that does 8 radiation damage at initiative 1")
        Group(faction='Immune System', size=2, hit_points=2, initiative=1,
            attack=8, attack_type='radiation',
            weaknesses=('fire',), immunities=('cold',))
        >>> Group.from_group_text("Immune System",
        ...     "2 units each with 2 hit points "
        ...     "(immune to cold) "
        ...     "with an attack that does 8 radiation damage at initiative 1")
        Group(faction='Immune System', size=2, hit_points=2, initiative=1,
            attack=8, attack_type='radiation',
            weaknesses=(), immunities=('cold',))
        >>> Group.from_group_text("Immune System",
        ...     "2 units each with 2 hit points "
        ...     "(weak to fire) "
        ...     "with an attack that does 8 radiation damage at initiative 1")
        Group(faction='Immune System', size=2, hit_points=2, initiative=1,
            attack=8, attack_type='radiation',
            weaknesses=('fire',), immunities=())
        >>> Group.from_group_text("Immune System",
        ...     "2 units each with 2 hit points "
        ...     "with an attack that does 8 radiation damage at initiative 1")
        Group(faction='Immune System', size=2, hit_points=2, initiative=1,
            attack=8, attack_type='radiation',
            weaknesses=(), immunities=())
        >>> Group.from_group_text("Infection",
        ...     "4485 units each with 2961 hit points "
        ...     "(immune to radiation; weak to fire, cold) "
        ...     "with an attack that does 12 slashing damage at initiative 4")
        Group(faction='Infection', size=4485, hit_points=2961, initiative=4,
            attack=12, attack_type='slashing',
            weaknesses=('fire', 'cold'), immunities=('radiation',))
        """
        match = cls.re_group.match(group_text)
        if not match:
            raise Exception(f"Could not parse '{group_text}'")
        size_str, hit_points_str, list_a_name, list_a_str, list_b_name, \
            list_b_str, attack_str, attack_type, initiative_str = \
            match.groups()

        unknown_list_names = \
            {list_a_name, list_b_name} - {'weak', 'immune', None}
        if unknown_list_names:
            raise Exception(
                f"Unknown list types {sorted(unknown_list_names)}: expected "
                f"'weak' or 'immune'")

        if list_a_name == 'weak':
            weaknesses_str = list_a_str
            immunities_str = list_b_str
        else:
            weaknesses_str = list_b_str
            immunities_str = list_a_str

        if weaknesses_str:
            weaknesses = tuple(weaknesses_str.split(", "))
        else:
            weaknesses = ()
        if immunities_str:
            immunities = tuple(immunities_str.split(", "))
        else:
            immunities = ()

        return cls(
            faction=faction,
            size=int(size_str), hit_points=int(hit_points_str),
            initiative=int(initiative_str), attack=int(attack_str),
            attack_type=attack_type, weaknesses=weaknesses,
            immunities=immunities)

    @property
    def effective_power(self):
        """
        >>> Group(
        ...     faction='Immune System', size=18, hit_points=729, initiative=10,
        ...     attack=23, attack_type='radiation',
        ...     weaknesses=('fire', 'radiation'),
        ...     immunities=('cold', 'slashing')).effective_power
        414
        """
        return self.size * self.attack

    def __hash__(self):
        return hash(self.initiative)

    def get_units_killed(self, enemy):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.groups[3].get_units_killed(group_set_a.groups[1])
        84
        """
        potential_attack = self.get_potential_attack(enemy)
        return min(potential_attack // enemy.hit_points, enemy.size)

    def filter_enemies(self, groups):
        return (
            group
            for group in groups
            if group.faction != self.faction
        )

    def get_potential_attack(self, enemy):
        """
        >>> group_set_a = GroupSet.from_groups_text(
        ...     "Immune System:\\n"
        ...     "17 units each with 5390 hit points (weak to radiation, "
        ...     "bludgeoning) with an attack that does 4507 fire damage at "
        ...     "initiative 2\\n"
        ...     "989 units each with 1274 hit points (immune to fire; weak to "
        ...     "bludgeoning, slashing) with an attack that does 25 slashing "
        ...     "damage at "
        ...     "initiative 3\\n"
        ...     "\\n"
        ...     "Infection:\\n"
        ...     "801 units each with 4706 hit points (weak to radiation) with "
        ...     "an attack that does 116 bludgeoning damage at initiative 1\\n"
        ...     "4485 units each with 2961 hit points (immune to radiation; "
        ...     "weak to fire, cold) with an attack that does 12 slashing "
        ...     "damage at "
        ...     "initiative 4\\n"
        ... )
        >>> group_set_a.groups[0].get_potential_attack(group_set_a.groups[2])
        76619
        >>> group_set_a.groups[0].attack_type
        'fire'
        >>> sorted(group_set_a.groups[3].weaknesses)
        ['cold', 'fire']
        >>> group_set_a.groups[0].get_potential_attack(group_set_a.groups[3])
        153238
        """
        if self.attack_type in enemy.immunities:
            return 0
        if self.attack_type in enemy.weaknesses:
            return 2 * self.effective_power

        return self.effective_power


GroupSet.group_class = Group


challenge = Challenge()
challenge.main()
