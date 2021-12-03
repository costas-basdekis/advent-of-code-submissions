#!/usr/bin/env python3
from dataclasses import dataclass, field
from itertools import combinations_with_replacement
from typing import Dict, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, helper, iterable_length
from year_2021.day_21.part_a import Game


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """"""
        """
        >>> Challenge().default_solve()
        42
        """
        return QuantumGameSearch\
            .from_game_text(_input)\
            .solve(debugger=debugger)\
            .best_player_winning_count


@dataclass
class QuantumDiracDie:
    counts: Dict[int, int]

    @classmethod
    def from_side_count(
        cls, side_count: int = 3, roll_count: int = 3,
    ) -> "QuantumDiracDie":
        rolls = combinations_with_replacement(
            range(1, 1 + side_count), roll_count,
        )
        roll_sums = map(sum, rolls)
        return cls(
            counts=helper.group_by(roll_sums, values_container=iterable_length),
        )

    @property
    def count(self) -> int:
        return sum(self.counts.values())


@dataclass(eq=True, frozen=True)
class ResidualGameState:
    player_1_position: int
    player_2_position: int
    player_1_score: int = 0
    player_2_score: int = 0
    next_player: int = 1
    position_count: int = 10
    winning_score: int = 21

    def __lt__(self, other: "ResidualGameState") -> bool:
        """
        >>> ResidualGameState(0, 0) < ResidualGameState(1, 0)
        True
        >>> ResidualGameState(0, 0) < ResidualGameState(0, 1)
        True
        """
        if self.non_hash != other.non_hash:
            raise Exception(f"Incomparable states: {self} vs {other}")
        return self.hash < other.hash

    @property
    def non_hash(self) -> Tuple[int, int]:
        return self.position_count, self.winning_score

    @property
    def hash(self) -> Tuple[int, int, int, int, int]:
        return (
            self.player_1_score,
            self.player_2_score,
            self.player_1_position,
            self.player_2_position,
            self.next_player,
        )

    def add_roll(self, roll: int) -> "ResidualGameState":
        if self.next_player == 1:
            position = self.player_1_position
            score = self.player_1_score
        elif self.next_player == 2:
            position = self.player_2_position
            score = self.player_2_score
        else:
            raise Exception(f"Unexpected next player: {self.next_player}")
        new_position = (position + roll + 1 - 1) % self.position_count + 1
        new_score = score + new_position
        cls = type(self)
        # noinspection PyArgumentList
        return cls(
            player_1_position=(
                new_position
                if self.next_player == 1 else
                self.player_1_position
            ),
            player_2_position=(
                new_position
                if self.next_player == 2 else
                self.player_2_position
            ),
            player_1_score=(
                new_score
                if self.next_player == 1 else
                self.player_1_score
            ),
            player_2_score=(
                new_score
                if self.next_player == 2 else
                self.player_2_score
            ),
            next_player=(
                2
                if self.next_player == 1 else
                1
            ),
            position_count=self.position_count,
            winning_score=self.winning_score,
        )

    @property
    def finished(self) -> bool:
        return self.player_1_has_won or self.player_2_has_won

    @property
    def player_1_has_won(self) -> bool:
        return self.player_1_score >= self.winning_score

    @property
    def player_2_has_won(self) -> bool:
        return self.player_2_score >= self.winning_score


@dataclass
class QuantumGameSearch:
    residual_state_counts: Dict[ResidualGameState, int]
    player_1_wins: int = 0
    player_2_wins: int = 0
    die: QuantumDiracDie = field(default_factory=QuantumDiracDie)
    move_count: int = 0

    @classmethod
    def from_game_text(cls, game_text: str) -> "QuantumGameSearch":
        player_1_position, player_2_position = \
            Game.get_player_initial_positions_from_game_text(game_text)
        return cls.from_initial_player_positions(
            player_1_position, player_2_position,
        )

    @classmethod
    def from_initial_player_positions(
        cls, player_1_position: int, player_2_position,
    ) -> "QuantumGameSearch":
        die = QuantumDiracDie.from_side_count()
        return cls(
            residual_state_counts={
                ResidualGameState(
                    player_1_position=player_1_position,
                    player_2_position=player_2_position,
                ): 1,
            },
            die=die,
        )

    @property
    def finished(self) -> bool:
        return not self.residual_state_counts

    def solve(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> "QuantumGameSearch":
        while not debugger.step_if(self.finished):
            self.advance_once()
            debugger.default_report_if(
                f"Done {self.move_count} moves, with "
                f"{len(self.residual_state_counts)} remaining states, "
                f"currently {self.player_1_wins} vs {self.player_2_wins}"
            )

        return self

    def advance_once(self) -> "QuantumGameSearch":
        if self.finished:
            return self

        next_state_counts: Dict[ResidualGameState, int] = helper.group_by(
            (
                (state.add_roll(roll), state_count * roll_count)
                for state, state_count in self.residual_state_counts.items()
                for roll, roll_count in self.die.counts.items()
            ),
            key=lambda state_and_count: state_and_count[0],
            value='auto',
            values_container=sum,
        )
        next_move_count = self.move_count + 1
        next_player_1_won_state_count = sum(
            state_count
            for state, state_count in next_state_counts.items()
            if state.player_1_has_won
        )
        next_player_2_won_state_count = sum(
            state_count
            for state, state_count in next_state_counts.items()
            if state.player_2_has_won
        )
        next_residual_state_counts = {
            state: state_count
            for state, state_count in next_state_counts.items()
            if not state.finished
        }

        self.player_1_wins += next_player_1_won_state_count
        self.player_2_wins += next_player_2_won_state_count
        self.move_count = next_move_count
        self.residual_state_counts = next_residual_state_counts

        return self

    @property
    def best_player_winning_count(self) -> int:
        return max(self.player_winning_counts)

    @property
    def player_winning_counts(self) -> Tuple[int, int]:
        """
        >>> QuantumGameSearch\\
        ...     .from_initial_player_positions(4, 8)\\
        ...     .player_winning_counts
        (444356092776315, 341960390180808)
        """
        self.solve()
        return self.player_1_wins, self.player_2_wins
