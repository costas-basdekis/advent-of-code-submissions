#!/usr/bin/env python3
import utils
from year_2018.day_18 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        191080
        """
        return AreaExtended.from_area_text(_input)\
            .step_many(1000000000)\
            .get_hash()


class AreaExtended(part_a.Area):
    @classmethod
    def from_frozen(cls, frozen):
        """
        >>> print(AreaExtended.from_frozen(AreaExtended.from_area_text(
        ...     ".|#\\n"
        ...     "#..\\n"
        ...     "||.\\n"
        ... ).freeze()).show())
        .|#
        #..
        ||.
        """
        items, width, height = frozen
        return cls(dict(items), width, height)

    def freeze(self):
        """
        >>> AreaExtended.from_area_text(
        ...     ".|#\\n"
        ...     "#..\\n"
        ...     "||.\\n"
        ... ).freeze()
        ((((0, 1), 'camp'), ((0, 2), 'tree'), ((1, 0), 'tree'),
            ((1, 2), 'tree'), ((2, 0), 'camp')), 3, 3)
        """
        return tuple(sorted(self.contents.items())), self.width, self.height

    def step_many(self, count):
        by_step = {0: self}
        by_frozen = {self.freeze(): 0}
        for step in range(1, count + 1):
            self.step()
            frozen = self.freeze()
            original_step = by_frozen.get(frozen)
            if original_step is not None:
                repeated_step = self.get_repeated_step(
                    original_step, step, count)
                repeated_frozen = by_step[repeated_step]
                repeated_area = type(self).from_frozen(repeated_frozen)
                self.contents = repeated_area.contents
                break
            by_step[step] = frozen
            by_frozen[frozen] = step

        return self

    def get_repeated_step(self, original_step, repeated_step, final_step):
        """
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 599, 571)
        571
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 599, 599)
        571
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 599, 598)
        598
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 599, 572)
        572
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 572, 571)
        571
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 572, 572)
        571
        >>> AreaExtended({}, 10, 10).get_repeated_step(571, 572, 1000)
        571
        """
        period = repeated_step - original_step
        delta = final_step - original_step
        return original_step + delta % period


challenge = Challenge()
challenge.main()
