#!/usr/bin/env python3
import utils
from year_2017.day_16 import part_a


class Challenge(utils.BaseChallenge):
    DEFAULT_GROUP = part_a.Challenge.DEFAULT_GROUP

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'cbolhmkgfpenidaj'
        """
        return ProgramExtended.from_program_text(_input)\
            .apply_many(self.DEFAULT_GROUP, 1 * 1000 * 1000 * 1000, debug=debug)


class ProgramExtended(part_a.Program):
    def apply_many(self, group, count, debug=False, report_count=1000):
        """
        >>> ProgramExtended.from_program_text('s1,x3/4,pe/b')\\
        ...     .apply_many('abcde', 2)
        'ceadb'
        """
        applied = group
        for step in range(count):
            applied = self.apply(applied)
            if applied == group:
                return self.apply_many(
                    group, count % (step + 1), debug=debug,
                    report_count=report_count)
            if debug:
                if step % report_count == 0:
                    print(f"{step} {applied}")

        return applied


Challenge.main()
challenge = Challenge()
