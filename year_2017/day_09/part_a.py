#!/usr/bin/env python3
from dataclasses import dataclass
from typing import List, Tuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        15922
        """
        return Node.from_node_text(_input.strip()).get_score()


class Node:
    @classmethod
    def from_node_text(cls, node_text):
        """
        >>> Group.from_node_text('{}')
        Group([])
        >>> Group.from_node_text('{{{}}}')
        Group([Group([Group([])])])
        >>> Group.from_node_text('{{},{}}')
        Group([Group([]), Group([])])
        >>> Group.from_node_text('{{{},{},{{}}}}')
        Group([Group([Group([]), Group([]), Group([Group([])])])])
        >>> Group.from_node_text('{<{},{},{{}}>}')
        Group([Garbage('{},{},{{}}')])
        >>> Group.from_node_text('{<a>,<a>,<a>,<a>}')
        Group([Garbage('a'), Garbage('a'), Garbage('a'), Garbage('a')])
        >>> Group.from_node_text('{{<a>},{<a>},{<a>},{<a>}}')
        Group([Group([Garbage('a')]), Group([Garbage('a')]),
            Group([Garbage('a')]), Group([Garbage('a')])])
        >>> Group.from_node_text('{{<!>},{<!>},{<!>},{<a>}}')
        Group([Group([Garbage('!>},{<!>},{<!>},{<a')])])
        >>> Group.from_node_text('{{<!>},{<!>},{<!>},{<a>}}asdsdasd')
        Traceback (most recent call last):
        ...
        Exception: ...
        >>> Group.from_node_text('{{<!>},{<!>},{<!>},{<a>}}{}')
        Traceback (most recent call last):
        ...
        Exception: ...
        """
        group, remaining = Group.parse(node_text)
        if remaining:
            raise Exception(
                f"Got extra text after end of group: "
                f"'{remaining[:10]}{'...' if len(remaining) > 10 else ''}'")

        return group

    @classmethod
    def parse(cls, text: str) -> Tuple['Node', str]:
        raise NotImplementedError()

    def get_score(self, parent_score=0):
        raise NotImplementedError()


@dataclass
class Garbage(Node):
    contents: str

    START = '<'
    END = '>'
    ESCAPE = '!'

    @classmethod
    def parse(cls, text: str) -> Tuple['Node', str]:
        """
        >>> Garbage.parse('<>')
        (Garbage(''), '')
        >>> Garbage.parse('<random characters>')
        (Garbage('random characters'), '')
        >>> Garbage.parse('<<<<>')
        (Garbage('<<<'), '')
        >>> Garbage.parse('<{!>}>')
        (Garbage('{!>}'), '')
        >>> Garbage.parse('<!!>')
        (Garbage('!!'), '')
        >>> Garbage.parse('<!!!>>')
        (Garbage('!!!>'), '')
        >>> Garbage.parse('<{o"i!a,<{i<a>')
        (Garbage('{o"i!a,<{i<a'), '')
        >>> Garbage.parse('<{o"i!a,<{i<a><sfdadsfds>')
        (Garbage('{o"i!a,<{i<a'), '<sfdadsfds>')
        """
        if text[:1] != cls.START:
            raise Exception(
                f"Was asked to parse garbage but didn't start with "
                f"'{cls.START}': "
                f"'{text[:10]}{'...' if len(text) > 10 else ''}'")

        remaining = text[1:]
        while remaining[:1] != cls.END:
            if not remaining:
                raise Exception(
                    f"Premature EOF: "
                    f"'{'...' if len(text) > 10 else ''}{text[-10:]}'")

            if remaining[0] == cls.ESCAPE:
                if len(remaining) < 2:
                    raise Exception(
                        f"Premature EOF: "
                        f"'{'...' if len(text) > 10 else ''}{text[-10:]}'")
                remaining = remaining[2:]
                continue

            remaining = remaining[1:]

        remaining = remaining[1:]
        return cls(text[1:-(len(remaining) + 1)]), remaining

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.contents)})"

    def get_score(self, parent_score=0):
        return 0


@dataclass
class Group(Node):
    contents: List[Node]

    START = '{'
    END = '}'
    DELIMITER = ','

    @classmethod
    def parse(cls, text: str) -> Tuple['Node', str]:
        """
        >>> Group.parse('{}')
        (Group([]), '')
        >>> Group.parse('{{{}}}')
        (Group([Group([Group([])])]), '')
        >>> Group.parse('{{},{}}')
        (Group([Group([]), Group([])]), '')
        >>> Group.parse('{{{},{},{{}}}}')
        (Group([Group([Group([]), Group([]), Group([Group([])])])]), '')
        >>> Group.parse('{<{},{},{{}}>}')
        (Group([Garbage('{},{},{{}}')]), '')
        >>> Group.parse('{<a>,<a>,<a>,<a>}')
        (Group([Garbage('a'), Garbage('a'), Garbage('a'), Garbage('a')]), '')
        >>> Group.parse('{{<a>},{<a>},{<a>},{<a>}}')
        (Group([Group([Garbage('a')]), Group([Garbage('a')]),
            Group([Garbage('a')]), Group([Garbage('a')])]), '')
        >>> Group.parse('{{<!>},{<!>},{<!>},{<a>}}')
        (Group([Group([Garbage('!>},{<!>},{<!>},{<a')])]), '')
        >>> Group.parse('{{<!>},{<!>},{<!>},{<a>}}asdsdasd')
        (Group([Group([Garbage('!>},{<!>},{<!>},{<a')])]), 'asdsdasd')
        """
        if text[:1] != cls.START:
            raise Exception(
                f"Was asked to parse group but didn't start with "
                f"'{cls.START}': "
                f"'{text[:10]}{'...' if len(text) > 10 else ''}'")

        remaining = text[1:]
        contents = []
        while remaining[:1] != cls.END:
            if not remaining:
                raise Exception(
                    f"Premature EOF: "
                    f"'{'...' if len(text) > 10 else ''}{text[-10:]}'")

            if contents:
                if remaining[0] != cls.DELIMITER:
                    raise Exception(
                        f"Expected '{cls.DELIMITER}' between contents but got "
                        f"'{remaining[0]}'")

                remaining = remaining[1:]
                if not remaining:
                    raise Exception(
                        f"Premature EOF: "
                        f"'{'...' if len(text) > 10 else ''}{text[-10:]}'")
            if remaining[0] == cls.START:
                content, remaining = cls.parse(remaining)
                contents.append(content)
            elif remaining[0] == Garbage.START:
                content, remaining = Garbage.parse(remaining)
                contents.append(content)
            else:
                raise Exception(
                    f"Expected a group or a garbage, but got '{remaining[0]}'")

        remaining = remaining[1:]
        return cls(contents), remaining

    def __repr__(self):
        return f"{type(self).__name__}({repr(self.contents)})"

    def get_score(self, parent_score=0):
        """
        >>> Node.from_node_text('{}').get_score()
        1
        >>> Node.from_node_text('{{{}}}').get_score()
        6
        >>> Node.from_node_text('{{{},{},{{}}}}').get_score()
        16
        >>> Node.from_node_text('{<a>,<a>,<a>,<a>}').get_score()
        1
        >>> Node.from_node_text('{{<ab>},{<ab>},{<ab>},{<ab>}}').get_score()
        9
        >>> Node.from_node_text('{{<!!>},{<!!>},{<!!>},{<!!>}}').get_score()
        9
        >>> Node.from_node_text('{{<a!>},{<a!>},{<a!>},{<ab>}}').get_score()
        3
        """
        my_score = parent_score + 1
        return my_score + sum(
            content.get_score(my_score)
            for content in self.contents
        )


challenge = Challenge()
challenge.main()
