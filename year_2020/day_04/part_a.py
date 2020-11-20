#!/usr/bin/env python3
import doctest
import re
from collections import namedtuple

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    242
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return len(PassportBatch.from_batch_text(_input).passports)


class PassportBatch:
    re_empty_lines = re.compile(r"\n\n+")

    @classmethod
    def from_batch_text(cls, batch_text):
        """
        >>> PassportBatch.from_batch_text("\\n" * 5).passports
        []
        >>> PassportBatch.from_batch_text(
        ...     "ecl:gry pid:860033327 eyr:2020 hcl:#fffffd\\n"
        ...     "byr:1937 iyr:2017 cid:147 hgt:183cm\\n"
        ...     "\\n"
        ...     "iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884\\n"
        ...     "hcl:#cfa07d byr:1929\\n"
        ...     "\\n"
        ...     "hcl:#ae17e1 iyr:2013\\n"
        ...     "eyr:2024\\n"
        ...     "ecl:brn pid:760753108 byr:1931\\n"
        ...     "hgt:179cm\\n"
        ...     "\\n"
        ...     "hcl:#cfa07d eyr:2025 pid:166559648\\n"
        ...     "iyr:2011 ecl:brn hgt:59in        \\n"
        ... ).passports
        [Passport(birth_year=1937, issue_year=2017, expiration_year=2020, height=183, hair_colour='#fffffd', eye_colour='gry', id='860033327', country_id='147'), \
Passport(birth_year=1931, issue_year=2013, expiration_year=2024, height=179, hair_colour='#ae17e1', eye_colour='brn', id='760753108', country_id=None)\
]
        """
        passport_texts = filter(None, cls.re_empty_lines.split(batch_text))
        passports = list(filter(
            None, map(Passport.from_passport_text, passport_texts)))

        return cls(passports)

    def __init__(self, passports):
        self.passports = passports


def parse_height(height_str):
    """
    >>> parse_height("187cm")
    187
    >>> parse_height("172in")
    436.88
    >>> parse_height("140")
    140
    >>> parse_height("1.6m")
    Traceback (most recent call last):
    ...
    Exception: Not a valid height: 1.6m
    """
    if height_str.endswith("cm"):
        return int(height_str[:-2])
    if height_str.endswith("in"):
        return int(height_str[:-2]) * 2.54
    if set("1234567890").issuperset(set(height_str)):
        return int(height_str)
    raise Exception(f"Not a valid height: {height_str}")


class Passport(namedtuple("Passport", (
        "birth_year", "issue_year", "expiration_year", "height",
        "hair_colour", "eye_colour", "id", "country_id"))):
    re_fields = re.compile(r"\s+")
    re_field = re.compile(r"^(\w+):(.+)$")

    REQUIRED_FIELDS = {
        "byr",
        "iyr",
        "eyr",
        "hgt",
        "hcl",
        "ecl",
        "pid",
    }
    FIELD_NAME_MAP = {
        "byr": "birth_year",
        "iyr": "issue_year",
        "eyr": "expiration_year",
        "hgt": "height",
        "hcl": "hair_colour",
        "ecl": "eye_colour",
        "cid": "country_id",
        "pid": "id",
    }
    FIELD_TRANSFORMATION_MAP = {
        "byr": int,
        "iyr": int,
        "eyr": int,
        "hgt": parse_height,
        "hcl": str,
        "ecl": str,
        "cid": str,
        "pid": str,
    }

    @classmethod
    def from_passport_text(cls, passport_text):
        """
        >>> Passport.from_passport_text(
        ...     "ecl:gry pid:860033327 eyr:2020 hcl:#fffffd\\n"
        ...     "byr:1937 iyr:2017 cid:147 hgt:183cm\\n"
        ... )
        Passport(birth_year=1937, issue_year=2017, expiration_year=2020, height=183, hair_colour='#fffffd', eye_colour='gry', id='860033327', country_id='147')
        >>> Passport.from_passport_text(
        ...     "ecl:gry pid:860033327 eyr:2020 hcl:#fffffd\\n"
        ...     "byr:1937 iyr:2017 hgt:183cm\\n"
        ... )
        Passport(birth_year=1937, issue_year=2017, expiration_year=2020, height=183, hair_colour='#fffffd', eye_colour='gry', id='860033327', country_id=None)
        >>> Passport.from_passport_text(
        ...     "ecl:gry pid:860033327 eyr:2020 hcl:#fffffd\\n"
        ...     "byr:1937 iyr:2017 cid:147 \\n"
        ... )
        >>> Passport.from_passport_text(
        ...     "iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884\\n"
        ...     "hcl:#cfa07d byr:1929\\n"
        ... )
        >>> Passport.from_passport_text(
        ...     "iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884\\n"
        ...     "hcl:#cfa07d byr:1929 hgt:183cm\\n"
        ... )
        Passport(birth_year=1929, issue_year=2013, expiration_year=2023, height=183, hair_colour='#cfa07d', eye_colour='amb', id='028048884', country_id='350')
        >>> Passport.from_passport_text(
        ...     "iyr:2013 ecl:amb eyr:2023 pid:028048884\\n"
        ...     "hcl:#cfa07d byr:1929 hgt:183cm\\n"
        ... )
        Passport(birth_year=1929, issue_year=2013, expiration_year=2023, height=183, hair_colour='#cfa07d', eye_colour='amb', id='028048884', country_id=None)
        """
        fields_str = filter(None, cls.re_fields.split(passport_text))
        raw_field_tuples = [
            cls.re_field.match(field_str).groups()
            for field_str in fields_str
        ]
        raw_fields = dict(raw_field_tuples)
        has_required_fields_missing = any(
            field
            for field in cls.REQUIRED_FIELDS
            if field not in raw_fields
        )
        if has_required_fields_missing:
            return None

        return cls(**{
            "country_id": None,
            **{
                cls.FIELD_NAME_MAP[field]:
                cls.FIELD_TRANSFORMATION_MAP[field](value)
                for field, value in raw_fields.items()
            },
        })


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
