#!/usr/bin/env python3
import datetime
import doctest
import re
from collections import namedtuple, defaultdict

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    143415
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    sleepiest_profile = Observations.from_lines(_input).attach_guard_ids()\
        .get_sleep_schedule()\
        .get_guards_sleep_profiles()\
        .get_sleepiest_profile_by_strategy_1()
    if not sleepiest_profile:
        raise Exception("No sleepiest profile")

    return sleepiest_profile.get_signature()


class GuardSleepProfiles:
    @classmethod
    def from_sleep_schedule(cls, sleep_durations):
        """
        >>> SleepSchedule([]).get_guards_sleep_profiles().sleep_profiles
        []
        >>> SleepSchedule([
        ...     SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=5, guard_id='10', duration_minutes=20),
        ...     SleepDuration(start_date='1518-11-01', start_hour=1, start_minute=5, guard_id='11', duration_minutes=20),
        ... ]).get_guards_sleep_profiles().sleep_profiles
        [GuardSleepProfile(guard_id='10', sleep_minute_count=20, most_common_minute=None), \
GuardSleepProfile(guard_id='11', sleep_minute_count=20, most_common_minute=None)]
        >>> SleepSchedule([
        ...     SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=5, guard_id='10', duration_minutes=20),
        ...     SleepDuration(start_date='1518-11-01', start_hour=2, start_minute=5, guard_id='10', duration_minutes=1),
        ...     SleepDuration(start_date='1518-11-01', start_hour=1, start_minute=5, guard_id='11', duration_minutes=20),
        ... ]).get_guards_sleep_profiles().sleep_profiles
        [GuardSleepProfile(guard_id='10', sleep_minute_count=21, most_common_minute=5), \
GuardSleepProfile(guard_id='11', sleep_minute_count=20, most_common_minute=None)]
        >>> SleepSchedule([
        ...     SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=5, guard_id='10', duration_minutes=20),
        ...     SleepDuration(start_date='1518-11-01', start_hour=2, start_minute=5, guard_id='10', duration_minutes=1),
        ...     SleepDuration(start_date='1518-11-01', start_hour=1, start_minute=5, guard_id='11', duration_minutes=20),
        ...     SleepDuration(start_date='1518-11-01', start_hour=1, start_minute=35, guard_id='11', duration_minutes=20),
        ... ]).get_guards_sleep_profiles().sleep_profiles
        [GuardSleepProfile(guard_id='10', sleep_minute_count=21, most_common_minute=5), \
GuardSleepProfile(guard_id='11', sleep_minute_count=40, most_common_minute=None)]
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:05] falls asleep\\n"
        ...     "[1518-11-01 00:25] wakes up\\n"
        ...     "[1518-11-01 00:30] falls asleep\\n"
        ...     "[1518-11-01 00:55] wakes up\\n"
        ...     "[1518-11-01 23:58] Guard #99 begins shift\\n"
        ...     "[1518-11-02 00:40] falls asleep\\n"
        ...     "[1518-11-02 00:50] wakes up\\n"
        ...     "[1518-11-03 00:05] Guard #10 begins shift\\n"
        ...     "[1518-11-03 00:24] falls asleep\\n"
        ...     "[1518-11-03 00:29] wakes up\\n"
        ...     "[1518-11-04 00:02] Guard #99 begins shift\\n"
        ...     "[1518-11-04 00:36] falls asleep\\n"
        ...     "[1518-11-04 00:46] wakes up\\n"
        ...     "[1518-11-05 00:03] Guard #99 begins shift\\n"
        ...     "[1518-11-05 00:45] falls asleep\\n"
        ...     "[1518-11-05 00:55] wakes up\\n"
        ... ).attach_guard_ids()\\
        ...     .get_sleep_schedule()\\
        ...     .get_guards_sleep_profiles()\\
        ...     .sleep_profiles
        [GuardSleepProfile(guard_id='10', sleep_minute_count=50, most_common_minute=24), \
GuardSleepProfile(guard_id='99', sleep_minute_count=30, most_common_minute=45)]
        """
        sleep_count_by_guard_and_minute = {}
        for sleep_duration in sleep_durations:
            sleep_minutes = sleep_duration.get_sleep_minutes()
            for minute in sleep_minutes:
                by_minute = sleep_count_by_guard_and_minute\
                    .setdefault(sleep_duration.guard_id,
                                defaultdict(lambda: 0))
                by_minute[minute] += 1
        return cls([
            GuardSleepProfile(
                guard_id, sum(by_minute.values()),
                cls.get_max_minute(by_minute))
            for guard_id, by_minute
            in sorted(sleep_count_by_guard_and_minute.items())
        ])

    @classmethod
    def get_max_minute(cls, by_minute):
        """
        >>> GuardSleepProfiles.get_max_minute({})
        >>> GuardSleepProfiles.get_max_minute({1: 1})
        1
        >>> GuardSleepProfiles.get_max_minute({1: 1, 2: 1})
        >>> GuardSleepProfiles.get_max_minute({1: 1, 2: 3})
        2
        >>> GuardSleepProfiles.get_max_minute({1: 1, 2: 3, 3: 1})
        2
        >>> GuardSleepProfiles.get_max_minute({1: 1, 2: 3, 3: 1, 4: 2})
        2
        >>> GuardSleepProfiles.get_max_minute({1: 1, 2: 3, 3: 1, 4: 3})
        """
        if not by_minute:
            return None
        max_count = max(by_minute.values())
        minutes_with_max_count = [
            minute
            for minute, count
            in by_minute.items()
            if count == max_count
        ]
        if len(minutes_with_max_count) > 1:
            return None

        minute_with_max_count, = minutes_with_max_count

        return minute_with_max_count

    def __init__(self, sleep_profiles):
        self.sleep_profiles = sleep_profiles

    def get_sleepiest_profile_by_strategy_1(self):
        """
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:05] falls asleep\\n"
        ...     "[1518-11-01 00:25] wakes up\\n"
        ...     "[1518-11-01 00:30] falls asleep\\n"
        ...     "[1518-11-01 00:55] wakes up\\n"
        ...     "[1518-11-01 23:58] Guard #99 begins shift\\n"
        ...     "[1518-11-02 00:40] falls asleep\\n"
        ...     "[1518-11-02 00:50] wakes up\\n"
        ...     "[1518-11-03 00:05] Guard #10 begins shift\\n"
        ...     "[1518-11-03 00:24] falls asleep\\n"
        ...     "[1518-11-03 00:29] wakes up\\n"
        ...     "[1518-11-04 00:02] Guard #99 begins shift\\n"
        ...     "[1518-11-04 00:36] falls asleep\\n"
        ...     "[1518-11-04 00:46] wakes up\\n"
        ...     "[1518-11-05 00:03] Guard #99 begins shift\\n"
        ...     "[1518-11-05 00:45] falls asleep\\n"
        ...     "[1518-11-05 00:55] wakes up\\n"
        ... ).attach_guard_ids()\\
        ...     .get_sleep_schedule()\\
        ...     .get_guards_sleep_profiles()\\
        ...     .get_sleepiest_profile_by_strategy_1()
        GuardSleepProfile(guard_id='10', sleep_minute_count=50, most_common_minute=24)
        """
        if not self.sleep_profiles:
            return None
        max_sleep_minute_count = max(
            sleep_profile.sleep_minute_count
            for sleep_profile in self.sleep_profiles
        )
        sleep_profiles_with_max_sleep_minute_count = [
            sleep_profile
            for sleep_profile in self.sleep_profiles
            if sleep_profile.sleep_minute_count == max_sleep_minute_count
        ]
        if len(sleep_profiles_with_max_sleep_minute_count) > 1:
            return None

        sleep_profile_with_max_sleep_minute_count, = \
            sleep_profiles_with_max_sleep_minute_count

        return sleep_profile_with_max_sleep_minute_count


