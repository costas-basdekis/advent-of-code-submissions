#!/usr/bin/env python3
import utils

from year_2020.day_04 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        186
        """
        return len(StrictPassportBatch.from_batch_text(_input).passports)


class NoValueAcceptedField(part_a.Field):
    def parse_and_validate(self, value):
        return False, None


class StrictHeightField(part_a.HeightField):
    CmField = part_a.NumberField(150, 193)
    InField = part_a.NumberField(59, 76)
    PlainField = NoValueAcceptedField()

    def parse_and_validate(self, value):
        """
        >>> StrictHeightField().parse_and_validate("187cm")
        (True, 187)
        >>> StrictHeightField().parse_and_validate("150cm")
        (True, 150)
        >>> StrictHeightField().parse_and_validate("193cm")
        (True, 193)
        >>> StrictHeightField().parse_and_validate("143cm")
        (False, None)
        >>> StrictHeightField().parse_and_validate("194cm")
        (False, None)
        >>> StrictHeightField().parse_and_validate("72in")
        (True, 182.88)
        >>> StrictHeightField().parse_and_validate("172in")
        (False, None)
        >>> StrictHeightField().parse_and_validate("140")
        (False, None)
        >>> StrictHeightField().parse_and_validate("1.6m")
        (False, None)
        """
        return super().parse_and_validate(value)


class ColourField(part_a.Field):
    HEX_NUMBERS = set("0123456789abcdef")

    def parse_and_validate(self, value):
        if len(value) != len("#123456"):
            return False, None

        if value[0] != "#":
            return False, None

        if not set(value[1:]).issubset(self.HEX_NUMBERS):
            return False, None

        return True, value


class FixedValuesField(part_a.Field):
    def __init__(self, fixed_values):
        self.fixed_values = set(fixed_values)

    def parse_and_validate(self, value):
        if value not in self.fixed_values:
            return False, None

        return True, value


class PassportField(part_a.Field):
    NUMBERS = set("0123456789")

    def parse_and_validate(self, value):
        if len(value) != 9:
            return False, None

        if not set(value).issubset(self.NUMBERS):
            return False, None

        return True, value


class StrictPassport(part_a.Passport):
    FIELD_TRANSFORMATION_MAP = {
        **part_a.Passport.FIELD_TRANSFORMATION_MAP,
        "byr": part_a.NumberField(1920, 2002).parse_and_validate,
        "iyr": part_a.NumberField(2010, 2020).parse_and_validate,
        "eyr": part_a.NumberField(2020, 2030).parse_and_validate,
        "hgt": StrictHeightField().parse_and_validate,
        "hcl": ColourField().parse_and_validate,
        "ecl": FixedValuesField({
            "amb", "blu", "brn", "gry", "grn", "hzl", "oth",
        }).parse_and_validate,
        "pid": PassportField().parse_and_validate,
    }


class StrictPassportBatch(part_a.PassportBatch):
    PASSPORT_CLASS = StrictPassport

    @classmethod
    def from_batch_text(cls, batch_text):
        """
        >>> StrictPassportBatch.from_batch_text("\\n" * 5).passports
        []
        >>> StrictPassportBatch.from_batch_text(
        ...     "eyr:1972 cid:100\\n"
        ...     "hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926\\n"
        ...     "\\n"
        ...     "iyr:2019\\n"
        ...     "hcl:#602927 eyr:1967 hgt:170cm\\n"
        ...     "ecl:grn pid:012533040 byr:1946\\n"
        ...     "\\n"
        ...     "hcl:dab227 iyr:2012\\n"
        ...     "ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277\\n"
        ...     "\\n"
        ...     "hgt:59cm ecl:zzz\\n"
        ...     "eyr:2038 hcl:74454a iyr:2023\\n"
        ...     "pid:3556412378 byr:2007\\n"
        ... ).passports
        []
        >>> StrictPassportBatch.from_batch_text(
        ...     "pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980\\n"
        ...     "hcl:#623a2f\\n"
        ...     "\\n"
        ...     "eyr:2029 ecl:blu cid:129 byr:1989\\n"
        ...     "iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm\\n"
        ...     "\\n"
        ...     "hcl:#888785\\n"
        ...     "hgt:164cm byr:2001 iyr:2015 cid:88\\n"
        ...     "pid:545766238 ecl:hzl\\n"
        ...     "eyr:2022\\n"
        ...     "\\n"
        ...     "iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719\\n"
        ... ).passports
        [StrictPassport(birth_year=1980, issue_year=2012, expiration_year=2030, height=187.96, hair_colour='#623a2f', eye_colour='grn', id='087499704', country_id=None), \
StrictPassport(birth_year=1989, issue_year=2014, expiration_year=2029, height=165, hair_colour='#a97842', eye_colour='blu', id='896056539', country_id='129'), \
StrictPassport(birth_year=2001, issue_year=2015, expiration_year=2022, height=164, hair_colour='#888785', eye_colour='hzl', id='545766238', country_id='88'), \
StrictPassport(birth_year=1944, issue_year=2010, expiration_year=2021, height=158, hair_colour='#b6652a', eye_colour='blu', id='093154719', country_id=None)\
]
        >>> StrictPassportBatch.from_batch_text(
        ...     "eyr:1972 cid:100\\n"
        ...     "hcl:#18171d ecl:amb hgt:170 pid:186cm iyr:2018 byr:1926\\n"
        ...     "\\n"
        ...     "iyr:2019\\n"
        ...     "hcl:#602927 eyr:1967 hgt:170cm\\n"
        ...     "ecl:grn pid:012533040 byr:1946\\n"
        ...     "\\n"
        ...     "hcl:dab227 iyr:2012\\n"
        ...     "ecl:brn hgt:182cm pid:021572410 eyr:2020 byr:1992 cid:277\\n"
        ...     "\\n"
        ...     "hgt:59cm ecl:zzz\\n"
        ...     "eyr:2038 hcl:74454a iyr:2023\\n"
        ...     "pid:3556412378 byr:2007\\n"
        ...     "\\n"
        ...     "pid:087499704 hgt:74in ecl:grn iyr:2012 eyr:2030 byr:1980\\n"
        ...     "hcl:#623a2f\\n"
        ...     "\\n"
        ...     "eyr:2029 ecl:blu cid:129 byr:1989\\n"
        ...     "iyr:2014 pid:896056539 hcl:#a97842 hgt:165cm\\n"
        ...     "\\n"
        ...     "hcl:#888785\\n"
        ...     "hgt:164cm byr:2001 iyr:2015 cid:88\\n"
        ...     "pid:545766238 ecl:hzl\\n"
        ...     "eyr:2022\\n"
        ...     "\\n"
        ...     "iyr:2010 hgt:158cm hcl:#b6652a ecl:blu byr:1944 eyr:2021 pid:093154719\\n"
        ... ).passports
        [StrictPassport(birth_year=1980, issue_year=2012, expiration_year=2030, height=187.96, hair_colour='#623a2f', eye_colour='grn', id='087499704', country_id=None), \
StrictPassport(birth_year=1989, issue_year=2014, expiration_year=2029, height=165, hair_colour='#a97842', eye_colour='blu', id='896056539', country_id='129'), \
StrictPassport(birth_year=2001, issue_year=2015, expiration_year=2022, height=164, hair_colour='#888785', eye_colour='hzl', id='545766238', country_id='88'), \
StrictPassport(birth_year=1944, issue_year=2010, expiration_year=2021, height=158, hair_colour='#b6652a', eye_colour='blu', id='093154719', country_id=None)\
]
        """
        return super().from_batch_text(batch_text)


Challenge.main()
challenge = Challenge()
