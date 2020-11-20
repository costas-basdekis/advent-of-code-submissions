#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Tuple, Dict

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3578
        """
        return RuleSet.from_rules_text(_input).get_diagnostic_checksum()


@dataclass
class RuleSet:
    start_state: str
    checksum_step: int
    rules: Dict[Tuple[str, int], 'Rule']

    re_start_state = re.compile(r"^Begin in state ([A-Z])\.$")
    re_checksum_step = re.compile(
        r"^Perform a diagnostic checksum after (\d+) steps\.$")

    @classmethod
    def from_rules_text(cls, rules_text):
        """
        >>> RuleSet.from_example_a()
        RuleSet(start_state='A', checksum_step=6,
            rules={('A', 0): Rule(match=('A', 0), value_write=1, move_offset=1,
                next_state='B'),
            ('A', 1): Rule(match=('A', 1), value_write=0, move_offset=-1,
                next_state='B'),
            ('B', 0): Rule(match=('B', 0), value_write=1, move_offset=-1,
                next_state='A'),
            ('B', 1): Rule(match=('B', 1), value_write=1, move_offset=1,
            next_state='A')})
        """
        first_block, *rules_blocks = rules_text.strip('\n').split('\n\n')
        start_state_line, checksum_step_line = first_block.splitlines()
        start_state, = cls.re_start_state.match(start_state_line).groups()
        checksum_step_str, = cls.re_checksum_step\
            .match(checksum_step_line).groups()
        checksum_step = int(checksum_step_str)

        rules = {
            rule.match: rule
            for rule in sum((
                StateRule.rules_from_state_rule_text(block)
                for block in rules_blocks
            ), [])
        }

        return cls(start_state, checksum_step, rules)

    @classmethod
    def from_example_a(cls):
        return cls.from_rules_text(
            "Begin in state A.\n"
            "Perform a diagnostic checksum after 6 steps.\n"
            "\n"
            "In state A:\n"
            "  If the current value is 0:\n"
            "    - Write the value 1.\n"
            "    - Move one slot to the right.\n"
            "    - Continue with state B.\n"
            "  If the current value is 1:\n"
            "    - Write the value 0.\n"
            "    - Move one slot to the left.\n"
            "    - Continue with state B.\n"
            "\n"
            "In state B:\n"
            "  If the current value is 0:\n"
            "    - Write the value 1.\n"
            "    - Move one slot to the left.\n"
            "    - Continue with state A.\n"
            "  If the current value is 1:\n"
            "    - Write the value 1.\n"
            "    - Move one slot to the right.\n"
            "    - Continue with state A.\n"
        )

    def get_rule(self, execution):
        return self.rules[(execution.state, execution.value)]

    def get_diagnostic_checksum(self):
        """
        >>> RuleSet.from_example_a().get_diagnostic_checksum()
        3
        """
        return Execution(self)\
            .step_many(self.checksum_step)\
            .get_diagnostic_checksum()


class Execution:
    def __init__(self, rule_set, tape=None, state=None, position=0):
        self.rule_set = rule_set
        if tape is None:
            tape = {}
        self.tape = tape
        if state is None:
            state = self.rule_set.start_state
        self.state = state
        self.position = position

    def get_diagnostic_checksum(self):
        """
        >>> Execution(RuleSet.from_example_a())\\
        ...     .step_many(6).get_diagnostic_checksum()
        3
        """
        return len(self.tape)

    def step_many(self, count):
        """
        >>> print("!" + Execution(RuleSet.from_example_a())
        ...       .step_many(6).show(range(-3, 3)))
        !... 0  1  1 [0] 1  0 ...
        """
        for _ in range(count):
            self.step()

        return self

    def step(self):
        """
        >>> rule_set = RuleSet.from_example_a()
        >>> print("!" + Execution(RuleSet.from_example_a())
        ...       .step().show(range(-3, 3)))
        !... 0  0  0  1 [0] 0 ...
        """
        rule = self.rule_set.get_rule(self)
        rule.apply(self)

        return self

    @property
    def value(self):
        return self.tape.get(self.position, 0)

    @value.setter
    def value(self, value):
        if value not in (0, 1):
            raise Exception(f"Expected value to be 0 or 1, not {value}")
        if value:
            self.tape[self.position] = 1
        else:
            if self.position in self.tape:
                del self.tape[self.position]

    def move(self, offset):
        self.position += offset

    def show(self, _range=None):
        """
        >>> print("!" + Execution(RuleSet('A', 6, {})).show(range(-3, 3)))
        !... 0  0  0 [0] 0  0 ...
        """
        if _range is None:
            _range = range(
                min(self.position, min(self.tape)),
                max(self.position, max(self.tape)) + 1,
            )
        return "...{}...".format(
            "".join(
                (
                    "[{}]"
                    if self.position == position else
                    " {} "
                ).format(self.tape.get(position, 0))
                for position in _range
            ),
        )


class StateRule:
    re_state = re.compile(r"^In state ([A-Z]):$")

    @classmethod
    def rules_from_state_rule_text(cls, state_rule_text):
        """
        >>> StateRule.rules_from_state_rule_text(
        ...     "In state A:\\n"
        ...     "  If the current value is 0:\\n"
        ...     "    - Write the value 1.\\n"
        ...     "    - Move one slot to the right.\\n"
        ...     "    - Continue with state B.\\n"
        ...     "  If the current value is 1:\\n"
        ...     "    - Write the value 0.\\n"
        ...     "    - Move one slot to the left.\\n"
        ...     "    - Continue with state B.\\n"
        ... )
        [Rule(match=('A', 0), value_write=1, move_offset=1, next_state='B'),
            Rule(match=('A', 1), value_write=0, move_offset=-1, next_state='B')]
        """
        first_line, *rule_lines = state_rule_text.splitlines()
        state, = cls.re_state.match(first_line).groups()
        return [
            Rule.from_rule_text(state, "\n".join(rule_lines[start:start + 4]))
            for start in range(0, len(rule_lines), 4)
        ]


@dataclass
class Rule:
    match: Tuple[str, int]
    value_write: int
    move_offset: int
    next_state: str

    re_current_value = re.compile(r"^\s*If the current value is ([01]):$")
    re_value_write = re.compile(r"^\s*- Write the value ([01])\.$")
    re_move_offset = re.compile(r"^\s*- Move one slot to the (left|right)\.$")
    re_next_state = re.compile(r"^\s*- Continue with state ([A-Z])\.$")
    regexes = [re_current_value, re_value_write, re_move_offset, re_next_state]

    OFFSET_MAP = {
        'left': -1,
        'right': 1,
    }

    @classmethod
    def from_rule_text(cls, state, rule_text):
        """
        >>> Rule.from_rule_text('A',
        ...     "  If the current value is 0:\\n"
        ...     "    - Write the value 1.\\n"
        ...     "    - Move one slot to the right.\\n"
        ...     "    - Continue with state B.\\n"
        ... )
        Rule(match=('A', 0), value_write=1, move_offset=1, next_state='B')
        """
        lines = list(rule_text.strip('\n').splitlines())
        if len(lines) != len(cls.regexes):
            raise Exception(f"Expected {len(cls.regexes)} but got {len(lines)}")
        (value_str,), (value_write_str,), (move_offset_str,), (next_state,) = (
            regex.match(line).groups()
            for regex, line in zip(cls.regexes, lines)
        )

        value = int(value_str)
        match = (state, value)
        value_write = int(value_write_str)
        move_offset = cls.OFFSET_MAP[move_offset_str]

        return cls(match, value_write, move_offset, next_state)

    def apply(self, execution):
        execution.value = self.value_write
        execution.move(self.move_offset)
        execution.state = self.next_state


challenge = Challenge()
challenge.main()
