#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from typing import Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1002474
        """
        return Game.from_game_text(_input).play_all_rounds().game_hash


@dataclass
class DiracDie:
    side_count: int = 100
    next_number: int = 1
    roll_count: int = 0

    def roll(self) -> int:
        number = self.next_number
        self.next_number += 1
        self.next_number = (self.next_number - 1) % self.side_count + 1
        self.roll_count += 1
        return number

    def roll_many(self, count: int) -> Tuple[int, ...]:
        """
        >>> die = DiracDie(side_count=3)
        >>> die.roll_many(7)
        (1, 2, 3, 1, 2, 3, 1)
        >>> die
        DiracDie(side_count=3, next_number=2, roll_count=7)
        """
        rolls = []
        for _ in range(count):
            rolls.append(self.roll())

        return tuple(rolls)


@dataclass
class Game:
    player_1_position: int
    player_2_position: int
    player_1_score: int = 0
    player_2_score: int = 0
    next_player: int = 1
    position_count: int = 10
    winning_score: int = 1000
    die_roll_count: int = 3
    die: DiracDie = field(default_factory=DiracDie)

    re_player = re.compile(r"^Player ([12]) starting position: (\d+)$")

    @classmethod
    def from_game_text(cls, game_text: str, **kwargs) -> "Game":
        """
        >>> Game.from_game_text('''
        ...     Player 1 starting position: 5
        ...     Player 2 starting position: 6
        ... ''')
        Game(player_1_position=5, player_2_position=6, ...)
        """
        player_1_position, player_2_position = \
            cls.get_player_initial_positions_from_game_text(game_text)
        return cls(
            player_1_position=player_1_position,
            player_2_position=player_2_position,
            **kwargs,
        )

    @classmethod
    def get_player_initial_positions_from_game_text(
        cls, game_text: str,
    ) -> Tuple[int, int]:
        players_lines = filter(None, map(str.strip, game_text.splitlines()))
        (
            (player_a_name_str, player_a_position),
            (player_b_name_str, player_b_position)
        ) = (cls.re_player.match(line).groups() for line in players_lines)
        if player_a_name_str == "1":
            player_positions_str = player_a_position, player_b_position
        else:
            player_positions_str = player_b_position, player_a_position
        player_1_position, player_2_position = map(int, player_positions_str)

        return player_1_position, player_2_position

    @property
    def finished(self) -> bool:
        return self.winner is not None

    @property
    def winner(self) -> Optional[int]:
        if self.player_1_score >= self.winning_score:
            return 1
        if self.player_2_score >= self.winning_score:
            return 2
        else:
            return None

    def play_all_rounds(self) -> "Game":
        """
        >>> Game(4, 8).play_all_rounds()
        Game(player_1_position=10, player_2_position=3, player_1_score=1000,
            player_2_score=745, next_player=2, position_count=10,
            winning_score=1000, die_roll_count=3,
            die=DiracDie(side_count=100, next_number=94, roll_count=993))
        """
        while not self.finished:
            self.play_round()

        return self

    @property
    def game_hash(self) -> int:
        """
        >>> Game(4, 8).play_all_rounds().game_hash
        739785
        """
        if self.player_1_score >= self.player_2_score:
            losing_player_score = self.player_2_score
        else:
            losing_player_score = self.player_1_score
        return losing_player_score * self.die.roll_count

    def play_round(self) -> "Game":
        if self.finished:
            return self

        rolls = self.die.roll_many(self.die_roll_count)
        moves = sum(rolls)
        if self.next_player == 1:
            player_position = self.player_1_position
        elif self.next_player == 2:
            player_position = self.player_2_position
        else:
            raise Exception(f"Unexpected next player {self.next_player}")
        player_position += moves
        player_position = (player_position - 1) % self.position_count + 1
        if self.next_player == 1:
            self.player_1_position = player_position
            self.player_1_score += player_position
            self.next_player = 2
        elif self.next_player == 2:
            self.player_2_position = player_position
            self.player_2_score += player_position
            self.next_player = 1
        else:
            raise Exception(f"Unexpected next player {self.next_player}")


Challenge.main()
challenge = Challenge()
