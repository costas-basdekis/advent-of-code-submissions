#!/usr/bin/env python3
import itertools

import utils
from year_2020.day_23 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        42
        """
        return GameExtended.from_game_text(_input)\
            .pad(1000000)\
            .step_many(10000000, debug=True)\
            .get_star_hash()


class GameExtended(part_a.Game):
    """
    >>> tuple(GameExtended((3, 8, 9, 1, 2, 5, 4, 6, 7)).step_many(10).cups)
    (8, 3, 7, 4, 1, 9, 2, 6, 5)
    >>> GameExtended((3, 8, 9, 1, 2, 5, 4, 6, 7)).step_many(100)\\
    ...     .get_order_hash()
    '67384529'
    """
    def __init__(self, cups):
        if isinstance(cups, tuple):
            cups = LTTuple(cups)
        super().__init__(cups)

    def pad(self, new_length):
        """
        >>> GameExtended.from_game_text('54321').pad(10)
        GameExtended(cups=LTCombined((LTTuple((5, 4, 3, 2, 1)),
            LTRange(range(6, 11)))))
        >>> GameExtended.from_game_text('54321').pad(100)
        GameExtended(cups=LTCombined((LTTuple((5, 4, 3, 2, 1)),
            LTRange(range(6, 101)))))
        >>> GameExtended.from_game_text('54321').pad(1000000)
        GameExtended(cups=LTCombined((LTTuple((5, 4, 3, 2, 1)),
            LTRange(range(6, 1000001)))))
        >>> game_a = GameExtended.from_game_text('739862541').pad(1000000)
        >>> game_a
        GameExtended(cups=LTCombined((LTTuple((7, 3, 9, 8, 6, 2, 5, 4, 1)),
            LTRange(range(10, 1000001)))))
        >>> game_a.step()
        GameExtended(cups=LTCombined((LTTuple((6, 3, 9, 8, 2, 5, 4, 1)),
            LTRange(range(10, 1000001)), LTTuple((7,)))))
        >>> game_a.step()
        GameExtended(cups=LTCombined((LTTuple((2, 5, 3, 9, 8, 4, 1)),
            LTRange(range(10, 1000001)), LTTuple((7, 6)))))
        >>> game_a.step_many(4)
        GameExtended(cups=LTCombined((LTRange(range(16, 1000001)),
            LTTuple((7, 4, 1, 5, 6, 2, 9)),
            LTRange(range(10, 12)),
            LTRange(range(13, 16)),
            LTTuple((8, 3)),
            LTRange(range(12, 13)))))
        """
        self.cups += LTRange(range(len(self.cups) + 1, new_length + 1))
        return self

    def get_star_hash(self):
        """"""
        """
        >>> GameExtended((3, 8, 9, 1, 2, 5, 4, 6, 7))\\
        ...     .pad(1000000).step_many(1000000).get_star_hash()
        149245887792
        """
        cup_a, cup_b = self.cups[1:3]
        return cup_a * cup_b


class LazyTuple:
    def __add__(self, other):
        if isinstance(self, LTCombined):
            lhs = self
        else:
            lhs = LTCombined((self,))
        if isinstance(other, LTCombined):
            rhs = other
        else:
            rhs = LTCombined((other,))
        return LTCombined(lhs.parts + rhs.parts)


class LTTuple(LazyTuple):
    def __init__(self, values):
        if not isinstance(values, tuple):
            raise Exception(f"Expected tuple, not {type(values)}")
        self.values = values

    def __repr__(self):
        """
        >>> LTTuple((1, 2, 3))
        LTTuple((1, 2, 3))
        """
        return f"{type(self).__name__}({self.values})"

    def __getitem__(self, item):
        """
        >>> LTTuple((1, 2, 3))[2]
        3
        >>> LTTuple((1, 2, 3))[4]
        Traceback (most recent call last):
        ...
        IndexError: tuple index out of range
        >>> LTTuple((1, 2, 3))[:2]
        LTTuple((1, 2))
        >>> LTTuple((1, 2, 3))[2:]
        LTTuple((3,))
        >>> LTTuple((1, 2, 3))[4:]
        LTTuple(())
        """
        if isinstance(item, int):
            return self.values[item]
        elif isinstance(item, slice):
            return LTTuple(self.values[item])
        else:
            raise Exception(f"Expected int or slice, not {type(item)}")

    def __len__(self):
        """
        >>> len(LTTuple((1, 2, 3))[:2])
        2
        >>> len(LTTuple((1, 2, 3))[2:])
        1
        >>> len(LTTuple((1, 2, 3))[4:])
        0
        """
        return len(self.values)

    def __iter__(self):
        """
        >>> tuple(LTTuple((1, 2, 3))[:2])
        (1, 2)
        >>> tuple(LTTuple((1, 2, 3))[2:])
        (3,)
        >>> tuple(LTTuple((1, 2, 3))[4:])
        ()
        """
        return iter(self.values)

    def index(self, value):
        return self.values.index(value)


class LTRange(LazyTuple):
    def __init__(self, _range):
        if not isinstance(_range, range):
            raise Exception(f"Expected range, not {type(_range)}")
        self.range = _range

    def __repr__(self):
        """
        >>> LTRange(range(5))
        LTRange(range(0, 5))
        >>> LTRange(range(5, 10))
        LTRange(range(5, 10))
        """
        return f"{type(self).__name__}({self.range})"

    def __getitem__(self, item):
        """
        >>> LTRange(range(5))[2]
        2
        >>> LTRange(range(5))[6]
        Traceback (most recent call last):
        ...
        IndexError: range object index out of range
        >>> LTRange(range(5))[2:4]
        LTRange(range(2, 4))
        >>> LTRange(range(5))[6:8]
        LTRange(range(5, 5))
        """
        if isinstance(item, int):
            return self.range[item]
        elif isinstance(item, slice):
            return LTRange(self.range[item])
        else:
            raise Exception(f"Expected int or slice, not {type(item)}")

    def __len__(self):
        """
        >>> len(LTRange(range(5))[2:4])
        2
        >>> len(LTRange(range(5))[6:8])
        0
        """
        return len(self.range)

    def __iter__(self):
        """
        >>> tuple(LTRange(range(5))[2:4])
        (2, 3)
        >>> tuple(LTRange(range(5))[6:8])
        ()
        """
        return iter(self.range)

    def index(self, value):
        return self.range.index(value)


class LTSkipRange(LazyTuple):
    @classmethod
    def combine_ranges(cls, lhs, rhs):
        """
        >>> LTSkipRange.combine_ranges(
        ...     LTRange(range(13, 16)), LTRange(range(17, 20)))
        LTSkipRange(13, 3, 2, 2)
        >>> LTSkipRange.combine_ranges(
        ...     LTRange(range(13, 16)), LTRange(range(18, 21)))
        LTSkipRange(13, 3, 3, 2)
        >>> LTSkipRange.combine_ranges(
        ...     LTRange(range(13, 16)), LTRange(range(17, 21)))
        >>> LTSkipRange.combine_ranges(
        ...     LTRange(range(13, 16)), LTRange(range(18, 20)))
        """
        if not isinstance(lhs, LTRange):
            raise Exception(f"Expected LTRange not {type(lhs)}")
        if not isinstance(rhs, LTRange):
            raise Exception(f"Expected LTRange not {type(rhs)}")
        if len(lhs) != len(rhs):
            return None

        if lhs.range.start > rhs.range.start:
            lhs, rhs = rhs, lhs

        return cls(
            lhs.range.start, len(lhs), rhs.range.start - lhs.range.stop + 1, 2)

    def __init__(self, start, length, skip, count):
        self.start = start
        self.length = length
        self.skip = skip
        self.count = count

    def __repr__(self):
        return (
            f"{type(self).__name__}"
            f"({self.start}, {self.length}, {self.skip}, {self.count})"
        )

    def combine(self, other):
        """
        >>> LTSkipRange(13, 3, 2, 2).combine(LTRange(range(21, 24)))
        LTSkipRange(13, 3, 2, 3)
        >>> LTSkipRange(13, 3, 2, 2).combine(LTRange(range(9, 12)))
        LTSkipRange(9, 3, 2, 3)
        >>> LTSkipRange(13, 3, 2, 2).combine(LTSkipRange(21, 3, 2, 2))
        LTSkipRange(13, 3, 2, 4)
        >>> LTSkipRange(21, 3, 2, 2).combine(LTSkipRange(13, 3, 2, 2))
        LTSkipRange(13, 3, 2, 4)
        >>> LTSkipRange(13, 3, 2, 2).combine(LTSkipRange(9, 3, 2, 1))
        LTSkipRange(9, 3, 2, 3)
        """
        cls = type(self)
        if isinstance(other, LTSkipRange):
            if (self.length, self.skip) != (other.length, other.skip):
                return None
            if self.start < other.start:
                lhs, rhs = self, other
            else:
                lhs, rhs = other, self

            if lhs.get_start_for_step(lhs.count) == rhs.start:
                return cls(
                    lhs.start, lhs.length, lhs.skip, lhs.count + rhs.count)
        elif isinstance(other, LTRange):
            if self.length != len(other):
                return None
            if self.get_start_for_step(self.count) == other.range.start:
                return cls(self.start, self.length, self.skip, self.count + 1)
            elif self.get_start_for_step(-1) == other.range.start:
                return cls(
                    self.get_start_for_step(-1), self.length, self.skip,
                    self.count + 1)
            return None
        else:
            raise Exception(f"Expected range or LTRange, not {type(other)}")

        return None

    def __getitem__(self, item):
        """
        >>> LTSkipRange(13, 3, 2, 3)[0]
        13
        >>> LTSkipRange(13, 3, 2, 3)[4]
        18
        >>> LTSkipRange(13, 3, 2, 3)[9]
        Traceback (most recent call last):
        ...
        IndexError: skip range index out of range
        >>> LTSkipRange(13, 3, 2, 3)[:3]
        LTSkipRange(13, 3, 2, 1)
        >>> LTSkipRange(13, 3, 2, 3)[3:6]
        LTSkipRange(17, 3, 2, 1)
        >>> LTSkipRange(13, 3, 2, 3)[6:9]
        LTSkipRange(21, 3, 2, 1)
        >>> LTSkipRange(13, 3, 2, 3)[6:]
        LTSkipRange(21, 3, 2, 1)
        >>> LTSkipRange(13, 3, 2, 3)[6:1235]
        LTSkipRange(21, 3, 2, 1)
        >>> LTSkipRange(13, 3, 2, 3)[:2]
        LTRange(range(13, 15))
        >>> LTSkipRange(13, 3, 2, 3)[:5]
        LTCombined((LTSkipRange(13, 3, 2, 1), LTRange(range(17, 19))))
        >>> LTSkipRange(13, 3, 2, 3)[3:8]
        LTCombined((LTSkipRange(17, 3, 2, 1), LTRange(range(21, 23))))
        >>> LTSkipRange(13, 3, 2, 3)[1:6]
        LTCombined((LTRange(range(14, 16)), LTSkipRange(17, 3, 2, 1)))
        >>> LTSkipRange(13, 3, 2, 3)[1:5]
        LTCombined((LTSkipRange(14, 2, 2, 2)))
        >>> LTSkipRange(13, 3, 2, 3)[1:8]
        LTCombined((LTRange(range(14, 16)), LTSkipRange(17, 3, 2, 1),
            LTRange(range(21, 23))))
        >>> LTSkipRange(13, 3, 2, 3)[1:9]
        LTCombined((LTRange(range(14, 16)), LTSkipRange(17, 3, 2, 2)))
        >>> LTSkipRange(13, 3, 2, 4)[1:11]
        LTCombined((LTRange(range(14, 16)), LTSkipRange(17, 3, 2, 2),
            LTRange(range(25, 27))))
        """
        if isinstance(item, int):
            if item < 0:
                return self[len(self) + item]
            if not (0 <= item < len(self)):
                raise IndexError("skip range index out of range")
            step = item // self.length
            offset = item % self.length
            return self.get_start_for_step(step) + offset
        elif isinstance(item, slice):
            if item.step not in (None, 1):
                raise Exception(
                    f"Can only handle slices with step=1, not {item.step}")
            start = item.start
            if start is None:
                start = 0
            stop = item.stop
            if stop is None:
                stop = len(self)
            if start < 0 or stop < 0:
                raise Exception(f"Can only handle positive slices, not {item}")
            if stop <= start:
                return LTCombined([])
            stop = min(stop, len(self))

            start_step = start // self.length
            start_offset = start % self.length

            stop_step = stop // self.length
            stop_offset = stop % self.length

            if (start_offset, stop_offset) == (0, 0):
                return LTSkipRange(
                    self[start], self.length, self.skip,
                    stop_step - start_step)

            if start_step == stop_step:
                return LTRange(range(self[start], self[stop]))

            if stop_step == start_step + 1:
                if start_offset == 0:
                    return LTCombined([
                        LTSkipRange(
                            self.get_start_for_step(start_step), self.length,
                            self.skip, stop_step - start_step),
                        LTRange(range(
                            self.get_start_for_step(stop_step),
                            self[stop]
                        )),
                    ])

                return LTCombined([
                    LTRange(range(
                        self[start],
                        self.get_start_for_step(stop_step) - self.skip + 1,
                    )),
                    LTRange(range(
                        self.get_start_for_step(stop_step),
                        self[stop],
                    )),
                ])

            return LTCombined([
                LTRange(range(
                    self[start],
                    self.get_start_for_step(start_step + 1) - self.skip + 1,
                )),
                LTSkipRange(
                    self.get_start_for_step(start_step + 1), self.length,
                    self.skip, stop_step - start_step - 1,
                ),
                LTRange(range(
                    self.get_start_for_step(stop_step),
                    self.get_start_for_step(stop_step) + stop_offset,
                )),
            ])
        else:
            raise Exception(f"Expected int or slice, not {type(item)}")

    def __len__(self):
        """
        >>> len(LTSkipRange(13, 3, 2, 1))
        3
        >>> len(LTSkipRange(13, 3, 2, 3))
        9
        """
        return self.length * self.count

    def __iter__(self):
        """
        >>> tuple(LTSkipRange(13, 3, 2, 1))
        (13, 14, 15)
        >>> tuple(LTSkipRange(13, 3, 2, 3))
        (13, 14, 15, 17, 18, 19, 21, 22, 23)
        """
        return (
            item
            for start in (
                self.get_start_for_step(step)
                for step in range(self.count)
            )
            for item in range(start, start + self.length)
        )

    def get_start_for_step(self, step):
        """
        >>> LTSkipRange(13, 3, 2, 1).get_start_for_step(0)
        13
        >>> LTSkipRange(13, 3, 2, 1).get_start_for_step(1)
        17
        >>> LTSkipRange(13, 3, 2, 1).get_start_for_step(-1)
        9
        """
        return self.start + step * (self.length + self.skip - 1)

    def index(self, value):
        """
        >>> LTSkipRange(13, 3, 2, 2).index(13)
        0
        >>> LTSkipRange(13, 3, 2, 2).index(14)
        1
        >>> LTSkipRange(13, 3, 2, 2).index(15)
        2
        >>> LTSkipRange(13, 3, 2, 2).index(16)
        Traceback (most recent call last):
        ...
        ValueError: 16 is not in skip range
        >>> LTSkipRange(13, 3, 2, 2).index(17)
        3
        >>> LTSkipRange(13, 3, 2, 2).index(21)
        Traceback (most recent call last):
        ...
        ValueError: 21 is not in skip range
        >>> LTSkipRange(13, 3, 2, 2).index(12)
        Traceback (most recent call last):
        ...
        ValueError: 12 is not in skip range
        """
        full_step = (value - self.start) // (self.length + self.skip - 1)
        full_offset = (value - self.start) % (self.length + self.skip - 1)
        if not (0 <= full_step < self.count):
            raise ValueError(f"{value} is not in skip range")
        if not (0 <= full_offset < self.length):
            raise ValueError(f"{value} is not in skip range")

        return full_step * self.length + full_offset


class LTCombined(LazyTuple):
    def __init__(self, parts, skip_optimisation=False,
                 min_consolidation_size=30, max_consolidation_part_size=20):
        """
        >>> LTCombined([(1, 2), (6, 7), range(5), (8, 9), (20, 21)])
        LTCombined((LTTuple((1, 2, 6, 7)), LTRange(range(0, 5)),
            LTTuple((8, 9, 20, 21))))
        >>> LTCombined([LTTuple((1, 2))])
        LTCombined((LTTuple((1, 2))))
        >>> LTCombined([range(1, 2)])
        LTCombined((LTRange(range(1, 2))))
        >>> LTCombined([range(2, 2)])
        LTCombined(())
        >>> LTCombined([()])
        LTCombined(())
        >>> LTCombined([LTRange(range(13, 16)), LTRange(range(17, 20))])
        LTCombined((LTSkipRange(13, 3, 2, 2)))
        >>> LTCombined([LTSkipRange(13, 3, 2, 2), LTRange(range(21, 24))])
        LTCombined((LTSkipRange(13, 3, 2, 3)))
        >>> LTCombined([LTCombined([LTSkipRange(13, 3, 2, 2)]),
        ...     LTRange(range(21, 24))])
        LTCombined((LTSkipRange(13, 3, 2, 3)))
        >>> LTCombined([
        ...     LTCombined([LTRange(range(13, 16))]),
        ...     LTCombined([LTRange(range(17, 20))]),
        ... ])
        LTCombined((LTSkipRange(13, 3, 2, 2)))
        """
        if not parts:
            self.parts = ()
            return
        if skip_optimisation:
            self.parts = tuple(parts)
        else:
            self.parts = ()
            self.add_parts(parts)
            self.consolidate(
                min_consolidation_size, max_consolidation_part_size)

    def consolidate(self, min_consolidation_size, max_consolidation_part_size):
        if len(self.parts) < min_consolidation_size:
            return
        parts = self.parts
        self.parts = ()
        for part in parts:
            if len(part) <= max_consolidation_part_size:
                part = LTTuple(tuple(part))
            self.add_part(part)

    def add_parts(self, parts):
        for part in parts:
            self.add_part(part)

    def add_part(self, part):
        if isinstance(part, tuple):
            part = LTTuple(part)
        elif isinstance(part, range):
            part = LTRange(part)
        elif type(part) == LazyTuple:
            raise Exception(f"Expected a concrete type of LazyTuple")
        elif not isinstance(part, LazyTuple):
            raise Exception(f"Expected a lazy tuple not {type(part)}")

        if not part:
            return

        if isinstance(part, LTCombined):
            if part.parts:
                remaining_parts = tuple(part.parts)
                while remaining_parts:
                    first_part = remaining_parts[0]
                    remaining_parts = remaining_parts[1:]
                    self.add_part(first_part)
                    if self.parts[-1] == first_part:
                        self.add_parts(remaining_parts)
                        break
            return
        elif not self.parts:
            self.insert_part(part)
            return

        previous_part = self.parts[-1]
        if isinstance(previous_part, LTTuple) \
                and isinstance(part, LTTuple) \
                and len(previous_part) < 1000:
            self.replace_last_part(
                LTTuple(previous_part.values + part.values))
        elif isinstance(previous_part, LTRange) \
                and isinstance(part, LTRange):
            combined = LTSkipRange.combine_ranges(previous_part, part)
            if combined is not None:
                self.replace_last_part(combined)
            else:
                self.insert_part(part)
        elif isinstance(previous_part, LTSkipRange) \
                and isinstance(part, (LTRange, LTSkipRange)):
            combined = previous_part.combine(part)
            if combined is not None:
                self.replace_last_part(combined)
            else:
                self.insert_part(part)
        else:
            self.insert_part(part)

    def insert_part(self, part):
        self.parts += (part,)

    def replace_last_part(self, part):
        self.parts = self.parts[:-1] + (part,)

    def __repr__(self):
        return f"{type(self).__name__}(({', '.join(map(repr, self.parts))}))"

    def __getitem__(self, item):
        """
        >>> LTCombined([(1, 2, 3)])[2]
        3
        >>> LTCombined([(1, 2, 3)])[4]
        Traceback (most recent call last):
        ...
        IndexError: combined index out of range
        >>> LTCombined([(1, 2, 3)])[:2]
        LTCombined((LTTuple((1, 2))))
        >>> LTCombined([(1, 2, 3)])[2:]
        LTCombined((LTTuple((3,))))
        >>> LTCombined([(1, 2, 3)])[4:]
        LTCombined(())
        >>> LTCombined((range(5),))[2]
        2
        >>> LTCombined((range(5),))[6]
        Traceback (most recent call last):
        ...
        IndexError: combined index out of range
        >>> LTCombined((range(5),))[2:4]
        LTCombined((LTRange(range(2, 4))))
        >>> LTCombined((range(5),))[6:8]
        LTCombined(())
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[0]
        1
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[3]
        7
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[4]
        0
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[8]
        4
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[9]
        8
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[20]
        Traceback (most recent call last):
        ...
        IndexError: combined index out of range
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[1:3]
        LTCombined((LTTuple((2, 6))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[:3]
        LTCombined((LTTuple((1, 2, 6))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[5:7]
        LTCombined((LTRange(range(1, 3))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[10:12]
        LTCombined((LTTuple((9, 20))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[10:]
        LTCombined((LTTuple((9, 20, 21))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[3:7]
        LTCombined((LTTuple((7,)), LTRange(range(0, 3))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[7:12]
        LTCombined((LTRange(range(3, 5)), LTTuple((8, 9, 20))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[3:12]
        LTCombined((LTTuple((7,)), LTRange(range(0, 5)), LTTuple((8, 9, 20))))
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)])[:]
        LTCombined((LTTuple((1, 2, 6, 7)), LTRange(range(0, 5)),
            LTTuple((8, 9, 20, 21))))
        """
        if isinstance(item, int):
            if item < 0:
                raise Exception(
                    f"Can only handle positive indexes, not {item}")
            total_length = 0
            for part in self.parts:
                part_item = item - total_length
                total_length += len(part)
                if 0 <= part_item < len(part):
                    return part[part_item]
            else:
                raise IndexError("combined index out of range")
        elif isinstance(item, slice):
            if item.step not in (None, 1):
                raise Exception(
                    f"Can only handle slices with step=1, not {item.step}")
            start = item.start
            if start is None:
                start = 0
            stop = item.stop
            if stop is None:
                stop = len(self)
            if start < 0:
                raise Exception(f"Can only handle positive slices, not {item}")
            if stop <= start:
                return LTCombined([])
            values = []
            total_length = 0
            for part in self.parts:
                part_start = max(0, start - total_length)
                part_stop = stop - total_length
                total_length += len(part)
                if part_start >= len(part):
                    continue
                if part_stop <= 0:
                    break
                values.append(part[part_start:part_stop])

            return LTCombined(values, skip_optimisation=True)
        else:
            raise Exception(f"Expected int or slice, not {type(item)}")

    def __len__(self):
        """
        >>> len(LTCombined([]))
        0
        >>> len(LTCombined((LTTuple((2, 6)),)))
        2
        >>> len(LTCombined((LTRange(range(1, 3)),)))
        2
        >>> len(LTCombined((LTTuple((7,)), LTRange(range(0, 3)))))
        4
        >>> len(LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)]))
        13
        """
        return sum(map(len, self.parts))

    def __iter__(self):
        """
        >>> tuple(LTCombined([]))
        ()
        >>> tuple(LTCombined((LTTuple((2, 6)),)))
        (2, 6)
        >>> tuple(LTCombined((LTRange(range(1, 3)),)))
        (1, 2)
        >>> tuple(LTCombined((LTTuple((7,)), LTRange(range(0, 3)))))
        (7, 0, 1, 2)
        >>> tuple(LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)]))
        (1, 2, 6, 7, 0, 1, 2, 3, 4, 8, 9, 20, 21)
        """
        return itertools.chain(*map(iter, self.parts))

    def index(self, value):
        """
        >>> LTCombined([]).index(1)
        Traceback (most recent call last):
        ...
        ValueError: 1 is not in combined
        >>> LTCombined((LTTuple((2, 6)),)).index(1)
        Traceback (most recent call last):
        ...
        ValueError: 1 is not in combined
        >>> LTCombined((LTTuple((2, 6)),)).index(2)
        0
        >>> LTCombined((LTRange(range(1, 3)),)).index(10)
        Traceback (most recent call last):
        ...
        ValueError: 10 is not in combined
        >>> LTCombined((LTRange(range(1, 3)),)).index(1)
        0
        >>> LTCombined((LTTuple((7,)), LTRange(range(0, 3)))).index(10)
        Traceback (most recent call last):
        ...
        ValueError: 10 is not in combined
        >>> LTCombined((LTTuple((7,)), LTRange(range(0, 3)))).index(7)
        0
        >>> LTCombined((LTTuple((7,)), LTRange(range(0, 3)))).index(0)
        1
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)]).index(10)
        Traceback (most recent call last):
        ...
        ValueError: 10 is not in combined
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)]).index(1)
        0
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)]).index(4)
        8
        >>> LTCombined([(1, 2, 6, 7), range(5), (8, 9, 20, 21)]).index(21)
        12
        """
        total_length = 0
        for part in self.parts:
            try:
                return part.index(value) + total_length
            except ValueError:
                pass
            total_length += len(part)
        else:
            raise ValueError(f"{value} is not in combined")


challenge = Challenge()
challenge.main()
# challenge.main(sys_args=[None, 'run'])
