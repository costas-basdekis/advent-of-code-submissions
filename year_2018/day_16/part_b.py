#!/usr/bin/env python3
import functools
import itertools

import utils

from year_2018.day_16 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        674
        """

        result = Program.from_samples_and_program_text(_input)\
            .run((0, 0, 0, 0))

        return result[0]


class Program:
    @classmethod
    def from_samples_and_program_text(cls, samples_and_program_text):
        samples_text, program_text = samples_and_program_text.split('\n' * 4)
        sample_set = SampleSetExtended.from_samples_text(samples_text)
        op_code_mapping = sample_set.get_instruction_op_code_mapping()
        return cls.from_program_text_and_op_code_mapping(
            program_text, op_code_mapping)

    @classmethod
    def from_program_text_and_op_code_mapping(
            cls, program_text, op_code_mapping):
        non_empty_lines = filter(None, program_text.splitlines())
        instructions = (
            tuple(map(int, instruction_text.split(' ')))
            for instruction_text in non_empty_lines
        )
        return cls([
            op_code_mapping[instruction[0]](*instruction[1:])
            for instruction in instructions
        ])

    def __init__(self, instructions):
        self.instructions = instructions

    def run(self, registers):
        for instruction in self.instructions:
            registers = instruction.step(registers)

        return registers


class SampleSetExtended(part_a.SampleSet):
    def get_instruction_op_code_mapping(self):
        candidates_by_op_code = self.get_candidates_by_opcode()
        if len(candidates_by_op_code) \
                != len(part_a.Instruction.instruction_classes):
            raise Exception(
                f"Op codes and instructions don't match: "
                f"{len(candidates_by_op_code)} "
                f"vs {len(part_a.Instruction.instruction_classes)}")

        instruction_class_by_op_code = {}
        remaining_candidates_by_op_code = dict(candidates_by_op_code)
        while remaining_candidates_by_op_code:
            op_codes_with_one_candidate = [
                op_code
                for op_code, candidates
                in remaining_candidates_by_op_code.items()
                if len(candidates) == 1
            ]
            if not op_codes_with_one_candidate:
                raise Exception(
                    f"Cannot find any more op codes with 1 candidate: "
                    f"{remaining_candidates_by_op_code}")
            op_code = op_codes_with_one_candidate[0]
            instruction_class, = remaining_candidates_by_op_code[op_code]
            instruction_class_by_op_code[op_code] = instruction_class
            del remaining_candidates_by_op_code[op_code]
            for candidates in remaining_candidates_by_op_code.values():
                candidates -= {instruction_class}

        return instruction_class_by_op_code

    def get_candidates_by_opcode(self):
        candidate_sets_by_op_code = {
            op_code: [
                candidate_set
                for _, candidate_set in candidate_sets
            ]
            for op_code, candidate_sets in itertools.groupby(sorted((
                (sample.instruction_op_code,
                 sample.get_instruction_candidates())
                for sample in self.samples
            ), key=lambda item: item[0]), key=lambda item: item[0])
        }

        return {
            op_code: functools.reduce(set.__and__, map(set, candidate_sets))
            for op_code, candidate_sets in candidate_sets_by_op_code.items()
        }


class SampleExtended(part_a.Sample):
    @property
    def instruction_op_code(self):
        return self.instruction[0]


SampleSetExtended.sample_class = SampleExtended


challenge = Challenge()
challenge.main()
