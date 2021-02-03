#!/usr/bin/env python3
import re

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        32413
        """
        game = Game.from_game_text(_input)
        game.complete()
        return game.get_winner().get_score()


class Game:
    player_class = NotImplemented

    @classmethod
    def from_game_text(cls, game_text):
        """
        >>> Game.from_game_text(
        ...     "Player 1:|9|2|6|3|1\\n\\n"
        ...     "Player 2:|5|8|4|7|10\\n".replace("|", "\\n"))
        Game(players=(Player(id=1, cards=(9, 2, 6, 3, 1)),
            Player(id=2, cards=(5, 8, 4, 7, 10))))
        """
        players_texts = game_text.split("\n\n")
        players = tuple(map(cls.player_class.from_player_text, players_texts))
        if len(players) != 2:
            raise Exception(
                f"Exactly 2 players were expected, not {len(players)}")
        return cls(players)

    def __init__(self, players):
        self.players = players

    def __repr__(self):
        return f"{type(self).__name__}(players={self.players})"

    def complete(self):
        """
        >>> Game(players=(Player(id=1, cards=(9, 2, 6, 3, 1)),
        ...     Player(id=2, cards=(5, 8, 4, 7, 10)))).complete()
        Game(players=(Player(id=1, cards=()),
            Player(id=2, cards=(3, 2, 10, 6, 8, 5, 9, 4, 7, 1))))
        """
        while not self.has_finished():
            self.step()

        return self

    def step(self):
        """
        >>> Game((Player(1, (1, 2, 3)), Player(2, (4, 5, 6)))).step()
        Game(players=(Player(id=1, cards=(2, 3)),
            Player(id=2, cards=(5, 6, 4, 1))))
        >>> Game(players=(Player(id=1, cards=(9, 2, 6, 3, 1)),
        ...     Player(id=2, cards=(5, 8, 4, 7, 10)))).step()
        Game(players=(Player(id=1, cards=(2, 6, 3, 1, 9, 5)),
            Player(id=2, cards=(8, 4, 7, 10))))
        """
        if self.has_finished():
            return self

        next_cards = [
            player.draw_card()
            for player in self.players
        ]
        winner_index = self.determine_step_winner_index(next_cards)
        winner = self.players[winner_index]
        winner.collect_cards(next_cards, winner_index)

        return self

    def determine_step_winner_index(self, next_cards):
        return next_cards.index(max(next_cards))

    def has_finished(self):
        """
        >>> Game((Player(1, (1, 2, 3)), Player(2, (4, 5, 6)))).has_finished()
        False
        >>> Game((Player(1, ()), Player(2, (4, 5, 6)))).has_finished()
        True
        >>> Game((Player(1, (1, 2, 3)), Player(2, ()))).has_finished()
        True
        >>> Game((Player(1, ()), Player(2, ()))).has_finished()
        True
        >>> Game(players=(Player(id=1, cards=()),
        ...     Player(id=2, cards=(3, 2, 10, 6, 8, 5, 9, 4, 7, 1))))\\
        ...     .has_finished()
        True
        """
        return not all(player.cards for player in self.players)

    def get_winner(self):
        """
        >>> Game((Player(1, (1, 2, 3)), Player(2, (4, 5, 6)))).get_winner()
        >>> Game(players=(Player(id=1, cards=()),
        ...     Player(id=2, cards=(3, 2, 10, 6, 8, 5, 9, 4, 7, 1))))\\
        ...     .get_winner()
        Player(id=2, cards=(3, 2, 10, 6, 8, 5, 9, 4, 7, 1))
        """
        if not self.has_finished():
            return None

        winner, = [
            player
            for player in self.players
            if player.cards
        ]

        return winner


class Player:
    re_id = re.compile(r"^Player (\d+):$")

    @classmethod
    def from_player_text(cls, player_text):
        """
        >>> Player.from_player_text("Player 1:|9|2|6|3|1".replace("|", "\\n"))
        Player(id=1, cards=(9, 2, 6, 3, 1))
        """
        id_text, *cards_text = player_text.strip().splitlines()
        id_str, = cls.re_id.match(id_text).groups()
        _id = int(id_str)
        cards = tuple(map(int, cards_text))

        return cls(_id, cards)

    # noinspection PyShadowingBuiltins
    def __init__(self, id, cards):
        self.id = id
        self.cards = cards

    def __repr__(self):
        """
        >>> Player(1, (1, 2, 3))
        Player(id=1, cards=(1, 2, 3))
        """
        return f"{type(self).__name__}(id={self.id}, cards={self.cards})"

    def draw_card(self):
        """
        >>> player_1 = Player(1, (1, 2, 3))
        >>> player_1.draw_card(), player_1
        (1, Player(id=1, cards=(2, 3)))
        """
        card, *rest = self.cards
        self.cards = tuple(rest)

        return card

    def collect_cards(self, cards, winner_index):
        """
        >>> Player(1, (1, 2, 3)).collect_cards((9, 5), 0)
        Player(id=1, cards=(1, 2, 3, 9, 5))
        >>> Player(1, (1, 2, 3)).collect_cards((9, 5), 1)
        Player(id=1, cards=(1, 2, 3, 5, 9))
        """
        self.cards += self.sort_collected_cards(cards, winner_index)

        return self

    def sort_collected_cards(self, cards, winner_index):
        """
        >>> Player(1, ()).sort_collected_cards((9, 5), 0)
        (9, 5)
        >>> Player(1, ()).sort_collected_cards((9, 5), 1)
        (5, 9)
        """
        return (cards[winner_index],) + tuple(
            cards[:winner_index]
            + cards[winner_index + 1:]
        )

    def get_score(self):
        """
        >>> Player(2, cards=(3, 2, 10, 6, 8, 5, 9, 4, 7, 1)).get_score()
        306
        """
        return sum(
            index * card
            for index, card in enumerate(reversed(self.cards), 1)
        )


Game.player_class = Player


Challenge.main()
challenge = Challenge()
