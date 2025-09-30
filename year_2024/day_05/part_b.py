#!/usr/bin/env python3
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_05 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        6204
        """
        return PrinterProtocolExtended.from_text(_input)\
            .invalid_only()\
            .fix()\
            .get_sum_of_middle_pages_of_valid_updates()


class PrinterProtocolExtended(part_a.PrinterProtocol[part_a.Ruleset, "UpdateExtended"]):
    def fix(self) -> "PrinterProtocolExtended":
        """
        >>> _protocol = PrinterProtocolExtended.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ...
        ...     75,47,61,53,29
        ...     97,61,53,29,13
        ...     75,29,13
        ...     75,97,47,61,53
        ...     61,13,29
        ...     97,13,75,29,47
        ... ''')
        >>> _protocol.invalid_only().fix().get_sum_of_middle_pages_of_valid_updates()
        123
        """
        return PrinterProtocolExtended(
            ruleset=self.ruleset,
            updates=[
                update.fix(self.ruleset)
                for update in self.updates
            ],
        )

    def invalid_only(self) -> "PrinterProtocolExtended":

        return PrinterProtocolExtended(
            ruleset=self.ruleset,
            updates=[
                update
                for update in self.updates
                if not update.is_valid(self.ruleset)
            ],
        )


class UpdateExtended(part_a.Update):
    def fix(self, ruleset: part_a.Ruleset) -> "UpdateExtended":
        """
        >>> _ruleset = part_a.Ruleset.from_text('''
        ...     47|53
        ...     97|13
        ...     97|61
        ...     97|47
        ...     75|29
        ...     61|13
        ...     75|53
        ...     29|13
        ...     97|29
        ...     53|29
        ...     61|53
        ...     97|53
        ...     61|29
        ...     47|13
        ...     75|47
        ...     97|75
        ...     47|61
        ...     75|61
        ...     47|29
        ...     75|13
        ...     53|13
        ... ''')
        >>> print(UpdateExtended.from_text("97,13,75,29,47").fix(_ruleset))
        97,75,47,29,13
        """
        if self.is_valid(ruleset):
            return self
        pages = [self.pages[0]]
        for page in self.pages[1:]:
            next_pages = ruleset.next_pages.get(page, set()) & set(pages)
            if next_pages:
                min_index = min(map(pages.index, next_pages))
                pages.insert(min_index, page)
            else:
                pages.append(page)
        return UpdateExtended(pages=pages)
        # return UpdateExtended(pages=sorted(self.pages, key=lambda page: (len(ruleset.previous_pages.get(page, set()) - set(self.pages)), self.pages.index(page))))


Challenge.main()
challenge = Challenge()
