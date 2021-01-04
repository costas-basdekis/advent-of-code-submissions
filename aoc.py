#!/usr/bin/env python3
import copy
import distutils.dir_util
import glob
import importlib
import itertools
import json
import re
import shutil
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


@click.group(invoke_without_command=True, chain=True)
@click.pass_context
def aoc(ctx):
    ctx.obj = {}
    update_context_object(ctx, {
        'site_data': get_cached_site_data(),
        'years_and_days': get_years_and_days(),
    })
    if ctx.invoked_subcommand:
        return
    ctx.invoke(list_years_and_days)


def update_context_object(ctx, updates):
    ctx.obj.update(updates)
    ctx.obj['combined_data'] = combine_data(
        ctx.obj['site_data'], ctx.obj['years_and_days'])


def get_cached_site_data():
    try:
        site_data_file = Path('./site_data.json').open()
    except FileNotFoundError:
        return None

    with site_data_file:
        return json.load(site_data_file)


@aoc.command()
@click.pass_context
def dump_data(ctx):
    print(json.dumps(ctx.obj["combined_data"], indent=2))


@aoc.command(context_settings={'ignore_unknown_options': True})
@click.argument('year', type=int)
@click.argument('day', type=int)
@click.argument('part', type=click.Choice(['a', 'b']))
@click.argument('rest', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def challenge(ctx, year: int, day: int, part: str, rest):
    combined_data = ctx.obj['combined_data']
    challenge_instance = get_challenge_instance(combined_data, year, day, part)
    if not challenge_instance:
        should_create_challenge = click.prompt(
            f"Do you want to create challenge "
            f"{click.style(f'{year} {day} {part.upper()}', fg='green')}?",
            type=bool, default=True)
        if not should_create_challenge:
            return
        ctx.invoke(add, year=year, day=day, part=part)
        combined_data = ctx.obj['combined_data']
        challenge_instance = get_challenge_instance(
            combined_data, year, day, part)
    challenge_instance.run_main_arguments(args=rest)


@aoc.command()
@click.argument('year', type=int)
@click.argument('day', type=int)
@click.argument('part', type=click.Choice(['a', 'b']))
@click.pass_context
def add(ctx, year: int, day: int, part: str):
    year_path = Path("year_{}/__init__.py".format(year))
    day_path = Path("year_{}/day_{:0>2}/__init__.py".format(year, day, part))
    part_path = Path("year_{}/day_{:0>2}/part_{}.py".format(year, day, part))

    if part_path.exists():
        click.echo(
            f"Challenge "
            f"{click.style(f'{year} {day} {part.upper()}', fg='yellow')} "
            f"already exists at {click.style(str(part_path), fg='yellow')}")
        return

    if not year_path.exists():
        Path(year_path.parent).mkdir(exist_ok=True)
        year_path.touch()
    if not day_path.exists():
        distutils.dir_util.copy_tree(
            "example_year/example_day", "year_{}/day_{:0>2}".format(
                year, day))
        part_a_path = Path(
            "year_{}/day_{:0>2}/part_{}.py".format(year, day, "a"))
        Path("year_{}/day_{:0>2}/example_part.py".format(year, day)) \
            .rename(part_a_path)
        ctx.invoke(refresh_challenge_input, year=year, day=day)
    if not part_path.exists():
        shutil.copy(
            Path("example_year/example_day/example_part.py"),
            part_path)

    click.echo(
        f"Added challenge "
        f"{click.style(f'{year} {day} {part.upper()}', fg='green')} at "
        f"{click.style(str(part_path), fg='green')}")

    update_context_object(ctx, {
        'years_and_days': get_years_and_days(),
    })


@aoc.command()
@click.argument('year', type=int)
@click.argument('day', type=int)
def refresh_challenge_input(year, day):
    input_path = Path("year_{}/day_{:0>2}/part_a_input.txt".format(year, day))
    _input = get_input_from_site(year, day)
    if not _input:
        click.echo(
            f"Could not update input for "
            f"{click.style(f'{year} {day}', fg='red')}")
        return

    if input_path.exists() and _input == input_path.read_text():
        click.echo(
            f"Input did not change for "
            f"{click.style(f'{year} {day}', fg='yellow')} "
            f"({click.style(f'{len(_input)} bytes', fg='yellow')})")
        return

    input_path.write_text(_input)

    click.echo(
        f"Updated input for {click.style(f'{year} {day}', fg='green')} at "
        f"{click.style(str(input_path), fg='green')} "
        f"({click.style(f'{len(_input)} bytes', fg='green')})")


def get_input_from_site(year, day):
    session_id = getattr(settings, 'AOC_SESSION_ID')
    if not session_id:
        click.echo(
            f"You haven't set {click.style('AOC_SESSION_ID', fg='red')} in "
            f"{click.style('settings.py', fg='red')}")
        return None

    response = requests.get(
        f'https://adventofcode.com/{year}/day/{day}/input',
        cookies={"session": session_id},
        headers={"User-Agent": "advent-of-code-submissions"},
    )
    if not response.ok:
        if response.status_code == 404:
            click.echo(
                f"AOC did not know about challenge's "
                f"{click.style(f'{year} {day}', fg='red')} input: did you "
                f"enter the wrong year/day, is the URL wrong, or are you "
                f"banned?")
        else:
            click.echo(
                f"Could not get {click.style('the input', fg='red')} from "
                f"AOC site - is the internet down, AOC down, the URL is wrong, "
                f"or are you banned?")
        return None

    return response.text


def get_challenge_instance(combined_data, year: int, day: int, part: str):
    year_data = combined_data["years"].get(str(year))
    if not year_data:
        click.echo(
            f"It looks like there is no code for "
            f"{click.style(str(year), fg='red')}")
        return None
    day_data = year_data["days"].get(str(day))
    if not day_data:
        click.echo(
            f"It looks like there is no code for "
            f"{click.style(f'{year} day {day}', fg='red')}")
        return None
    part_data = day_data["parts"].get(part)
    if not part_data:
        click.echo(
            f"It looks like there is no code for "
            f"{click.style(f'{year} day {day} part {part}', fg='red')}")
        return None
    module_name = part_data["module_name"]
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        click.echo(f"Could not find {click.style(module_name, fg='red')}")
        return None

    if not hasattr(module, 'challenge'):
        challenge_class = getattr(module, 'Challenge')
        if not isinstance(challenge_class, type) \
                or not issubclass(challenge_class, utils.BaseChallenge):
            click.echo(
                f"Challenge {click.style(module_name, fg='red')} does not "
                f"use `BaseChallenge` and doesn't specify a `challenge` "
                f"instance")
            return None
        challenge_instance = challenge_class()
    else:
        challenge_instance = getattr(module, 'challenge')

    if not isinstance(challenge_instance, utils.BaseChallenge):
        click.echo(
            f"Challenge {click.style(module_name, fg='red')} `challenge` "
            f"instance is not of `BaseChallenge`")
        return None

    return challenge_instance


@aoc.command(name='list')
@click.option('-y', '--year', type=int)
@click.pass_context
def list_years_and_days(ctx, year: int):
    combined_data = ctx.obj['combined_data']
    if year is None:
        list_years(combined_data)
    else:
        list_days(combined_data, year=str(year))


def list_years(combined_data):
    year_count_text = click.style(
        str(len(combined_data["years"])), fg='green')
    total_stars_text = click.style(str(
        combined_data["total_stars"]) + ' stars', fg='yellow')
    click.echo(f"Found {year_count_text} years with {total_stars_text}:")
    for year, year_data in sorted(combined_data["years"].items(), reverse=True):
        days_with_code = year_data["days_with_code"]
        year_stars = year_data["stars"]
        click.echo(
            f"  * {click.style(year, fg='green')} "
            f"{click.style(str(days_with_code), fg='green')} days with "
            f"code and {click.style(str(year_stars) + ' stars', fg='yellow')}")


def list_days(combined_data, year: str):
    if year not in combined_data["years"]:
        click.echo(
            f"Could not find {click.style(year, fg='red')} in code "
            f"nor any stars")
        return
    year_data = combined_data["years"][year]
    if not year_data["days_with_code"]:
        click.echo(
            f"Could not find {click.style(year, fg='red')} in code, "
            f"but found "
            f"{click.style(str(year_data['stars']) + ' stars', fg='yellow')}")
        return
    click.echo(
        f"Found {click.style(str(year_data['days_with_code']), fg='green')} "
        f"days with code in {click.style(year, fg='green')} with "
        f"{click.style(str(year_data['stars']) + ' stars', fg='yellow')}:")
    days_string = ', '.join(
        (
            click.style(day, fg='green')
            + get_styled_part_status_icon(day_data["parts"]["a"]["status"])
            + get_styled_part_status_icon(day_data["parts"]["b"]["status"])
        )
        for day, day_data in reversed(year_data["days"].items())
        if day_data["has_code"]
    )
    click.echo(f"  * {days_string}")


def get_styled_part_status_icon(status):
    if status == PART_STATUS_COMPLETE:
        return click.style('*', fg='yellow')
    elif status == PART_STATUS_FAILED:
        return click.style('x', fg='red')
    elif status == PART_STATUS_DID_NOT_ATTEMPT:
        return ''
    elif status == PART_STATUS_COULD_NOT_ATTEMPT:
        return click.style('!', fg='white')
    else:
        raise Exception(f"Unknown part status '{status}'")


PART_STATUS_COMPLETE = 'complete'
PART_STATUS_FAILED = 'failed'
PART_STATUS_DID_NOT_ATTEMPT = 'did-not-attempt'
PART_STATUS_COULD_NOT_ATTEMPT = 'could-not-attempt'

PART_STATUSES = [
    PART_STATUS_COMPLETE,
    PART_STATUS_FAILED,
    PART_STATUS_DID_NOT_ATTEMPT,
    PART_STATUS_COULD_NOT_ATTEMPT,
]


def combine_data(site_data, years_and_days):
    if site_data is None:
        combined_data = {
            "has_site_data": False,
            "user_name": None,
            "total_stars": 0,
            "years": {},
        }
    else:
        combined_data = copy.deepcopy(site_data)
        combined_data["has_site_data"] = True
    days_by_year = {
        str(year): days
        for year, days, missing_days in years_and_days
    }
    for year in days_by_year:
        if year not in combined_data['years']:
            combined_data['years'][year] = {
                "stars": 0,
                "days": {
                    str(day): 0
                    for day in range(1, 26)
                },
            }
    for year, year_data in combined_data["years"].items():
        year_stars = year_data["stars"]
        year_data["year"] = year
        year_data["has_code"] = Path("year_{}/__init__.py".format(year))\
            .exists()
        for day, day_stars in list(year_data["days"].items()):
            has_part_a = Path("year_{}/day_{:0>2}/part_{}.py".format(
                year, day, "a",
            )).exists()
            has_part_b = Path("year_{}/day_{:0>2}/part_{}.py".format(
                year, day, "b",
            )).exists()
            if day_stars >= 1:
                part_a_status = PART_STATUS_COMPLETE
            elif has_part_a:
                part_a_status = PART_STATUS_FAILED
            else:
                part_a_status = PART_STATUS_DID_NOT_ATTEMPT
            if day_stars == 2:
                part_b_status = PART_STATUS_COMPLETE
            elif day_stars == 1:
                if day == "25" and year_stars < 49:
                    part_b_status = PART_STATUS_COULD_NOT_ATTEMPT
                elif has_part_b:
                    part_b_status = PART_STATUS_FAILED
                else:
                    part_b_status = PART_STATUS_DID_NOT_ATTEMPT
            elif has_part_a:
                part_b_status = PART_STATUS_COULD_NOT_ATTEMPT
            else:
                part_b_status = PART_STATUS_DID_NOT_ATTEMPT
            year_data["days"][day] = {
                "year": year,
                "day": "{:0>2}".format(day),
                "stars": day_stars,
                "has_code": has_part_a or has_part_b,
                "parts": {
                    part: {
                        "year": year,
                        "day": "{:0>2}".format(day),
                        "part": part,
                        "has_code": has_part,
                        "star": day_stars >= minimum_stars,
                        "status": part_status,
                        "module_name": "year_{}.day_{:0>2}.part_{}".format(
                            year, day, part),
                    }
                    for part, minimum_stars, has_part, part_status
                    in [
                        ("a", 1, has_part_a, part_a_status),
                        ("b", 2, has_part_b, part_b_status),
                    ]
                }
            }
        year_data["by_part_status"] = {
            **{
                status: 0
                for status in PART_STATUSES
            },
            **{
                part_status: len(list(items))
                for part_status, items in itertools.groupby(sorted(
                    part["status"]
                    for day in year_data["days"].values()
                    for part in day["parts"].values()
                ))
            },
        }
        year_data["days_with_code"] = sum(
            1
            for day_data in year_data["days"].values()
            if day_data["has_code"]
        )
    combined_data["years_with_code"] = sum(
        1
        for year_data in combined_data["years"].values()
        if year_data["days_with_code"] > 0
    )

    return combined_data


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
@click.pass_context
def fetch(ctx):
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
        update_context_object(ctx, {
            'site_data': data,
        })
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
        str(year): {
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

    return str(day), stars


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
    stars_match = re.compile(r'^(\d+)\*$').match(stars_node.text.strip())
    if not stars_match:
        return default

    stars_text, = stars_match.groups()
    return int(stars_text)


@aoc.command()
@click.pass_context
def update_readme(ctx):
    combined_data = ctx.obj["combined_data"]
    if not combined_data["has_site_data"]:
        click.echo(
            f"Since {click.style('local site data', fg='red')} are missing the "
            f"README {click.style('cannot be updated', fg='red')}: run "
            f"`aoc fetch` first")
        return

    readme_path = Path('./README.md')
    readme_text = readme_path.read_text()

    updated_readme_text = update_readme_text(combined_data, readme_text)
    if updated_readme_text == readme_text:
        click.echo(f"No need to update {click.style('README', fg='green')}")
        return

    readme_path.write_text(updated_readme_text)
    click.echo(f"Updated {click.style('README', fg='green')} with site data")


def update_readme_text(combined_data, readme_text):
    updated_readme_text = update_summary_in_readme_text(
        combined_data, readme_text)
    updated_readme_text = update_submissions_in_readme_text(
        combined_data, updated_readme_text)

    return updated_readme_text


def update_submissions_in_readme_text(combined_data, readme_text):
    submissions_indexes = get_readme_submissions_indexes(readme_text)
    if not submissions_indexes:
        return readme_text

    submissions_text = get_submissions_text(combined_data)

    return replace_text(readme_text, submissions_indexes, submissions_text)


def get_submissions_text(combined_data):
    years = sorted(combined_data["years"], reverse=True)
    headers = ('',) + tuple(years)
    dividers = (' ---:',) + (':---:',) * len(years)
    year_stars = ('',) + tuple(
        get_submission_year_stars_text(combined_data["years"][year])
        for year in years
    )
    year_links_tuples = [
        (
            (
                f"[Code][co-{str(year)[-2:]}]"
                if year_data["has_code"] else
                'Code'
            ),
            '&',
            '',
            f"[Challenges][ch-{year[-2:]}]",
        )
        for year in years
        for year_data in (combined_data["years"][year],)
    ]
    day_links_tuples_list = [
        [
            get_submission_year_day_stars_tuple(
                combined_data["years"][year]["days"][str(day)])
            for year in years
        ]
        for day in range(1, 26)
    ]

    list_of_tuples_to_align = [
        list(column)
        for column
        in zip(*([year_links_tuples] + day_links_tuples_list))
    ]
    list_of_aligned_tuples = [
        align_rows(column)
        for column in list_of_tuples_to_align
    ]

    aligned_year_links_tuples = [
        _tuple[0]
        for _tuple in list_of_aligned_tuples
    ]
    aligned_day_links_tuples_list = list(zip(*(
        _tuple[1:]
        for _tuple in list_of_aligned_tuples
    )))

    year_links = ('',) + tuple(map(' '.join, aligned_year_links_tuples))
    day_links_list = [
        ('{: >2}'.format(day),) + tuple(map(' '.join, day_links_tuples))
        for day, day_links_tuples
        in zip(range(1, 26), aligned_day_links_tuples_list)
    ]

    table_rows = [
        headers,
        dividers,
        year_links,
        year_stars,
    ] + day_links_list

    aligned_table_rows = align_rows(table_rows)

    table = "\n".join(
        '| {} |'.format(' | '.join(row))
        for row in aligned_table_rows
    )

    link_definitions = "\n\n".join(
        "\n".join([
            "[ch-{}]: https://adventofcode.com/{}".format(year[-2:], year),
            "[co-{}]: year_{}".format(year[-2:], year),
        ] + sum((
            [
                "[ch-{}-{:0>2}]: https://adventofcode.com/{}/day/{}".format(
                    year[-2:],
                    day,
                    year,
                    day,
                ),
                "[co-{}-{:0>2}]: year_{}/day_{:0>2}".format(
                    year[-2:],
                    day,
                    year,
                    day,
                ),
            ]
            for day in range(1, 26)
        ), []))
        for year in years
    )

    return "\n\n{}\n\n{}\n\n".format(
        table,
        link_definitions,
    )


def align_rows(rows):
    row_sizes = set(map(len, rows))
    if len(row_sizes) != 1:
        raise Exception(
            f"Expected rows of equal size but got multiple sizes: "
            f"{', '.join(map(str, sorted(row_sizes)))}")
    column_lengths = tuple(
        max(map(len, column))
        for column in zip(*rows)
    )
    column_formats = tuple(
        f"{{: <{column_length}}}"
        for column_length in column_lengths
    )

    return [
        tuple(
            _format.format(cell)
            for _format, cell in zip(column_formats, row)
        )
        for row in rows
    ]


PART_STATUS_EMOJI_MAP = {
    PART_STATUS_COMPLETE: ':star:',
    PART_STATUS_FAILED: ':x:',
    PART_STATUS_DID_NOT_ATTEMPT: '',
    PART_STATUS_COULD_NOT_ATTEMPT: ':grey_exclamation:',
}


def get_submission_year_day_stars_tuple(day_data):
    year = day_data["year"]
    day = day_data["day"]
    has_part_a = day_data["parts"]["a"]["has_code"]
    return (
        (
            "[Code][co-{}-{}]".format(year[-2:], day)
            if has_part_a else
            'Code'
        ),
        PART_STATUS_EMOJI_MAP[day_data["parts"]["a"]["status"]],
        PART_STATUS_EMOJI_MAP[day_data["parts"]["b"]["status"]],
        "[Challenge][ch-{}-{}]".format(year[-2:], day),
    )


def get_submission_year_stars_text(year_data):
    if year_data["stars"] == 50:
        return f"50 :star: :star:"

    return "{} :star: / {} :x: / {} :grey_exclamation:".format(
        year_data["stars"],
        year_data["by_part_status"][PART_STATUS_FAILED],
        year_data["by_part_status"][PART_STATUS_COULD_NOT_ATTEMPT],
    )


def update_summary_in_readme_text(combined_data, readme_text):
    summary_indexes = get_readme_summary_indexes(readme_text)
    if not summary_indexes:
        return readme_text

    summary_text = get_summary_text(combined_data)

    return replace_text(readme_text, summary_indexes, summary_text)


def get_summary_text(combined_data):
    headers = ['Total'] + sorted(combined_data["years"], reverse=True)
    return "\n\n{}\n{}\n{}\n\n".format(
        '| {} |'.format(' | '.join(headers)),
        '| {} |'.format(' | '.join(['---'] * len(headers))),
        '| {} |'.format(' | '.join(
            "{} :star:{}".format(
                stars,
                ' :star:' if header != 'Total' and stars == 50 else '',
            )
            for header in headers
            for stars in ((
                combined_data["total_stars"]
                if header == 'Total' else
                combined_data["years"][header]["stars"]
            ),)
        )),
    )


def replace_text(original, indexes, replacement):
    start_index, end_index = indexes

    return "".join([
        original[:start_index],
        replacement,
        original[end_index:],
    ])


def get_readme_summary_indexes(readme_text):
    summary_start_marker = "[//]: # (summary-start)"
    summary_end_marker = "[//]: # (summary-end)"

    return get_readme_marker_indexes(
        readme_text, summary_start_marker, summary_end_marker, "summary")


def get_readme_submissions_indexes(readme_text):
    submissions_start_marker = "[//]: # (submissions-start)"
    submissions_end_marker = "[//]: # (submissions-end)"

    return get_readme_marker_indexes(
        readme_text, submissions_start_marker, submissions_end_marker,
        "submissions")


def get_readme_marker_indexes(readme_text, start_marker, end_marker,
                              marker_name):
    if start_marker in readme_text:
        start_index = (
            readme_text.index(start_marker)
            + len(start_marker)
        )
    else:
        start_index = None
    if end_marker in readme_text:
        end_index = readme_text.index(end_marker)
    else:
        end_index = None

    missing_markers = [
        marker
        for marker, index in [
            (start_marker, start_index),
            (end_marker, end_index),
        ]
        if index is None
    ]
    if missing_markers:
        missing_markers_text = ', '.join(
            click.style(marker, fg='red')
            for marker in sorted(missing_markers)
        )
        click.echo(
            f"There were some {click.style('missing markers', fg='red')} in "
            f"the README: {missing_markers_text} - did you "
            f"accidentally remove or change them?")
        return None

    if end_index < start_index:
        click.echo(
            f"Markers for {marker_name} where in the "
            f"{click.style('opposite order', fg='red')}: "
            f"{click.style(start_marker, fg='red')} should be before "
            f"{click.style(end_marker, fg='red')}, not the other way "
            f"around")
        return None

    return start_index, end_index


if __name__ == '__main__':
    aoc()
