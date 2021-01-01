#!/usr/bin/env python3
import glob
import importlib
import itertools
import json
import re
import string
from pathlib import Path
from typing import List, Tuple

import bs4
import click
import requests

try:
    import settings
except ImportError:
    import example_settings as settings
import utils

YearsAndDays = List[Tuple[int, List[int], List[int]]]


@click.group(invoke_without_command=True)
@click.pass_context
def aoc(ctx):
    ctx.obj = {'site_data': get_cached_site_data()}
    if ctx.invoked_subcommand:
        return
    ctx.invoke(list_years_and_days)


def get_cached_site_data():
    try:
        site_data_file = Path('./site_data.json').open()
    except FileNotFoundError:
        return None

    with site_data_file:
        return json.load(site_data_file)


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
@click.pass_context
def list_years_and_days(ctx, year: int):
    years_and_days = get_years_and_days()
    if year is None:
        list_years(ctx.obj['site_data'], years_and_days)
    else:
        list_days(ctx.obj['site_data'], years_and_days, year=year)


def list_years(site_data, years_and_days: YearsAndDays):
    if site_data is not None:
        years_with_stars = set(site_data['years'])
        total_stars = site_data['total_stars']
    else:
        years_with_stars = set()
        total_stars = 0
    years_with_stars_or_code = (
        set(str(year) for year, _, _ in years_and_days)
        | years_with_stars
    )
    year_count_text = click.style(
        str(len(years_with_stars_or_code)), fg='green')
    click.echo(
        f"Found {year_count_text} years "
        f"with {click.style(str(total_stars) + ' stars', fg='yellow')}:")
    days_by_year = {
        str(year): days
        for year, days, _ in years_and_days
    }
    for year in sorted(years_with_stars_or_code, reverse=True):
        days_with_code = days_by_year.get(year, [])
        if site_data is not None:
            if str(year) in site_data['years']:
                year_stars = site_data['years'][str(year)]['stars']
            else:
                year_stars = 0
        else:
            year_stars = 0
        click.echo(
            f"  * {click.style(str(year), fg='green')} "
            f"{click.style(str(len(days_with_code)), fg='green')} days with "
            f"code and {click.style(str(year_stars) + ' stars', fg='yellow')}")


def list_days(site_data, years_and_days: YearsAndDays, year: int):
    days_with_code, days_without_code = next((
        (days, missing_days)
        for _year, days, missing_days
        in years_and_days
        if _year == year
    ), (None, None))
    if site_data is not None:
        if str(year) in site_data['years']:
            year_stars = site_data['years'][str(year)]['stars']
            days_stars = site_data['years'][str(year)]['days']
        else:
            year_stars = 0
            days_stars = {}
    else:
        year_stars = 0
        days_stars = {}
    if days_with_code is None:
        if year_stars:
            click.echo(
                f"Could not find {click.style(str(year), fg='red')} in code, "
                f"but found "
                f"{click.style(str(year_stars) + ' stars', fg='yellow')}")
        else:
            click.echo(
                f"Could not find {click.style(str(year), fg='red')} in code "
                f"nor any stars")
        return
    click.echo(
        f"Found {click.style(str(len(days_with_code)), fg='green')} days with "
        f"code in {click.style(str(year), fg='green')} with "
        f"{click.style(str(year_stars) + ' stars', fg='yellow')}:")
    if days_with_code:
        days_string = ', '.join(
            (
                click.style(str(day), fg='green')
                + click.style('*' * days_stars.get(str(day), 1), fg='yellow')
            )
            for day in reversed(days_with_code)
        )
        click.echo(f"  * {days_string}")
    if days_without_code:
        missing_days_string = ', '.join(
            (
                click.style(str(day), fg='white')
                + click.style('*' * days_stars.get(str(day), 1), fg='yellow')
            )
            for day in reversed(days_without_code)
        )
        click.echo(f"  * Missing code {missing_days_string}")


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


@aoc.command()
def fetch():
    data = update_data_from_site()
    if data is None:
        click.echo(f"Could {click.style('not fetch data', fg='red')}")
        return

    with Path('./site_data.json').open('w') as f:
        json.dump(data, f, indent=2)

    if data['total_stars'] is None:
        star_count_text = 'unknown'
    else:
        star_count_text = str(data['total_stars'])
    click.echo(
        f"Fetched data for {click.style(data['user_name'], fg='green')}: "
        f"{click.style(star_count_text + ' stars', fg='yellow')} in "
        f"{click.style(str(len(data['years'])), fg='green')} years")