class GuardSleepProfile(namedtuple(
        "GuardSleepProfile", (
            "guard_id", "sleep_minute_count", "most_common_minute"))):
    def get_signature(self):
        """
        >>> GuardSleepProfile('10', 55, 24).get_signature()
        240
        """
        return int(self.guard_id) * self.most_common_minute


class SleepSchedule:
    @classmethod
    def from_observations(cls, observations):
        """
        >>> SleepSchedule.from_observations([]).sleep_durations
        []
        >>> Observations([
        ...     Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'),
        ...     Observation(date='1518-11-01', hour=0, minute=5, guard_id=None, type='fall-asleep'),
        ...     Observation(date='1518-11-01', hour=0, minute=25, guard_id=None, type='wake-up'),
        ... ]).attach_guard_ids().get_sleep_schedule().sleep_durations
        [SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=5, guard_id='10', duration_minutes=20)]
        >>> Observations([
        ...     Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'),
        ...     Observation(date='1518-11-01', hour=0, minute=5, guard_id=None, type='fall-asleep'),
        ...     Observation(date='1518-11-01', hour=0, minute=25, guard_id=None, type='wake-up'),
        ...     Observation(date='1518-11-01', hour=1, minute=0, guard_id='11', type='begin-shift'),
        ...     Observation(date='1518-11-01', hour=1, minute=5, guard_id=None, type='fall-asleep'),
        ...     Observation(date='1518-11-01', hour=1, minute=25, guard_id=None, type='wake-up'),
        ... ]).attach_guard_ids().get_sleep_schedule().sleep_durations
        [SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=5, guard_id='10', duration_minutes=20), \
SleepDuration(start_date='1518-11-01', start_hour=1, start_minute=5, guard_id='11', duration_minutes=20)]
        >>> Observations([
        ...     Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'),
        ...     Observation(date='1518-11-01', hour=0, minute=5, guard_id=None, type='fall-asleep'),
        ...     Observation(date='1518-11-01', hour=1, minute=0, guard_id='11', type='begin-shift'),
        ...     Observation(date='1518-11-01', hour=1, minute=5, guard_id=None, type='fall-asleep'),
        ...     Observation(date='1518-11-01', hour=1, minute=25, guard_id=None, type='wake-up'),
        ... ]).attach_guard_ids().get_sleep_schedule().sleep_durations
        [SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=5, guard_id='10', duration_minutes=55), \
SleepDuration(start_date='1518-11-01', start_hour=1, start_minute=5, guard_id='11', duration_minutes=20)]
        """
        if not observations:
            return cls([])
        if observations[-1].type == Observation.TYPE_FALL_ASLEEP:
            raise Exception("Last observation can't be falling asleep")

        return cls(list(filter(None, (
            SleepDuration.from_observation_pair(previous, observation)
            for previous, observation in zip(observations, observations[1:])
        ))))

    def __init__(self, sleep_durations):
        self.sleep_durations = sleep_durations

    def get_guards_sleep_profiles(self):
        return GuardSleepProfiles.from_sleep_schedule(self.sleep_durations)


