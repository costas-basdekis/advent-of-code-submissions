#!/usr/bin/env python3
import itertools
import re
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        162
        """
        rule_set, message_set = RuleSet.from_rules_and_messages_text(_input)
        return message_set.get_matching_message_count(rule_set)


class MessageSet:
    @classmethod
    def from_messages_text(cls, messages_text):
        """
        >>> MessageSet.from_messages_text(
        ...     "ababbb\\n"
        ...     "bababa\\n"
        ...     "abbbab\\n"
        ...     "aaabbb\\n"
        ...     "aaaabbb\\n"
        ... ).messages
        ['ababbb', 'bababa', 'abbbab', 'aaabbb', 'aaaabbb']
        """
        return cls(messages_text.strip().splitlines())

    def __init__(self, messages):
        self.messages = messages

    def get_matching_message_count(self, rule_set):
        """
        >>> rule_set_a, message_set_a = RuleSet.from_rules_and_messages_text(
        ...     '0: 4 1 5\\n'
        ...     '1: 2 3 | 3 2\\n'
        ...     '2: 4 4 | 5 5\\n'
        ...     '3: 4 5 | 5 4\\n'
        ...     '4: "a"\\n'
        ...     '5: "b"\\n'
        ...     '\\n'
        ...     'ababbb\\n'
        ...     'bababa\\n'
        ...     'abbbab\\n'
        ...     'aaabbb\\n'
        ...     'aaaabbb\\n'
        ... )
        >>> message_set_a.get_matching_message_count(rule_set_a)
        2
        """
        return sum(
            1
            for _ in self.get_matching_messages(rule_set)
        )

    def get_matching_messages(self, rule_set):
        """
        >>> rule_set_a, message_set_a = RuleSet.from_rules_and_messages_text(
        ...     '0: 4 1 5\\n'
        ...     '1: 2 3 | 3 2\\n'
        ...     '2: 4 4 | 5 5\\n'
        ...     '3: 4 5 | 5 4\\n'
        ...     '4: "a"\\n'
        ...     '5: "b"\\n'
        ...     '\\n'
        ...     'ababbb\\n'
        ...     'bababa\\n'
        ...     'abbbab\\n'
        ...     'aaabbb\\n'
        ...     'aaaabbb\\n'
        ... )
        >>> list(message_set_a.get_matching_messages(rule_set_a))
        ['ababbb', 'abbbab']
        """
        matches = rule_set.get_matches()
        return (
            message
            for message in self.messages
            if message in matches
        )


class RuleSet:
    rule_class = NotImplemented
    message_set_class = MessageSet

    @classmethod
    def from_rules_and_messages_text(cls, text):
        """
        >>> rule_set_a, message_set_a = RuleSet.from_rules_and_messages_text(
        ...     '0: 4 1 5\\n'
        ...     '1: 2 3 | 3 2\\n'
        ...     '2: 4 4 | 5 5\\n'
        ...     '3: 4 5 | 5 4\\n'
        ...     '4: "a"\\n'
        ...     '5: "b"\\n'
        ...     '\\n'
        ...     'ababbb\\n'
        ...     'bababa\\n'
        ...     'abbbab\\n'
        ...     'aaabbb\\n'
        ...     'aaaabbb\\n'
        ... )
        >>> rule_set_a.rules_by_id
        {'_cached': {},
         0: Rule(id=0, node=Ref(references=(4, 1, 5))),
         1: Rule(id=1, node=Either(branches=(Ref(references=(2, 3)),
            Ref(references=(3, 2))))),
         2: Rule(id=2, node=Either(branches=(Ref(references=(4, 4)),
            Ref(references=(5, 5))))),
         3: Rule(id=3, node=Either(branches=(Ref(references=(4, 5)),
            Ref(references=(5, 4))))),
         4: Rule(id=4, node=Literal(content='a')),
         5: Rule(id=5, node=Literal(content='b'))}
        >>> message_set_a.messages
        ['ababbb', 'bababa', 'abbbab', 'aaabbb', 'aaaabbb']
        """
        rules_text, messages_text = text.split('\n\n')
        rule_set = cls.from_rules_text(rules_text)
        message_set = cls.message_set_class.from_messages_text(messages_text)
        return rule_set, message_set

    @classmethod
    def from_rules_text(cls, rules_text):
        """
        >>> RuleSet.from_rules_text(
        ...     '0: 1 2\\n'
        ...     '1: "a"\\n'
        ...     '2: 1 3 | 3 1\\n'
        ...     '3: "b"\\n'
        ... ).rules_by_id
        {'_cached': {},
         0: Rule(id=0, node=Ref(references=(1, 2))),
         1: Rule(id=1, node=Literal(content='a')),
         2: Rule(id=2, node=Either(branches=(Ref(references=(1, 3)),
            Ref(references=(3, 1))))),
         3: Rule(id=3, node=Literal(content='b'))}
        """
        rules = map(
            cls.rule_class.from_rule_text,
            rules_text.strip().splitlines())
        return cls({
            rule.id: rule
            for rule in rules
        })

    def __init__(self, rules_by_id):
        self.rules_by_id = {
            "_cached": {},
            **rules_by_id,
        }

    def get_matches(self):
        """
        >>> RuleSet.from_rules_text(
        ...     '0: 1 2\\n'
        ...     '1: "a"\\n'
        ...     '2: 1 3 | 3 1\\n'
        ...     '3: "b"\\n'
        ... ).get_matches()
        ['aab', 'aba']
        """
        return self.rules_by_id[0].get_matches(self.rules_by_id)


class Rule(namedtuple("Rule", ("id", "node"))):
    node_class = NotImplemented
    re_rule = re.compile(r"^(\d+): (.*)$")

    @classmethod
    def from_rule_text(cls, rule_text):
        """
        >>> Rule.from_rule_text('4: "a"')
        Rule(id=4, node=Literal(content='a'))
        >>> Rule.from_rule_text("0: 4 1 5")
        Rule(id=0, node=Ref(references=(4, 1, 5)))
        >>> Rule.from_rule_text("1: 2 3 | 3 2")
        Rule(id=1, node=Either(branches=(Ref(references=(2, 3)),
            Ref(references=(3, 2)))))
        """
        id_str, node_text = cls.re_rule.match(rule_text).groups()
        _id = int(id_str)
        node = cls.node_class.parse(node_text)

        return cls(_id, node)

    def get_matches(self, rules_by_id):
        return self.node.get_matches(rules_by_id)


RuleSet.rule_class = Rule


class Node:
    name = NotImplemented
    node_classes = {}

    @classmethod
    def register(cls, node_class, override=False):
        name = node_class.name
        class_name = node_class.__name__
        if name is NotImplemented:
            raise Exception(f"{class_name} did not define name")
        existing = cls.node_classes.get(name)
        if not override and existing:
            existing_class_name = existing.__name__
            raise Exception(
                f"{class_name} redefined {name} that was defined by "
                f"{existing_class_name}")
        cls.node_classes[name] = node_class

        return node_class

    @classmethod
    def parse(cls, node_text):
        """
        >>> Node.parse('"a"')
        Literal(content='a')
        >>> Node.parse("4 1 5")
        Ref(references=(4, 1, 5))
        >>> Node.parse("2 3 | 3 2")
        Either(branches=(Ref(references=(2, 3)), Ref(references=(3, 2))))
        """
        for node_class in cls.node_classes.values():
            node = node_class.try_parse(node_text)
            if node:
                return node

        raise Exception(f"Could not parse '{node_text}'")

    @classmethod
    def try_parse(cls, node_text):
        raise NotImplementedError()

    def get_matches(self, rules_by_id):
        if rules_by_id:
            cached = rules_by_id.get("_cached")
            if cached is not None:
                if self not in cached:
                    cached[self] = self.generate_matches(rules_by_id)
                return cached[self]

        return self.generate_matches(rules_by_id)

    def generate_matches(self, rules_by_id):
        raise NotImplementedError()


Rule.node_class = Node


@Node.register
class Literal(Node, namedtuple("Literal", ("content",))):
    name = "literal"
    re_literal = re.compile(r"^\"([ab])\"$")

    @classmethod
    def try_parse(cls, node_text):
        """
        >>> Literal.try_parse('"a"')
        Literal(content='a')
        >>> Literal.try_parse('"b"')
        Literal(content='b')
        >>> Literal.try_parse('"c"')
        >>> Literal.try_parse("4 1 5")
        >>> Literal.try_parse("2 3 | 3 2")
        """
        match = cls.re_literal.match(node_text)
        if not match:
            return None
        content, = match.groups()
        return cls(content)

    def generate_matches(self, rules_by_id):
        """
        >>> Literal("a").generate_matches(None)
        ['a']
        """
        return [self.content]


@Node.register
class Ref(Node, namedtuple("Ref", ("references",))):
    name = "ref"
    re_ref = re.compile(r"^(\d+(?: \d+)*)$")

    @classmethod
    def try_parse(cls, node_text):
        """
        >>> Ref.try_parse('"a"')
        >>> Ref.try_parse("4 1 5")
        Ref(references=(4, 1, 5))
        >>> Ref.try_parse("4")
        Ref(references=(4,))
        >>> Ref.try_parse("2 3 | 3 2")
        """
        match = cls.re_ref.match(node_text)
        if not match:
            return None
        sub_rules_str, = match.groups()
        references = tuple(map(int, sub_rules_str.split(" ")))

        return cls(references)

    def generate_matches(self, rules_by_id):
        """
        >>> Ref((1, 2)).generate_matches({1: Literal("a"), 2: Literal("b")})
        ['ab']
        >>> Ref((1, 2)).generate_matches({
        ...     1: Literal("a"), 2: Either((Literal("a"), Literal("b"))),
        ... })
        ['aa', 'ab']
        """
        return [
            "".join(matches)
            for matches in itertools.product(*(
                rules_by_id[rule_id].get_matches(rules_by_id)
                for rule_id in self.references
            ))
        ]


@Node.register
class Either(Node, namedtuple("Either", ("branches",))):
    name = "either"

    @classmethod
    def try_parse(cls, node_text):
        """
        >>> Either.try_parse('"a"')
        >>> Either.try_parse("4 1 5")
        >>> Either.try_parse("2 3 | 3 2")
        Either(branches=(Ref(references=(2, 3)), Ref(references=(3, 2))))
        >>> Either.try_parse("2 3 | 3 2 | 4 5 | 6")
        Either(branches=(Ref(references=(2, 3)), Ref(references=(3, 2)),
            Ref(references=(4, 5)), Ref(references=(6,))))
        """
        if " | " not in node_text:
            return None
        branches_strs = node_text.split(" | ")
        branches = tuple(map(cls.parse, branches_strs))

        return cls(branches)

    def generate_matches(self, rules_by_id):
        """
        >>> Either((Literal("a"), Literal("b"))).generate_matches(None)
        ['a', 'b']
        """
        return sum((
            node.get_matches(rules_by_id)
            for node in self.branches
        ), [])


challenge = Challenge()
challenge.main()
