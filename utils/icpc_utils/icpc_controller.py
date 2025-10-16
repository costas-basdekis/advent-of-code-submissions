from itertools import zip_longest
import string
import traceback
from pathlib import Path
from typing import Tuple, Union, Optional

import click

from aox.challenge import Debugger
from aox.controller.controller import Controller
from aox.settings import settings_proxy
from aox.styling.shortcuts import e_error, e_value, e_success, e_warn
from aox.utils import try_import_module, has_method_arguments, pretty_duration, Timer

__all__ = ['IcpcController']


class IcpcController:
    controller: Controller

    def __init__(self):
        self.controller = Controller()
        self.controller.get_or_create_challenge = lambda year, day, part, force: self.get_or_create_challenge(year, part, force)

    def list_years(self):
        icpc_root: Path = settings_proxy().path.absolute().parent.parent / "icpc"
        years = [
            int(directory.name.split("_")[1])
            for directory in icpc_root.glob("year_*")
            if directory.is_dir()
            and not (set(directory.name.split("_")[1]) - set(string.digits))
        ]
        click.echo(f"Found {e_success(str(len(years)))} years with code:")
        for year in sorted(years, reverse=True):
            year_directory = icpc_root / f"year_{year}"
            problem_file_count = sum(1 for _ in year_directory.glob("problem_*.py"))
            click.echo(
                f"  * {e_success(str(year))}: "
                f"{e_success(str(problem_file_count))} problems with code")

    def test_and_run_challenge(self, year, part, force, filters_texts,
                               debug, debug_interval):
        return self.controller.test_and_run_challenge(year, 1, part, force, filters_texts, debug, debug_interval)

    def test_challenge(self, year, part, force, filters_texts):
        return self.controller.test_challenge(year, 1, part, force, filters_texts)

    def run_challenge_many(self, year, part, input_names, all_inputs, force, debug, debug_interval):
        if all_inputs:
            input_names = settings_proxy().challenges_boilerplate\
                .get_icpc_problem_file_names(year, part)
            if not input_names:
                print(e_error("No inputs found"))
                return
        if not input_names:
            self.controller.run_challenge(year, 1, part, force, debug, debug_interval)
            return
        for input_name in input_names:
            input_file = None
            actual_input_name = input_name
            try:
                input_file = settings_proxy().challenges_boilerplate\
                    .get_icpc_problem_file(year, part, input_name, partial_match=True)
            except FileNotFoundError:
                pass
            else:
                actual_input_name = input_file.name[:-len(".in")]
            print(f"Running with {actual_input_name}:")
            self.run_challenge(year, part, input_name, force, debug, debug_interval, input_file=input_file)

    def run_challenge(self, year: int, part: str, input_name: str, force: bool, debug: bool, debug_interval: int, input_file: Optional[Path] = None) -> Tuple[bool, Optional[Union[int, str]]]:
        challenge_instance = self.get_or_create_challenge(year, part, force)
        if not challenge_instance:
            return False, None
        if input_file is None:
            input_file = settings_proxy().challenges_boilerplate\
                .get_icpc_problem_file(year, part, input_name, partial_match=True)
        with Timer() as timer:
            debugger = Debugger(enabled=debug, min_report_interval_seconds=debug_interval)
            solution = challenge_instance.solve(_input=input_file.read_text(), debugger=debugger)
        if solution is None:
            styled_solution = e_error(str(solution))
        else:
            styled_solution = e_value(str(solution))
        click.echo(
            f"Solution: {styled_solution}"
            f" (in {timer.get_pretty_duration(2)})")

        return True, solution


    def play_challenge(self, year, part, force):
        return self.controller.play_challenge(year, 1, part, force)

    def get_or_create_challenge(self, year, part, force):
        module_name = f"icpc.year_{year}.problem_{part}"
        module = try_import_module(module_name)
        if not module:
            if not self.add_challenge_if_agreed(year, part, force):
                click.echo(f"Could not find {e_error(module_name)}!")
                return None
            module = try_import_module(module_name)
            if not module:
                click.echo(
                    f"Could not import challenge module {e_error(module_name)} "
                    f"even after creating it")
                return None

        from .base_icpc_challenge import BaseIcpcChallenge
        if not hasattr(module, 'challenge'):
            challenge_class = getattr(module, 'Challenge')
            if not isinstance(challenge_class, type) \
                    or not issubclass(challenge_class, BaseIcpcChallenge):
                click.echo(
                    f"Challenge {e_error(module.__name__)} does not use "
                    f"`BaseIcpcChallenge` and doesn't specify a `challenge` "
                    f"instance")
                return None
            challenge_instance = challenge_class()
        else:
            challenge_instance = getattr(module, 'challenge')

        if not isinstance(challenge_instance, BaseIcpcChallenge):
            click.echo(
                f"Challenge {e_error(module.__name__)} `challenge` instance is "
                f"not of `BaseIcpcChallenge`")
            return None

        return challenge_instance
        #
        # if not challenge_instance:
        #     if not self.add_challenge_if_agreed(year, day, part, force):
        #         return
        #     challenge_instance = self.combined_info \
        #         .get_challenge_instance(year, day, part)
        # return challenge_instance

    def add_challenge_if_agreed(self, year: int, part: str, force: bool) -> bool:
        if not force:
            should_create_challenge = click.prompt(
                f"Do you want to create challenge "
                f"{e_value(f'{year} {part.upper()}')}?",
                type=bool, default=True)
        else:
            should_create_challenge = True
        if not should_create_challenge:
            return False
        return bool(self.add_challenge(year, part))

    def add_challenge(self, year: int, part: str) -> bool:
        problem_path = settings_proxy().challenges_boilerplate.create_icpc_part(year, part)
        if not problem_path:
            return False
        click.echo(
            f"Added challenge {e_success(f'{year} {part.upper()}')} at "
            f"{e_value(str(problem_path))}")
        return True

    def check_challenge_many(self, year, part, force, input_names, all_inputs, verbose, very_verbose, debug, debug_interval):
        verbose = verbose or very_verbose
        if all_inputs:
            input_names = settings_proxy().challenges_boilerplate\
                .get_icpc_problem_file_names(year, part)
            if not input_names:
                print(e_error("No inputs found"))
                return
            input_names = sorted(input_names)
        if not input_names:
            print(e_error("No input names provided"))
            return
        if verbose or all_inputs or len(input_names) > 1:
            print(f"Checking {len(input_names)} inputs...")
        success_count = 0
        error_names = []
        total_challenge_time = 0
        max_challenge_time = 0
        for input_name in input_names:
            try:
                file_pair = None
                if verbose:
                    actual_input_name = input_name
                    try:
                        file_pair = settings_proxy().challenges_boilerplate\
                            .get_icpc_problem_file_pair(year, part, input_name, partial_match=True)
                    except FileNotFoundError:
                        pass
                    else:
                        actual_input_name = file_pair[0].name[:-len(".in")]
                    print(f" * Checking {e_value(actual_input_name)}...", end="\n" if very_verbose else "")
                _, success, _, duration = self.check_challenge(year, part, force, input_name, very_verbose, debug, debug_interval, file_pair=file_pair)
                total_challenge_time += duration
                max_challenge_time = max(max_challenge_time, duration)
                if verbose and not very_verbose:
                    print()
                if success:
                    success_count += 1
                else:
                    error_names.append(input_name)
                if len(input_names) == 1:
                    print()
            except KeyboardInterrupt:
                break
        if verbose or all_inputs or len(input_names) > 1:
            if not verbose:
                print()
            if not input_names or (success_count > 0 and len(error_names) > 0):
                print(f"{e_success(str(success_count))}/{len(input_names)} succeeded and {e_error(str(len(error_names)))}/{len(input_names)} failed", end="")
            elif success_count > 0:
                print(f"{e_success(str(success_count))}/{len(input_names)} succeeded", end="")
            else:
                print(f"{e_error(str(len(error_names)))}/{len(input_names)} failed", end="")
            print(f", in {e_value(pretty_duration(total_challenge_time, 2))}", end="")
            if input_names:
                print(f" (avg: {pretty_duration(total_challenge_time / len(input_names), 2)}, max: {pretty_duration(max_challenge_time, 2)})")
            else:
                print()
            if error_names:
                print(f"First few errors: {e_error(' '.join(error_names[:5]))}")

    def check_challenge(self, year: int, part: str, force: bool, input_name: str, verbose: bool, debug: bool, debug_interval: int, file_pair: Optional[Tuple[Path, Path]] = None) -> Tuple[bool, bool, Union[None, str, int], float]:
        if file_pair is None:
            file_pair = settings_proxy().challenges_boilerplate\
            .get_icpc_problem_file_pair(year, part, input_name, partial_match=True)
        input_file, output_file = file_pair
        _input = input_file.read_text().strip()
        output = output_file.read_text().strip()
        challenge_instance = self.get_or_create_challenge(year, part, force)
        if not challenge_instance:
            return False, False, None, 0
        debugger = Debugger(
            enabled=debug, min_report_interval_seconds=debug_interval)
        duration = 0
        # noinspection PyBroadException
        try:
            matches, solution, duration = challenge_instance.check_solve(_input, output, debugger=debugger)
            failed = False
        except Exception:
            if verbose:
                traceback.print_exc()
            matches, solution, failed = False, None, True
        if solution is None or not matches:
            styled_solution = e_error(str(solution))
        else:
            styled_solution = e_value(str(solution))
        if not verbose:
            if matches:
                print(e_success("✓"), end="", flush=True)
            elif failed:
                print(e_warn("⚠︎"), end="", flush=True)
            else:
                print(e_error("×"), end="", flush=True)
        else:
            if not matches and not failed and "\n" in output:
                solution_lines = solution.splitlines()
                output_lines = output.splitlines()
                click.echo("Mismatch: \n{}\n (in {})".format(
                    "\n".join(
                        (
                            e_success(solution_line)
                            if solution_line == output_line else 
                            f"{e_error(solution_line)}{e_value(output_line)}"
                        )
                        for solution_line, output_line in zip_longest(solution_lines, output_lines, fillvalue="")
                    ),
                    pretty_duration(duration, 2),
                ))
            else:
                click.echo(
                    f"Solution: {styled_solution}"
                    f" (in {pretty_duration(duration, 2)})")
                if matches:
                    print(e_success(f"Matches!"))
                elif failed:
                    print(e_warn("Failed!"))
                else:
                    print(f"{e_error('Does not match')} {e_value(output)}")

        return True, matches, solution, duration