class SleepDuration(namedtuple(
        "SleepDuration", (
            "start_date", "start_hour", "start_minute", "guard_id",
            "duration_minutes"))):
    @classmethod
    def from_observation_pair(cls, previous, observation):
        """
        >>> SleepDuration.from_observation_pair(
        ...     Observation('1518-11-01', 0, 0, '10', 'begin-shift'),
        ...     Observation('1518-11-01', 2, 5, '10', 'begin-shift'))
        >>> SleepDuration.from_observation_pair(
        ...     Observation('1518-11-01', 0, 0, '10', 'fall-asleep'),
        ...     Observation('1518-11-01', 0, 0, '10', 'begin-shift'))
        >>> SleepDuration.from_observation_pair(
        ...     Observation('1518-11-01', 0, 0, '10', 'fall-asleep'),
        ...     Observation('1518-11-01', 2, 5, '10', 'begin-shift'))
        SleepDuration(start_date='1518-11-01', start_hour=0, start_minute=0, guard_id='10', duration_minutes=125)
        """
        if previous.type != Observation.TYPE_FALL_ASLEEP:
            return None
        if observation.type not in \
                [Observation.TYPE_WAKE_UP, Observation.TYPE_BEGIN_SHIFT]:
            raise Exception(
                f"Unexpected second observation type {observation.type}")
        duration_minutes = observation.duration_minutes_since(previous)
        if duration_minutes < 0:
            raise Exception("Second observation was in the past")
        if not duration_minutes:
            return None
        return cls(
            previous.date, previous.hour, previous.minute, previous.guard_id,
            duration_minutes)

    def get_sleep_minutes(self):
        """
        >>> SleepDuration('1518-11-01', 0, 0, '10', 5).get_sleep_minutes()
        [0, 1, 2, 3, 4]
        >>> SleepDuration('1518-11-01', 0, 57, '10', 5).get_sleep_minutes()
        [57, 58, 59, 0, 1]
        >>> SleepDuration('1518-11-01', 0, 57, '10', 65).get_sleep_minutes()[:6]
        [57, 58, 59, 0, 1, 2]
        >>> SleepDuration('1518-11-01', 0, 57, '10', 65).get_sleep_minutes()[-6:]
        [56, 57, 58, 59, 0, 1]
        """
        return [
            minute % 60
            for minute
            in range(self.start_minute,
                     self.start_minute + self.duration_minutes)
        ]


