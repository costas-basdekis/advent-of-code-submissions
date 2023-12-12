#!/usr/bin/env python3
from dataclasses import dataclass
import re
from functools import cached_property
from typing import Callable, ClassVar, Dict, List, Optional, Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        59336987801432
        """
        return Device.from_text(_input).get_output()


@dataclass
class Device:
    values: Dict[str, Optional[bool]]
    wires: List["Wire"]

    @classmethod
    def from_text(cls, text: str) -> "Device":
        """
        >>> _device = Device.from_text(SMALL_EXAMPLE_TEXT)
        >>> (len(_device.values), len(_device.wires))
        (9, 3)
        """
        gates_str, wires_str = text.strip().split("\n\n")
        values = {
            gate: {"1": True, "0": False}[value]
            for line in gates_str.strip().splitlines()
            for gate, value in [line.strip().split(": ")]
        }
        wires = list(map(Wire.from_text, map(str.strip, wires_str.strip().splitlines())))
        for wire in wires:
            values.setdefault(wire.result, None)
        return cls(values=values, wires=wires)

    def __getitem__(self, key: str) -> Optional[bool]:
        value = self.values[key]
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: bool):
        self.values[key] = value

    def __contains__(self, item: str) -> bool:
        return self.values[item] is not None

    @cached_property
    def wires_by_result(self) -> Dict[str, "Wire"]:
        return{
            wire.result: wire
            for wire in self.wires
        }

    def get_output(self) -> int:
        """
        >>> Device.from_text(SMALL_EXAMPLE_TEXT).get_output()
        4
        >>> Device.from_text(LARGE_EXAMPLE_TEXT).get_output()
        2024
        """
        return self.get_variable("z")

    def get_variable(self, variable: str) -> int:
        return sum(
            1 << index
            for index, value in enumerate(reversed(self.get_variable_values(variable)))
            if value
        )

    def get_variable_values(self, variable: str) -> List[bool]:
        """
        >>> Device.from_text(SMALL_EXAMPLE_TEXT).get_variable_values("z")
        [True, False, False]
        """
        gates = self.get_variable_gates(variable)
        stack = list(gates)
        seen = set(stack)
        while stack:
            gate = stack[-1]
            if gate in self:
                stack.pop()
                continue
            wire = self.wires_by_result[gate]
            dependencies = {wire.left, wire.right}
            if all(dependency in self for dependency in dependencies):
                self[gate] = wire.calculate(self)
                stack.pop()
                continue
            next_items = dependencies - seen
            stack.extend(next_items)
            seen.update(next_items)
        return [self[gate] for gate in gates]

    def get_variable_gates(self, variable: str) -> List[str]:
        """
        >>> Device.from_text(SMALL_EXAMPLE_TEXT).get_variable_gates("z")
        ['z02', 'z01', 'z00']
        """
        return sorted((
            gate
            for gate in self.values
            if gate.startswith(variable)
        ), reverse=True)


@dataclass(frozen=True)
class Wire:
    left: str
    right: str
    result: str
    operator: Callable[[bool, bool], bool]

    re_wire = re.compile(r"^(\w+) (AND|OR|XOR) (\w+) -> (\w+)$")

    operator_map: ClassVar[Dict[str, Callable[[bool, bool], bool]]] = {
        "AND": lambda left, right: left & right,
        "OR": lambda left, right: left | right,
        "XOR": lambda left, right: left ^ right,
    }
    reverse_operator_map: ClassVar[Dict[Callable[[bool, bool], bool], str]] = {
        method: name
        for name, method in operator_map.items()
    }

    @classmethod
    def from_text(cls, text: str) -> "Wire":
        """
        >>> print(Wire.from_text("x00 AND y00 -> z00"))
        x00 AND y00 -> z00
        """
        match = cls.re_wire.match(text.strip())
        if not match:
            raise Exception(f"Could not parse '{text.strip()}'")
        left, operator_str, right, result = match.groups()
        return cls(left=left, right=right, result=result, operator=cls.operator_map[operator_str])

    def __str__(self) -> str:
        return f"{self.left} {self.reverse_operator_map[self.operator]} {self.right} -> {self.result}"

    def calculate(self, device: Device) -> bool:
        left = device[self.left]
        right = device[self.right]
        return self.operator(left, right)


SMALL_EXAMPLE_TEXT = """
    x00: 1
    x01: 1
    x02: 1
    y00: 0
    y01: 1
    y02: 0

    x00 AND y00 -> z00
    x01 XOR y01 -> z01
    x02 OR y02 -> z02
"""


LARGE_EXAMPLE_TEXT = """
    x00: 1
    x01: 0
    x02: 1
    x03: 1
    x04: 0
    y00: 1
    y01: 1
    y02: 1
    y03: 1
    y04: 1

    ntg XOR fgs -> mjb
    y02 OR x01 -> tnw
    kwq OR kpj -> z05
    x00 OR x03 -> fst
    tgd XOR rvg -> z01
    vdt OR tnw -> bfw
    bfw AND frj -> z10
    ffh OR nrd -> bqk
    y00 AND y03 -> djm
    y03 OR y00 -> psh
    bqk OR frj -> z08
    tnw OR fst -> frj
    gnj AND tgd -> z11
    bfw XOR mjb -> z00
    x03 OR x00 -> vdt
    gnj AND wpb -> z02
    x04 AND y00 -> kjc
    djm OR pbm -> qhw
    nrd AND vdt -> hwm
    kjc AND fst -> rvg
    y04 OR y02 -> fgs
    y01 AND x02 -> pbm
    ntg OR kjc -> kwq
    psh XOR fgs -> tgd
    qhw XOR tgd -> z09
    pbm OR djm -> kpj
    x03 XOR y03 -> ffh
    x00 XOR y04 -> ntg
    bfw OR bqk -> z06
    nrd XOR fgs -> wpb
    frj XOR qhw -> z04
    bqk OR frj -> z07
    y03 OR x01 -> nrd
    hwm AND bqk -> z03
    tgd XOR rvg -> z12
    tnw OR pbm -> gnj
"""


Challenge.main()
challenge = Challenge()
