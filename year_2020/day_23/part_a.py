#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        '94238657'
        """
        return Game.from_game_text(_input).step_many(100).get_order_hash()


class Game:
    @classmethod
    def from_game_text(cls, game_text):
        """
        >>> Game.from_game_text("32415")
        Game(cups=(3, 2, 4, 1, 5))
        """
        return cls(tuple(map(int, game_text.strip())))

    def __init__(self, cups):
        self.cups = cups

    def __repr__(self):
        return f"{type(self).__name__}(cups={self.cups})"

    def get_order_hash(self):
        """
        >>> Game((3, 8, 9, 1, 2, 5, 4, 6, 7)).step_many(100).get_order_hash()
        '67384529'
        """
        cup_1_index = self.cups.index(1)
        cups_in_order = self.cups[cup_1_index + 1:] + self.cups[:cup_1_index]
        return "".join(map(str, cups_in_order))

    def step_many(self, count):
        """
        >>> Game((3, 8, 9, 1, 2, 5, 4, 6, 7)).step_many(10)
        Game(cups=(8, 3, 7, 4, 1, 9, 2, 6, 5))
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> Game((3, 8, 9, 1, 2, 5, 4, 6, 7)).step()
        Game(cups=(2, 8, 9, 1, 5, 4, 6, 7, 3))
        >>> Game((2, 8, 9, 1, 5, 4, 6, 7, 3)).step()
        Game(cups=(5, 4, 6, 7, 8, 9, 1, 3, 2))
        """
        current_cup = self.cups[0]
        picked_cups, destination_cup = \
            self.select_picked_and_destination_cups()
        cups = tuple(cup for cup in self.cups if cup not in picked_cups)
        destination_index = cups.index(destination_cup)
        cups = (
            cups[:destination_index + 1]
            + picked_cups
            + cups[destination_index + 1:]
        )
        updated_current_index = cups.index(current_cup)
        current_index = updated_current_index + 1
        if current_index == len(self.cups):
            current_index = 0
        self.cups = cups[current_index:] + cups[:current_index]

        return self

    def select_picked_and_destination_cups(self):
        """
        >>> Game((3, 8, 9, 1, 2, 5, 4, 6, 7))\\
        ...     .select_picked_and_destination_cups()
        ((8, 9, 1), 2)
        >>> Game((2, 8, 9, 1, 5, 4, 6, 7, 3))\\
        ...     .select_picked_and_destination_cups()
        ((8, 9, 1), 7)
        """
        picked_cups = (self.cups * 2)[1:4]
        for offset in range(4):
            destination_cup = (
                self.cups[0]
                - 1 - offset + len(self.cups) - 1
            ) % len(self.cups) + 1
            if destination_cup not in picked_cups:
                break
        else:
            raise Exception(f"Could not find a destination cup")

        return picked_cups, destination_cup


Challenge.main()
challenge = Challenge()
