#!/usr/bin/env python3
from typing import ClassVar, Dict, List, Tuple, Union

import click

from aox.challenge import Debugger
from utils import BaseChallenge
from year_2024.day_17 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        236555995274861
        """
        return OptimisedMachine().find_smallest_value_for_output()

    def play(self):
        machine = part_a.Machine.from_text(self.input)
        print(f"\n".join(f"{line_number}: {instruction.disassemble(operand.opcode)}" for line_number, instruction, operand in zip(range(0, len(machine.instructions), 2), machine.instructions[::2], machine.instructions[1::2])))

    def play_show_iterations(self):
        pass

        """
        2,4,1,3,7,5,4,2,0,3,1,5,5,5,3,0
        
        0: 2
        1: 4
        2: 1
        3: 3
        4: 7
        5: 5
        6: 4
        7: 2
        8: 0
        9: 3
        10: 1
        11: 5
        12: 5
        13: 5
        14: 3
        15: 0
        
        0: 2(4)
        2: 1(3)
        4: 7(5)
        6: 4(2)
        8: 0(3)
        10: 1(5)
        12: 5(5)
        14: 3(0)
        
        0: bst(4)
        2: bxl(3)
        4: cdv(5)
        6: bxc(2)
        8: adv(3)
        10: bxl(5)
        12: out(5)
        14: jnz(0)
        
        0: b = a % 8
        2: b = b ^ 3
        4: c = a // 2 ** b
        6: b = b ^ c
        8: a = a // 8
        10: b = b ^ 5
        12: out(b % 8)
        14: if a != 0: goto 0
        
        while a != 0:
            b = a % 8
            b = b ^ 3
            c = a // 2 ** b
            b = b ^ c
            a = a // 8
            b = b ^ 5
            out(b)
            
        while a != 0:
            out((((a % 8) ^ 3) ^ (a // 2 ** ((a % 8) ^ 3)) ^ 5) % 8)
            a = a // 8
        """

        expected_output = OptimisedMachine.expected_output
        print(f"Expected output: {expected_output}")

        possible_bases = [0]
        for iteration in range(len(expected_output), 0, -1):
            print(f"Iteration {iteration}")
            iteration_maps = [
                OptimisedMachine().get_3_bit_iteration_map(base * 8)
                for base in possible_bases
            ]
            iteration_expected_output = expected_output[iteration - 1]
            iteration_expected_output_list = expected_output[iteration - 1:]
            debug_iteration_maps = "\n".join(
                " * {} -> {}".format(
                    click.style(str(base), fg="blue"),
                    ", ".join(
                        "{}: {}".format(
                            (
                                click.style(str(a), fg="green")
                                if value == iteration_expected_output else
                                a
                            ),
                            (
                                click.style(str(value), fg="yellow")
                                if value == iteration_expected_output else
                                value
                            ),
                        )
                        for a, value in iteration_map.items()
                    ),
                )
                for base, iteration_map in zip(possible_bases, iteration_maps)
            )
            print(f"Iteration maps (expecting {click.style(str(iteration_expected_output), fg='yellow')}):\n{debug_iteration_maps}")
            possible_bases = [
                a + base * 8
                for base, iteration_map in zip(possible_bases, iteration_maps)
                for a, result in iteration_map.items()
                if result == iteration_expected_output
            ]
            print(f"Possible bases: {possible_bases}")
            validations = [
                OptimisedMachine().get_output(base)
                for base in possible_bases
            ]
            validation_text = "\n".join(
                " * {}: [{}]".format(
                    click.style(str(base), fg=("green" if base_output == iteration_expected_output_list else "red")),
                    ", ".join(
                        click.style(str(output_value), fg=("green" if output_index < len(iteration_expected_output_list) and output_value == iteration_expected_output_list[output_index] else "red"))
                        for output_index, output_value in enumerate(base_output)
                    ),
                )
                for base, base_output in zip(possible_bases, validations)
            )
            print(f"Expecting [{', '.join(click.style(str(value), fg='green') for value in iteration_expected_output_list)}], validation:\n{validation_text}")
            if not all(validation == iteration_expected_output_list for validation in validations) or not possible_bases:
                print(click.style(f"Failed, exiting", fg="red"))
                break


class OptimisedMachine:
    expected_output: ClassVar[List[int]] = [2, 4, 1, 3, 7, 5, 4, 2, 0, 3, 1, 5, 5, 5, 3, 0]

    def find_smallest_value_for_output(self) -> int:
        return min(self.find_values_for_output())

    def find_values_for_output(self) -> List[int]:
        possible_bases = [0]
        for iteration in range(len(self.expected_output), 0, -1):
            iteration_maps = [
                OptimisedMachine().get_3_bit_iteration_map(base * 8)
                for base in possible_bases
            ]
            iteration_expected_output = self.expected_output[iteration - 1]
            iteration_expected_output_list = self.expected_output[iteration - 1:]
            possible_bases = [
                a + base * 8
                for base, iteration_map in zip(possible_bases, iteration_maps)
                for a, result in iteration_map.items()
                if result == iteration_expected_output
            ]
            validations = [
                OptimisedMachine().get_output(base)
                for base in possible_bases
            ]
            if not all(validation == iteration_expected_output_list for validation in validations) or not possible_bases:
                validation_str = "\n".join(
                    f" * For {base}: {output}"
                    for base, output in zip(possible_bases, validations)
                )
                raise Exception(f"Some bases didn't validate\nExpected {iteration_expected_output_list}\nGot:\n{validation_str}")
        return possible_bases

    def get_output(self, a: int) -> List[int]:
        """
        >>> OptimisedMachine().get_output(30118712)
        [1, 7, 6, 5, 1, 0, 5, 0, 7]
        """
        out = []
        while a != 0:
            a, output = self.get_iteration(a)
            out.append(output)
        return out

    def get_iteration(self, a: int) -> Tuple[int, int]:
        return a // 8, (((a % 8) ^ 3) ^ (a // 2 ** ((a % 8) ^ 3)) ^ 5) % 8

    def get_3_bit_iteration_map(self, base: int) -> Dict[int, int]:
        return {
            a: self.get_iteration(base + a)[1]
            for a in range(8)
        }


Challenge.main()
challenge = Challenge()
