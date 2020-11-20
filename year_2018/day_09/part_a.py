#!/usr/bin/env python3
import doctest
import re
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    436720
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return MarbleGame.from_marble_game_text(_input).get_high_score()


class MarbleGame(namedtuple("MarbleGame", ("player_count", "marble_count"))):
    re_game = re.compile(r"^(\d+) players; last marble is worth (\d+) points$")

    @classmethod
    def from_marble_game_text(cls, marble_game_text):
        """
        >>> MarbleGame.from_marble_game_text(
        ...     "10 players; last marble is worth 1618 points")
        MarbleGame(player_count=10, marble_count=1619)
        """
        player_count_str, max_marble_value_str = \
            cls.re_game.match(marble_game_text).groups()
        player_count = int(player_count_str)
        marble_count = int(max_marble_value_str) + 1
        return cls(player_count, marble_count)

    def get_high_score(self):
        """
        >>> MarbleGame(10, 1619).get_high_score()
        8317
        >>> MarbleGame(13, 8000).get_high_score()
        146373
        >>> MarbleGame(17, 1105).get_high_score()
        2764
        >>> MarbleGame(21, 6112).get_high_score()
        54718
        >>> MarbleGame(30, 5808).get_high_score()
        37305
        """
        scores = [0] * self.player_count
        for step, score in self.get_scores():
            player = step % self.player_count
            scores[player] += score

        return max(scores)

    def get_scores(self):
        for _, _, step, score in self.get_all_steps():
            if score:
                yield step, score

    def play_game(self):
        """
        >>> MarbleGame(9, 1).play_game()
        ((0,), 0, [0, 0, 0, 0, 0, 0, 0, 0, 0])
        >>> MarbleGame(9, 26).play_game()
        ((0, 16, 8, 17, 4, 18, 19, 2, 24, 20, 25, 10, 21, 5, 22, 11, 1, 12, 6, 13, 3, 14, 7, 15), 10, [0, 0, 0, 0, 32, 0, 0, 0, 0])
        >>> MarbleGame(9, 47).play_game()
        ((0, 39, 16, 40, 8, 41, 42, 4, 43, 18, 44, 19, 45, 2, 24, 20, 25, 10, 26, 21, 27, 5, 28, 22, 29, 11, 30, 1, 31, 12, 32, 6, 33, 13, 34, 3, 35, 14, 36, 7, 37, 15, 38), 6, [63, 0, 0, 0, 32, 0, 0, 0, 0])
        >>> max(MarbleGame(10, 1619).play_game()[2])
        8317
        >>> max(MarbleGame(13, 8000).play_game()[2])
        146373
        >>> max(MarbleGame(17, 1105).play_game()[2])
        2764
        >>> max(MarbleGame(21, 6112).play_game()[2])
        54718
        >>> max(MarbleGame(30, 5808).play_game()[2])
        37305
        """
        scores = [0] * self.player_count
        circle = ()
        position = 0
        for circle, position, step, score in self.get_all_steps():
            player = step % self.player_count
            scores[player] += score

        return circle, position, scores

    def get_all_steps(self):
        marbles_left = list(range(self.marble_count))
        circle = (marbles_left.pop(0),)
        position = 0
        step = 0
        yield circle, position, step, 0
        yield from self.exhaust_marbles(circle, position, step, marbles_left)

    def exhaust_marbles(self, circle, position, step, marbles_left):
        while marbles_left:
            marble = marbles_left.pop(0)
            circle, position, removed_marbles = \
                self.do_step(circle, position, marble)
            yield circle, position, step, sum(removed_marbles)
            step += 1

    def do_step(self, circle, position, marble):
        if marble % 23 == 0:
            circle, position, removed_marbles =\
                self.remove_marbles(circle, position, marble)
        else:
            circle, position = self.insert_marble(circle, position, marble)
            removed_marbles = ()

        return circle, position, removed_marbles

    def remove_marbles(self, circle, position, marble):
        """
        >>> MarbleGame(1, 1).remove_marbles(
        ...     (0, 16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12,
        ...      6, 13, 3, 14, 7, 15), 13, 23)
        ((0, 16, 8, 17, 4, 18, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12, 6, 13, 3, 14, 7, 15), 6, (23, 9))
        >>> MarbleGame(1, 1).remove_marbles(
        ...     (0, 16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12,
        ...      6, 13, 3, 14, 7, 15), 7, 23)
        ((16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12, 6, 13, 3, 14, 7, 15), 0, (23, 0))
        >>> MarbleGame(1, 1).remove_marbles(
        ...     (0, 16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12,
        ...      6, 13, 3, 14, 7, 15), 6, 23)
        ((0, 16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12, 6, 13, 3, 14, 7), 0, (23, 15))
        >>> MarbleGame(1, 1).remove_marbles(
        ...     (0, 16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 12,
        ...      6, 13, 3, 14, 7, 15), 0, 23)
        ((0, 16, 8, 17, 4, 18, 9, 19, 2, 20, 10, 21, 5, 22, 11, 1, 6, 13, 3, 14, 7, 15), 16, (23, 12))
        """
        position = (position - 7 + len(circle)) % len(circle)
        removed_marble = circle[position]
        circle = circle[:position] + circle[position + 1:]
        position = position % len(circle)

        return circle, position, (marble, removed_marble)

    def insert_marble(self, circle, position, marble):
        """
        >>> MarbleGame(1, 1).insert_marble((0,), 0, 1)
        ((0, 1), 1)
        >>> MarbleGame(1, 1).insert_marble((0, 1), 1, 2)
        ((0, 2, 1), 1)
        >>> MarbleGame(1, 1).insert_marble((0, 2, 1), 1, 3)
        ((0, 2, 1, 3), 3)
        >>> MarbleGame(1, 1).insert_marble((0, 2, 1, 3), 3, 4)
        ((0, 4, 2, 1, 3), 1)
        >>> MarbleGame(1, 1).insert_marble((0, 4, 2, 1, 3), 1, 5)
        ((0, 4, 2, 5, 1, 3), 3)
        >>> MarbleGame(1, 1).insert_marble((0, 4, 2, 5, 1, 3), 3, 6)
        ((0, 4, 2, 5, 1, 6, 3), 5)
        >>> MarbleGame(1, 1).insert_marble((0, 4, 2, 5, 1, 6, 3), 5, 7)
        ((0, 4, 2, 5, 1, 6, 3, 7), 7)
        >>> MarbleGame(1, 1).insert_marble((0, 4, 2, 5, 1, 6, 3, 7), 7, 8)
        ((0, 8, 4, 2, 5, 1, 6, 3, 7), 1)
        """
        position = (position + 1) % len(circle) + 1
        circle = circle[:position] + (marble,) + circle[position:]

        return circle, position


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
