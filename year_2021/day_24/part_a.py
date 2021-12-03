#!/usr/bin/env python3
import re
from operator import add, mul, mod
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Union

from aox.challenge import Debugger
from utils import BaseChallenge, iterable_length, product


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        53999995829399
        """
        return find_maximum_valid_input(debugger=debugger)


InputList = List[int]
State = List[int]


def find_maximum_valid_input(
    debugger: Debugger = Debugger(enabled=False),
) -> int:
    return find_first_valid_input(range(9, 0, -1), debugger=debugger)


def find_first_valid_input(
    digits: Iterable[int], debugger: Debugger = Debugger(enabled=False),
) -> int:
    def get_next_chains(
        _chains: Iterable[Tuple[InputList, int]], _index: int,
    ) -> Iterable[Tuple[InputList, int]]:
        for previous_inputs, previous_state in debugger.stepping(_chains):
            if debugger.should_report():
                debugger.default_report(
                    f"Looking at {''.join(map(str, previous_inputs))}, giving "
                    f"{run_program_optimised(previous_inputs, True)}/"
                    f"{run_program_optimised_list(previous_inputs, True)}",
                )
            for next_input in digits:
                state = get_program_optimised_state(
                    previous_state, _index, next_input,
                )
                if state >= AAC[_index]:
                    continue
                yield previous_inputs + [next_input], state

    chains: Iterable[Tuple[InputList, int]] = (
        ([], 0)
        for _ in range(1)
    )
    for index in range(14):
        chains = get_next_chains(chains, index)

    valid_inputs = (
        _input
        for _input, state in chains
        if not state
    )

    valid_input = next(iter(valid_inputs), None)
    if valid_input is None:
        raise Exception(f"Could not a valid input")

    return int("".join(map(str, valid_input)))


AA = [1, 1, 1, 1, 1, 26, 1, 26, 26, 1, 26, 26, 26, 26]
AAC = [product(AA[i + 1:]) for i in range(len(AA))]
AA2 = [a == 26 for a in AA]
AA2C = [iterable_length(filter(None, AA2[i + 1:])) for i in range(len(AA2))]
BB = [15, 10, 12, 10, 14, -11, 10, -16, -9, 11, -8, -8, -10, -9]
CC = [13, 16, 2, 8, 11, 6, 12, 2, 2, 15, 1, 10, 14, 10]


def run_program_optimised_list(
    inp: List[int], allow_partial_input: bool = False,
) -> List[int]:
    """
    >>> run_program_optimised_list([9] * 14)
    [22, 25, 11, 17, 19]
    >>> run_program_optimised_list([5, 3, 9, 9, 9, 9, 9, 5, 8, 2, 9, 3, 9, 9])
    []
    """
    if not allow_partial_input:
        check_input(inp)

    state = []
    for i in range(len(inp)):
        state = get_program_optimised_list_state(state, i, inp[i])

    return state


def get_program_optimised_list_state(
    previous: List[int], index: int, next_input: int,
) -> List[int]:
    zz = list(previous)
    must_match = (zz[-1] if zz else 0) + BB[index]
    if AA2[index]:
        if zz:
            zz.pop()
    if next_input != must_match:
        zz.append(next_input + CC[index])
        if zz == [0]:
            zz = []
    return zz


def run_program_optimised(
    inp: List[int], allow_partial_input: bool = False,
) -> int:
    """
    >>> run_program_optimised([9] * 14)
    10500769
    >>> run_program_optimised([5, 3, 9, 9, 9, 9, 9, 5, 8, 2, 9, 3, 9, 9])
    0
    """
    if not allow_partial_input:
        check_input(inp)

    state = 0
    for i in range(len(inp)):
        state = get_program_optimised_state(state, i, inp[i])

    return state


def get_program_optimised_state(
    previous: int, index: int, next_input: int,
) -> int:
    z = previous
    must_match = z % 26 + BB[index]
    z //= AA[index]
    if next_input != must_match:
        z = z * 26 + next_input + CC[index]

    return z


def check_input(inp: List[int]) -> None:
    if len(inp) != 14:
        raise Exception(f"Expected 14 numbers, but got {len(inp)}")
    extra_types = set(map(type, inp)) - {int}
    if extra_types:
        extra_types_str = ', '.join(sorted(
            _type.__name__
            for _type in extra_types
        ))
        raise Exception(f"Expected integers but got {extra_types_str}")
    min_inp, max_inp = min(inp), max(inp)
    if min_inp < 1 or max_inp > 9:
        raise Exception(
            f"Expected input to be between 1 and 9, but it was between "
            f"{min_inp} and {max_inp}"
        )


def run_program_loop_python_simplified(
    inp: List[int], allow_partial_input: bool = False,
) -> int:
    """
    >>> run_program_loop_python_simplified([9] * 14)
    10500769
    >>> run_program_loop_python_simplified(
    ...     [5, 3, 9, 9, 9, 9, 9, 5, 8, 2, 9, 3, 9, 9])
    0
    """
    if not allow_partial_input:
        check_input(inp)

    _, variables = run_raw_program_loop_python_simplified(inp)

    return variables["z"]


def run_raw_program_loop_python_simplified(
    inputs: List[int],
) -> Tuple[bool, Dict[str, int]]:
    """
    >>> run_raw_program_loop_python_simplified([9] * 14)
    (True, {'x': 1, 'y': 19, 'z': 10500769, 'w': 9, ...})
    """
    vs: Dict[str, int]
    variables: Dict[str, int]
    vs = variables = {
        "x": 0, "y": 0, "z": 0, "w": 0,
        "a": None, "b": None, "c": None,
    }

    iterable_inputs_and_abc = iter(zip(inputs, AA, BB, CC))

    for _ in range(14):
        try:
            vs["w"], vs["a"], vs["b"], vs["c"] = next(iterable_inputs_and_abc)
        except StopIteration:
            return False, variables
        vs["x"] = vs["z"] % 26 + vs["b"]
        vs["x"] = 0 if (vs["z"] % 26 + vs["b"]) == vs["w"] else 1
        vs["z"] //= vs["a"]
        # noinspection DuplicatedCode
        vs["y"] *= 0
        vs["y"] += 25
        vs["y"] *= vs["x"]
        vs["y"] += 1
        vs["z"] *= vs["y"]
        vs["y"] *= 0
        vs["y"] += vs["w"]
        vs["y"] += vs["c"]
        vs["y"] *= vs["x"]
        vs["z"] += vs["y"]

    return True, variables


def run_program_loop_python(
    inp: List[int], allow_partial_input: bool = False,
) -> int:
    """
    >>> run_program_loop_python([9] * 14)
    10500769
    >>> run_program_loop_python([5, 3, 9, 9, 9, 9, 9, 5, 8, 2, 9, 3, 9, 9])
    0
    """
    if not allow_partial_input:
        check_input(inp)

    _, variables = run_raw_program_loop_python(inp)

    return variables["z"]


def run_raw_program_loop_python(
    inputs: List[int],
) -> Tuple[bool, Dict[str, int]]:
    """
    >>> run_raw_program_loop_python([9] * 14)
    (True, {'x': 1, 'y': 19, 'z': 10500769, 'w': 9, ...})
    """
    vs = variables = {
        "x": 0, "y": 0, "z": 0, "w": 0,
        "a": None, "b": None, "c": None,
    }

    iterable_inputs_and_abc = iter(zip(inputs, AA, BB, CC))

    for _ in range(14):
        try:
            vs["w"], vs["a"], vs["b"], vs["c"] = next(iterable_inputs_and_abc)
        except StopIteration:
            return False, variables
        vs["x"] *= 0
        vs["x"] += vs["z"]
        vs["x"] %= 26
        vs["z"] //= vs["a"]
        vs["x"] += vs["b"]
        vs["x"] = 1 if vs["x"] == vs["w"] else 0
        vs["x"] = 1 if vs["x"] == 0 else 0
        # noinspection DuplicatedCode
        vs["y"] *= 0
        vs["y"] += 25
        vs["y"] *= vs["x"]
        vs["y"] += 1
        vs["z"] *= vs["y"]
        vs["y"] *= 0
        vs["y"] += vs["w"]
        vs["y"] += vs["c"]
        vs["y"] *= vs["x"]
        vs["z"] += vs["y"]

    return True, variables


def run_program_loop(
    inp: List[int], allow_partial_input: bool = False,
) -> int:
    """
    >>> run_program_loop([9] * 14)
    10500769
    >>> run_program_loop([5, 3, 9, 9, 9, 9, 9, 5, 8, 2, 9, 3, 9, 9])
    0
    """
    if not allow_partial_input:
        check_input(inp)

    _, variables = run_raw_program_loop(inp)

    return variables["z"]


def run_raw_program_loop(inputs: List[int]) -> Tuple[bool, Dict[str, int]]:
    """
    >>> run_raw_program_loop([9] * 14)
    (True, {'x': 1, 'y': 19, 'z': 10500769, 'w': 9, ...})
    """
    program_text = """
        inp w
        mul x 0
        add x z
        mod x 26
        div z a
        add x b
        eql x w
        eql x 0
        mul y 0
        add y 25
        mul y x
        add y 1
        mul z y
        mul y 0
        add y w
        add y c
        mul y x
        add z y
    """
    variables = {
        "x": 0, "y": 0, "z": 0, "w": 0,
        "a": None, "b": None, "c": None,
    }

    iterable_inputs_and_abc = iter(zip(inputs, AA, BB, CC))

    # noinspection DuplicatedCode
    def make_parser(
        expression: str,
    ) -> Callable[[str], Optional[Tuple[str, ...]]]:
        regex = re.compile(expression)

        def _parser(_line: str) -> Optional[Tuple[str, ...]]:
            match = regex.match(_line)
            if not match:
                return None

            return tuple(match.groups())

        return _parser

    re_inp = make_parser(r"^inp ([xyzw])$")

    def do_inp(_groups: Tuple[str, ...]) -> bool:
        variable, = _groups
        try:
            (
                variables[variable],
                variables["a"],
                variables["b"],
                variables["c"],
            ) = next(iterable_inputs_and_abc)
        except StopIteration:
            return False

        return True

    # noinspection DuplicatedCode
    def make_do_binary(
        operation: Callable[[int, int], int],
    ) -> Callable[[Tuple[str, ...]], bool]:
        # noinspection DuplicatedCode
        def do_binary(_groups: Tuple[str, ...]) -> bool:
            variable_1, variable_or_value_str_2 = _groups
            if variable_or_value_str_2 in variables:
                value_2 = variables[variable_or_value_str_2]
            else:
                value_str_2 = variable_or_value_str_2
                value_2 = int(value_str_2)

            variables[variable_1] = operation(variables[variable_1], value_2)

            return True

        return do_binary

    re_add = make_parser(r"^add ([xyzw]) ([xyzwabc]|-?\d+)$")
    do_add = make_do_binary(add)

    re_mul = make_parser(r"^mul ([xyzw]) ([xyzwabc]|-?\d+)$")
    do_mul = make_do_binary(mul)

    re_div = make_parser(r"^div ([xyzw]) ([xyzwabc]|-?\d+)$")
    do_div = make_do_binary(lambda lhs, rhs: lhs // rhs)

    re_mod = make_parser(r"^mod ([xyzw]) ([xyzwabc]|-?\d+)$")
    do_mod = make_do_binary(mod)

    re_eql = make_parser(r"^eql ([xyzw]) ([xyzwabc]|-?\d+)$")
    do_eql = make_do_binary(lambda lhs, rhs: 1 if lhs == rhs else 0)

    parsers_and_makers = [
        (re_inp, do_inp),
        (re_add, do_add),
        (re_mul, do_mul),
        (re_div, do_div),
        (re_mod, do_mod),
        (re_eql, do_eql),
    ]

    # noinspection DuplicatedCode
    for _ in range(14):
        # noinspection DuplicatedCode
        lines = filter(None, map(str.strip, program_text.splitlines()))
        for line in lines:
            for parser, maker in parsers_and_makers:
                groups = parser(line)
                if groups is None:
                    continue
                if not maker(groups):
                    return False, variables
                break
            else:
                raise Exception(f"Could not parse '{line}'")

    return True, variables


def run_program(
    inp: List[int], allow_partial_input: bool = False,
) -> int:
    """
    >>> run_program([5, 3, 9, 9, 9, 9, 9, 5, 8, 2, 9, 3, 9, 9])
    0
    """
    if not allow_partial_input:
        check_input(inp)

    _, variables = run_raw_program(inp)

    return variables["z"]


def run_raw_program(inputs: List[int]) -> Tuple[bool, Dict[str, int]]:
    """
    >>> run_raw_program([9] * 14)
    (True, {'x': 1, 'y': 19, 'z': 10500769, 'w': 9})
    """
    program_text = (Path(__file__).parent / 'input.txt').read_text()
    variables = {"x": 0, "y": 0, "z": 0, "w": 0}

    iterable_inputs = iter(inputs)

    # noinspection DuplicatedCode
    def make_parser(
        expression: str,
    ) -> Callable[[str], Optional[Tuple[str, ...]]]:
        regex = re.compile(expression)

        def _parser(_line: str) -> Optional[Tuple[str, ...]]:
            match = regex.match(_line)
            if not match:
                return None

            return tuple(match.groups())

        return _parser

    re_inp = make_parser(r"^inp ([xyzw])$")

    def do_inp(_groups: Tuple[str, ...]) -> bool:
        variable, = _groups
        try:
            variables[variable] = next(iterable_inputs)
        except StopIteration:
            return False

        return True

    # noinspection DuplicatedCode
    def make_do_binary(
        operation: Callable[[int, int], int],
    ) -> Callable[[Tuple[str, ...]], bool]:
        # noinspection DuplicatedCode
        def do_binary(_groups: Tuple[str, ...]) -> bool:
            variable_1, variable_or_value_str_2 = _groups
            if variable_or_value_str_2 in variables:
                value_2 = variables[variable_or_value_str_2]
            else:
                value_str_2 = variable_or_value_str_2
                value_2 = int(value_str_2)

            variables[variable_1] = operation(variables[variable_1], value_2)

            return True

        return do_binary

    re_add = make_parser(r"^add ([xyzw]) ([xyzw]|-?\d+)$")
    do_add = make_do_binary(add)

    re_mul = make_parser(r"^mul ([xyzw]) ([xyzw]|-?\d+)$")
    do_mul = make_do_binary(mul)

    re_div = make_parser(r"^div ([xyzw]) ([xyzw]|-?\d+)$")
    do_div = make_do_binary(lambda lhs, rhs: lhs // rhs)

    re_mod = make_parser(r"^mod ([xyzw]) ([xyzw]|-?\d+)$")
    do_mod = make_do_binary(mod)

    re_eql = make_parser(r"^eql ([xyzw]) ([xyzw]|-?\d+)$")
    do_eql = make_do_binary(lambda lhs, rhs: 1 if lhs == rhs else 0)

    parsers_and_makers = [
        (re_inp, do_inp),
        (re_add, do_add),
        (re_mul, do_mul),
        (re_div, do_div),
        (re_mod, do_mod),
        (re_eql, do_eql),
    ]

    # noinspection DuplicatedCode
    lines = filter(None, map(str.strip, program_text.splitlines()))
    for line in lines:
        for parser, maker in parsers_and_makers:
            groups = parser(line)
            if groups is None:
                continue
            if not maker(groups):
                return False, variables
            break
        else:
            raise Exception(f"Could not parse '{line}'")

    return True, variables


Challenge.main()
challenge = Challenge()
