#!/usr/bin/env python3
import itertools
import string

import click

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        220480
        """
        cave = Cave.from_cave_text(_input)
        cave.tick_many(debug=debug)
        return cave.get_outcome()

    def play(self):
        cave = Cave.from_cave_text(self.input)
        snapshots = [cave.show(show_health=True, add_stats=True)]
        while not cave.has_finished():
            cave.tick()
            snapshots.append(cave.show(show_health=True, add_stats=True))

        index = 0
        while True:
            print(snapshots[index])
            click.echo(
                f"At step {index}/{len(snapshots) - 1}: left for previous, "
                f"right for next, q to quit")
            user_input = click.getchar()
            while user_input not in ('q', '\x1b[D', '\x1b[C'):
                click.echo(
                    "Invalid command: left for previous, right for next, q to "
                    "quit")
                user_input = click.getchar()
            if user_input == 'q':
                break
            if user_input == '\x1b[D':
                index = max(0, index - 1)
            else:
                index = min(len(snapshots) - 1, index + 1)


class Cave:
    @classmethod
    def from_cave_text(cls, cave_text):
        """
        >>> Cave.from_cave_text(
        ...     "#####\\n"
        ...     "#.GE#\\n"
        ...     "#####\\n"
        ... )
        Cave(spaces=((False, False, False, False, False),
            (False, True, True, True, False),
                (False, False, False, False, False)),
            units=(Goblin(position=(2, 1), attack=3, health=200),
                Elf(position=(3, 1), attack=3, health=200)))
        """
        lines = list(filter(None, cave_text.splitlines()))
        spaces = tuple(
            tuple(
                spot in ('.', 'G', 'E')
                for spot in line
            )
            for line in lines
        )
        units = tuple(sorted(
            Goblin((x, y))
            if spot == 'G' else
            Elf((x, y))
            for y, line in enumerate(lines)
            for x, spot in enumerate(line)
            if spot in ('G', 'E')
        ))

        return cls(spaces, units)

    @classmethod
    def parse_distances(cls, distances_text):
        """
        >>> dict(sorted(Cave.parse_distances(
        ...     "#########\\n"
        ...     "#.G1012G#\\n"
        ...     "#.32123.#\\n"
        ...     "#..323..#\\n"
        ...     "#G..3..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).items()))
        {(2, 2): 3, (3, 1): 1, (3, 2): 2, (3, 3): 3, (4, 1): 0, (4, 2): 1, \
(4, 3): 2, (4, 4): 3, (5, 1): 1, (5, 2): 2, (5, 3): 3, (6, 1): 2, (6, 2): 3}
        """
        lines = list(filter(None, distances_text.splitlines()))
        distance_digits = set(string.hexdigits) - set(string.ascii_uppercase)
        return {
            (x, y): int(spot)
            for y, line in enumerate(lines)
            for x, spot in enumerate(line)
            if spot in distance_digits
        }

    def __init__(self, spaces, units, step_count=0):
        self.spaces = spaces
        self.units = units
        self.step_count = step_count

    def __repr__(self):
        return f"{type(self).__name__}" \
               f"(spaces={repr(self.spaces)}, " \
               f"units={repr(self.units)})"

    @classmethod
    def sort_key_health_reading_order(cls, unit):
        return unit.health, cls.sort_key_reading_order_position(unit.position)

    @classmethod
    def sort_key_reading_order(cls, unit):
        return cls.sort_key_reading_order_position(unit.position)

    @classmethod
    def sort_key_reading_order_position(cls, position):
        x, y = position
        return y, x

    def get_outcome(self, allow_provisional=False):
        """
        >>> Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G.....G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).get_outcome()
        0
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_outcome()
        27730
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#G..#E#\\n"
        ...     "#E#E.E#\\n"
        ...     "#G.##.#\\n"
        ...     "#...#E#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_outcome()
        36334
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#E..EG#\\n"
        ...     "#.#G.E#\\n"
        ...     "#E.##E#\\n"
        ...     "#G..#.#\\n"
        ...     "#..E#.#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_outcome()
        39514
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#E.G#.#\\n"
        ...     "#.#G..#\\n"
        ...     "#G.#.G#\\n"
        ...     "#G..#.#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_outcome()
        27755
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.E...#\\n"
        ...     "#.#..G#\\n"
        ...     "#.###.#\\n"
        ...     "#E#G#G#\\n"
        ...     "#...#G#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_outcome()
        28944
        >>> Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G......#\\n"
        ...     "#.E.#...#\\n"
        ...     "#..##..G#\\n"
        ...     "#...##..#\\n"
        ...     "#...#...#\\n"
        ...     "#.G...G.#\\n"
        ...     "#.....G.#\\n"
        ...     "#########\\n"
        ... ).tick_many().get_outcome()
        18740
        """
        if not allow_provisional and not self.has_finished():
            raise Exception("Cave has not finished yet")
        return self.get_total_health() * self.step_count

    def get_total_health(self):
        """
        >>> Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).get_total_health()
        1800
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#G..#E#\\n"
        ...     "#E#E.E#\\n"
        ...     "#G.##.#\\n"
        ...     "#...#E#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_total_health()
        982
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#E..EG#\\n"
        ...     "#.#G.E#\\n"
        ...     "#E.##E#\\n"
        ...     "#G..#.#\\n"
        ...     "#..E#.#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_total_health()
        859
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#E.G#.#\\n"
        ...     "#.#G..#\\n"
        ...     "#G.#.G#\\n"
        ...     "#G..#.#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_total_health()
        793
        >>> Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.E...#\\n"
        ...     "#.#..G#\\n"
        ...     "#.###.#\\n"
        ...     "#E#G#G#\\n"
        ...     "#...#G#\\n"
        ...     "#######\\n"
        ... ).tick_many().get_total_health()
        536
        >>> Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G......#\\n"
        ...     "#.E.#...#\\n"
        ...     "#..##..G#\\n"
        ...     "#...##..#\\n"
        ...     "#...#...#\\n"
        ...     "#.G...G.#\\n"
        ...     "#.....G.#\\n"
        ...     "#########\\n"
        ... ).tick_many().get_total_health()
        937
        """
        return sum(
            unit.health
            for unit in self.units
        )

    def tick_many(self, count=None, debug=False):
        """
        >>> print(Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).tick_many(3).show())
        #########
        #.......#
        #..GGG..#
        #..GEG..#
        #G..G...#
        #......G#
        #.......#
        #.......#
        #########
        >>> print(Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).tick_many().show())
        #########
        #.......#
        #..GGG..#
        #..G.G..#
        #G..G...#
        #......G#
        #.......#
        #.......#
        #########
        >>> cave_a = Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.G...#\\n"
        ...     "#...EG#\\n"
        ...     "#.#.#G#\\n"
        ...     "#..G#E#\\n"
        ...     "#.....#\\n"
        ...     "#######\\n"
        ... )
        >>> print(cave_a.tick_many(1).show(show_health=True))
        #######
        #..G..#   G(200)
        #...EG#   E(197), G(197)
        #.#G#G#   G(200), G(197)
        #...#E#   E(197)
        #.....#
        #######
        >>> print(cave_a.tick_many(1).show(show_health=True))
        #######
        #...G.#   G(200)
        #..GEG#   G(200), E(188), G(194)
        #.#.#G#   G(194)
        #...#E#   E(194)
        #.....#
        #######
        >>> print(cave_a.tick_many(1).show(show_health=True))
        #######
        #...G.#   G(200)
        #..GEG#   G(200), E(179), G(191)
        #.#.#G#   G(191)
        #...#E#   E(191)
        #.....#
        #######
        >>> print(cave_a.tick_many(20).show())
        #######
        #...G.#
        #..G.G#
        #.#.#G#
        #...#E#
        #.....#
        #######
        >>> print(cave_a.tick_many().show())
        #######
        #G....#
        #.G...#
        #.#.#G#
        #...#.#
        #....G#
        #######
        >>> print(Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#G..#E#\\n"
        ...     "#E#E.E#\\n"
        ...     "#G.##.#\\n"
        ...     "#...#E#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).tick_many().show(show_health=True))
        #######
        #...#E#   E(200)
        #E#...#   E(197)
        #.E##.#   E(185)
        #E..#E#   E(200), E(200)
        #.....#
        #######
        >>> print(Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#E..EG#\\n"
        ...     "#.#G.E#\\n"
        ...     "#E.##E#\\n"
        ...     "#G..#.#\\n"
        ...     "#..E#.#\\n"
        ...     "#######\\n"
        ... ).tick_many().show(show_health=True))
        #######
        #.E.E.#   E(164), E(197)
        #.#E..#   E(200)
        #E.##.#   E(98)
        #.E.#.#   E(200)
        #...#.#
        #######
        >>> print(Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#E.G#.#\\n"
        ...     "#.#G..#\\n"
        ...     "#G.#.G#\\n"
        ...     "#G..#.#\\n"
        ...     "#...E.#\\n"
        ...     "#######\\n"
        ... ).tick_many().show(show_health=True))
        #######
        #G.G#.#   G(200), G(98)
        #.#G..#   G(200)
        #..#..#
        #...#G#   G(95)
        #...G.#   G(200)
        #######
        >>> print(Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.E...#\\n"
        ...     "#.#..G#\\n"
        ...     "#.###.#\\n"
        ...     "#E#G#G#\\n"
        ...     "#...#G#\\n"
        ...     "#######\\n"
        ... ).tick_many().show(show_health=True))
        #######
        #.....#
        #.#G..#   G(200)
        #.###.#
        #.#.#.#
        #G.G#G#   G(98), G(38), G(200)
        #######
        >>> print(Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G......#\\n"
        ...     "#.E.#...#\\n"
        ...     "#..##..G#\\n"
        ...     "#...##..#\\n"
        ...     "#...#...#\\n"
        ...     "#.G...G.#\\n"
        ...     "#.....G.#\\n"
        ...     "#########\\n"
        ... ).tick_many().show(show_health=True))
        #########
        #.G.....#   G(137)
        #G.G#...#   G(200), G(200)
        #.G##...#   G(200)
        #...##..#
        #.G.#...#   G(200)
        #.......#
        #.......#
        #########
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        for _ in steps:
            if self.has_finished():
                break
            self.tick(debug=debug)

        return self

    def tick(self, debug=False):
        """
        >>> cave_a = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> move_order_a = cave_a.get_move_order()
        >>> units_by_position_a = cave_a.get_units_by_position()
        >>> move_order_a[0].tick(cave_a.spaces, units_by_position_a)
        False
        >>> print(cave_a.show())
        #########
        #.G.G..G#
        #.......#
        #.......#
        #G..E..G#
        #.......#
        #.......#
        #G..G..G#
        #########
        >>> move_order_a[1].tick(cave_a.spaces, units_by_position_a)
        False
        >>> print(cave_a.show())
        #########
        #.G....G#
        #...G...#
        #.......#
        #G..E..G#
        #.......#
        #.......#
        #G..G..G#
        #########
        >>> print(Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).tick().show())
        #########
        #.G...G.#
        #...G...#
        #...E..G#
        #.G.....#
        #.......#
        #G..G..G#
        #.......#
        #########
        """
        if self.has_finished():
            return self

        units_by_position = self.get_units_by_position()
        move_order = self.get_move_order()
        finished = False
        if debug:
            print(self.step_count, len(move_order), ":", end="", flush=True)
        for unit in move_order:
            if debug:
                print(f"{move_order.index(unit)}, ", end="", flush=True)
            if unit.is_dead():
                continue
            finished = unit.tick(
                self.spaces, units_by_position, debug=False)
            if finished:
                break
        else:
            self.step_count += 1
        if debug:
            print("done")

        self.units = [unit for unit in self.units if unit.is_alive()]
        if finished and not self.has_finished():
            raise Exception(
                "A unit reported that the game has finished, but there are "
                "many unit types")

        return self

    def has_finished(self):
        """
        >>> Cave((), []).has_finished()
        True
        >>> Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).has_finished()
        False
        >>> Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G.....G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).has_finished()
        True
        """
        return len(set(map(type, self.units))) <= 1

    def get_units_by_position(self):
        return {
            unit.position: unit
            for unit in self.units
        }

    def get_move_order(self):
        """
        >>> [unit.position for unit in Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.G.E.#\\n"
        ...     "#E.G.E#\\n"
        ...     "#.G.E.#\\n"
        ...     "#######\\n"
        ... ).get_move_order()]
        [(2, 1), (4, 1), (1, 2), (3, 2), (5, 2), (2, 3), (4, 3)]
        >>> [unit.position for unit in Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ).get_move_order()]
        [(1, 1), (4, 1), (7, 1), (1, 4), (4, 4), (7, 4), (1, 7), (4, 7), (7, 7)]
        """
        return sorted(self.units, key=self.unit_sort_key_reading_order)

    def unit_sort_key_reading_order(self, unit):
        return self.position_sort_key_reading_order(unit.position)

    def position_sort_key_reading_order(self, position):
        x, y = position
        return y, x

    def show(self, distances=None, show_health=False, add_stats=False):
        """
        >>> print(Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.G.E.#\\n"
        ...     "#E.G.E#\\n"
        ...     "#.G.E.#\\n"
        ...     "#######\\n"
        ... ).show())
        #######
        #.G.E.#
        #E.G.E#
        #.G.E.#
        #######
        >>> print(Cave.from_cave_text(
        ...     "#######\\n"
        ...     "#.G.E.#\\n"
        ...     "#E.G.E#\\n"
        ...     "#.G.E.#\\n"
        ...     "#######\\n"
        ... ).show(show_health=True, add_stats=True))
        #######
        #.G.E.#   G(200), E(200)
        #E.G.E#   E(200), G(200), E(200)
        #.G.E.#   G(200), E(200)
        #######
        Step: 0, health: 1400, outcome: 0
        """
        units_by_position = self.get_units_by_position()
        shown = "\n".join(
            self.show_line(y, line, units_by_position, distances, show_health)
            for y, line in enumerate(self.spaces)
        )
        if add_stats:
            shown += (
                f"\nStep: {self.step_count}, "
                f"health: {self.get_total_health()}, "
                f"outcome: {self.get_outcome(allow_provisional=True)}"
            )

        return shown

    def show_line(self, y, line, units_by_position, distances, show_health):
        line_str = "".join(
            str(distances[(x, y)])
            if distances and (x, y) in distances else
            "#"
            if not space else
            "."
            if (x, y) not in units_by_position else
            units_by_position[(x, y)].show()
            for x, space in enumerate(line)
        )
        if show_health:
            line_str += "   {}".format(", ".join(
                units_by_position[(x, y)].show(show_health=True)
                for x in range(len(line))
                if (x, y) in units_by_position
            )).rstrip()

        return line_str


