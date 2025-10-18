import sys
from abc import ABC
from typing import List, Tuple, Union

from aox.settings import settings_proxy
from aox.utils import has_method_arguments, Timer
from utils.base_challenge import BaseChallenge


__all__ = ['BaseIcpcChallenge']


class BaseIcpcChallenge(BaseChallenge, ABC):
    @classmethod
    def get_main_args(cls, extra_args=None):
        """The CLI arguments to simulate an invocation of this challenge"""
        if extra_args is None:
            extra_args = sys.argv[1:]
        return [
            'icpc',
            'challenge',
            '--path', cls.get_module().__file__,
            '0',
            'a',
        ] + extra_args

    def get_input(self):
        return settings_proxy().challenges_boilerplate\
            .get_icpc_sample_problem_file(self.year, self.part)\
            .read_text()

    def check_solve(self, _input: str, output: str, debugger=None) -> Tuple[bool, Union[str, int], float]:
        """Convenient method to call `solve` with a particular input from the disk"""
        if debugger is None:
            from aox.challenge import Debugger
            debugger = Debugger(enabled=False)
        with Timer() as timer:
            if has_method_arguments(self.solve, "debugger"):
                result = self.solve(_input, debugger=debugger)
            else:
                # noinspection PyArgumentList
                result = self.solve(_input, debug=debugger)
        return self.does_solution_match_output(result, output), result, timer.duration

    def does_solution_match_output(self, result: str, output: str) -> bool:
        return str(result) == output

    def filter_cases(self, _input: str, case_indexes: List[int]) -> str:
        """Filters the input to only include the specified cases"""
        cases = self.split_cases(_input)
        selected_cases = [cases[i - 1] for i in case_indexes]
        return self.join_cases(selected_cases)

    def split_cases(self, _input: str) -> List[str]:
        """Splits the input into separate cases"""
        raise NotImplementedError()

    def join_cases(self, cases: List[str]) -> str:
        """Joins separate cases into a single input"""
        raise NotImplementedError()

    def filter_outputs(self, output: str, case_indexes: List[int]) -> str:
        cases = output.strip().splitlines()
        selected_cases = [cases[i - 1] for i in case_indexes]
        return "\n".join(selected_cases)