def update_data_from_site():
    events_page = get_events_page()

    user_name = get_user_name(events_page)
    if not user_name:
        return None

    total_stars = get_total_stars(events_page)

    years_and_details = get_years_and_details(events_page)

    return {
        "user_name": user_name,
        "total_stars": total_stars,
        "years": years_and_details,
    }


def get_events_page():
    session_id = getattr(settings, 'AOC_SESSION_ID')
    if not session_id:
        click.echo(
            f"You haven't set {click.style('AOC_SESSION_ID', fg='red')} in "
            f"{click.style('settings.py', fg='red')}")
        return None

    response = requests.get(
        'https://adventofcode.com/events',
        cookies={"session": session_id},
        headers={"User-Agent": "advent-of-code-submissions"},
    )
    if not response.ok:
        click.echo(
            f"Could not get {click.style('events information', fg='red')} from "
            f"AOC site - is the internet down, AOC down, the URL is wrong, or "
            f"are you banned?")
        return None

    return bs4.BeautifulSoup(response.text, "html.parser")


def get_years_and_details(events_page):
    stars_nodes = events_page.select(".eventlist-event .star-count")
    years_nodes = [node.parent for node in stars_nodes]
    years_and_stars = [
        (year, stars)
        for year, stars in filter(None, map(get_year_and_stars, years_nodes))
        if stars
    ]
    return {
        year: {
            "stars": stars,
            "days": get_year_day_stars(year),
        }
        for year, stars in years_and_stars
    }


def get_total_stars(events_page):
    total_stars_nodes = events_page.select("p > .star-count")
    return parse_star_count(total_stars_nodes)


def get_user_name(events_page):
    user_nodes = events_page.select(".user")
    if not user_nodes:
        click.echo(
            f"Either the session ID in "
            f"{click.style('AOC_SESSION_ID', fg='red')} is wrong, or it has "
            f"expired: could not find the user name")
        return None

    user_node = user_nodes[0]
    text_children = [
        child
        for child in user_node.children
        if isinstance(child, str)
    ]
    if not text_children:
        click.echo(
            f"Either the user name is blank or the format has changed")
        return None
    return text_children[0].strip()


def get_year_day_stars(year):
    year_page = get_year_page(year)
    if year_page is None:
        return {}

    days_nodes = year_page.select('.calendar > a[class^="calendar-day"]')
    return dict(filter(None, map(get_day_and_stars, days_nodes)))


def get_year_page(year):
    session_id = getattr(settings, 'AOC_SESSION_ID')
    if not session_id:
        click.echo(
            f"You haven't set {click.style('AOC_SESSION_ID', fg='red')} in "
            f"{click.style('settings.py', fg='red')}")
        return None

    response = requests.get(
        f'https://adventofcode.com/{year}',
        cookies={"session": session_id},
        headers={"User-Agent": "advent-of-code-submissions"},
    )
    if not response.ok:
        click.echo(
            f"Could not get "
            f"{click.style(f'year {year} information', fg='red')} from AOC "
            f"site (status was {response.status_code}) - is the internet down, "
            f"AOC down, the URL is wrong, or are you banned?")
        return None

    return bs4.BeautifulSoup(response.text, "html.parser")


def get_day_and_stars(day_node):
    day_name_nodes = day_node.select(".calendar-day")
    if not day_name_nodes:
        return None
    day_name_node = day_name_nodes[0]
    day_text = day_name_node.text
    try:
        day = int(day_text)
    except ValueError:
        return None

    class_names = day_node.attrs['class']
    if 'calendar-verycomplete' in class_names:
        stars = 2
    elif 'calendar-complete' in class_names:
        stars = 1
    else:
        stars = 0

    return day, stars


def get_year_and_stars(year_node):
    year_name_node = year_node.findChild('a')
    if not year_name_node:
        return None
    year_name_match = re.compile(r'^\[(\d+)]$').match(year_name_node.text)
    if not year_name_match:
        return None
    year_text, = year_name_match.groups()
    year = int(year_text)

    stars_nodes = year_node.select('.star-count')
    stars = parse_star_count(stars_nodes, default=0)

    return year, stars


def parse_star_count(stars_nodes, default=None):
    if not stars_nodes:
        return default
    stars_node = stars_nodes[0]
    stars_match = re.compile(r'^(\d+)\*$').match(stars_node.text)
    if not stars_match:
        return default

    stars_text, = stars_match.groups()
    return int(stars_text)


if __name__ == '__main__':
    aoc()
