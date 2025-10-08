#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from itertools import permutations
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar, Iterator,
)

import click

from aox.challenge import Debugger
from aox.styling.shortcuts import e_error
from utils import (
    BaseIcpcChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)


class Challenge(BaseIcpcChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        '1 3 2 7 5 6 4\\n7 1 5 3 2 6 4'
        """
        heap = Heap.from_text(_input)
        # return heap.get_min_and_max_sequence_string()
        min_and_max_sequences = heap.get_min_and_max_sequences(debugger=debugger)
        if not min_and_max_sequences:
            return "impossible"
        min_sequence, max_sequence = min_and_max_sequences
        return f"{' '.join(map(str, min_sequence))}\n{' '.join(map(str, max_sequence))}"

    def play(self):
        self.undo()

    def build_up(self):
        heap = None
        while True:
            value = click.prompt('Enter a number', type=str)
            if heap is None:
                heap = Heap.from_value(value)
            else:
                heap = heap.insert(value)
            print(heap)

    def undo(self):
        heap = Heap.from_values_text("4 9 1 10 8 15 13 2 12 3 5 11 6 14 7")
        while True:
            print(heap)
            possible_removals = list(heap.iterate_undoable_values())
            # print(possible_removals)
            value = int(click.prompt("Enter a number", type=click.Choice(list(map(str, possible_removals)))))
            _, next_heap = heap.undo_insert(value)
            if not next_heap:
                break
            check_heap = next_heap.insert(value)
            if check_heap != heap:
                print(e_error(f"New heap doesn't match old heap after insertion: {check_heap}"))
            heap = next_heap


@dataclass
class Heap:
    value: int
    left: Optional["Heap"]
    right: Optional["Heap"]

    @classmethod
    def from_text(cls, text: str) -> "Heap":
        """
        >>> print(Heap.from_text('''
        ...     7
        ...     2 3
        ...     4 5
        ...     6 7
        ...     0 0
        ...     0 0
        ...     0 0
        ...     0 0
        ... '''))
        1[2[4,5],3[6,7]]
        """
        lines = iter(map(str.strip, text.strip().splitlines()))
        count = int(next(lines))
        nodes_by_id = {
            index: cls.from_value(index)
            for index in range(1, count + 1)
        }
        for index, line in enumerate(lines, start=1):
            left, right = map(int, line.split(" "))
            if left != 0:
                nodes_by_id[index].left = nodes_by_id[left]
            if right != 0:
                nodes_by_id[index].right = nodes_by_id[right]
        return nodes_by_id[1]

    @classmethod
    def from_values_text(cls, text: str) -> "Heap":
        """
        >>> print(Heap.from_values_text("1 3 2 7 5 6 4"))
        1[2[4,5],3[6,7]]
        >>> print(Heap.from_values_text("7 1 5 3 2 6 4"))
        1[2[4,5],3[6,7]]
        """
        return cls.from_values(list(map(int, text.strip().split(" "))))

    @classmethod
    def from_values(cls, values: List[int]) -> "Heap":
        """
        >>> print(Heap.from_values_text("4 9 1 10 8 15 13 2 12 3 5 11 6 14 7"))
        1[4[5[7,9[13]],6[8[12]]],2[3[14],10[11,15]]]
        >>> print(Heap.from_values_text("13 4 1 15 12 10 9 2 8 14 5 11 6 3 7"))
        1[4[5[7,9[13]],6[8[12]]],2[3[14],10[11,15]]]
        >>> print(Heap.from_text('''
        ...     15
        ...     4 2
        ...     3 10
        ...     14 0
        ...     5 6
        ...     7 9
        ...     8 0
        ...     0 0
        ...     12 0
        ...     13 0
        ...     11 15
        ...     0 0
        ...     0 0
        ...     0 0
        ...     0 0
        ...     0 0
        ... '''))
        1[4[5[7,9[13]],6[8[12]]],2[3[14],10[11,15]]]
        """
        if not values:
            raise Exception(f"No values passed")
        heap = cls.from_value(values[0])
        return heap.insert_many(values[1:])

    @classmethod
    def from_value(cls, value: int) -> "Heap":
        return cls(value=value, left=None, right=None)

    def __str__(self) -> str:
        return self.show()

    def __iter__(self) -> Iterator[int]:
        queue = [self]
        while queue:
            item = queue.pop(0)
            yield item.value
            if item.left:
                queue.append(item.left)
            if item.right:
                queue.append(item.right)

    def show(self, verbose: bool = False, indent: str = "") -> str:
        """
        >>> print(Heap.from_text('''
        ...     7
        ...     2 3
        ...     4 5
        ...     6 7
        ...     0 0
        ...     0 0
        ...     0 0
        ...     0 0
        ... ''').show(verbose=True))
        1
         * 2
           * 4
             * None
             * None
           * 5
             * None
             * None
         * 3
           * 6
             * None
             * None
           * 7
             * None
             * None
        """
        if verbose:
            return "{}{}{}".format(
                self.value,
                f" * {self.left.show(indent=indent + '  ', verbose=verbose)}" if self.left else " * None",
                f" * {self.right.show(indent=indent + '  ', verbose=verbose)}" if self.right else " * None",
            )
        return (
            f"{self.value}"
            f"{'[' if self.left or self.right else ''}"
            f"{self.left.show(verbose=verbose) if self.left else ''}"
            f"{',' if self.right else ''}"
            f"{self.right.show(verbose=verbose) if self.right else ''}"
            f"{']' if self.right or self.left else ''}"
        )

    def insert_many(self, values: List[int]) -> "Heap":
        heap = self
        for value in values:
            heap = heap.insert(value)
        return heap

    def insert(self, value: int) -> "Heap":
        """
        >>> print(Heap.from_values_text("4 9 1 10 8 15").insert(13))
        1[4[9[13],8],10[15]]
        """
        if self.value < value:
            return Heap(value=self.value, left=self.right.insert(value) if self.right else Heap.from_value(value), right=self.left)
        return Heap(value=value, left=self, right=None)

    def undo_insert(self, value: int) -> Tuple[bool, Optional["Heap"]]:
        if value == self.value:
            if self.right:
                return False, None
            return True, self.left
        if value < self.value:
            return False, None
        if not self.left:
            return False, None
        stack = [self, self.left]
        while True:
            item = stack[-1]
            if value == item.value:
                if item.right:
                    return False, None
                stack[-1] = item.left
                break
            if value < item.value:
                return False, None
            if not item.left:
                return False, None
            stack.append(item.left)
        while len(stack) > 1:
            last_item = stack.pop()
            item = stack[-1]
            stack[-1] = Heap(value=item.value, left=item.right, right=last_item)
        return True, stack[0]

    def iterate_undoable_values(self) -> Iterable[int]:
        item = self
        while item:
            if not item.right:
                yield item.value
                if item.left and not item.left.left and not item.left.right:
                    yield item.left.value
                break
            item = item.left

    def get_min_and_max_sequence_string(self) -> str:
        min_sequence_string = self.get_min_sequence_string()
        if min_sequence_string is None:
            return "impossible"
        max_sequence_string = self.get_max_sequence_string()
        if max_sequence_string is None:
            return "impossible"
        return min_sequence_string + "\n" + max_sequence_string

    def get_min_sequence_string(self) -> Optional[str]:
        return self.get_sequence_string(max)

    def get_max_sequence_string(self) -> Optional[str]:
        return self.get_sequence_string(min)

    def get_sequence_string(self, choice_func: Callable) -> Optional[str]:
        sequence_str = ""
        for value in self.iterate_sequence(choice_func):
            if value is None:
                return None
            if not sequence_str:
                sequence_str = str(value)
                continue
            sequence_str = f"{value} " + sequence_str
        return sequence_str

    def get_min_and_max_sequences(self, debugger: Debugger = Debugger(enabled=False)) -> Optional[Tuple[List[int], List[int]]]:
        """
        >>> Heap.from_values_text("4 9 1 10 8 15 13 2 12 3 5 11 6 14 7").get_min_and_max_sequences()
        ([4, 9, 1, 10, 8, 15, 13, 2, 12, 3, 5, 11, 6, 14, 7],
            [13, 4, 1, 15, 12, 10, 9, 2, 8, 14, 5, 11, 6, 3, 7])
        >>> Heap.from_text('''
        ...     15
        ...     4 2
        ...     3 10
        ...     14 0
        ...     5 6
        ...     7 9
        ...     8 0
        ...     0 0
        ...     12 0
        ...     13 0
        ...     11 15
        ...     0 0
        ...     0 0
        ...     0 0
        ...     0 0
        ...     0 0
        ... ''').get_min_and_max_sequences()
        ([4, 9, 1, 10, 8, 15, 13, 2, 12, 3, 5, 11, 6, 14, 7],
            [13, 4, 1, 15, 12, 10, 9, 2, 8, 14, 5, 11, 6, 3, 7])
        """
        min_sequence = self.get_min_sequence()
        if min_sequence is None:
            return None
        max_sequence = self.get_max_sequence()
        if max_sequence is None:
            return None
        return min_sequence, max_sequence

    def get_min_sequence(self) -> Optional[List[int]]:
        sequence = []
        for value in self.iterate_min_sequence():
            if value is None:
                return None
            sequence.append(value)
        return list(reversed(sequence))

    def iterate_min_sequence(self) -> Iterable[Optional[int]]:
        return self.iterate_sequence(max)

    def get_max_sequence(self) -> Optional[List[int]]:
        sequence = []
        for value in self.iterate_max_sequence():
            if value is None:
                return None
            sequence.append(value)
        return list(reversed(sequence))

    def iterate_max_sequence(self) -> Iterable[Optional[int]]:
        return self.iterate_sequence(min)

    def iterate_sequence(self, choice_func: Callable) -> Iterable[Optional[int]]:
        heap = self
        while heap:
            next_value = choice_func(heap.iterate_undoable_values(), default=None)
            if next_value is None:
                yield None
                return
            yield next_value
            _, heap = heap.undo_insert(next_value)

    def get_min_and_max_sequences_by_iterating(self, debugger: Debugger = Debugger(enabled=False)) -> Optional[Tuple[List[int], List[int]]]:
        sequences = iter(self.iterate_possible_sequences(debugger=debugger))
        for sequence in sequences:
            min_sequence = max_sequence = list(sequence)
            break
        else:
            return None
        for sequence in sequences:
            if sequence < min_sequence:
                min_sequence = list(sequence)
            elif sequence > max_sequence:
                max_sequence = list(sequence)
        return min_sequence, max_sequence

    def iterate_possible_sequences(self, debugger: Debugger = Debugger(enabled=False)) -> Iterable[List[int]]:
        debugger.default_report_if(f"Checking sequences of length {sum(1 for _ in self)}")
        stack = [(self, iter(self.iterate_undoable_values()))]
        path = []
        while stack:
            heap, values = stack[-1]
            for value in debugger.stepping(values):
                if debugger.should_report():
                    debugger.default_report_if(f"At level {len(path)}")
                removed, next_heap = heap.undo_insert(value)
                if not removed:
                    continue
                path.insert(0, value)
                if not next_heap:
                    yield path
                    path.pop(0)
                    continue
                stack.append((next_heap, iter(next_heap.iterate_undoable_values())))
                break
            else:
                stack.pop()
                if not stack:
                    break
                path.pop(0)


Challenge.main()
challenge = Challenge()
