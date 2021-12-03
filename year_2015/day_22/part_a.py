#!/usr/bin/env python3
import re
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Generic, Type, Optional, Any

import click

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        953
        """
        return Game.from_boss_text(_input).find_min_mana_necessary(debugger)

    def play(self):
        game = Game.from_boss_text(self.input)
        debugger = Debugger()
        while not game.finished:
            click.echo(game)
            options = game.get_play_options()
            if options:
                for index, option in enumerate(options, 1):
                    click.echo(
                        f"{index}. {click.style(option.name, fg='green')}"
                    )
                user_choices = (
                    list(map(str, range(1, len(options) + 1)))
                    + ["a"]
                )
                user_choice = click.prompt(
                    click.style("Select a choice", fg='yellow'),
                    type=click.Choice(user_choices),
                    default=1 if len(options) == 1 else None,
                )
                if user_choice == "a":
                    option = None
                else:
                    option = options[int(user_choice) - 1]
            else:
                click.echo(f"{click.style('No options', fg='red')}")
                user_choice = None
                option = None
            if user_choice == "a":
                for option in options:
                    game_copy = deepcopy(game)
                    result = game_copy.play_turn(option, debugger=debugger)
                    if result:
                        click.echo(f"Result:\n{click.style(result, fg='blue')}")
                    click.echo(game_copy)
            else:
                result = game.play_turn(option, debugger=debugger)
                if result:
                    click.echo(f"Result:\n{click.style(result, fg='blue')}")

        click.echo(game)
        click.echo(f"Winner: {click.style(game.winner.name, fg='blue')}")


PlayerT = TV["Player"]
BossT = TV["Boss"]


class CharacterEnum(Enum):
    Player = "Player"
    Boss = "Boss"

    def __repr__(self):
        return f"{type(self).__name__}.{self.name}"


@dataclass
class Game(Generic[PlayerT, BossT]):
    player: PlayerT
    boss: BossT
    next_turn_character_type: CharacterEnum
    winner: Optional[CharacterEnum]

    @classmethod
    def get_player_class(cls) -> Type[PlayerT]:
        return get_type_argument_class(cls, PlayerT)

    @classmethod
    def get_boss_class(cls) -> Type[BossT]:
        return get_type_argument_class(cls, BossT)

    @classmethod
    def from_boss_text(cls, boss_text: str) -> "Game":
        """
        >>> Game.from_boss_text('''
        ...     Hit Points: 55
        ...     Damage: 8
        ... ''')
        Game(player=Player(hit_points=50, mana=500, mana_spent=0,
            active_spell_timers={}),
            boss=Boss(hit_points=55, damage=8),
            next_turn_character_type=CharacterEnum.Player,
            winner=None)
        """
        player_class = cls.get_player_class()
        boss_class = cls.get_boss_class()
        return cls(
            player=player_class(),
            boss=boss_class.from_boss_text(boss_text),
            next_turn_character_type=CharacterEnum.Player,
            winner=None,
        )

    def __str__(self):
        """
        >>> print(Game.from_boss_text('''
        ...     Hit Points: 55
        ...     Damage: 8
        ... '''))
        Next to play: Player
        * Player: 50HP/500M (0M spent), no spells
        * Boss: 55HP/8DMG
        """
        if self.winner:
            next_to_play_str = f"Winner: {self.winner.name}"
        else:
            next_to_play_str = (
                f"Next to play: {self.next_turn_character_type.name}"
            )

        return (
            f"{next_to_play_str}"
            f"\n* {self.player}"
            f"\n* {self.boss}"
        )

    @property
    def finished(self) -> bool:
        return self.winner is not None

    def find_min_mana_necessary(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        debugger.default_report_if(
            "Searching for a winning game, no winner yet..."
        )
        stack = [deepcopy(self)]
        min_mana_spent = None
        while stack:
            debugger.step()
            if min_mana_spent is None:
                min_mana_spent_str = "no winner yet"
            else:
                min_mana_spent_str = f"best is {min_mana_spent}"
            debugger.default_report_if(
                f"Searching for a winning game, {min_mana_spent_str}..."
            )
            game = stack.pop(0)
            if min_mana_spent is not None \
                    and game.player.mana_spent >= min_mana_spent:
                continue
            next_games = game.get_next_games(debugger)
            for next_game in next_games:
                if not next_game.finished:
                    continue
                if next_game.winner != CharacterEnum.Player:
                    continue
                if (
                    min_mana_spent is not None
                    and next_game.player.mana_spent >= min_mana_spent
                ):
                    continue
                min_mana_spent = next_game.player.mana_spent
            stack.extend(next_games)

        if min_mana_spent is None:
            min_mana_spent_str = "no winner yet"
        else:
            min_mana_spent_str = f"best is {min_mana_spent}"
        debugger.default_report_if(f"Finished searching: {min_mana_spent_str}")

        if min_mana_spent is None:
            raise Exception(f"Could not find a winning game")

        return min_mana_spent

    def get_next_games(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> List["Game"]:
        def play_turn(option: Any) -> Game:
            game = deepcopy(self)
            game.play_turn(option, debugger)
            return game

        return list(map(play_turn, self.get_play_options()))

    def play_first_option(self) -> Optional[str]:
        options = self.get_play_options()
        if options:
            option = None
        else:
            option = options[0]

        return self.play_turn(option)

    def get_play_options(self) -> List[Any]:
        if self.winner:
            return []

        character = self.next_turn_character
        return character.get_play_options()

    def play_turn(
        self, option: Any, debugger: Debugger = Debugger(enabled=False),
    ) -> Optional[str]:
        if self.finished:
            return None

        if option is None:
            self.winner = self.next_turn_other_character_type
            return None

        character = self.next_turn_character
        other = self.next_turn_other_character

        actions = list(filter(None, [
            character.apply_spells_start_of_turn(other),
            other.apply_spells_start_of_turn(character),
            character.play(other, option),
            character.apply_spells_end_of_turn(other),
            other.apply_spells_end_of_turn(character),
        ]))
        if actions:
            result = "\n".join(actions)
        else:
            result = None

        if other.is_dead:
            self.winner = self.next_turn_character_type
            return result

        self.next_turn_character_type = self.next_turn_other_character_type
        return result

    @property
    def next_turn_character(self) -> "Character":
        return self.get_character_by_type(self.next_turn_character_type)

    @property
    def next_turn_other_character_type(self) -> CharacterEnum:
        return {
            CharacterEnum.Player: CharacterEnum.Boss,
            CharacterEnum.Boss: CharacterEnum.Player,
        }[self.next_turn_character_type]

    @property
    def next_turn_other_character(self) -> "Character":
        return self.get_character_by_type(self.next_turn_other_character_type)

    def get_character_by_type(self, _type: CharacterEnum) -> "Character":
        return {
            CharacterEnum.Player: self.player,
            CharacterEnum.Boss: self.boss,
        }[_type]


class SpellEnum(Enum):
    MagicMissile = "MagicMissile"
    Drain = "Drain"
    Shield = "Shield"
    Poison = "Poison"
    Recharge = "Recharge"

    def __lt__(self, other):
        return self.name < other.name


class Character:
    def get_play_options(self) -> List[Any]:
        raise NotImplementedError()

    def play(self, other: "Character", option: Any) -> str:
        raise NotImplementedError()

    @property
    def is_dead(self) -> bool:
        raise NotImplementedError()

    @property
    def shield(self) -> int:
        raise NotImplementedError()

    def attack(self, amount: int) -> int:
        raise NotImplementedError()

    def apply_spells_start_of_turn(self, other: "Character") -> Optional[str]:
        raise NotImplementedError()

    def apply_spells_end_of_turn(self, other: "Character") -> Optional[str]:
        raise NotImplementedError()


@dataclass
class Player(Character):
    hit_points: int = 50
    mana: int = 500
    mana_spent: int = 0
    active_spell_timers: Dict[SpellEnum, int] = field(default_factory=dict)

    SPELL_COST = {
        SpellEnum.MagicMissile: 53,
        SpellEnum.Drain: 73,
        SpellEnum.Shield: 113,
        SpellEnum.Poison: 173,
        SpellEnum.Recharge: 229,
    }

    SPELL_DURATION = {
        SpellEnum.Shield: 7,
        SpellEnum.Poison: 7,
        SpellEnum.Recharge: 6,
    }

    def __str__(self):
        """
        >>> print(Player())
        Player: 50HP/500M (0M spent), no spells
        >>> print(Player(
        ...     active_spell_timers={SpellEnum.Poison: 2, SpellEnum.Shield: 3},
        ... ))
        Player: 50HP/500M (0M spent), Poison: 2r, Shield: 3r
        """
        if any(self.active_spell_timers.values()):
            spells_str = ", ".join(
                f"{spell.name}: {timer}r"
                for spell, timer in self.active_spell_timers.items()
            )
        else:
            spells_str = "no spells"
        return (
            f"Player: {self.hit_points}HP/{self.mana}M "
            f"({self.mana_spent}M spent), {spells_str}"
        )

    def get_available_spells(self) -> List[SpellEnum]:
        return sorted(
            spell
            for spell in SpellEnum
            if self.active_spell_timers.get(spell, 0) <= 0
            and self.SPELL_COST[spell] <= self.mana
        )

    @property
    def shield(self) -> int:
        if self.active_spell_timers.get(SpellEnum.Shield, 0) <= 0:
            return 0

        return 7

    def get_play_options(self) -> List[Any]:
        return self.get_available_spells()

    def play(self, other: "Character", option: Any) -> str:
        assert isinstance(other, Boss)
        assert isinstance(option, SpellEnum)
        assert self.active_spell_timers.get(option, 0) <= 0
        assert self.SPELL_COST[option] <= self.mana

        self.mana -= self.SPELL_COST[option]
        self.mana_spent += self.SPELL_COST[option]
        if option == SpellEnum.MagicMissile:
            attack_amount = other.attack(4)
            return f"Magic missile attacked for {attack_amount}DMG"
        elif option == SpellEnum.Drain:
            attack_amount = other.attack(2)
            self.hit_points += 2
            return f"Drain attacked for {attack_amount}DMG, healed 2HP"
        else:
            self.active_spell_timers[option] = self.SPELL_DURATION[option]
            return (
                f"Casted spell {option.name} for {self.SPELL_DURATION[option]} "
                f"rounds"
            )

    @property
    def is_dead(self) -> bool:
        """
        >>> Player().is_dead
        False
        >>> Player(hit_points=1).is_dead
        False
        >>> Player(hit_points=0).is_dead
        True
        >>> Player(hit_points=-5).is_dead
        True
        """
        return self.hit_points <= 0

    def attack(self, amount: int) -> int:
        attack_amount = max(amount - self.shield, 1)
        self.hit_points -= attack_amount
        return attack_amount

    def apply_spells_start_of_turn(self, other: "Character") -> Optional[str]:
        actions = []
        if self.active_spell_timers.get(SpellEnum.Poison, 0) > 0:
            attack_amount = other.attack(3)
            actions.append(f"Poison attacked for {attack_amount}DMG")
        if self.active_spell_timers.get(SpellEnum.Recharge, 0) > 0:
            self.mana += 101
            actions.append("Recharged 101M")

        if actions:
            return f", ".join(actions)
        else:
            return None

    def apply_spells_end_of_turn(self, other: "Character") -> Optional[str]:
        actions = ", ".join(
            f"{spell}'s timer is now {timer - 1}"
            for spell, timer in self.active_spell_timers.items()
            if timer > 0
        )
        self.active_spell_timers = {
            spell: timer - 1
            for spell, timer in self.active_spell_timers.items()
            if timer > 1
        }
        if actions:
            return actions
        else:
            return None


class BossChoicesEnum(Enum):
    Attack = "Attack"


@dataclass
class Boss(Character):
    hit_points: int
    damage: int

    re_boss = re.compile(
        r"^\s*Hit Points:\s*(\d+)\s*Damage:\s*(\d+)\s*$"
    )

    @classmethod
    def from_boss_text(cls, boss_text: str) -> "Boss":
        """
        >>> Boss.from_boss_text('''
        ...     Hit Points: 55
        ...     Damage: 8
        ... ''')
        Boss(hit_points=55, damage=8)
        """
        hit_points_str, damage_str = cls.re_boss.match(boss_text).groups()
        return cls(
            hit_points=int(hit_points_str),
            damage=int(damage_str),
        )

    def __str__(self):
        """
        >>> print(Boss.from_boss_text('''
        ...     Hit Points: 55
        ...     Damage: 8
        ... '''))
        Boss: 55HP/8DMG
        """
        return f"Boss: {self.hit_points}HP/{self.damage}DMG"

    def get_play_options(self) -> List[Any]:
        return [BossChoicesEnum.Attack]

    def play(self, other: "Character", option: Any) -> str:
        assert isinstance(other, Player)
        assert option == BossChoicesEnum.Attack

        attack_amount = other.attack(self.damage)
        return f"Attacked for {attack_amount}DMG"

    @property
    def is_dead(self) -> bool:
        """
        >>> Boss(hit_points=50, damage=8).is_dead
        False
        >>> Boss(hit_points=1, damage=8).is_dead
        False
        >>> Boss(hit_points=0, damage=8).is_dead
        True
        >>> Boss(hit_points=-5, damage=8).is_dead
        True
        """
        return self.hit_points <= 0

    @property
    def shield(self) -> int:
        return 0

    def attack(self, amount: int) -> int:
        attack_amount = max(amount - self.shield, 1)
        self.hit_points -= attack_amount
        return attack_amount

    def apply_spells_start_of_turn(self, other: "Character") -> Optional[str]:
        return None

    def apply_spells_end_of_turn(self, other: "Character") -> Optional[str]:
        return None


Challenge.main()
challenge = Challenge()