class Observations:
    @classmethod
    def from_lines(cls, observations_text):
        """
        >>> Observations.from_lines("").observations
        []
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:05] falls asleep\\n"
        ...     "[1518-11-01 00:25] wakes up\\n"
        ... ).observations
        [Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=5, guard_id=None, type='fall-asleep'), \
Observation(date='1518-11-01', hour=0, minute=25, guard_id=None, type='wake-up')]
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:05] falls asleep\\n"
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:25] wakes up\\n"
        ... ).observations
        [Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=5, guard_id=None, type='fall-asleep'), \
Observation(date='1518-11-01', hour=0, minute=25, guard_id=None, type='wake-up')]
        """
        lines = observations_text.splitlines()
        non_empty_lines = filter(None, lines)
        return cls(sorted(map(Observation.from_line, non_empty_lines)))

    def __init__(self, observations):
        self.observations = observations

    def attach_guard_ids(self):
        """
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:05] falls asleep\\n"
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:25] wakes up\\n"
        ... ).attach_guard_ids().observations
        [Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=5, guard_id='10', type='fall-asleep'), \
Observation(date='1518-11-01', hour=0, minute=25, guard_id='10', type='wake-up')]
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:05] Guard #11 begins shift\\n"
        ...     "[1518-11-01 00:10] Guard #12 begins shift\\n"
        ... ).attach_guard_ids().observations
        [Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=5, guard_id='11', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=10, guard_id='12', type='begin-shift')]
        >>> Observations.from_lines(
        ...     "[1518-11-01 00:00] Guard #10 begins shift\\n"
        ...     "[1518-11-01 00:01] falls asleep\\n"
        ...     "[1518-11-01 00:05] Guard #11 begins shift\\n"
        ...     "[1518-11-01 00:06] falls asleep\\n"
        ...     "[1518-11-01 00:10] Guard #12 begins shift\\n"
        ...     "[1518-11-01 00:11] falls asleep\\n"
        ... ).attach_guard_ids().observations
        [Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=1, guard_id='10', type='fall-asleep'), \
Observation(date='1518-11-01', hour=0, minute=5, guard_id='11', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=6, guard_id='11', type='fall-asleep'), \
Observation(date='1518-11-01', hour=0, minute=10, guard_id='12', type='begin-shift'), \
Observation(date='1518-11-01', hour=0, minute=11, guard_id='12', type='fall-asleep')]
        """
        if not self.observations:
            return
        for index, (previous, observation) \
                in enumerate(zip(self.observations, self.observations[1:]), 1):
            self.observations[index] = observation.with_guard_id_from(previous)

        return self

    def get_sleep_schedule(self):
        return SleepSchedule.from_observations(self.observations)


