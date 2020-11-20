#!/usr/bin/env python3
import time

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        3072905352
        """
        return Nodes.from_input(_input)\
            .step_many()\
            .get_star_hash()


class Nodes:
    @classmethod
    def from_input(cls, _input, size=1000000):
        return cls(Node.circle_from_input(_input, size), int(_input[0]))

    def __init__(self, by_content, start_content):
        self.by_content = by_content
        self.current_node = by_content[start_content]

    def get_star_hash(self):
        node_a = self.by_content[1].next
        node_b = node_a.next
        content_a = node_a.content
        content_b = node_b.content
        return content_a * content_b

    def step_many(self, step_count=10000000, debug=False,
                  report_interval=10000):
        if debug:
            start_time = time.time()
        for step in range(step_count):
            self.step()
            if debug:
                if step % report_interval == 0:
                    end_time = time.time()
                    duration = end_time - start_time
                    start_time = end_time
                    print(
                        step, duration / report_interval,
                        duration / report_interval
                        * ((step_count - step) or 1) / 3600)
        return self

    def step(self):
        picked_nodes = [
            self.current_node.next,
            self.current_node.next.next,
            self.current_node.next.next.next,
        ]
        destination_node = next(
            node
            for node in (
                self.by_content[
                    (self.current_node.content - offset - 1)
                    % len(self.by_content) + 1
                ]
                for offset in range(1, 5)
            )
            if node not in picked_nodes
        )
        picked_nodes[0].previous.replace_next(picked_nodes[-1].next)
        destination_node.insert_next(picked_nodes[0], picked_nodes[-1])
        self.current_node = self.current_node.next
        return self


class Node:
    @classmethod
    def circle_from_input(cls, _input, size=1000000):
        return cls.circle_from_contents(
            list(map(int, _input.strip())) + list(range(10, size + 1)))

    @classmethod
    def circle_from_contents(cls, contents):
        by_content = {}
        first_content, rest = contents[0], contents[1:]
        first_node = cls(first_content, None)
        by_content[first_content] = first_node
        previous_node = first_node
        for content in rest:
            node = cls(content, previous_node)
            previous_node.next = node
            by_content[content] = node
            previous_node = node
        previous_node.next = first_node
        first_node.previous = previous_node

        return by_content

    def __init__(self, content, previous, _next=None):
        self.content = content
        self.previous = previous
        self.next = _next

    def replace_next(self, new_next):
        if self.next:
            self.next.previous = None
        if new_next and new_next.previous:
            new_next.previous.next = None
        self.next = new_next
        if new_next:
            new_next.previous = self

    def insert_next(self, new_next, new_last):
        _next = self.next
        self.replace_next(new_next)
        if new_last:
            new_last.replace_next(_next)


challenge = Challenge()
challenge.main()
# challenge.main(sys_args=[None, 'run'])
