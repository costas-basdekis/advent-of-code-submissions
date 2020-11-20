#!/usr/bin/env python3
import utils
from year_2020.day_22 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        31596
        """
        game = RecursiveGame.from_game_text(_input)
        game.complete()
        return game.get_winner().get_score()


class RecursiveGame(part_a.Game):
    """
    >>> RecursiveGame.from_game_text(
    ...     "Player 1:|9|2|6|3|1\\n\\n"
    ...     "Player 2:|5|8|4|7|10\\n".replace("|", "\\n"))
    RecursiveGame(players=(RecursivePlayer(id=1, cards=(9, 2, 6, 3, 1)),
        RecursivePlayer(id=2, cards=(5, 8, 4, 7, 10))))
    """

    def __init__(self, players):
        super().__init__(players)
        self.previous_configurations = set()

    def get_configuration_key(self):
        """
        >>> RecursiveGame(players=(
        ...     RecursivePlayer(id=1, cards=(9, 2, 6, 3, 1)),
        ...     RecursivePlayer(id=2, cards=(5, 8, 4, 7, 10)),
        ... )).get_configuration_key()
        ((9, 2, 6, 3, 1), (5, 8, 4, 7, 10))
        """
        return tuple(
            player.cards
            for player in self.players
        )

    def step(self):
        """
        >>> RecursiveGame(players=(
        ...     RecursivePlayer(id=1, cards=(9, 2, 6, 3, 1)),
        ...     RecursivePlayer(id=2, cards=(5, 8, 4, 7, 10)),
        ... )).complete().get_winner()
        RecursivePlayer(id=2, cards=(7, 5, 6, 2, 4, 1, 10, 8, 9, 3))
        """
        configuration = self.get_configuration_key()
        super().step()
        self.previous_configurations.add(configuration)

    def determine_step_winner_index(self, next_cards):
        all_players_have_enough_cards = all(
            len(player.cards) >= card
            for player, card in zip(self.players, next_cards)
        )
        if not all_players_have_enough_cards:
            return super().determine_step_winner_index(next_cards)

        cls = type(self)
        sub_game = cls(tuple(
            cls.player_class(player.id, player.cards[:card])
            for player, card in zip(self.players, next_cards)
        ))

        sub_game.complete()
        return sub_game.get_winner_index()

    def has_finished(self):
        return (
            super().has_finished()
            or self.has_game_repeated()
        )

    def has_game_repeated(self):
        return self.get_configuration_key() in self.previous_configurations

    def get_winner(self):
        if self.has_game_repeated():
            return self.players[0]

        return super().get_winner()

    def get_winner_index(self):
        winner = self.get_winner()
        if not winner:
            return None

        return self.players.index(winner)


class RecursivePlayer(part_a.Player):
    pass


RecursiveGame.player_class = RecursivePlayer


challenge = Challenge()
challenge.main()
