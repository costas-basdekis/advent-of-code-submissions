#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import List, Union, Generic, Type

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        2006
        """
        return GameSet.from_games_text(_input, Cubes(12, 13, 14))\
            .get_sum_of_possible_ids()


GameT = TV["Game"]


@dataclass
class GameSet(Generic[GameT]):
    games: List["Game"]

    @classmethod
    def get_game_class(cls) -> Type[GameT]:
        return get_type_argument_class(cls, GameT)

    @classmethod
    def from_games_text(
        cls, games_text: str, configuration: "Cubes",
    ) -> "GameSet":
        game_cls = cls.get_game_class()
        return cls(
            [
                game_cls.from_game_text(line, configuration)
                for line in games_text.strip().splitlines()
            ],
        )

    def get_sum_of_possible_ids(self) -> int:
        """
        >>> GameSet.from_games_text('''
        ...     Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
        ...     Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
        ...     Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
        ...     Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
        ...     Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
        ... ''', Cubes(12, 13, 14)).get_sum_of_possible_ids()
        8
        """
        return sum((
            game.id
            for game in self.games
            if game.are_reveals_possible()
        ), 0)


@dataclass
class Game:
    id: int
    configuration: "Cubes"
    reveals: List["Cubes"]

    re_game = re.compile(r"Game (\d+): (.+)")

    @classmethod
    def from_game_text(cls, game_text: str, configuration: "Cubes") -> "Game":
        """
        >>> Game.from_game_text(
        ...     "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
        ...     Cubes(1, 1, 1))
        Game(id=1, configuration=Cubes(red=1, green=1, blue=1),
            reveals=[Cubes(red=4, green=0, blue=3),
            Cubes(red=1, green=2, blue=6), Cubes(red=0, green=2, blue=0)])
        """
        match = cls.re_game.match(game_text.strip())
        if not match:
            raise Exception(f"Could not parse '{game_text}'")
        id_str, rest = match.groups()
        return cls(
            int(id_str),
            configuration,
            list(map(Cubes.from_reveal_text, rest.split("; "))),
        )

    def are_reveals_possible(self) -> bool:
        """
        >>> configuration = Cubes(12, 13, 14)
        >>> Game.from_game_text(
        ...     "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
        ...     configuration,
        ... ).are_reveals_possible()
        True
        >>> Game.from_game_text(
        ...     "Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue",
        ...     configuration,
        ... ).are_reveals_possible()
        True
        >>> Game.from_game_text(
        ...     "Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red",
        ...     configuration,
        ... ).are_reveals_possible()
        False
        >>> Game.from_game_text(
        ...     "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red",
        ...     configuration,
        ... ).are_reveals_possible()
        False
        >>> Game.from_game_text(
        ...     "Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green",
        ...     configuration,
        ... ).are_reveals_possible()
        True
        """
        return all(
            reveal.is_possible_reveal_for(self.configuration)
            for reveal in self.reveals
        )


@dataclass
class Cubes:
    red: int
    green: int
    blue: int

    re_text = re.compile(
        r"((?P<count_1>\d+) (?P<colour_1>red|green|blue))?"
        r"(, )?"
        r"((?P<count_2>\d+) (?P<colour_2>red|green|blue))?"
        r"(, )?"
        r"((?P<count_3>\d+) (?P<colour_3>red|green|blue))?"
    )

    @classmethod
    def from_reveal_text(cls, reveal_text: str) -> "Cubes":
        """
        >>> Cubes.from_reveal_text("3 blue, 4 red")
        Cubes(red=4, green=0, blue=3)
        """
        match = cls.re_text.match(reveal_text)
        if not match:
            raise Exception(f"Could not parse '{reveal_text}'")
        counts = {
            "red": 0,
            "green": 0,
            "blue": 0,
        }
        for index in (1, 2, 3):
            count_str = match.group(f"count_{index}")
            colour = match.group(f"colour_{index}")
            if not count_str or not colour:
                break
            counts[colour] = int(count_str)

        return cls(counts["red"], counts["green"], counts["blue"])

    def is_possible_reveal_for(self, configuration: "Cubes") -> bool:
        """
        >>> Cubes(2, 3, 4).is_possible_reveal_for(Cubes(5, 5, 5))
        True
        >>> Cubes(2, 3, 4).is_possible_reveal_for(Cubes(4, 4, 4))
        True
        >>> Cubes(2, 3, 4).is_possible_reveal_for(Cubes(3, 3, 3))
        False
        """
        return (
            self.red <= configuration.red
            and self.green <= configuration.green
            and self.blue <= configuration.blue
        )


Challenge.main()
challenge = Challenge()
