#!/usr/bin/env python3
from typing import List, Union

from aox.challenge import Debugger
from utils import BaseChallenge, min_and_max_tuples
from year_2023.day_02.part_a import Game, Cubes, GameSet


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        84911
        """
        return GameSetExtended\
            .from_games_text(_input, CubesExtended(12, 13, 14))\
            .get_power_sum()


class GameSetExtended(GameSet["GameExtended"]):
    games: List["GameExtended"]

    def get_power_sum(self) -> int:
        """
        >>> GameSetExtended.from_games_text('''
        ...     Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
        ...     Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
        ...     Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
        ...     Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
        ...     Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
        ... ''', Cubes(1, 1, 1)).get_power_sum()
        2286
        """
        return sum((
            game.get_minimum_configuration().get_power()
            for game in self.games
        ), 0)


class GameExtended(Game["CubesExtended"]):
    reveals: List["CubesExtended"]

    def get_minimum_configuration(self) -> "CubesExtended":
        """
        >>> GameExtended.from_game_text(
        ...     "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green",
        ...     CubesExtended(1, 1, 1),
        ... ).get_minimum_configuration()
        CubesExtended(red=4, green=2, blue=6)
        >>> GameExtended.from_game_text(
        ...     "Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue",
        ...     CubesExtended(1, 1, 1),
        ... ).get_minimum_configuration()
        CubesExtended(red=1, green=3, blue=4)
        >>> GameExtended.from_game_text(
        ...     "Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red",
        ...     CubesExtended(1, 1, 1),
        ... ).get_minimum_configuration()
        CubesExtended(red=20, green=13, blue=6)
        >>> GameExtended.from_game_text(
        ...     "Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red",
        ...     CubesExtended(1, 1, 1),
        ... ).get_minimum_configuration()
        CubesExtended(red=14, green=3, blue=15)
        >>> GameExtended.from_game_text(
        ...     "Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green",
        ...     CubesExtended(1, 1, 1),
        ... ).get_minimum_configuration()
        CubesExtended(red=6, green=3, blue=2)
        """
        _, max_values = min_and_max_tuples(
            reveal.get_values()
            for reveal in self.reveals
        )
        return CubesExtended.from_values(max_values)


class CubesExtended(Cubes):
    @classmethod
    def from_values(cls, values: (int, int, int)) -> "CubesExtended":
        red, green, blue = values
        return cls(red, green, blue)

    def get_values(self) -> (int, int, int):
        return self.red, self.green, self.blue

    def get_power(self) -> int:
        """
        >>> CubesExtended(2, 3, 5).get_power()
        30
        """
        return self.red * self.green * self.blue


Challenge.main()
challenge = Challenge()
