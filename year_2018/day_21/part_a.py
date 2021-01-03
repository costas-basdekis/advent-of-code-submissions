#!/usr/bin/env python3
import utils
from year_2018.day_19 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        11592302
        """
        # By analysing the program, it only terminates when we pass in the
        # following number as register a
        return get_acceptable_a()


def get_acceptable_a(start=0):
    """
    >>> get_acceptable_a()
    11592302
    """
    c = start | 65536
    b = 10605201
    while True:
        b = (((b + (c & 255)) & 16777215) * 65899) & 16777215
        if c < 256:
            break
        c = c // 256

    return b


class ProgramExtended(part_a.Program):
    def run(self, registers=(0,) * 6, instruction_pointer=None, debug=False,
            report_count=1000000, report_only_changes=None):
        seen_registers = {registers}
        final_registers = registers
        for step, previous_registers, final_registers \
                in self.iter_run(registers, instruction_pointer):
            self.debug(step, previous_registers, final_registers,
                       debug, report_only_changes, report_count)
            if final_registers in seen_registers:
                raise Exception(f"Endless loop detected")
            seen_registers.add(final_registers)

        return final_registers


challenge = Challenge()
challenge.main()
