#!/usr/bin/env python3
import re
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Generic, Type, Optional, Any, Callable

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
        Game.from_boss_text(self.input).play()


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
    options_played: List[Any]

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
            winner=None, options_played=[])
        """
        player_class = cls.get_player_class()
        boss_class = cls.get_boss_class()
        return cls(
            player=player_class(),
            boss=boss_class.from_boss_text(boss_text),
            next_turn_character_type=CharacterEnum.Player,
            winner=None,
            options_played=[],
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

    def play(self):
        while not self.finished:
            click.echo(self)
            result = self.pre_play_turn()
            if result:
                click.echo(
                    f"Pre-play result:\n{click.style(result, fg='blue')}"
                )

            options = self.get_play_options()
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
                    game_copy = deepcopy(self)
                    result = game_copy.play_turn(option)
                    if result:
                        click.echo(f"Result:\n{click.style(result, fg='blue')}")
                    click.echo(game_copy)
            else:
                result = self.play_turn(option)
                if result:
                    click.echo(f"Result:\n{click.style(result, fg='blue')}")

        click.echo(self)
        click.echo(f"Winner: {click.style(self.winner.name, fg='blue')}")

    @property
    def finished(self) -> bool:
        return self.winner is not None

    def find_min_mana_necessary(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        def reporting_format(_: Debugger, message: str) -> str:
            if min_mana_spent is None:
                min_mana_spent_str = "no winner yet"
            else:
                min_mana_spent_str = f"best is {min_mana_spent}"
            return f"{message} ({min_mana_spent_str}, {len(stack)} in stack)"

        with debugger.adding_extra_report_format(reporting_format):
            stack = [deepcopy(self)]
            min_mana_spent = None
            min_mana_game = None
            debugger.default_report_if("Searching for a winning game...")
            while debugger.step_if(stack):
                debugger.default_report_if("Searching for a winning game...")
                game = stack.pop(0)
                if min_mana_spent is not None \
                        and game.player.mana_spent >= min_mana_spent:
                    continue
                next_games = game.get_next_games(debugger)
                for next_game in next_games:
                    if (
                        min_mana_spent is not None
                        and next_game.player.mana_spent >= min_mana_spent
                    ):
                        continue
                    if next_game.winner == CharacterEnum.Player:
                        min_mana_spent = next_game.player.mana_spent
                        min_mana_game = next_game
                        debugger.report(f"Better game found: {min_mana_spent}")
                    stack.append(next_game)

            debugger.default_report(f"Finished searching")

        if min_mana_spent is None:
            raise Exception(f"Could not find a winning game")

        options_played_str = ', '.join(
            option.name
            for option in min_mana_game.options_played
            if isinstance(option, SpellEnum)
        )
        debugger.report(f"Min mana game moves: {options_played_str}")

        return min_mana_spent

    def get_next_games(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> List["Game"]:
        def play_turn(option: Any) -> Game:
            next_game = deepcopy(game)
            next_game.play_turn(option)
            return next_game

        game = deepcopy(self)
        game.pre_play_turn()
        return list(map(play_turn, game.get_play_options()))

    def get_play_options(self) -> List[Any]:
        if self.winner:
            return []

        character = self.next_turn_character
        return character.get_play_options()

    def pre_play_turn(self) -> Optional[str]:
        if self.finished:
            return None

        character = self.next_turn_character
        other = self.next_turn_other_character

        steps = self.get_pre_play_steps(character, other)
        return self.apply_play_steps(steps)

    def play_turn(self, option: Any) -> Optional[str]:
        if self.finished:
            return None

        self.options_played.append(option)

        if option is None:
            self.winner = self.next_turn_other_character_type
            return None

        character = self.next_turn_character
        other = self.next_turn_other_character

        steps = self.get_play_steps(character, other, option)
        result = self.apply_play_steps(steps)
        if self.finished:
            return result

        self.next_turn_character_type = self.next_turn_other_character_type
        return result

    def apply_play_steps(
        self, steps: List[Callable[[], Optional[str]]],
    ) -> Optional[str]:
        character = self.next_turn_character
        other = self.next_turn_other_character

        actions = []
        for step in steps:
            actions.append(step())
            if character.is_dead or other.is_dead:
                break
        actions = list(filter(None, actions))
        if actions:
            result = "\n".join(actions)
        else:
            result = None

        if character.is_dead:
            self.winner = self.next_turn_other_character_type
            return result
        elif other.is_dead:
            self.winner = self.next_turn_character_type
            return result

        return result

    def get_pre_play_steps(
        self, character: "Character", other: "Character",
    ) -> List[Callable[[], Optional[str]]]:
        return [
            lambda: character.apply_spells(other),
            lambda: other.apply_spells(character),
        ]

    def get_play_steps(
        self, character: "Character", other: "Character", option: Any,
    ) -> List[Callable[[], Optional[str]]]:
        return [
            lambda: character.play(other, option),
        ]

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

    def attack(self, amount: int, force: bool = False) -> int:
        raise NotImplementedError()

    def apply_spells(self, other: "Character") -> Optional[str]:
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
        SpellEnum.Shield: 6,
        SpellEnum.Poison: 6,
        SpellEnum.Recharge: 5,
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
        mana = self.mana
        if self.active_spell_timers.get(SpellEnum.Recharge, 0) > 0:
            mana += 101
        return sorted(
            spell
            for spell in SpellEnum
            if self.active_spell_timers.get(spell, 0) <= 0
            and self.SPELL_COST[spell] <= mana
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

    def attack(self, amount: int, force: bool = False) -> int:
        if force:
            attack_amount = 1
        else:
            attack_amount = max(amount - self.shield, 1)
        self.hit_points -= attack_amount
        return attack_amount

    def apply_spells(self, other: "Character") -> Optional[str]:
        actions = []

        if self.active_spell_timers.get(SpellEnum.Poison, 0) > 0:
            attack_amount = other.attack(3)
            actions.append(f"Poison attacked for {attack_amount}DMG")
        if self.active_spell_timers.get(SpellEnum.Recharge, 0) > 0:
            self.mana += 101
            actions.append("Recharged 101M")

        spell_timer_actions = ", ".join(
            f"{spell}'s timer is now {timer - 1}"
            for spell, timer in self.active_spell_timers.items()
            if timer > 0
        )
        self.active_spell_timers = {
            spell: timer - 1
            for spell, timer in self.active_spell_timers.items()
            if timer > 1
        }
        if spell_timer_actions:
            actions.append(spell_timer_actions)

        if actions:
            return f", ".join(actions)
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

    def attack(self, amount: int, force: bool = False) -> int:
        if force:
            attack_amount = 1
        else:
            attack_amount = max(amount - self.shield, 1)
        self.hit_points -= attack_amount
        return attack_amount

    def apply_spells(self, other: "Character") -> Optional[str]:
        return None


Challenge.main()
challenge = Challenge()
