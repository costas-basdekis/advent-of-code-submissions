#!/usr/bin/env python3
import utils

from year_2018.day_09 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3527845091
        """
        game = part_a.MarbleGame.from_marble_game_text(_input)
        # noinspection PyProtectedMember
        game = game._replace(marble_count=game.marble_count * 100)
        _, _, scores = game.play_game()

        return max(scores)


class MarbleGameExtended(part_a.MarbleGame):
    """
    >>> MarbleGameExtended(9, 26).play_game() \\
    ...     == part_a.MarbleGame(9, 26).play_game()
    True
    >>> MarbleGameExtended(9, 47).play_game() \\
    ...     == part_a.MarbleGame(9, 47).play_game()
    True
    >>> max(MarbleGameExtended(10, 1619).play_game()[2]) \\
    ...     == max(part_a.MarbleGame(10, 1619).play_game()[2])
    True
    >>> max(MarbleGameExtended(10, 8000).play_game()[2]) \\
    ...     == max(part_a.MarbleGame(10, 8000).play_game()[2])
    True
    >>> max(MarbleGameExtended(10, 1105).play_game()[2]) \\
    ...     == max(part_a.MarbleGame(10, 1105).play_game()[2])
    True
    >>> max(MarbleGameExtended(10, 6112).play_game()[2]) \\
    ...     == max(part_a.MarbleGame(10, 6112).play_game()[2])
    True
    >>> max(MarbleGameExtended(10, 5808).play_game()[2]) \\
    ...     == max(part_a.MarbleGame(10, 5808).play_game()[2])
    True
    """

    PRE_FIRST_22_ITERATION, PRE_FIRST_22_POSITION, _ = \
        part_a.MarbleGame(9, 1).play_game()
    FIRST_22_ITERATION, _, _ = part_a.MarbleGame(9, 23).play_game()
    PRE_SECOND_22_ITERATION, PRE_SECOND_22_POSITION, _ = \
        part_a.MarbleGame(9, 24).play_game()
    SECOND_22_ITERATION, _, _ = part_a.MarbleGame(9, 46).play_game()

    def get_all_steps(self):
        marbles_left = list(range(self.marble_count))
        circle = (marbles_left.pop(0),)
        position = 0
        step = 0
        while len(marbles_left) >= 23:
            marbles_left = marbles_left[23:]
            circle, position, removed_marbles = \
                self.do_next_23_iterations(circle, position)
            step += 22
            yield circle, position, step, sum(removed_marbles)
            step += 1
        if len(marbles_left) >= 22:
            marbles_left = marbles_left[22:]
            circle, position = self.do_next_22_iterations(circle, position)
            removed_marbles = ()
            step += 21
            yield circle, position, step, sum(removed_marbles)
            step += 1
        yield from self.exhaust_marbles(circle, position, step, marbles_left)

    def do_next_23_iterations(self, circle, position):
        """
        >>> MarbleGameExtended(1, 1).do_next_23_iterations(
        ...     *part_a.MarbleGame(9, 1).play_game()[:2])[:2] \\
        ...     == part_a.MarbleGame(9, 24).play_game()[:2]
        True
        """
        circle, position = self.do_next_22_iterations(circle, position)
        marble = max(circle) + 1
        return self.do_step(circle, position, marble)

    def do_next_22_iterations(self, circle, position):
        """
        >>> [
        ...     count
        ...     for count in range(1, 1619, 23)
        ...     if MarbleGameExtended(9, 1000).do_next_22_iterations(
        ...         *part_a.MarbleGame(9, count).play_game()[:2])
        ...     != part_a.MarbleGame(9, count + 22).play_game()[:2]
        ... ]
        []
        """
        if circle == self.PRE_FIRST_22_ITERATION\
                and position == self.PRE_FIRST_22_POSITION:
            circle = self.FIRST_22_ITERATION
            position = circle.index(max(circle))
            return circle, position

        if circle == self.PRE_SECOND_22_ITERATION\
                and position == self.PRE_SECOND_22_POSITION:
            circle = self.SECOND_22_ITERATION
            position = circle.index(max(circle))
            return circle, position

        if (len(circle) - 1) % 21 != 0:
            raise Exception(
                f"Expected a circle with length a multiple of 21 + 1 but got "
                f"{len(circle)}")
        marble = ((len(circle) - 1) // 21) * 23 + 1
        marbles = list(range(marble, marble + 22))
        if position + 1 + 22 < len(circle):
            circle = circle[:position + 1] + tuple(
                item
                for pair in zip(circle[position + 1:], marbles)
                for item in pair
            ) + circle[position + 22 + 1:]
            position += 22 * 2
        else:
            marble_count_in_front = position + 1 + 22 - len(circle)
            marbles_in_front = marbles[-marble_count_in_front:]
            circle = circle[:position + 1] + tuple(
                item
                for pair in zip(circle[position + 1:], marbles)
                for item in pair
            ) + circle[position + 22 + 1:]
            circle = tuple(
                item
                for pair in zip(circle, marbles_in_front)
                for item in pair
            ) + circle[marble_count_in_front:]
            position = marble_count_in_front * 2 - 1

        return circle, position


Challenge.main()
challenge = Challenge()
