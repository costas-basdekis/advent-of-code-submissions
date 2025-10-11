import traceback
from typing import Tuple, Union

import click

from aox.challenge import Debugger
from aox.controller.controller import Controller
from aox.settings import settings_proxy
from aox.styling.shortcuts import e_error, e_value, e_success, e_warn
from aox.utils import try_import_module, has_method_arguments, pretty_duration

__all__ = ['IcpcController']


class IcpcController(Controller):
    def get_or_create_challenge(self, year, day, part, force):
        module_name = f"icpc.year_{year}.problem_{part}"
        module = try_import_module(module_name)
        if not module:
            click.echo(f"Could not find {e_error(module_name)}!")

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

    def check_challenge_many(self, year, day, part, force, input_names, all_inputs, verbose, very_verbose, debug, debug_interval):
        verbose = verbose or very_verbose
        if all_inputs:
            input_names = settings_proxy().challenges_boilerplate\
                .get_icpc_problem_file_names(year, part)
            if not input_names:
                print(e_error("No inputs found"))
                return
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
                if verbose:
                    print(f" * Checking {e_value(input_name)}...", end="\n" if very_verbose else "")
                _, success, _, duration = self.check_challenge(year, day, part, force, input_name, very_verbose, debug, debug_interval)
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

    def check_challenge(self, year, day, part, force, input_name, verbose, debug, debug_interval) -> Tuple[bool, bool, Union[None, str, int], float]:
        input_file, output_file = settings_proxy().challenges_boilerplate\
            .get_icpc_problem_file_pair(year, part, input_name)
        _input = input_file.read_text().strip()
        output = output_file.read_text().strip()
        challenge_instance = self.get_or_create_challenge(
            year, day, part, force)
        if not challenge_instance:
            return False, False, None
        debugger = Debugger(
            enabled=debug, min_report_interval_seconds=debug_interval)
        try:
            if has_method_arguments(
                    challenge_instance.default_solve, "debugger"):
                matches, solution, duration = challenge_instance.check_solve(_input, output, debugger=debugger)
            else:
                matches, solution, duration = challenge_instance.check_solve(_input, output, debug=debugger)
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
