#!/usr/bin/env python3
from itertools import groupby, combinations, permutations
from typing import Dict, List, Optional, Set, Tuple, Union

import click
import pyperclip

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_24 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        'ctg,dmh,dvq,rpb,rpv,z11,z31,z38'
        """
        return 'ctg,dmh,dvq,rpb,rpv,z11,z31,z38'

    def play(self):
        device = DeviceExtended.from_text(self.input)
        """
        z00 =
        y00 XOR x00
        p00
        o00 = r0
        
        z01 =
        ((x01 XOR y01) XOR (x00 AND y00))
        p01 XOR r00
        p01 XOR o00
        o01 = ((p01 AND o00) OR r01)
        
        z02 =
        ((y02 XOR x02) XOR (((x01 XOR y01) AND (x00 AND y00)) OR (y01 AND x01)))
        p02 XOR ((p01 AND r00) OR r01)
        p02 XOR o01
        o02 = ((p02 AND o01) OR r02)
        
        z03 =
        ((x03 XOR y03) XOR (((y02 XOR x02) AND (((x01 XOR y01) AND (x00 AND y00)) OR (y01 AND x01))) OR (y02 AND x02)))
        p03 XOR ((p02 AND ((p01 AND r00) OR r01)) OR r02)
        p03 XOR ((p02 AND o01) OR r02)
        p03 XOR o02
        o03 = ((p03 AND o02) OR r03)
        
        z04 =
        ((((x03 XOR y03) AND (((y02 XOR x02) AND (((x01 XOR y01) AND (x00 AND y00)) OR (y01 AND x01))) OR (y02 AND x02))) OR (y03 AND x03)) XOR (x04 XOR y04))
        (((p03 AND ((p02 AND ((p01 AND r00) OR r01)) OR r02)) OR r03) XOR p04)
        (((p03 AND ((p02 AND ((p01 AND o00) OR r01)) OR r02)) OR r03) XOR p04)
        (((p03 AND o02) OR r03) XOR p04)
        p04 XOR ((p03 AND o02) OR r03)
        p04 XOR o03
        o04 = ((p04 AND o03) OR r04)
        
        z(n) = 
            n > 0: p(n) XOR o(n - 1)
            n = 0: p(n)
        p(n) = x(n) XOR y(n)
        o(n) = 
            n > 0: ((p(n) AND o(n - 1)) OR r(n))
            n = 0: r(n)
        r(n) = x(n) AND y(n)
        """
        device = device.swap_wires_by_name([
            ('z11', 'rpv'),
            ('ctg', 'rpb'),
            ('z31', 'dmh'),
            ('z38', 'dvq'),
            # ('bvk', 'hhv'),
        ])
        # self.swap_8_wires(device)
        self.show_diff(device)
        # self.compare_expressions(device)
        self.copy_graph(device)

    def compare_expressions(self, device: "DeviceExtended"):
        actual_device = device.sort()
        expected_device = device.get_expected_device()#.remap(actual_device)
        actual_map = {
            expression: list(wires)
            for expression, wires in groupby(sorted((
                wire
                for wire in actual_device.wires
                # if not wire.result.startswith("z")
            ), key=actual_device.get_wire_expression), key=actual_device.get_wire_expression)
        }
        expected_map = {
            expression: list(wires)
            for expression, wires in groupby(sorted((
                wire
                for wire in expected_device.wires
                # if not wire.result.startswith("z")
            ), key=expected_device.get_wire_expression), key=expected_device.get_wire_expression)
        }
        actual_duplicates = {
            expression: wires
            for expression, wires in actual_map.items()
            if len(wires) > 1
        }
        expected_duplicates = {
            expression: wires
            for expression, wires in expected_map.items()
            if len(wires) > 1
        }
        missing_from_actual = sorted(set(expected_map) - set(actual_map), key=lambda gate: min(expected_map[gate], key=lambda wire: wire.result).result)
        missing_from_expected = sorted(set(actual_map) - set(expected_map), key=lambda gate: min(actual_map[gate], key=lambda wire: wire.result).result)
        if actual_duplicates:
            print(f"{len(actual_duplicates)} {click.style('Actual duplicates', fg='red')}:\n" + "\n".join(f" * {expression}: {wires}" for expression, wires in actual_duplicates.items()))
        else:
            print(click.style("No actual duplicates", fg="green"))
        if expected_duplicates:
            print(f"{len(expected_duplicates)} {click.style('Expected duplicates', fg='red')}:\n" + "\n".join(f" * {expression}: {wires}" for expression, wires in expected_duplicates.items()))
        else:
            print(click.style("No expected duplicates", fg="green"))
        if missing_from_actual:
            print(f"{len(missing_from_actual)} {click.style('Missing from actual', fg='red')}:\n" + "\n".join(f" * {', '.join(wire.result for wire in wires)}" for expression in missing_from_actual for wires in [expected_map[expression]]))
        else:
            print(click.style("No missing from actual", fg="green"))
        if missing_from_expected:
            print(f"{len(missing_from_expected)} {click.style('Missing from expected', fg='red')}:\n" + "\n".join(f" * {', '.join(wire.result for wire in wires)}" for expression in missing_from_expected for wires in [actual_map[expression]]))
        else:
            print(click.style("No missing from expected", fg="green"))

    def show_diff(self, device: "DeviceExtended"):
        sorted_device = device.sort()
        expected_device = device.get_expected_device().sort()#.remap(sorted_device)
        _, unneeded_red_style, _ = (click.style("!", fg="red") + click.style("!", fg="red")).split("!")
        _, unneeded_yellow_style, _ = (click.style("!", fg="yellow") + click.style("!", fg="yellow")).split("!")
        difference_count = 0
        for gate in device.get_variable_gates("z"):
            actual_expression = sorted_device.get_gate_expression(gate)
            expected_expression = expected_device.get_gate_expression(gate)
            annotated_actual_expression = "".join(
                actual
                if actual == expected else
                click.style(actual, fg="red")
                for actual, expected in zip(actual_expression, expected_expression.ljust(len(actual_expression), "!"))
            ).replace(unneeded_red_style, "")
            annotated_expected_expression = "".join(
                expected
                if actual == expected else
                click.style(expected, fg="yellow")
                for actual, expected in zip(actual_expression.ljust(len(expected_expression), "!"), expected_expression)
            ).replace(unneeded_yellow_style, "")
            difference = sorted_device.find_difference(gate, expected_device, gate)
            if difference:
                difference_count += 1
                print(f"{click.style(gate, fg='red')}: {annotated_actual_expression}")
                print(f"{click.style(gate, fg='yellow')}: {annotated_expected_expression}")
                if isinstance(difference, list):
                    print("\n".join(f" {click.style('*', fg='red')} {d}" for d in difference))
                elif isinstance(difference, tuple):
                    print(f" {click.style('*', fg='red')} {difference[0]} vs {difference[1]} = {difference[2]}")
        if difference_count > 0:
            print(f"{click.style(str(difference_count), fg='red')} differences found")
        else:
            print(click.style(f"Everything matches up!", fg="green"))

    def swap_8_wires(self, device: "DeviceExtended") -> None:
        x = device.get_variable("x")
        y = device.get_variable("y")
        z = device.get_variable("z")
        print(f"{x} + {y} =? {z} != {x + y}")
        highlighted_bin_z, highlighted_bin_x_plus_y = self.highlight_numbers(z, x + y)
        wrong_output_gates = device.get_wrong_output_gates()
        print(f"{bin(x)} + {bin(y)} =?\n{highlighted_bin_z} !=\n{highlighted_bin_x_plus_y}\nWrong outputs ({len(wrong_output_gates)}): {', '.join(wrong_output_gates)}")
        # self.print_dependency_tree("z11", device)
        print(self.get_count_counts(device, wrong_output_gates))
        x = device.get_variable("x")
        y = device.get_variable("y")
        wrong_output_gates = device.get_wrong_output_gates()
        true_wrong_output_gates_2 = [
            gate
            for gate in set(wrong_output_gates) & {wire.result for wire in device.get_gates_dependency_counts(wrong_output_gates)}
            if device[gate]
        ]
        false_wrong_output_gates_2 = list(set(wrong_output_gates) - set(true_wrong_output_gates_2))
        if not true_wrong_output_gates_2 or not false_wrong_output_gates_2:
            print(f"{len(true_wrong_output_gates_2)} true gates and {len(false_wrong_output_gates_2)} false gates")
            return
        swapped_gates_2 = true_wrong_output_gates_2[0], false_wrong_output_gates_2[0]
        swapped_wires_2 = [device.wires_by_result[gate] for gate in swapped_gates_2]
        device_2 = device.swap_wires([swapped_wires_2])
        z_2 = device_2.get_output()
        highlighted_bin_z_2, highlighted_bin_x_plus_y_2 = self.highlight_numbers(z_2, x + y)
        wrong_output_gates_2 = device_2.get_wrong_output_gates()
        print(f"Chose {', '.join(swapped_gates_2)} with values {', '.join(map(str, [device_2[gate] for gate in swapped_gates_2]))}")
        print(f"{bin(x)} + {bin(y)} =?\n{highlighted_bin_z_2} !=\n{highlighted_bin_x_plus_y_2}\nWrong outputs ({len(wrong_output_gates_2)}): {', '.join(wrong_output_gates_2)}")
        print(self.get_count_counts(device_2, wrong_output_gates_2))

        true_wrong_output_gates_3 = [
            gate
            for gate in (set(wrong_output_gates_2) & {wire.result for wire in device_2.get_gates_dependency_counts(wrong_output_gates_2)}) - set(swapped_gates_2)
            if device_2[gate]
        ]
        false_wrong_output_gates_3 = list(set(wrong_output_gates_2) - set(true_wrong_output_gates_3))
        if not true_wrong_output_gates_3 or not false_wrong_output_gates_3:
            print(f"{len(true_wrong_output_gates_3)} true gates and {len(false_wrong_output_gates_3)} false gates")
            return
        swapped_gates_3 = true_wrong_output_gates_3[0], false_wrong_output_gates_3[0]
        swapped_wires_3 = [device.wires_by_result[gate] for gate in swapped_gates_3]
        device_3 = device.swap_wires([swapped_wires_3])
        z_3 = device_3.get_output()
        highlighted_bin_z_3, highlighted_bin_x_plus_y_3 = self.highlight_numbers(z_3, x + y)
        wrong_output_gates_3 = device_3.get_wrong_output_gates()
        print(f"Chose {', '.join(swapped_gates_3)} with values {', '.join(map(str, [device_3[gate] for gate in swapped_gates_3]))}")
        print(f"{bin(x)} + {bin(y)} =?\n{highlighted_bin_z_3} !=\n{highlighted_bin_x_plus_y_3}\nWrong outputs ({len(wrong_output_gates_3)}): {', '.join(wrong_output_gates_3)}")
        print(self.get_count_counts(device_3, wrong_output_gates_3))

        true_wrong_output_gates_4 = [
            gate
            for gate in (set(wrong_output_gates_3) & {wire.result for wire in device_3.get_gates_dependency_counts(wrong_output_gates_3)}) - set(swapped_gates_2) - set(swapped_gates_3)
            if device_3[gate]
        ]
        false_wrong_output_gates_4 = list(set(wrong_output_gates_3) - set(true_wrong_output_gates_4))
        if not true_wrong_output_gates_4 or not false_wrong_output_gates_4:
            print(f"{len(true_wrong_output_gates_4)} true gates and {len(false_wrong_output_gates_4)} false gates")
            return
        swapped_gates_4 = true_wrong_output_gates_4[0], false_wrong_output_gates_4[0]
        swapped_wires_4 = [device.wires_by_result[gate] for gate in swapped_gates_4]
        device_4 = device.swap_wires([swapped_wires_4])
        z_4 = device_4.get_output()
        highlighted_bin_z_4, highlighted_bin_x_plus_y_4 = self.highlight_numbers(z_4, x + y)
        wrong_output_gates_4 = device_4.get_wrong_output_gates()
        print(f"Chose {', '.join(swapped_gates_4)} with values {', '.join(map(str, [device_4[gate] for gate in swapped_gates_4]))}")
        print(f"{bin(x)} + {bin(y)} =?\n{highlighted_bin_z_4} !=\n{highlighted_bin_x_plus_y_4}\nWrong outputs ({len(wrong_output_gates_4)}): {', '.join(wrong_output_gates_4)}")
        print(self.get_count_counts(device_4, wrong_output_gates_4))

    def get_count_counts(self, device: "DeviceExtended", wrong_output_gates: List[str]) -> Dict[int, int]:
        return  {
            count: len(list(items))
            for count, items in groupby(sorted(device.get_gates_dependency_counts(wrong_output_gates).values()))
        }

    def copy_graph(self, device: "DeviceExtended") -> None:
        wrong_output_gates = device.get_wrong_output_gates()
        z_gates = device.get_variable_gates("z")
        shape_map = {"AND": "square", "XOR": "diamond", "OR": "circle", None: "invhouse"}
        graph = "\n".join([
            f"{gate}["
            f"label=\"{gate}\\n{part_a.Wire.reverse_operator_map[device.wires_by_result[gate].operator] if gate in device.wires_by_result else ''}\""
            f",shape={shape_map[part_a.Wire.reverse_operator_map[device.wires_by_result[gate].operator] if gate in device.wires_by_result else None]}"
            f"{',style=filled,fillcolor=red' if gate in wrong_output_gates else ''}"
            f"{',color=blue' if gate in z_gates else ''}"
            f"];"
            for gate in device.values
        ] + [
            f"{wire.result} -> {wire.left}, {wire.right};"
            for wire in device.wires
        ])
        pyperclip.copy(graph)
        print(f"Copied {len(graph)} characters to clipboard, paste into https://dreampuf.github.io/GraphvizOnline/")

    def print_dependency_tree(self, gate: str, device: "DeviceExtended", indent: str = ""):
        print(gate)
        wire = device.wires_by_result.get(gate)
        if not wire:
            return
        for next_gate in [wire.left, wire.right]:
            print(f"{indent} * ", end="")
            self.print_dependency_tree(next_gate, device, indent + "  ")

    def highlight_numbers(self, actual: int, expected: int) -> Tuple[str, str]:
        bin_actual = bin(actual)
        bin_expected = bin(expected)
        highlighted_actual = "0b{}".format(
            "".join(
                (
                    click.style(digit, fg="red")
                    if digit != other_digit else
                    digit
                )
                for index, digit in enumerate(bin_actual[2:], start=2)
                for binary_index in [len(bin_actual) - index]
                for other_index in [len(bin_expected) - binary_index]
                for other_digit in [bin_expected[other_index] if other_index < len(bin_expected) else ""]
            )
        )
        highlighted_expected = "0b{}".format(
            "".join(
                (
                    click.style(digit, fg="yellow")
                    if digit != other_digit else
                    digit
                )
                for index, digit in enumerate(bin_expected[2:], start=2)
                for binary_index in [len(bin_expected) - index]
                for other_index in [len(bin_actual) - binary_index]
                for other_digit in [bin_actual[other_index] if other_index < len(bin_actual) else ""]
            )
        )
        return highlighted_actual, highlighted_expected


class DeviceExtended(part_a.Device):
    def find_difference(self, self_gate: str, other: "DeviceExtended", other_gate: str) -> Optional[Union[Tuple[str, str, List[str]], List[str]]]:
        self_wire = self.wires_by_result[self_gate]
        other_wire = other.wires_by_result[other_gate]
        self_left_expression = self.get_gate_expression(self_wire.left)
        self_right_expression = self.get_gate_expression(self_wire.right)
        other_left_expression = other.get_gate_expression(other_wire.left)
        other_right_expression = other.get_gate_expression(other_wire.right)
        if self_left_expression == other_left_expression and self_wire.operator == other_wire.operator and self_right_expression == other_right_expression:
            return None
        if self_left_expression == other_left_expression and self_right_expression == other_right_expression:
            gates_by_expression = {
                expression: list(gates)
                for expression, gates in groupby(sorted(self.values, key=self.get_gate_expression), key=self.get_gate_expression)
            }
            return self_wire.result, other_wire.result, gates_by_expression[other.get_wire_expression(other_wire)]
        if self_wire.operator == other_wire.operator and self_right_expression == other_right_expression:
            return self.find_difference(self_wire.left, other, other_wire.left)
        if self_left_expression == other_left_expression and self_wire.operator == other_wire.operator:
            return self.find_difference(self_wire.right, other, other_wire.right)
        gates_by_expression = {
            expression: list(gates)
            for expression, gates in groupby(sorted(self.values, key=self.get_gate_expression), key=self.get_gate_expression)
        }
        return list(filter(None, [
            f"left {self_left_expression} vs {other_left_expression}" if self_left_expression != other_left_expression else None,
            f"operator {self_wire.reverse_operator_map[self_wire.operator]} vs {other_wire.reverse_operator_map[other_wire.operator]}" if self_wire.operator != other_wire.operator else None,
            f"right {self_right_expression} vs {other_right_expression}" if self_right_expression != other_right_expression else None,
            f"result {self_wire.result} vs " + ", ".join(gates_by_expression[other.get_wire_expression(other_wire)]) if other.get_wire_expression(other_wire) in gates_by_expression else None,
            f"left {self_wire.left} vs " + ", ".join(gates_by_expression[other_left_expression]) if other_left_expression in gates_by_expression else None,
            f"right {self_wire.right} vs " + ", ".join(gates_by_expression[other_right_expression]) if other_right_expression in gates_by_expression else None,
        ]))

    def remap(self, other: "DeviceExtended") -> "DeviceExtended":
        if len(self.wires) != len(other.wires):
            raise Exception(f"Self has {len(self.wires)} and other has {len(other.wires)} wires")
        other_wire_name_by_expression = {
            other.get_wire_expression(wire): wire.result
            for wire in other.wires
        }
        if len(other_wire_name_by_expression) != len(other.wires):
            raise Exception(f"Expected {len(other.wires)} wires to have unique expressions, but there were only {len(other_wire_name_by_expression)} distinct ones")
        self_wire_name_by_expression = {
            self.get_wire_expression(wire): wire.result
            for wire in self.wires
        }
        if len(self_wire_name_by_expression) != len(self.wires):
            raise Exception(f"Expected {len(self.wires)} wires to have unique expressions, but there were only {len(self_wire_name_by_expression)} distinct ones")
        if set(other_wire_name_by_expression) != set(self_wire_name_by_expression):
            raise Exception(f"Expressions don't match")
        translation_map = {
            old_name: new_name
            for expression, old_name in self_wire_name_by_expression.items()
            for new_name in [other_wire_name_by_expression[expression]]
        }
        translation_map.update({
            name: name
            for names in [self.get_variable_gates("x"), self.get_variable_gates("y")]
            for name in names
        })
        values = {
            translation_map[gate]: value
            for gate, value in self.values.items()
        }
        wires = [
            part_a.Wire(translation_map[wire.left], translation_map[wire.right], translation_map[wire.result], wire.operator)
            for wire in self.wires
        ]
        return DeviceExtended(values=values, wires=wires)

    def sort(self) -> "DeviceExtended":
        wires = [
            part_a.Wire(left, right, wire.result, wire.operator)
            for wire in self.wires
            for left, right in [sorted([wire.left, wire.right], key=self.get_gate_expression)]
        ]
        values = dict(self.values)
        return DeviceExtended(values=values, wires=wires)

    def get_expected_device(self) -> "DeviceExtended":
        pass
        """
        z(n) = 
            n = c - 1: o(n - 1)
            n > 0: p(n) XOR o(n - 1)
            n = 0: p(n)
        p(n) = x(n) XOR y(n)
        o(n) = 
            n > 0: ((p(n) AND o(n - 1)) OR r(n))
            n = 0: r(n)
        r(n) = x(n) AND y(n)        
        """
        count = len(self.get_variable_values("z"))
        values = {
            gate: None
            for index in range(count)
            for prefix in ['x', 'y', 'z', 'p', 'o', 'r', 'a']
            for gate in [self._n((prefix, index))]
            if gate not in ['o00', 'p00']
        }
        wires = [
            wire
            for index in range(count)
            for method in [self.z_n, self.p_n, self.o_n, self.r_n]
            if (method, index) not in [(self.o_n, 0), (self.p_n, 0)]
            for wire in method(index)
        ]
        return DeviceExtended(values=values, wires=wires).sort()

    def z_n(self, n: int) -> List[part_a.Wire]:
        if n == 0:
            return [self._m(('x', n), "XOR", ('y', n), ('z', n))]
        return [self._m(('p', n), "XOR", ('o', n - 1), ('z', n))]

    def p_n(self, n: int) -> List[part_a.Wire]:
        return [self._m(('x', n), "XOR", ('y', n), ('p', n))]

    def o_n(self, n: int) -> List[part_a.Wire]:
        if n == 0:
            return [self._m(('x', n), "AND", ('y', n), ('o', n))]
        return [
            self._m(('p', n), "AND", ('o', n - 1), ('a', n)),
            self._m(('a', n), "OR", ('r', n), ('o', n)),
        ]

    def r_n(self, n: int) -> List[part_a.Wire]:
        return [self._m(('x', n), "AND", ('y', n), ('r', n))]

    def x_n(self, n: int) -> str:
        return self._n(('x', n))

    def y_n(self, n: int) -> str:
        return self._n(('y', n))

    def _m(self, left: Tuple[str, int], operator: str, right: Tuple[str, int], result: Tuple[str, int]) -> part_a.Wire:
        replacement_map = {
            'o00': 'r00',
            'p00': 'z00',
        }
        left_n = self._n(left)
        left_n = replacement_map.get(left_n, left_n)
        right_n = self._n(right)
        right_n = replacement_map.get(right_n, right_n)
        result_n = self._n(result)
        if result_n in replacement_map:
            raise Exception(f"You are not supposed to define {result_n}")
        return part_a.Wire(left_n, right_n, result_n, part_a.Wire.operator_map[operator])

    def _n(self, item: Tuple[str, int]) -> str:
        prefix, index = item
        return f"{prefix}{str(index).rjust(2, '0')}"

    def get_wire_expression(self, wire: part_a.Wire, seen: Optional[Set[str]] = None) -> str:
        if seen is None:
            seen = set()
        if wire.left in seen or wire.right in seen:
            raise Exception(f"Wire {wire} has already seen {seen}")
        next_seen = seen | {wire.left, wire.right}
        left_expression = self.get_gate_expression(wire.left, seen=next_seen)
        operator_expression = wire.reverse_operator_map[wire.operator]
        right_expression = self.get_gate_expression(wire.right, seen=next_seen)
        left_expression, right_expression = sorted([left_expression, right_expression], reverse=True)
        return f"({left_expression} {operator_expression} {right_expression})"

    def get_gate_expression(self, gate: str, seen: Optional[Set[str]] = None) -> str:
        wire = self.wires_by_result.get(gate)
        if not wire:
            return gate
        return self.get_wire_expression(wire, seen=seen)

    def find_swaps(self, count: int = 4, debugger: Debugger = Debugger(enabled=False)) -> Optional[List[Tuple[str, str]]]:
        pass
        """
        >>> DeviceExtended.from_text('''
        ...     x00: 0
        ...     x01: 1
        ...     x02: 0
        ...     x03: 1
        ...     x04: 0
        ...     x05: 1
        ...     y00: 0
        ...     y01: 0
        ...     y02: 1
        ...     y03: 1
        ...     y04: 0
        ...     y05: 1
        ...
        ...     x00 AND y00 -> z05
        ...     x01 AND y01 -> z02
        ...     x02 AND y02 -> z01
        ...     x03 AND y03 -> z03
        ...     x04 AND y04 -> z04
        ...     x05 AND y05 -> z00
        ... ''').find_swaps(2)
        [('z00', 'z05'), ('z01', 'z02')]
        """
        wrong_output_gates = self.get_wrong_output_gates()
        dependencies = self.get_gates_dependencies(wrong_output_gates)
        candidate_gates = sorted(set(wrong_output_gates) & dependencies)
        print(wrong_output_gates, dependencies, candidate_gates)
        for unordered_group in combinations(candidate_gates, r=count * 2):
            print(unordered_group)
            for group in permutations(unordered_group):
                device = self
                for index in range(0, len(group), 2):
                    first_wire = device.wires_by_result[group[index]]
                    second_wire = device.wires_by_result[group[index + 1]]
                    device = device.swap_wires([first_wire, second_wire])
                if device.is_output_addition():
                    return sorted([
                        tuple(sorted((group[index], group[index + 1])))
                        for index in range(0, len(group), 2)
                    ])
        return None

    def is_output_addition(self) -> bool:
        x = self.get_variable("x")
        y = self.get_variable("y")
        z = self.get_variable("z")
        return z == x + y

    def find_swaps_2(self, count: int = 4, exclude: Optional[Set[str]] = None, debugger: Debugger = Debugger(enabled=False)) -> Optional[List[Tuple[str, str]]]:
        if count == 0:
            x = self.get_variable("x")
            y = self.get_variable("y")
            z = self.get_variable("z")
            if z == x + y:
                return []
            else:
                return None
        wires = self.wires
        if exclude is None:
            exclude = set()
        else:
            wires = [
                wire
                for wire in wires
                if wire.result
            ]
        for wire_a, wire_b in debugger.stepping(combinations(wires, 2)):
            next_device = self.swap_wires([wire_a, wire_b])
            next_exclude = exclude | {wire_a.result, wire_b.result}
            next_swaps = next_device.find_swaps_2(count - 1, exclude=next_exclude)
            if next_swaps is not None:
                return [(wire_a.result, wire_b.result)] + next_swaps
            if debugger.should_report():
                debugger.default_report_if(f"")
        return None

    def swap_wires_by_name(self, pairs: List[Tuple[str, str]]) -> "DeviceExtended":
        return self.swap_wires([(self.wires_by_result[first], self.wires_by_result[second]) for first, second in pairs])

    def swap_wires(self, pairs: List[Tuple[part_a.Wire, part_a.Wire]]) -> "DeviceExtended":
        wires = list(self.wires)
        for first, second in pairs:
            new_first = part_a.Wire(left=first.left, right=first.right, result=second.result, operator=first.operator)
            new_second = part_a.Wire(left=second.left, right=second.right, result=first.result, operator=second.operator)
            wires.remove(first)
            wires.remove(second)
            wires.append(new_first)
            wires.append(new_second)
        values = {
            gate: value if gate[0] in "xy" else None
            for gate, value in self.values.items()
        }
        return DeviceExtended(values=values, wires=wires)

    def get_gates_dependency_counts(self, gates: List[str]) -> Dict[part_a.Wire, int]:
        counts = {}
        for gate in gates:
            dependencies = self.get_gate_dependencies(gate)
            for dependency in dependencies:
                counts.setdefault(dependency, 0)
                counts[dependency] += 1
        return counts

    def get_gates_dependencies(self, gates: List[str]) -> Set[str]:
        return {
            dependency.result
            for gate in gates
            for dependency in self.get_gate_dependencies(gate)
        }

    def get_gate_dependencies(self, gate: str) -> Set[part_a.Wire]:
        dependencies = set()
        if gate not in self.wires_by_result:
            return dependencies
        wire = self.wires_by_result[gate]
        queue = [wire]
        dependencies = {wire}
        while queue:
            wire = queue.pop(0)
            next_gates = [wire.left, wire.right]
            next_wires = set(filter(None, map(self.wires_by_result.get, next_gates))) - dependencies
            queue.extend(next_wires)
            dependencies.update(next_wires)
        return dependencies

    def get_wrong_output_gates(self) -> List[str]:
        x = self.get_variable("x")
        y = self.get_variable("y")
        z = self.get_variable("z")
        bin_z = bin(z)
        bin_x_plus_y = bin(x + y)
        return [
            f"z{str(binary_index - 1).rjust(2, '0')}"
            for index, digit in enumerate(bin_z[2:], start=2)
            for binary_index in [len(bin_z) - index]
            for other_index in [len(bin_x_plus_y) - binary_index]
            for other_digit in [bin_x_plus_y[other_index] if other_index < len(bin_x_plus_y) else ""]
            if digit != other_digit
        ]


Challenge.main()
challenge = Challenge()
