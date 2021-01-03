#!/usr/bin/env python3
import functools
import re

import utils
from year_2020.day_19 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        267
        """
        rule_set, message_set = self.parse(_input)
        return self.get_matching_text_count(rule_set, message_set.messages)

    re_replaced = re.compile(r"^((?:<42>)+)((?:<31>)+)$")

    def get_matching_text_count(self, rule_set, texts):
        sets = rule_set.simplify()
        return sum(
            1
            for text in texts
            if self.text_matches(rule_set, text, sets=sets)
        )

    def text_matches(self, rule_set, text, sets=None):
        matches, replaced = rule_set\
            .replace_with_simplified_sets(text, sets=sets)
        if not matches:
            return False
        match = self.re_replaced.match(replaced)
        if not match:
            return False
        text_42, text_31 = match.groups()
        len_42 = len(text_42.replace("<42>", "|"))
        len_31 = len(text_31.replace("<31>", "|"))

        return len_42 > len_31

    def parse(self, _input):
        rule_set, message_set = RuleSetExtended\
            .from_rules_and_messages_text(_input)
        rule_set.rules_by_id[8] = part_a.Rule(
            8, part_a.Either((part_a.Ref((42,)), part_a.Ref((42, 8)))))
        rule_set.rules_by_id[11] = part_a.Rule(
            11, part_a.Either((
                part_a.Ref((42, 31)),
                part_a.Ref((42, 11, 31)),
            )))
        return rule_set, message_set


class RuleSetExtended(part_a.RuleSet):
    def replace_with_simplified_sets(self, text, sets=None):
        if sets is None:
            sets = self.simplify()
        replaced = ""
        remaining = text
        length, = set(map(len, set(
            functools.reduce(set.__or__, sets.values()))))
        id_by_pattern = {
            pattern: _id
            for _id, patterns in sets.items()
            for pattern in patterns
        }
        while remaining:
            _next, remaining = remaining[:length], remaining[length:]
            _id = id_by_pattern.get(_next)
            if _id is None:
                return False, replaced + _next + remaining
            replaced += f"<{_id}>"

        return True, replaced

    def simplify(self, exclude_ids=(0, 8, 11)):
        simple_rules = self.get_simple_rules()
        excluded_rules = {
            _id: branches
            for _id, branches in simple_rules.items()
            if _id in exclude_ids
        }
        for _id in exclude_ids:
            del simple_rules[_id]
        self.replace_all_rules(simple_rules)
        return_regex_ids = set(sum(sum(excluded_rules.values(), ()), ()))
        overlaps = functools.reduce(set.__and__, (
            set(map("".join, branches))
            for _id, branches in simple_rules.items()
            if _id in return_regex_ids
        ))
        lengths = set(map(len, functools.reduce(set.__or__, (
            set(map("".join, branches))
            for _id, branches in simple_rules.items()
            if _id in return_regex_ids
        ))))
        if len(lengths) != 1:
            raise Exception(f"There are {len(lengths)} different lengths")
        if overlaps:
            raise Exception(f"There are {len(overlaps)} overlaps")

        return {
            _id: set(map("".join, branches))
            for _id, branches in simple_rules.items()
            if _id in return_regex_ids
        }

    def get_regexes(self, replaced_simple_rules):
        return {
            _id: ("({})+".format("|".join(sorted(map("".join, branches)))))
            for _id, branches in replaced_simple_rules.items()
        }

    def get_simple_rules(self):
        return {
            rule.id: (
                (rule.node.references,)
                if isinstance(rule.node, part_a.Ref) else
                tuple(branch.references for branch in rule.node.branches)
                if isinstance(rule.node, part_a.Either) else
                ((rule.node.content,),)
            )
            for rule in self.rules_by_id.values()
            if isinstance(rule, part_a.Rule)
        }

    def replace_all_rules(self, simple_rules):
        for _id in list(simple_rules):
            self.replace_rule(simple_rules, _id)

    def replace_rule(self, simple_rules, _id):
        while True:
            new_rule = self.replace_rule_step(simple_rules, _id)
            if new_rule == simple_rules[_id]:
                return
            simple_rules[_id] = new_rule

    def replace_rule_step(self, simple_rules, _id):
        rule = simple_rules[_id]
        if all(isinstance(item, str) for branch in rule for item in branch):
            return rule
        branch_index = next(
            index
            for index, branch in enumerate(rule)
            for item in branch
            if isinstance(item, int)
        )
        item_index = next(
            index
            for index, branch in enumerate(rule[branch_index])
            if isinstance(branch, int)
        )
        inlined_rule = simple_rules[rule[branch_index][item_index]]
        return (
            rule[:branch_index]
            + tuple(
                (
                    rule[branch_index][:item_index]
                    + inlined_branch
                    + rule[branch_index][item_index + 1:]
                )
                for inlined_branch in inlined_rule
            )
            + rule[branch_index + 1:]
        )


challenge = Challenge()
challenge.main()