class Observation(namedtuple(
        "Observation", ("date", "hour", "minute", "guard_id", "type"))):
    TYPE_BEGIN_SHIFT = 'begin-shift'
    TYPE_FALL_ASLEEP = 'fall-asleep'
    TYPE_WAKE_UP = 'wake-up'

    re_parse = re.compile(r"^\[(\d+-\d+-\d+) (\d+):(\d+)] (.*)$")
    re_parse_begin_shift = re.compile(r"^Guard #(\d+) begins shift$")

    @classmethod
    def from_line(cls, observation_text):
        """
        >>> Observation.from_line("[1518-11-01 00:00] Guard #10 begins shift")
        Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift')
        >>> Observation.from_line("[1518-11-01 00:05] falls asleep")
        Observation(date='1518-11-01', hour=0, minute=5, guard_id=None, type='fall-asleep')
        >>> Observation.from_line("[1518-11-01 00:25] wakes up")
        Observation(date='1518-11-01', hour=0, minute=25, guard_id=None, type='wake-up')
        """
        _date, hour_str, minute_str, type_str = \
            cls.re_parse.match(observation_text).groups()
        if type_str == 'falls asleep':
            _type = cls.TYPE_FALL_ASLEEP
            guard_id = None
        elif type_str == 'wakes up':
            _type = cls.TYPE_WAKE_UP
            guard_id = None
        else:
            _type = cls.TYPE_BEGIN_SHIFT
            guard_id, = cls.re_parse_begin_shift.match(type_str).groups()

        return cls(
            date=_date, hour=int(hour_str), minute=int(minute_str),
            guard_id=guard_id, type=_type)

    def __lt__(self, other):
        """
        >>> Observation('1518-11-01', 0, 0, '10', 'begin-shift') \\
        ...     < Observation('1518-11-01', 0, 5, '10', 'begin-shift')
        True
        >>> Observation('1518-11-01', 0, 0, '10', 'begin-shift') \\
        ...     > Observation('1518-11-01', 0, 5, '10', 'begin-shift')
        False
        >>> Observation('1518-11-01', 0, 5, '10', 'begin-shift') \\
        ...     < Observation('1518-11-01', 0, 0, '10', 'begin-shift')
        False
        >>> Observation('1518-11-01', 0, 5, '10', 'begin-shift') \\
        ...     < Observation('1518-11-05', 0, 0, '10', 'begin-shift')
        True
        """
        return self.datetime_sort_key < other.datetime_sort_key

    @property
    def datetime_sort_key(self):
        return self.date, self.hour, self.minute

    def with_guard_id_from(self, other):
        """
        >>> Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift').with_guard_id_from(None)
        Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift')
        >>> Observation(date='1518-11-01', hour=0, minute=0, guard_id=None, type='fall-asleep')\\
        ...     .with_guard_id_from(Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift'))
        Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='fall-asleep')
        """
        if self.guard_id:
            return self

        if not other.guard_id:
            raise Exception("No guard ID from other observation")

        return self._replace(guard_id=other.guard_id)

    def duration_minutes_since(self, previous):
        """
        >>> Observation('1518-11-01', 0, 0, '10', 'begin-shift')\\
        ...     .duration_minutes_since(Observation('1518-11-01', 0, 0, '10', 'begin-shift'))
        0
        >>> Observation('1518-11-01', 0, 5, '10', 'begin-shift')\\
        ...     .duration_minutes_since(Observation('1518-11-01', 0, 0, '10', 'begin-shift'))
        5
        >>> Observation('1518-11-01', 2, 5, '10', 'begin-shift')\\
        ...     .duration_minutes_since(Observation('1518-11-01', 0, 0, '10', 'begin-shift'))
        125
        >>> Observation('1518-11-01', 2, 5, '10', 'begin-shift')\\
        ...     .duration_minutes_since(Observation('1518-10-01', 0, 0, '10', 'begin-shift'))
        44765
        >>> Observation('1518-11-01', 0, 0, '10', 'begin-shift')\\
        ...     .duration_minutes_since(Observation('1518-11-01', 2, 5, '10', 'begin-shift'))
        -125
        """
        duration = self.get_datetime() - previous.get_datetime()
        return int(duration.total_seconds() // 60)

    def get_datetime(self):
        """
        >>> Observation(date='1518-11-01', hour=0, minute=0, guard_id='10', type='begin-shift').get_datetime()
        datetime.datetime(1518, 11, 1, 0, 0)
        """
        year_str, month_str, day_str = self.date.split('-')
        return datetime.datetime(
            year=int(year_str), month=int(month_str), day=int(day_str),
            hour=self.hour, minute=self.minute)


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
