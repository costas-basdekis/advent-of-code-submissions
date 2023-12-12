#!/usr/bin/env python3
import operator
from abc import ABC
from dataclasses import dataclass
import re
from enum import Enum
from typing import Callable, ClassVar, Dict, Iterable, List, Optional, Set, Union

from aox.challenge import Debugger
from utils import BaseChallenge, PolymorphicParser, cached_classmethod


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        386787
        """
        return System.from_text(_input).get_accepted_parts_rating_sum()


@dataclass
class System:
    workflows_by_name: Dict[str, "Workflow"]
    parts: List["Part"]

    @classmethod
    def from_text(cls, text: str) -> "System":
        """
        >>> System.from_text('''
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
        ... ''')
        System(...)
        """
        workflows_str, parts_str = text.strip().split("\n\n")
        workflows = list(map(Workflow.from_text, workflows_str.strip().split("\n")))
        return cls(
            workflows_by_name={
                workflow.name: workflow
                for workflow in workflows
            },
            parts=list(map(Part.from_text, parts_str.strip().splitlines())),
        )

    def get_accepted_parts_rating_sum(self) -> int:
        """
        >>> _system = System.from_text('''
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
        ... ''')
        >>> _system.get_accepted_parts_rating_sum()
        19114
        """
        return sum((
            part.get_rating_sum()
            for part in self.get_accepted_parts()
        ), 0)

    def get_accepted_parts(self) -> Iterable["Part"]:
        """
        >>> _system = System.from_text('''
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
        ... ''')
        >>> [_part.coolness for _part in _system.get_accepted_parts()]
        [787, 2036, 2127]
        """
        for part in self.parts:
            if self.evaluate(part):
                yield part

    def evaluate(self, part: "Part") -> bool:
        """
        >>> _system = System.from_text('''
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
        ... ''')
        >>> _system.evaluate(Part.from_text("{x=787,m=2655,a=1222,s=2876}"))
        True
        """
        workflow_name = None
        for workflow_name in self.evaluation_chain(part):
            pass
        if workflow_name is None:
            raise Exception(f"Evaluation chain was empty")
        if workflow_name == self.acceptance_workflow_name:
            return True
        if workflow_name == self.rejection_workflow_name:
            return False
        raise Exception(f"Evaluation chain ended in '{workflow_name}'")

    start_workflow_name: ClassVar[str] = "in"
    acceptance_workflow_name: ClassVar[str] = "A"
    rejection_workflow_name: ClassVar[str] = "R"
    terminal_workflow_names: ClassVar[Set[str]] = {acceptance_workflow_name, rejection_workflow_name}

    def evaluation_chain(self, part: "Part") -> Iterable[str]:
        """
        >>> _system = System.from_text('''
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
        ... ''')
        >>> list(_system.evaluation_chain(Part.from_text("{x=787,m=2655,a=1222,s=2876}")))
        ['in', 'qqz', 'qs', 'lnx', 'A']
        """
        workflow_name = self.start_workflow_name
        yield workflow_name
        while workflow_name not in self.terminal_workflow_names:
            workflow = self.workflows_by_name[workflow_name]
            workflow_name = workflow.evaluate(part)
            yield workflow_name


@dataclass
class Workflow:
    name: str
    rules: List["Rule"]

    re_parse: ClassVar[re.Pattern] = re.compile(r"^(\w+)\{([^}]+)}$")

    @classmethod
    def from_text(cls, text: str) -> "Workflow":
        """
        >>> Workflow.from_text("px{a<2006:qkq,m>2090:A,rfg}")
        Workflow(name='px', rules=[CompareRule(attribute=CompareRuleAttribute.Aerodynamicity, operation=CompareRuleOperation.LessThan, value=2006, target_name='qkq'),
            CompareRule(attribute=CompareRuleAttribute.Musicality, operation=CompareRuleOperation.GreaterThan, value=2090, target_name='A'),
            DefaultRule(target_name='rfg')])
        """
        match = cls.re_parse.match(text.strip())
        if not match:
            raise Exception(f"Could not parse '{text}'")
        name, rules_str = match.groups()
        rule_str_list = rules_str.split(",")
        return cls(name=name, rules=list(map(Rule.parse, rule_str_list)))

    def evaluate(self, part: "Part") -> str:
        """
        >>> _workflow = Workflow.from_text("in{s<1351:px,qqz}")
        >>> _workflow.evaluate(Part.from_text("{x=787,m=2655,a=1222,s=2876}"))
        'qqz'
        """
        for rule in self.rules:
            result = rule.evaluate(part)
            if result is not None:
                return result
        raise Exception(f"Could not evaluate {part}")


@dataclass
class Rule(PolymorphicParser, ABC, root=True):
    """
    >>> Rule.parse("a<2006:qkq")
    CompareRule(attribute=CompareRuleAttribute.Aerodynamicity, operation=CompareRuleOperation.LessThan, value=2006, target_name='qkq')
    >>> Rule.parse("rfg")
    DefaultRule(target_name='rfg')
    """

    def evaluate(self, part: "Part") -> Optional[str]:
        raise NotImplementedError()


class CompareRuleAttribute(Enum):
    Coolness = "x"
    Musicality = "m"
    Aerodynamicity = "a"
    Shininess = "s"

    @classmethod
    def parse(cls, text: str) -> "CompareRuleAttribute":
        return cls.get_parse_map()[text]

    @classmethod
    @cached_classmethod
    def get_parse_map(cls) -> Dict[str, "CompareRuleAttribute"]:
        return {
            item.value: item
            for item in cls
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


class CompareRuleOperation(Enum):
    LessThan = "<"
    GreaterThan = ">"

    @classmethod
    def parse(cls, text: str) -> "CompareRuleOperation":
        return cls.get_parse_map()[text]

    @classmethod
    @cached_classmethod
    def get_parse_map(cls) -> Dict[str, "CompareRuleOperation"]:
        return {
            item.value: item
            for item in cls
        }

    @classmethod
    @cached_classmethod
    def get_operator_map(cls) -> Dict["CompareRuleOperation", Callable[[float, float], bool]]:
        return {
            CompareRuleOperation.LessThan: operator.lt,
            CompareRuleOperation.GreaterThan: operator.gt,
        }

    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"

    def operate(self, left: float, right: float) -> bool:
        return self.get_operator_map()[self](left, right)


@Rule.register
@dataclass
class CompareRule(Rule):
    name = "compare"

    attribute: CompareRuleAttribute
    operation: CompareRuleOperation
    value: int
    target_name: str

    re_rule: ClassVar[re.Pattern] = re.compile(r"^([xmas])([<>])(-?\d+):(\w+)$")

    @classmethod
    def try_parse(cls, text: str) -> Optional["CompareRule"]:
        """
        >>> CompareRule.try_parse("a<2006:qkq")
        CompareRule(attribute=CompareRuleAttribute.Aerodynamicity, operation=CompareRuleOperation.LessThan, value=2006, target_name='qkq')
        """
        match = cls.re_rule.match(text)
        if not match:
            return None
        attribute_str, operation_str, value_str, target_name = match.groups()
        return cls(
            attribute=CompareRuleAttribute.parse(attribute_str),
            operation=CompareRuleOperation.parse(operation_str),
            value=int(value_str),
            target_name=target_name,
        )

    operator_map: ClassVar[Dict[CompareRuleOperation, Callable[[int, int], bool]]] = {
        CompareRuleOperation.LessThan: operator.lt,
        CompareRuleOperation.GreaterThan: operator.gt,
    }

    def evaluate(self, part: "Part") -> Optional[str]:
        part_value = part[self.attribute]
        success = self.operation.operate(part_value, self.value)
        if not success:
            return None
        return self.target_name


@Rule.register
@dataclass
class DefaultRule(Rule):
    name = "default"

    target_name: str

    re_rule: ClassVar[re.Pattern] = re.compile(r"^(\w+)$")

    @classmethod
    def try_parse(cls, text: str) -> Optional["DefaultRule"]:
        """
        >>> DefaultRule.try_parse("rfg")
        DefaultRule(target_name='rfg')
        """
        match = cls.re_rule.match(text)
        if not match:
            return None
        target_name, = match.groups()
        return cls(target_name=target_name)

    def evaluate(self, part: "Part") -> Optional[str]:
        return self.target_name


@dataclass
class Part:
    coolness: int
    musicality: int
    aerodynamicity: int
    shininess: int

    re_text: ClassVar[re.Pattern] = re.compile(r"^\{x=(-?\d+),m=(-?\d+),a=(-?\d+),s=(-?\d+)}$")

    @classmethod
    def from_text(cls, text: str) -> "Part":
        """
        >>> Part.from_text('{x=787,m=2655,a=1222,s=2876}')
        Part(coolness=787, musicality=2655, aerodynamicity=1222, shininess=2876)
        """
        match = cls.re_text.match(text.strip())
        if not match:
            raise Exception(f"Could not parse '{text}'")
        coolness_str, musicality_str, aerodynamicity_str, shininess_str = match.groups()
        return cls(
            coolness=int(coolness_str),
            musicality=int(musicality_str),
            aerodynamicity=int(aerodynamicity_str),
            shininess=int(shininess_str),
        )

    def __getitem__(self, attribute: CompareRuleAttribute) -> int:
        return {
            CompareRuleAttribute.Coolness: self.coolness,
            CompareRuleAttribute.Musicality: self.musicality,
            CompareRuleAttribute.Aerodynamicity: self.aerodynamicity,
            CompareRuleAttribute.Shininess: self.shininess,
        }[attribute]

    def get_rating_sum(self) -> int:
        """
        >>> Part.from_text("{x=787,m=2655,a=1222,s=2876}").get_rating_sum()
        7540
        """
        return sum(
            self[attribute]
            for attribute in CompareRuleAttribute
        )


Challenge.main()
challenge = Challenge()