class Unit:
    show_symbol = NotImplemented

    def __init__(self, position, attack=3, health=200):
        self.position = position
        self.attack = attack
        self.health = health
        self.cached_distances = None
        self.cached_distances_key = None

    def __repr__(self):
        return f"{type(self).__name__}" \
               f"(position={self.position}, " \
               f"attack={self.attack}, " \
               f"health={self.health})"

    def __lt__(self, other):
        return self.position < other.position

    def is_alive(self):
        """
        >>> Elf((0, 0)).is_alive()
        True
        >>> Elf((0, 0), health=1).is_alive()
        True
        >>> Elf((0, 0), health=0).is_alive()
        False
        >>> Elf((0, 0), health=-1).is_alive()
        False
        """
        return self.health > 0

    def is_dead(self):
        """
        >>> Elf((0, 0)).is_dead()
        False
        >>> Elf((0, 0), health=1).is_dead()
        False
        >>> Elf((0, 0), health=0).is_dead()
        True
        >>> Elf((0, 0), health=-1).is_dead()
        True
        """
        return not self.is_alive()

    def tick(self, spaces, units_by_position, debug=False):
        """
        >>> cave_a = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_a = cave_a.get_units_by_position()
        >>> cave_a.units[0].tick(cave_a.spaces, units_by_position_a)
        False
        >>> print(cave_a.show())
        #########
        #.G.G..G#
        #.......#
        #.......#
        #G..E..G#
        #.......#
        #.......#
        #G..G..G#
        #########
        >>> cave_b = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#.G.G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_b = cave_b.get_units_by_position()
        >>> units_by_position_b[(4, 1)].tick(cave_b.spaces, units_by_position_b)
        False
        >>> print(cave_b.show())
        #########
        #.G....G#
        #...G...#
        #.......#
        #G..E..G#
        #.......#
        #.......#
        #G..G..G#
        #########
        >>> cave_c = Cave.from_cave_text(
        ...     "G.E\\n"
        ... )
        >>> units_by_position_c = cave_c.get_units_by_position()
        >>> unit_c = units_by_position_c[(0, 0)]
        >>> unit_c.get_enemies(units_by_position_c)
        [Elf(position=(2, 0), attack=3, health=200)]
        >>> unit_c.tick(cave_c.spaces, units_by_position_c)
        False
        >>> print(cave_c.show(show_health=True))
        .GE   G(200), E(197)
        """
        enemies = self.get_enemies(units_by_position)
        if not enemies:
            return True
        next_position, closest_enemy = self.get_next_step_to_closest_enemy(
            spaces, enemies, units_by_position, debug=debug)
        if not next_position:
            return False
        if next_position != self.position:
            self.move(next_position, units_by_position, spaces=spaces)
            next_position, closest_enemy = self.get_next_step_to_closest_enemy(
                spaces, enemies, units_by_position, debug=debug)
        if next_position == self.position:
            self.attack_enemy(closest_enemy, units_by_position)

        return False

    def get_next_step_to_closest_enemy(self, spaces, enemies,
                                       units_by_position, debug=False):
        """
        >>> cave_a = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_a = cave_a.get_units_by_position()
        >>> enemies_a = [unit for unit in cave_a.units if isinstance(unit, Elf)]
        >>> cave_a.units[0].get_next_step_to_closest_enemy(
        ...     cave_a.spaces, enemies_a, units_by_position_a)
        ((2, 1), Elf(position=(4, 4), attack=3, health=200))
        >>> cave_b = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#GE.G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_b = cave_b.get_units_by_position()
        >>> enemies_b = [unit for unit in cave_b.units if isinstance(unit, Elf)]
        >>> cave_b.units[0].get_next_step_to_closest_enemy(
        ...     cave_b.spaces, enemies_b, units_by_position_b)
        ((1, 1), Elf(position=(2, 1), attack=3, health=200))
        """
        distances = self.get_distances(spaces, enemies, units_by_position)
        closest_enemy = self.get_closest_enemy(enemies, distances)
        if not closest_enemy:
            return None, None
        next_step = self.get_next_step(
            distances, closest_enemy.position, debug=debug)

        return next_step, closest_enemy

    def get_next_step(self, distances, target, debug=False):
        """
        >>> Goblin((1, 1)).get_next_step(Cave.parse_distances(
        ...     "#########\\n"
        ...     "#012G6.G#\\n"
        ...     "#123456.#\\n"
        ...     "#23456..#\\n"
        ...     "#G456..G#\\n"
        ...     "#656....#\\n"
        ...     "#.6.....#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ), (4, 4))
        (2, 1)
        >>> Goblin((1, 1)).get_next_step(Cave.parse_distances(
        ...     "#########\\n"
        ...     "#01.G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ), (2, 1))
        (1, 1)
        >>> Goblin((4, 1)).get_next_step(Cave.parse_distances(
        ...     "#########\\n"
        ...     "#.G1012G#\\n"
        ...     "#.32123.#\\n"
        ...     "#..323..#\\n"
        ...     "#G..3..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ), (4, 4))
        (4, 2)
        >>> Goblin((4, 1)).get_next_step(Cave.parse_distances(
        ...     "#########\\n"
        ...     "#G21012G#\\n"
        ...     "#.32123.#\\n"
        ...     "#..323..#\\n"
        ...     "#G..3..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... ), (4, 4))
        (4, 2)
        """
        if distances[target] == 0:
            raise Exception("Tried to get next steps for same position")
        elif distances[target] == 1:
            return self.position

        stack = [target]
        next_steps = set()
        if debug:
            print("Get next step: ", end="", flush=True)
        while stack:
            position = stack.pop(0)
            next_distance, next_positions = self.get_next_step_iteration(
                distances, position)
            if debug:
                print(next_distance, ", ", end="", flush=True)
            if next_distance == 1:
                next_steps.update(next_positions)
                continue
            for next_position in next_positions:
                if next_position not in stack:
                    stack.append(next_position)
        if debug:
            print(f"done: {len(next_steps)}")

        if not next_steps:
            raise Exception(
                f"No next steps found from {self.position} to {target}")

        return min(next_steps, key=Cave.sort_key_reading_order_position)

    def get_next_step_iteration(self, distances, position):
        """
        >>> distances_a = Cave.parse_distances(
        ...     "#########\\n"
        ...     "#.G1012G#\\n"
        ...     "#.32123.#\\n"
        ...     "#..323..#\\n"
        ...     "#G..3..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> Goblin((4, 1)).get_next_step_iteration(distances_a, (4, 4))
        (2, [(4, 3)])
        """
        distance = distances[position]
        next_distance = distance - 1
        next_positions = [
            next_position
            for next_position, next_position_distance in distances.items()
            if next_position_distance == next_distance
            and self.are_neighbours(next_position, position)
        ]
        return next_distance, next_positions

    def are_neighbours(self, lhs, rhs):
        """
        >>> Goblin((0, 0)).are_neighbours((0, 0), (0, 1))
        True
        >>> Goblin((0, 0)).are_neighbours((0, 0), (-1, 0))
        True
        >>> Goblin((0, 0)).are_neighbours((0, 0), (0, 0))
        False
        >>> Goblin((0, 0)).are_neighbours((0, 0), (1, 1))
        False
        >>> Goblin((0, 0)).are_neighbours((0, 0), (-5, 4))
        False
        """
        lhs_x, lhs_y = lhs
        rhs_x, rhs_y = rhs
        return abs(lhs_x - rhs_x) + abs(lhs_y - rhs_y) == 1

    def get_closest_enemy(self, enemies, distances):
        """
        >>> cave_a = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_a = cave_a.get_units_by_position()
        >>> unit_a = units_by_position_a[(1, 1)]
        >>> enemies_a = [
        ...     unit for unit in cave_a.units
        ...     if not isinstance(unit, type(unit_a))
        ... ]
        >>> distances_a = unit_a.get_distances(
        ...     cave_a.spaces, enemies_a, units_by_position_a)
        >>> unit_a.get_closest_enemy(enemies_a, distances_a)
        Elf(position=(4, 4), attack=3, health=200)
        >>> cave_b = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#.G.G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_b = cave_b.get_units_by_position()
        >>> unit_b = units_by_position_b[(4, 1)]
        >>> enemies_b = [
        ...     unit for unit in cave_b.units
        ...     if not isinstance(unit, type(unit_b))
        ... ]
        >>> distances_b = unit_b.get_distances(
        ...     cave_b.spaces, enemies_b, units_by_position_b)
        >>> unit_b.get_closest_enemy(enemies_b, distances_b)
        Elf(position=(4, 4), attack=3, health=200)
        >>> cave_c = Cave.from_cave_text(
        ...     "####\\n"
        ...     "#GE#\\n"
        ...     "#E.#\\n"
        ...     "####\\n"
        ... )
        >>> units_by_position_c = cave_c.get_units_by_position()
        >>> unit_c = units_by_position_c[(1, 1)]
        >>> enemies_c = [
        ...     unit for unit in cave_c.units
        ...     if not isinstance(unit, type(unit_c))
        ... ]
        >>> distances_c = unit_c.get_distances(
        ...     cave_c.spaces, enemies_c, units_by_position_c)
        >>> unit_c.get_closest_enemy(enemies_c, distances_c)
        Elf(position=(2, 1), attack=3, health=200)
        >>> units_by_position_c[(1, 2)].health = 100
        >>> unit_c.get_closest_enemy(enemies_c, distances_c)
        Elf(position=(1, 2), attack=3, health=100)
        >>> cave_c = Cave.from_cave_text(
        ...     "#####\\n"
        ...     "#G.E#\\n"
        ...     "#...#\\n"
        ...     "#E..#\\n"
        ...     "#####\\n"
        ... )
        >>> units_by_position_c = cave_c.get_units_by_position()
        >>> unit_c = units_by_position_c[(1, 1)]
        >>> enemies_c = [
        ...     unit for unit in cave_c.units
        ...     if not isinstance(unit, type(unit_c))
        ... ]
        >>> distances_c = unit_c.get_distances(
        ...     cave_c.spaces, enemies_c, units_by_position_c)
        >>> unit_c.get_closest_enemy(enemies_c, distances_c)
        Elf(position=(3, 1), attack=3, health=200)
        >>> units_by_position_c[(1, 3)].health = 100
        >>> unit_c.get_closest_enemy(enemies_c, distances_c)
        Elf(position=(3, 1), attack=3, health=200)
        """
        enemies_distances = {
            enemy: distances[enemy.position]
            for enemy in enemies
            if enemy.position in distances
        }
        if not enemies_distances:
            return None
        closest_distance = min(enemies_distances.values())
        closest_enemies = [
            enemy
            for enemy, distance in enemies_distances.items()
            if distance == closest_distance
        ]
        if closest_distance == 1:
            closest_enemy = min(
                closest_enemies, key=Cave.sort_key_health_reading_order)
        else:
            closest_enemy = min(
                closest_enemies, key=Cave.sort_key_reading_order)

        return closest_enemy

    def get_distances(self, spaces, enemies, units_by_position):
        """
        >>> cave_a = Cave.from_cave_text(
        ...     "#########\\n"
        ...     "#G..G..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..E..G#\\n"
        ...     "#.......#\\n"
        ...     "#.......#\\n"
        ...     "#G..G..G#\\n"
        ...     "#########\\n"
        ... )
        >>> units_by_position_a = cave_a.get_units_by_position()
        >>> unit_a = units_by_position_a[(1, 1)]
        >>> enemies_a = [
        ...     unit for unit in cave_a.units
        ...     if not isinstance(unit, type(unit_a))
        ... ]
        >>> distances_a = unit_a.get_distances(
        ...     cave_a.spaces, enemies_a, units_by_position_a)
        >>> print(cave_a.show(distances_a))
        #########
        #012G6.G#
        #123456.#
        #23456..#
        #G456..G#
        #656....#
        #.6.....#
        #G..G..G#
        #########
        >>> unit_b = units_by_position_a[(4, 4)]
        >>> enemies_b = [
        ...     unit for unit in cave_a.units
        ...     if not isinstance(unit, type(unit_b))
        ... ]
        >>> distances_b = unit_b.get_distances(
        ...     cave_a.spaces, enemies_b, units_by_position_a)
        >>> print(cave_a.show(distances_b))
        #########
        #G..3..G#
        #..323..#
        #.32123.#
        #3210123#
        #.32123.#
        #..323..#
        #G..3..G#
        #########
        >>> unit_c = units_by_position_a[(4, 1)]
        >>> enemies_c = [
        ...     unit for unit in cave_a.units
        ...     if not isinstance(unit, type(unit_c))
        ... ]
        >>> distances_c = unit_c.get_distances(
        ...     cave_a.spaces, enemies_c, units_by_position_a)
        >>> print(cave_a.show(distances_c))
        #########
        #G21012G#
        #.32123.#
        #..323..#
        #G..3..G#
        #.......#
        #.......#
        #G..G..G#
        #########
        """
        cached_distances_key = \
            hash((spaces, tuple(sorted(units_by_position.items()))))
        if cached_distances_key == self.cached_distances_key:
            return self.cached_distances
        enemy_positions = {enemy.position for enemy in enemies}
        distances = {self.position: 0}
        stack = [self.position]
        closest_distance = None
        while stack:
            position = stack.pop(0)
            distance = distances[position]
            next_distance = distance + 1
            if closest_distance is not None \
                    and next_distance > closest_distance:
                continue
            for neighbour in self.get_neighbours(position, spaces):
                if neighbour in distances:
                    continue
                neighbour_x, neighbour_y = neighbour
                if not spaces[neighbour_y][neighbour_x]:
                    continue
                if neighbour in enemy_positions:
                    distances[neighbour] = next_distance
                    if closest_distance is None:
                        closest_distance = next_distance
                    elif next_distance < closest_distance:
                        closest_distance = next_distance
                elif neighbour not in units_by_position:
                    distances[neighbour] = next_distance
                    stack.append(neighbour)

        self.cached_distances_key = cached_distances_key
        self.cached_distances = distances

        return distances

    NEIGHBOUR_OFFSETS = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    def get_neighbours(self, position, spaces):
        """
        >>> sorted(Elf((0, 0)).get_neighbours((0, 0), ((True,),)))
        []
        >>> sorted(Elf((0, 0)).get_neighbours((0, 0), ((True,) * 3,) * 3))
        [(0, 1), (1, 0)]
        >>> sorted(Elf((0, 0)).get_neighbours((1, 1), ((True,) * 3,) * 3))
        [(0, 1), (1, 0), (1, 2), (2, 1)]
        >>> sorted(Elf((0, 0)).get_neighbours((2, 2), ((True,) * 3,) * 3))
        [(1, 2), (2, 1)]
        """
        x, y = position
        return (
            neighbour
            for neighbour in (
                (x + d_x, y + d_y)
                for d_x, d_y in self.NEIGHBOUR_OFFSETS
            )
            if self.is_position_space(neighbour, spaces)
        )

    def is_position_space(self, position, spaces):
        x, y = position
        return (
            0 <= x < len(spaces[0])
            and 0 <= y < len(spaces)
        )

    def move(self, next_position, units_by_position, spaces):
        """
        >>> elf, goblin = Elf((0, 0)), Goblin((1, 0))
        >>> units_by_position_a = {(0, 0): elf, (1, 0): goblin}
        >>> elf.move((0, 1), units_by_position_a, ((True, True), (True, True)))
        >>> units_by_position_a
        {(1, 0): Goblin(position=(1, 0), attack=3, health=200),
            (0, 1): Elf(position=(0, 1), attack=3, health=200)}
        """
        if self.is_dead():
            raise Exception(f"Unit {self} tried to move but it was dead")
        if units_by_position.get(self.position) != self:
            raise Exception(
                f"Unit {self} tried to move from {self.position} but it wasn't "
                f"there: instead {units_by_position.get(self.position)} was")
        if next_position in units_by_position:
            raise Exception(
                f"Unit {self} tried to move to {next_position} but "
                f"{units_by_position[next_position]} was there")
        manhattan_distance = utils.Point2D(*self.position)\
            .manhattan_distance(utils.Point2D(*next_position))
        if manhattan_distance != 1:
            raise Exception(
                f"Unit {self} at {self.position} tried to move to "
                f"{next_position} but the distance was {manhattan_distance}")
        if not self.is_position_space(next_position, spaces):
            raise Exception(
                f"Unit {self} tried to move to {next_position} but it was not "
                f"a space")
        del units_by_position[self.position]
        self.position = next_position
        units_by_position[self.position] = self

    def attack_enemy(self, enemy, units_by_position):
        """
        >>> elf, goblin = Elf((0, 0)), Goblin((1, 0))
        >>> units_by_position_a = {(0, 0): elf, (1, 0): goblin}
        >>> elf.attack_enemy(goblin, units_by_position_a)
        >>> units_by_position_a
        {(0, 0): Elf(position=(0, 0), attack=3, health=200),
            (1, 0): Goblin(position=(1, 0), attack=3, health=197)}
        >>> goblin.health = 3
        >>> elf.attack_enemy(goblin, units_by_position_a)
        >>> units_by_position_a
        {(0, 0): Elf(position=(0, 0), attack=3, health=200)}
        >>> goblin.health = 1
        >>> units_by_position_a = {(0, 0): elf, (1, 0): goblin}
        >>> elf.attack_enemy(goblin, units_by_position_a)
        >>> units_by_position_a
        {(0, 0): Elf(position=(0, 0), attack=3, health=200)}
        """
        if self.is_dead():
            raise Exception(f"Unit {self} tried to attack but it was dead")
        if enemy.is_dead():
            raise Exception(f"Tried to attack {enemy} but it was dead")
        if units_by_position.get(self.position) != self:
            raise Exception(
                f"Unit {self} tried to attack from {self.position} but it "
                f"wasn't there: instead {units_by_position.get(self.position)} "
                f"was")
        if units_by_position.get(enemy.position) != enemy:
            raise Exception(
                f"Tried to attack {enemy} at {enemy.position} but it "
                f"wasn't there: instead "
                f"{units_by_position.get(enemy.position)} was")
        manhattan_distance = utils.Point2D(*self.position)\
            .manhattan_distance(utils.Point2D(*enemy.position))
        if manhattan_distance != 1:
            raise Exception(
                f"Unit {self} at {self.position} tried to attack {enemy} at "
                f"{enemy.position} but their distance was {manhattan_distance}")
        enemy.health -= self.attack
        if enemy.is_dead():
            del units_by_position[enemy.position]

    def get_enemies(self, units_by_position):
        """
        >>> Goblin((1, 1)).get_enemies({
        ...     (1, 1): Goblin(position=(1, 1), attack=3, health=200),
        ...     (1, 4): Goblin(position=(1, 4), attack=3, health=200),
        ...     (1, 7): Goblin(position=(1, 7), attack=3, health=200),
        ...     (4, 1): Goblin(position=(4, 1), attack=3, health=200),
        ...     (4, 4): Elf(position=(4, 4), attack=3, health=200),
        ...     (4, 7): Goblin(position=(4, 7), attack=3, health=200),
        ...     (7, 1): Goblin(position=(7, 1), attack=3, health=200),
        ...     (7, 4): Goblin(position=(7, 4), attack=3, health=200),
        ...     (7, 7): Goblin(position=(7, 7), attack=3, health=200),
        ... })
        [Elf(position=(4, 4), attack=3, health=200)]
        >>> [type(unit).__name__ for unit in Elf((4, 4)).get_enemies({
        ...     (1, 1): Goblin(position=(1, 1), attack=3, health=200),
        ...     (1, 4): Goblin(position=(1, 4), attack=3, health=200),
        ...     (1, 7): Goblin(position=(1, 7), attack=3, health=200),
        ...     (4, 1): Goblin(position=(4, 1), attack=3, health=200),
        ...     (4, 4): Elf(position=(4, 4), attack=3, health=200),
        ...     (4, 7): Goblin(position=(4, 7), attack=3, health=200),
        ...     (7, 1): Goblin(position=(7, 1), attack=3, health=200),
        ...     (7, 4): Goblin(position=(7, 4), attack=3, health=200),
        ...     (7, 7): Goblin(position=(7, 7), attack=3, health=200),
        ... })]
        ['Goblin', 'Goblin', 'Goblin', 'Goblin', 'Goblin', 'Goblin', 'Goblin',
            'Goblin']
        """
        cls = type(self)
        return [
            unit
            for unit in units_by_position.values()
            if not isinstance(unit, cls)
        ]

    def show(self, show_health=False):
        """
        >>> Elf((4, 4)).show()
        'E'
        >>> Elf((4, 4)).show(True)
        'E(200)'
        >>> Goblin((4, 4)).show()
        'G'
        >>> Goblin((4, 4), health=123).show()
        'G'
        >>> Goblin((4, 4), health=123).show(True)
        'G(123)'
        """
        if show_health:
            return f"{self.show_symbol}({self.health})"
        else:
            return self.show_symbol


class Goblin(Unit):
    show_symbol = "G"


class Elf(Unit):
    show_symbol = "E"


challenge = Challenge()
challenge.main()
