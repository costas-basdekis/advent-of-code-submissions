import doctest
import os
import sys
from pathlib import Path


def get_current_directory(file_path):
    return Path(os.path.dirname(os.path.realpath(file_path)))


def get_input(module_file):
    return get_current_directory(module_file)\
        .joinpath("part_a_input.txt")\
        .read_text()


class BaseChallenge:
    part_a_for_testing = None
    optionflags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

    def __init__(self):
        self.module = sys.modules[self.__module__]
        self.input = self.get_input()

    def get_input(self):
        return get_input(self.module.__file__)

    def main(self):
        main_module = sys.modules.get('__main__')
        if self.module != main_module:
            return
        arguments = self.get_main_arguments()
        self.run_main_arguments(arguments)

    def get_main_arguments(self):
        if len(sys.argv) > 2:
            raise Exception(
                "Only 1 optional argument is acceptable: run, test, play")
        if len(sys.argv) == 2:
            argument = sys.argv[1]
            if argument not in ('run', 'test', 'play'):
                raise Exception(
                    f"Only 1 optional argument is acceptable: run, test, play "
                    f"- not {argument}")
        else:
            argument = None

        return [argument]

    def run_main_arguments(self, arguments):
        argument, = arguments
        if argument in (None, 'test'):
            self.test()
        if argument in (None, 'run'):
            self.run()
        if argument == 'play':
            self.play()

    def default_solve(self, _input=None):
        if _input is None:
            _input = self.input
        return self.solve(_input)

    def solve(self, _input):
        raise NotImplementedError()

    def play(self):
        raise Exception(f"Challenge has not implemented play")

    def test(self):
        failed = doctest.testmod(optionflags=self.optionflags).failed
        if self.part_a_for_testing:
            failed |= doctest.testmod(
                self.part_a_for_testing, optionflags=self.optionflags).failed
        if failed:
            print("Tests failed")
        else:
            print("Tests passed")

    def run(self):
        print("Solution:", self.default_solve())
