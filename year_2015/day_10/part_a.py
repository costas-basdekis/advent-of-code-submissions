#!/usr/bin/env python3
from itertools import groupby, count
from typing import Optional

from aox.challenge import Debugger
from utils import BaseChallenge, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        252594
        """
        return LookAndSay().get_length_after_steps(
            _input.strip(), debugger=debugger)


class LookAndSay:
    def get_length_after_steps(self, sequence: str, step_count: int = 40,
                               debugger: Debugger = Debugger(enabled=False),
                               ) -> int:
        """
        >>> LookAndSay().get_length_after_steps("1", 5)
        6
        """
        return len(self.step_many(sequence, step_count, debugger=debugger))

    def step_many(self, sequence: str, step_count: int = 40,
                  debugger: Debugger = Debugger(enabled=False)) -> str:
        """
        >>> LookAndSay().step_many("1", 5)
        '312211'
        """
        debugger.reset()
        result = sequence
        for step in debugger.stepping(range(step_count)):
            result = self.step(result)
            if debugger.should_report():
                debugger.default_report(f"step {step}/{step_count}")

        return result

    def step(self, sequence: str) -> str:
        """
        >>> LookAndSay().step("")
        ''
        >>> LookAndSay().step("1")
        '11'
        >>> LookAndSay().step("11")
        '21'
        >>> LookAndSay().step("21")
        '1211'
        >>> LookAndSay().step("1211")
        '111221'
        >>> LookAndSay().step("111221")
        '312211'
        """
        result = ""
        for content, items in groupby(sequence):
            count = helper.iterable_length(items)
            result += f"{count}{content}"

        return result


Challenge.main()
challenge = Challenge()
