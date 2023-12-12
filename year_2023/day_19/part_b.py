#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, product
from year_2023.day_19 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        131029523269531
        """
        return SystemEvaluator.from_system_text(_input).get_combination_count()


@dataclass
class SystemEvaluator:
    workflows_by_name: Dict[str, "CompoundWorkflow"]

    @classmethod
    def from_system_text(cls, text: str) -> "SystemEvaluator":
        return cls.from_system(part_a.System.from_text(text))

    @classmethod
    def from_system(cls, system: part_a.System) -> "SystemEvaluator":
        return cls(workflows_by_name={
           workflow.name: workflow
            for workflow in
            map(CompoundWorkflow.from_workflow, system.workflows_by_name.values())
        })

    def __str__(self) -> str:
        return "\n".join(map(str, self.workflows_by_name.values()))

    def __getitem__(self, item: str) -> "CompoundWorkflow":
        return self.workflows_by_name[item]

    def get_combination_count(self) -> int:
        """
        >>> SystemEvaluator.from_system_text('''
        ...     px{a<2006:qkq,m>2090:A,rfg}
        ...     pv{a>1716:R,A}
        ...     lnx{m>1548:A,A}
        ...     rfg{s<537:gd,x>2440:R,A}
        ...     qs{s>3448:A,lnx}
        ...     qkq{x<1416:A,crn}
        ...     crn{x>2662:A,R}
        ...     in{s<1351:px,qqz}
        ...     qqz{s>2770:qs,m<1801:hdj,R}
        ...     gd{a>3333:R,R}
        ...     hdj{m>838:A,pv}
        ...
        ...     {x=787,m=2655,a=1222,s=2876}
        ...     {x=1679,m=44,a=2067,s=496}
        ...     {x=2036,m=264,a=79,s=2244}
        ...     {x=2461,m=1339,a=466,s=291}
        ...     {x=2127,m=1623,a=2188,s=1013}
        ... ''').get_combination_count()
        167409079868000
        """
        return self.simplify().distribute_rules().eliminate_all_leaves()["in"].get_combination_count()

    def simplify(self) -> "SystemEvaluator":
        """
        >>> print(SystemEvaluator.from_system_text('''
        ...     px{a<2006:qkq,m>2090:A,rfg}
        ...     pv{a>1716:R,A}
        ...     lnx{m>1548:A,A}
        ...     rfg{s<537:gd,x>2440:R,A}
        ...     qs{s>3448:A,lnx}
        ...     qkq{x<1416:A,crn}
        ...     crn{x>2662:A,R}
        ...     in{s<1351:px,qqz}
        ...     qqz{s>2770:qs,m<1801:hdj,R}
        ...     gd{a>3333:R,R}
        ...     hdj{m>838:A,pv}
        ...
        ...     {x=787,m=2655,a=1222,s=2876}
        ...     {x=1679,m=44,a=2067,s=496}
        ...     {x=2036,m=264,a=79,s=2244}
        ...     {x=2461,m=1339,a=466,s=291}
        ...     {x=2127,m=1623,a=2188,s=1013}
        ... ''').simplify())
        px{a<2006:qkq,m>2090:A,rfg}
        pv{a>1716:R,A}
        lnx{A}
        rfg{s<537:gd,x>2440:R,A}
        qs{s>3448:A,lnx}
        qkq{x<1416:A,crn}
        crn{x>2662:A,R}
        in{s<1351:px,qqz}
        qqz{s>2770:qs,m<1801:hdj,R}
        gd{R}
        hdj{m>838:A,pv}
        """
        workflows_by_name = {
            workflow.name: workflow.simplify()
            for workflow in self.workflows_by_name.values()
        }
        if workflows_by_name == self.workflows_by_name:
            return self
        return SystemEvaluator(workflows_by_name=workflows_by_name)

    def distribute_rules(self) -> "SystemEvaluator":
        """
        >>> print(SystemEvaluator.from_system_text('''
        ...     px{a<2006:qkq,m>2090:A,rfg}
        ...     pv{a>1716:R,A}
        ...     lnx{m>1548:A,A}
        ...     rfg{s<537:gd,x>2440:R,A}
        ...     qs{s>3448:A,lnx}
        ...     qkq{x<1416:A,crn}
        ...     crn{x>2662:A,R}
        ...     in{s<1351:px,qqz}
        ...     qqz{s>2770:qs,m<1801:hdj,R}
        ...     gd{a>3333:R,R}
        ...     hdj{m>838:A,pv}
        ...
        ...     {x=787,m=2655,a=1222,s=2876}
        ...     {x=1679,m=44,a=2067,s=496}
        ...     {x=2036,m=264,a=79,s=2244}
        ...     {x=2461,m=1339,a=466,s=291}
        ...     {x=2127,m=1623,a=2188,s=1013}
        ... ''').distribute_rules())
        px{a<2006:qkq,a>2005 & m>2090:A,a>2005 & m<2091:rfg}
        pv{a>1716:R,a<1717:A}
        lnx{m>1548:A,m<1549:A}
        rfg{s<537:gd,s>536 & x>2440:R,s>536 & x<2441:A}
        qs{s>3448:A,s<3449:lnx}
        qkq{x<1416:A,x>1415:crn}
        crn{x>2662:A,x<2663:R}
        in{s<1351:px,s>1350:qqz}
        qqz{s>2770:qs,s<2771 & m<1801:hdj,s<2771 & m>1800:R}
        gd{a>3333:R,a<3334:R}
        hdj{m>838:A,m<839:pv}
        """
        workflows_by_name = {
            workflow.name: workflow.distribute_rules()
            for workflow in self.workflows_by_name.values()
        }
        if workflows_by_name == self.workflows_by_name:
            return self
        return SystemEvaluator(workflows_by_name=workflows_by_name)

    def eliminate_all_leaves(self) -> "SystemEvaluator":
        evaluator = self
        while True:
            next_evaluator = evaluator.eliminate_leaves()
            if next_evaluator == evaluator:
                break
            evaluator = next_evaluator
        in_workflow = evaluator.workflows_by_name["in"]
        if not in_workflow.is_leaf():
            raise Exception(f"In workflow was not a leaf: {in_workflow}")
        return evaluator

    def eliminate_leaves(self) -> "SystemEvaluator":
        """
        >>> _evaluator = SystemEvaluator.from_system_text('''
        ...     px{a<2006:qkq,m>2090:A,rfg}
        ...     pv{a>1716:R,A}
        ...     lnx{m>1548:A,A}
        ...     rfg{s<537:gd,x>2440:R,A}
        ...     qs{s>3448:A,lnx}
        ...     qkq{x<1416:A,crn}
        ...     crn{x>2662:A,R}
        ...     in{s<1351:px,qqz}
        ...     qqz{s>2770:qs,m<1801:hdj,R}
        ...     gd{a>3333:R,R}
        ...     hdj{m>838:A,pv}
        ...
        ...     {x=787,m=2655,a=1222,s=2876}
        ...     {x=1679,m=44,a=2067,s=496}
        ...     {x=2036,m=264,a=79,s=2244}
        ...     {x=2461,m=1339,a=466,s=291}
        ...     {x=2127,m=1623,a=2188,s=1013}
        ... ''').distribute_rules()
        >>> _evaluator = _evaluator.eliminate_leaves()
        >>> print(_evaluator)
        px{a<2006:qkq,a>2005 & m>2090:A,a>2005 & m<2091:rfg}
        rfg{s<537 & a>3333:R,s<537 & a<3334:R,s>536 & x>2440:R,s>536 & x<2441:A}
        qs{s>3448:A,s<3449 & m>1548:A,s<3449 & m<1549:A}
        qkq{x<1416:A,x>1415 & x>2662:A,x>1415 & x<2663:R}
        in{s<1351:px,s>1350:qqz}
        qqz{s>2770:qs,s<2771 & m<1801:hdj,s<2771 & m>1800:R}
        hdj{m>838:A,m<839 & a>1716:R,m<839 & a<1717:A}
        """
        if len(self.workflows_by_name) <= 1:
            return self
        leaves_by_name = {
            workflow.name: workflow
            for workflow in self.workflows_by_name.values()
            if workflow.is_leaf()
        }
        if not leaves_by_name:
            raise Exception(f"Could not find leaves:\n{self}")
        workflows_by_name = {
            workflow.name: workflow.incorporate_leaves(leaves_by_name)
            for workflow in self.workflows_by_name.values()
            if workflow.name not in leaves_by_name
        }
        if workflows_by_name == self.workflows_by_name:
            return self
        return SystemEvaluator(workflows_by_name=workflows_by_name)


@dataclass
class CompoundWorkflow:
    name: str
    rules: List["CompoundRule"]

    @classmethod
    def from_workflow(cls, workflow: part_a.Workflow) -> "CompoundWorkflow":
        return cls(name=workflow.name, rules=list(map(CompoundRule.from_rule, workflow.rules)))

    def __str__(self) -> str:
        """
        >>> print(CompoundWorkflow.from_workflow(part_a.Workflow.from_text("pv{a>1716:R,A}")))
        pv{a>1716:R,A}
        """
        return "{}{{{}}}".format(
            self.name,
            f",".join(map(str, self.rules)),
        )

    def simplify(self) -> "CompoundWorkflow":
        """
        >>> print(CompoundWorkflow.from_workflow(part_a.Workflow.from_text("lnx{m>1548:A,A}")).simplify())
        lnx{A}
        >>> print(CompoundWorkflow.from_workflow(part_a.Workflow.from_text("pv{a>1716:R,A}")).simplify())
        pv{a>1716:R,A}
        """
        target_names = self.get_target_names()
        if target_names == {part_a.System.acceptance_workflow_name}:
            target_name, = target_names
            return CompoundWorkflow(name=self.name, rules=[CompoundRule(target_name=target_name, rules=[])])
        if target_names == {part_a.System.rejection_workflow_name}:
            target_name, = target_names
            return CompoundWorkflow(name=self.name, rules=[CompoundRule(target_name=target_name, rules=[])])
        return self

    def get_target_names(self) -> Set[str]:
        """
        >>> sorted(CompoundWorkflow.from_workflow(part_a.Workflow.from_text("pv{a>1716:R,A}")).get_target_names())
        ['A', 'R']
        """
        return {
            rule.target_name
            for rule in self.rules
        }

    def distribute_rules(self) -> "CompoundWorkflow":
        """
        >>> print(CompoundWorkflow.from_workflow(part_a.Workflow.from_text("rfg{s<537:gd,x>2440:R,A}")).distribute_rules())
        rfg{s<537:gd,s>536 & x>2440:R,s>536 & x<2441:A}
        """
        return CompoundWorkflow(
            name=self.name,
            rules=[
                rule.distribute_rules([sub_rule.rules[0] for sub_rule in self.rules[:index]])
                for index, rule in enumerate(self.rules)
            ],
        )

    def is_leaf(self) -> bool:
        return all(
            rule.target_name in part_a.System.terminal_workflow_names
            for rule in self.rules
        )

    def incorporate_leaves(self, leaves_by_name: Dict[str, "CompoundWorkflow"]) -> "CompoundWorkflow":
        if not (set(leaves_by_name) & set(self.get_target_names())):
            return self
        rules = [
            new_rule
            for rule in self.rules
            for new_rule in rule.incorporate_leaves(leaves_by_name)
        ]
        if rules == self.rules:
            return self
        return CompoundWorkflow(name=self.name, rules=rules)

    def get_combination_count(self) -> int:
        non_terminal_rules = [
            rule
            for rule in self.rules
            if rule.target_name not in part_a.System.terminal_workflow_names
        ]
        if non_terminal_rules:
            raise Exception(f"Non-terminal rules: {non_terminal_rules}")
        return sum(
            rule.get_combination_count()
            for rule in self.rules
            if rule.target_name == part_a.System.acceptance_workflow_name
        )


@dataclass
class CompoundRule:
    target_name: str
    rules: List[part_a.CompareRule]

    @classmethod
    def from_rule(cls, rule: part_a.Rule) -> "CompoundRule":
        if isinstance(rule, part_a.DefaultRule):
            rules = []
        else:
            rules = [rule]
        return cls(target_name=rule.target_name, rules=rules)

    def __str__(self) -> str:
        return "{}{}{}".format(
            " & ".join(
                str(rule).split(":")[0]
                for rule in self.rules
                if isinstance(rule, part_a.CompareRule)
            ),
            ":" if self.rules else "",
            self.target_name,
        )

    def get_opposite_rule(self, rule: part_a.CompareRule) -> part_a.CompareRule:
        """
        >>> print(CompoundRule("", []).get_opposite_rule(part_a.Rule.parse("m>1548:A")))
        m<1549:A
        >>> print(CompoundRule("", []).get_opposite_rule(part_a.Rule.parse("s<537:gd")))
        s>536:gd
        """
        if rule.operation == part_a.CompareRuleOperation.LessThan:
            return part_a.CompareRule(
                attribute=rule.attribute,
                operation=part_a.CompareRuleOperation.GreaterThan,
                value=rule.value - 1,
                target_name=rule.target_name,
            )
        if rule.operation == part_a.CompareRuleOperation.GreaterThan:
            return part_a.CompareRule(
                attribute=rule.attribute,
                operation=part_a.CompareRuleOperation.LessThan,
                value=rule.value + 1,
                target_name=rule.target_name,
            )
        raise Exception(f"Cannot get opposite of {rule}")

    def distribute_rules(self, rules: List[part_a.CompareRule]) -> "CompoundRule":
        """
        >>> print(CompoundRule.from_rule(part_a.Rule.parse("A")).distribute_rules(list(map(part_a.Rule.parse, "s<537:gd,x>2440:R".split(",")))))
        s>536 & x<2441:A
        >>> print(CompoundRule.from_rule(part_a.Rule.parse("x>2440:R")).distribute_rules(list(map(part_a.Rule.parse, "s<537:gd".split(",")))))
        s>536 & x>2440:R
        >>> print(CompoundRule.from_rule(part_a.Rule.parse("s<537:gd")).distribute_rules([]))
        s<537:gd
        """
        if not rules:
            return self
        return CompoundRule(target_name=self.target_name, rules=[
            self.get_opposite_rule(rule)
            for rule in rules
        ] + self.rules)

    def incorporate_leaves(self, leaves_by_name: Dict[str, "CompoundWorkflow"]) -> List["CompoundRule"]:
        leaf = leaves_by_name.get(self.target_name)
        if not leaf:
            return [self]
        return [
            CompoundRule(target_name=leaf_rule.target_name, rules=self.rules + leaf_rule.rules)
            for leaf_rule in leaf.rules
        ]

    def get_combination_count(self) -> int:
        """
        >>> CompoundRule.from_rule(part_a.Rule.parse("A")).distribute_rules(list(map(part_a.Rule.parse, "s<537:gd,x>2440:R".split(",")))).get_combination_count()
        135234560000000
        """
        attributes_ranges = self.get_combination_ranges()
        return product(
            attribute_max - attribute_min + 1
            for attribute_min, attribute_max in attributes_ranges.values()
        )

    def get_combination_ranges(self) -> Dict[part_a.CompareRuleAttribute, Tuple[int, int]]:
        """
        >>> CompoundRule.from_rule(part_a.Rule.parse("A")).distribute_rules(list(map(part_a.Rule.parse, "s<537:gd,x>2440:R".split(",")))).get_combination_ranges()
        {CompareRuleAttribute.Coolness: (1, 2440),
            CompareRuleAttribute.Musicality: (1, 4000),
            CompareRuleAttribute.Aerodynamicity: (1, 4000),
            CompareRuleAttribute.Shininess: (537, 4000)}
        """
        attributes_ranges = {
            attribute: (1, 4000)
            for attribute in part_a.CompareRuleAttribute
        }
        for rule in self.rules:
            attribute_min, attribute_max = attributes_ranges[rule.attribute]
            if rule.operation == part_a.CompareRuleOperation.LessThan:
                attribute_max = min(attribute_max, rule.value - 1)
            elif rule.operation == part_a.CompareRuleOperation.GreaterThan:
                attribute_min = max(attribute_min, rule.value + 1)
            else:
                raise Exception(f"Cannot get combination count of {rule}")
            attributes_ranges[rule.attribute] = (attribute_min, attribute_max)
        return attributes_ranges


"""
px{a<2006:qkq,m>2090:A,rfg}
pv{a>1716:R,A}
lnx{m>1548:A,A}
rfg{s<537:gd,x>2440:R,A}
qs{s>3448:A,lnx}
qkq{x<1416:A,crn}
crn{x>2662:A,R}
in{s<1351:px,qqz}
qqz{s>2770:qs,m<1801:hdj,R}
gd{a>3333:R,R}
hdj{m>838:A,pv}

in{
    s<1351 & x<1416:A,
    s<1351 & a<2006 & x>2662:A,
    s<1351 & a>2005 & m>2090:A,
    s<1351 & a>2005 & m<2091 & s>536 & x<2441:A,
    s>1350 & s>2770:A,
    s>1350 & s<2771 & m<1801 & m>838:A,
    s>1350 & s<2771 & m<1801 & m<839 & a<1717:A,
}

in{
    1351 * 1416 * 4000 * 4000:A,
    1351 * 2006 * (4000 - 2662) * 4000:A,
    s<1351 & a>2005 & m>2090:A,
    s<1351 & a>2005 & m<2091 & s>536 & x<2441:A,
    s>1350 & s>2770:A,
    s>1350 & s<2771 & m<1801 & m>838:A,
    s>1350 & s<2771 m<839 & a<1717:A,
}
"""


Challenge.main()
challenge = Challenge()
