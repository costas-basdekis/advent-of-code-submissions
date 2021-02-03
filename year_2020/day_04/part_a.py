#!/usr/bin/env python3
import re
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        242
        """
        return len(PassportBatch.from_batch_text(_input).passports)


class Field:
    def parse_and_validate(self, value):
        raise NotImplementedError()


class NumberField(Field):
    NUMBERS = set("0123456789")

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def parse_and_validate(self, value):
        """
        >>> NumberField().parse_and_validate(1821)
        (True, 1821)
        >>> NumberField().parse_and_validate(-1821)
        (True, -1821)
        >>> NumberField(1700, 1900).parse_and_validate(1821)
        (True, 1821)
        >>> NumberField(1700, 1900).parse_and_validate(-1821)
        (False, None)
        >>> NumberField(1700, 1900).parse_and_validate(1621)
        (False, None)
        """
        try:
            year = int(value)
        except (ValueError, TypeError):
            return False, None

        if self.min_value is not None and year < self.min_value:
            return False, None

        if self.max_value is not None and year > self.max_value:
            return False, None

        return True, year


class HeightField(NumberField):
    CmField = NumberField()
    InField = NumberField()
    PlainField = NumberField()

    def parse_and_validate(self, value):
        """
        >>> HeightField().parse_and_validate("187cm")
        (True, 187)
        >>> HeightField().parse_and_validate("172in")
        (True, 436.88)
        >>> HeightField().parse_and_validate("140")
        (True, 140)
        >>> HeightField().parse_and_validate("1.6m")
        (False, None)
        """
        if value.endswith("cm"):
            return self.CmField.parse_and_validate(value[:-2])
        if value.endswith("in"):
            validated, parsed = self.InField.parse_and_validate(value[:-2])
            if not validated:
                return validated, parsed
            return validated, parsed * 2.54
        return self.PlainField.parse_and_validate(value)


class NoValidationField(Field):
    def parse_and_validate(self, value):
        return True, value


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
        "byr": NumberField().parse_and_validate,
        "iyr": NumberField().parse_and_validate,
        "eyr": NumberField().parse_and_validate,
        "hgt": HeightField().parse_and_validate,
        "hcl": NoValidationField().parse_and_validate,
        "ecl": NoValidationField().parse_and_validate,
        "cid": NoValidationField().parse_and_validate,
        "pid": NoValidationField().parse_and_validate,
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
        valid_parsed_fields = {
            field: parsed
            for field, (validated, parsed) in (
                (cls.FIELD_NAME_MAP[field],
                 cls.FIELD_TRANSFORMATION_MAP[field](value))
                for field, value in raw_fields.items()
            )
            if validated
        }
        if len(valid_parsed_fields) != len(raw_fields):
            return None

        return cls(**{
            "country_id": None,
            **valid_parsed_fields,
        })


class PassportBatch:
    PASSPORT_CLASS = Passport
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
            None, map(cls.PASSPORT_CLASS.from_passport_text, passport_texts)))

        return cls(passports)

    def __init__(self, passports):
        self.passports = passports


Challenge.main()
challenge = Challenge()
