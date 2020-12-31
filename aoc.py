#!/usr/bin/env python3
import glob
import importlib
import itertools
import string
from typing import List, Tuple

import click

import utils

YearsAndDays = List[Tuple[int, List[int], List[int]]]


@click.group(invoke_without_command=True)
@click.pass_context
def aoc(ctx):
    if ctx.invoked_subcommand:
        return
    ctx.invoke(list_years_and_days)


@aoc.command(context_settings={'ignore_unknown_options': True})
@click.argument('year', type=int)
@click.argument('day', type=int)
@click.argument('part', type=click.Choice(['a', 'b']))
@click.argument('rest', nargs=-1, type=click.UNPROCESSED)
def challenge(year: int, day: int, part: str, rest):
    challenge_instance = get_challenge_instance(year, day, part)
    challenge_instance.run_main_arguments(args=rest)


def get_challenge_instance(year: int, day: int, part: str):
    module_name = "year_{}.day_{:0>2}.part_{}".format(year, day, part, )
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        click.echo(f"Could not find {click.style(module_name, fg='red')}")
        return

    if not hasattr(module, 'challenge'):
        challenge_class = getattr(module, 'Challenge')
        if not isinstance(challenge_class, type) \
                or not issubclass(challenge_class, utils.BaseChallenge):
            click.echo(
                f"Challenge {click.style(module_name, fg='red')} does not "
                f"use `BaseChallenge` and doesn't specify a `challenge` "
                f"instance")
            return
        challenge_instance = challenge_class()
    else:
        challenge_instance = getattr(module, 'challenge')

    if not isinstance(challenge_instance, utils.BaseChallenge):
        click.echo(
            f"Challenge {click.style(module_name, fg='red')} `challenge` "
            f"instance is not of `BaseChallenge`")
        return

    return challenge_instance


@aoc.command(name='list')
@click.option('-y', '--year', type=int)
def list_years_and_days(year: int):
    years_and_days = get_years_and_days()
    if year is None:
        list_years(years_and_days)
    else:
        list_days(years_and_days, year=year)


def list_years(years_and_days: YearsAndDays):
    click.echo(
        f"Found {click.style(str(len(years_and_days)), fg='green')} years:")
    for year, days, missing_days in reversed(years_and_days):
        click.echo(
            f"  * {click.style(str(year), fg='green')} with "
            f"{click.style(str(len(days)), fg='green')} days")


def list_days(years_and_days: YearsAndDays, year: int):
    days, missing_days = next((
        (days, missing_days)
        for _year, days, missing_days
        in years_and_days
        if _year == year
    ), (None, None))
    if days is None:
        click.echo(f"Could not find {click.style(str(year), fg='red')}")
        return
    click.echo(
        f"Found {click.style(str(len(days)), fg='green')} days in "
        f"{click.style(str(year), fg='green')}:")
    days_string = ', '.join(
        click.style(str(day), fg='green')
        for day in reversed(days)
    )
    click.echo(f"  * {days_string}")
    if missing_days:
        missing_days_string = ', '.join(
            click.style(str(day), fg='white')
            for day in reversed(missing_days)
        )
        click.echo(f"  * Missing {missing_days_string}")


def get_years_and_days() -> YearsAndDays:
    part_a_files = glob.glob("year_*/day_*/part_a.py")
    years_and_days = [
        (year, [month for _, month in items])
        for year, items in itertools.groupby(sorted(
            (int(year_text), int(day_text))
            for name in part_a_files
            for year_part, day_part, _ in [name.split('/', 2)]
            for year_text, day_text in [
                (year_part.replace('year_', ''), day_part.replace('day_', '')),
            ]
            if not set(year_text) - set(string.digits)
            and not set(day_text) - set(string.digits)
        ), key=lambda item: item[0])
    ]

    return [
        (year, days, sorted(set(range(1, 26)) - set(days)))
        for year, days in years_and_days
    ]


if __name__ == '__main__':
    aoc()
