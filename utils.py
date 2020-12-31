import copy
import doctest
import math
import os
import re
import sys
import timeit
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path
from typing import Tuple, List

import click


def get_current_directory(file_path):
    return Path(os.path.dirname(os.path.realpath(file_path)))


def get_input(module_file):
    return get_current_directory(module_file)\
        .joinpath("part_a_input.txt")\
        .read_text()


def custom_testmod_with_filter(
        m=None, name=None, globs=None, verbose=None, report=True, optionflags=0,
        extraglobs=None, raise_on_error=False, exclude_empty=False,
        finder=None, filters_text=""):
    if finder is None:
        finder = FilteringDocTestFinder
    return custom_testmod_with_finder(
        m, name, globs, verbose, report, optionflags, extraglobs,
        raise_on_error, exclude_empty,
        finder=finder(
            exclude_empty=exclude_empty, filters_text=filters_text))


def custom_testmod_with_finder(
        m=None, name=None, globs=None, verbose=None, report=True, optionflags=0,
        extraglobs=None, raise_on_error=False, exclude_empty=False,
        finder=None):
    # If no module was given, then use __main__.
    if m is None:
        # DWA - m will still be None if this wasn't invoked from the command
        # line, in which case the following TypeError is about as good an error
        # as we should expect
        m = sys.modules.get('__main__')

    # Check that we were actually given a module.
    import inspect
    if not inspect.ismodule(m):
        raise TypeError("testmod: module required; %r" % (m,))

    # If no name was given, then use the module's name.
    if name is None:
        name = m.__name__

    # Find, parse, and run all tests in the given module.
    if finder is None:
        finder = doctest.DocTestFinder(exclude_empty=exclude_empty)

    if raise_on_error:
        runner = doctest.DebugRunner(verbose=verbose, optionflags=optionflags)
    else:
        runner = doctest.DocTestRunner(verbose=verbose, optionflags=optionflags)

    for test in finder.find(m, name, globs=globs, extraglobs=extraglobs):
        runner.run(test)

    if report:
        runner.summarize()

    if doctest.master is None:
        doctest.master = runner
    else:
        doctest.master.merge(runner)

    return doctest.TestResults(runner.failures, runner.tries)


# If testmod has changed so that it can accept `finder`, use the original
# testmod. Otherwise, use the custom one
if 'filters_text' in doctest.testmod.__code__.co_varnames[
        :doctest.testmod.__code__.co_argcount]:
    testmod_with_filter = doctest.testmod
else:
    testmod_with_filter = custom_testmod_with_filter


class InvalidTestFilterException(Exception):
    pass


InvalidTestFilterException.__module__ = 'utils'


class FilteringDocTestFinder(doctest.DocTestFinder):
    def __init__(self, verbose=False, parser=doctest.DocTestParser(),
                 recurse=True, exclude_empty=True, filters_text=""):
        super().__init__(verbose=verbose, parser=parser, recurse=recurse,
                         exclude_empty=exclude_empty)
        self.filters = DocTestFilterParser().parse_filters(filters_text)

    def find(self, obj, name=None, module=None, globs=None, extraglobs=None):
        tests = super().find(obj, name, module, globs, extraglobs)

        if self.filters:
            tests = list(filter(None, map(self.filter_test, tests)))

        return tests

    def filter_test(self, test: doctest.DocTest):
        matching_filters = [
            _filter
            for _filter in self.filters
            if _filter.matches_test(test)
        ]
        if not matching_filters:
            return None
        examples = [
            example
            for index, example in enumerate(test.examples)
            if any(
                _filter.matches_example(test, example, index)
                for _filter in matching_filters
            )
        ]
        if not examples:
            return None

        if examples != test.examples:
            test = copy.copy(test)
            test.examples = examples

        return test


class DocTestFilter:
    def __init__(self, name_regex, number_ranges):
        self.name_regex = name_regex
        self.number_ranges = number_ranges

    def matches_test(self, test):
        return self.name_regex.match(test.name)

    def matches_example(self, test, example, index):
        return self.matches_example_by_example_index(test, example, index)

    def matches_example_by_example_index(self, test, example, index):
        return any(
            index
            in number_range
            for number_range in self.number_ranges
        )

    def matches_example_by_line_number(self, test, example, index):
        if any(line_number is None for line_number in self.number_ranges):
            return True
        if test.lineno is None or example.lineno is None:
            return True
        lineno = test.lineno + example.lineno + 1
        return any(
            lineno
            in number_range
            for number_range in self.number_ranges
        )


class DocTestFilterParser:
    def parse_filters(self, filters_text):
        return [
            self.parse_filter(filter_text)
            for filter_text in self.split_filter_texts(filters_text)
        ]

    def split_filter_texts(self, filters_text):
        """
        >>> DocTestFilterParser().split_filter_texts("")
        []
        >>> DocTestFilterParser().split_filter_texts(" " * 20)
        []
        >>> DocTestFilterParser().split_filter_texts("     abc def      ghi   ")
        ['abc', 'def', 'ghi']
        """
        filters_text = filters_text.strip()
        if not filters_text:
            return []
        return re.split(r"\s+", filters_text)

    def parse_filter(self, filter_text):
        test_name_text, line_numbers_text = self.get_filter_parts(filter_text)
        return DocTestFilter(
            self.parse_test_name(test_name_text),
            self.parse_number_ranges(line_numbers_text),
        )

    def get_filter_parts(self, filter_text):
        """
        >>> DocTestFilterParser().get_filter_parts("method")
        ('method', '')
        >>> DocTestFilterParser().get_filter_parts("method:512,3,-7")
        ('method', '512,3,-7')
        >>> DocTestFilterParser().get_filter_parts(":512,3,-7")
        ('', '512,3,-7')
        >>> DocTestFilterParser().get_filter_parts(":")
        ('', '')
        >>> DocTestFilterParser().get_filter_parts("method:512,3,-7:")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        """
        filter_text = filter_text.strip()
        parts = filter_text.split(':')
        if len(parts) > 2:
            raise InvalidTestFilterException(
                f"A filter should have at most two parts, name and ranges, "
                f"not {len(parts)}: '{filter_text}'")

        if len(parts) == 1:
            test_name_text, = parts
            numbers_text = ''
        else:
            test_name_text, numbers_text = parts

        return test_name_text, numbers_text

    def parse_test_name(self, test_name_text):
        """
        >>> def test(pattern):
        ...     regex = DocTestFilterParser().parse_test_name(pattern)
        ...     return [
        ...         name
        ...         for name in [
        ...             f'{part}.{_type}.{prefix}{method}{suffix}'
        ...             for part in ['part_a', 'part_b']
        ...             for _type in ['TypeA', 'TypeB']
        ...             for method in ['method', 'function']
        ...             for suffix in ['', '_plus']
        ...             for prefix in ['', 'plus_']
        ...         ]
        ...         if regex.match(name)
        ...     ]
        >>> test("method")
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method',
            'part_b.TypeA.method', 'part_b.TypeA.plus_method',
            'part_b.TypeB.method', 'part_b.TypeB.plus_method']
        >>> test("method*")
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeA.method_plus', 'part_a.TypeA.plus_method_plus',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method',
            'part_a.TypeB.method_plus', 'part_a.TypeB.plus_method_plus',
            'part_b.TypeA.method', 'part_b.TypeA.plus_method',
            'part_b.TypeA.method_plus', 'part_b.TypeA.plus_method_plus',
            'part_b.TypeB.method', 'part_b.TypeB.plus_method',
            'part_b.TypeB.method_plus', 'part_b.TypeB.plus_method_plus']
        >>> test("part_a.*method")
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method']
        >>> test("part_a.*method*")
        ['part_a.TypeA.method', 'part_a.TypeA.plus_method',
            'part_a.TypeA.method_plus', 'part_a.TypeA.plus_method_plus',
            'part_a.TypeB.method', 'part_a.TypeB.plus_method',
            'part_a.TypeB.method_plus', 'part_a.TypeB.plus_method_plus']
        >>> test("")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        """
        test_name_text = test_name_text.strip()
        if not test_name_text.replace("*", ""):
            raise InvalidTestFilterException(
                f"You need to specify at least some part of the test name")
        parts = re.split(r'\*+', '*' + test_name_text)
        escaped_parts = map(re.escape, parts)
        return re.compile(f"{'.*'.join(escaped_parts)}$")

    def parse_number_ranges(self, number_ranges_text):
        """
        >>> def test(pattern):
        ...     result = DocTestFilterParser().parse_number_ranges(pattern)
        ...     return sorted(set(sum(map(list, result), [])))[:1010]
        >>> test("")
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("-")
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("512")
        [512]
        >>> test("-512")
        [0, 1, 2, ..., 510, 511, 512]
        >>> test("512-")
        [512, 513, 514, ..., 1000, 1001, ...]
        >>> test("256-512")
        [256, 257, 258, ..., 510, 511, 512]
        >>> test("512-256")
        []
        >>> test("256-512-768")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("0xf")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("5-abc")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("1,5,7")
        [1, 5, 7]
        >>> test("1,10-20,7")
        [1, 7, 10, 11, 12, ..., 18, 19, 20]
        >>> test("1,20-10,7")
        [1, 7]
        >>> test("1,20-10,7,10,11")
        [1, 7, 10, 11]
        >>> test("1,10-20,-5")
        [0, 1, 2, 3, 4, 5, 10, 11, 12, ..., 18, 19, 20]
        >>> test("600-,10-20,-5")
        [0, 1, 2, 3, 4, 5, 10, 11, 12, ..., 18, 19, 20, 600, 601, 602,
            ..., 1000, 1001, ...]
        >>> test("600-,10-20,,-5")
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("600-,10-20-40,,-5")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("600-,10-0xf,,-5")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("600-,10-abc,,-5")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        """
        return [
            self.parse_number_range(number_range_text)
            for number_range_text in number_ranges_text.split(',')
        ]

    def parse_number_range(self, number_range_text):
        """
        >>> def test(pattern):
        ...     result = DocTestFilterParser().parse_number_range(pattern)
        ...     return sorted(result)[:1010]
        >>> test("")
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("-")
        [0, 1, 2, ..., 1000, 1001, ...]
        >>> test("512")
        [512]
        >>> test("-512")
        [0, 1, 2, ..., 510, 511, 512]
        >>> test("512-")
        [512, 513, 514, ..., 1000, 1001, ...]
        >>> test("256-512")
        [256, 257, 258, ..., 510, 511, 512]
        >>> test("512-256")
        []
        >>> test("256-512-768")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("0xf")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> test("5-abc")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        """
        number_range_text = number_range_text.strip()
        parts = number_range_text.split('-')
        if len(parts) > 2:
            raise InvalidTestFilterException(
                f"Number ranges must be either a single number "
                f"(eg '512'), or a range either without start (eg '-512'), "
                f"without end (eg '512-') or with just start and end "
                f"(eg '256-512), not with more parts: "
                f"'{number_range_text}'")

        if len(parts) == 1:
            number_text, = parts
            if not number_text:
                start = 0
                end = 10000
            else:
                start = end = self.parse_number(number_text)
        else:
            start_number_text, end_number_text = parts
            if not start_number_text and not end_number_text:
                start = 0
                end = 10000
            elif not start_number_text:
                start = 0
                end = self.parse_number(end_number_text)
            elif not end_number_text:
                start = self.parse_number(start_number_text)
                end = 10000
            else:
                start = self.parse_number(start_number_text)
                end = self.parse_number(end_number_text)

        return range(start, end + 1)

    def parse_number(self, number_text):
        """
        >>> DocTestFilterParser().parse_number("0")
        0
        >>> DocTestFilterParser().parse_number("512")
        512
        >>> DocTestFilterParser().parse_number("-4")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        >>> DocTestFilterParser().parse_number("0xf")
        Traceback (most recent call last):
        ...
        utils.InvalidTestFilterException: ...
        """
        try:
            number = int(number_text)
        except ValueError:
            number = None
        if number is not None and number < 0:
            number = None

        if number is None:
            raise InvalidTestFilterException(
                f"Line numbers must be positive integers, not "
                f"'{number_text}'")

        return number


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
        self.run_main_arguments()

    def run_main_arguments(self):
        cli = self.create_cli()
        cli()

    def create_cli(self):
        @click.group(invoke_without_command=True)
        @click.option('--test', '-t', 'filters_texts', multiple=True)
        @click.pass_context
        def cli(*args, **kwargs):
            self.default_command(*args, **kwargs)

        @cli.command(name="all")
        @click.option('--test', '-t', 'filters_texts', multiple=True)
        def run_all(*args, **kwargs):
            self.run_all(*args, **kwargs)

        @cli.command(name="test")
        @click.option('--test', '-t', 'filters_texts', multiple=True)
        def test(*args, **kwargs):
            self.test(*args, **kwargs)

        @cli.command(name="run")
        def run(*args, **kwargs):
            self.run(*args, **kwargs)

        @cli.command(name="play")
        def play(*args, **kwargs):
            self.play(*args, **kwargs)

        return cli

    def decorate_value(self, decorators, value):
        decorated = value
        for decorator in reversed(decorators):
            decorated = decorator(decorated)

        return decorated

    def default_solve(self, _input=None):
        if _input is None:
            _input = self.input
        return self.solve(_input)

    def solve(self, _input):
        raise NotImplementedError()

    def default_command(self, ctx, filters_texts=()):
        if ctx.invoked_subcommand:
            return
        self.run_all(filters_texts=filters_texts)

    def run_all(self, filters_texts=()):
        self.test(filters_texts=filters_texts)
        self.run()

    def play(self):
        raise Exception(f"Challenge has not implemented play")

    def test(self, filters_texts=()):
        filters_text = " ".join(filters_texts)
        test_modules = self.get_test_modules()
        with helper.time_it() as stats:
            results = [
                (module,
                 testmod_with_filter(
                     module, optionflags=self.optionflags,
                     filters_text=filters_text))
                for module in test_modules
            ]
        total_attempted = sum(result.attempted for _, result in results)
        total_failed = sum(result.failed for _, result in results)
        failed_modules = [
            module.__name__
            if module else
            'main'
            for module, result in results
            if result.failed
        ]
        if failed_modules:
            styled_test_counts = click.style(
                f'{total_failed}/{total_attempted} tests', fg='red')
            print(
                f"{styled_test_counts} "
                f"in {len(failed_modules)}/{len(test_modules)} modules "
                f"{click.style('failed', fg='red')} "
                f"in {round(stats['duration'], 2)}s"
                f": {click.style(', '.join(failed_modules), fg='red')}")
        else:
            print(
                f"{total_attempted} tests "
                f"in {len(test_modules)} modules "
                f"{click.style('passed', fg='green')} "
                f"in {round(stats['duration'], 2)}s")

    def get_test_modules(self):
        modules = [
            __import__(__name__),
            None,
        ]
        if self.part_a_for_testing:
            modules.append(self.part_a_for_testing)
        return modules

    def run(self):
        with helper.time_it() as stats:
            solution = self.default_solve()
        if solution is None:
            styled_solution = click.style(str(solution), fg='red')
        else:
            styled_solution = click.style(str(solution), fg='green')
        click.echo(
            f"Solution: {styled_solution}"
            f" (in {round(stats['duration'], 2)}s)")


class Helper:
    MANHATTAN_OFFSETS = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
    ]

    def get_manhattan_neighbours(self, position):
        """
        >>> sorted(Helper().get_manhattan_neighbours((0, 0)))
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        >>> sorted(Helper().get_manhattan_neighbours((-3, 5)))
        [(-4, 5), (-3, 4), (-3, 6), (-2, 5)]
        """
        return [
            self.add_points(position, offset)
            for offset in self.MANHATTAN_OFFSETS
        ]

    def add_points(self, lhs, rhs):
        """
        >>> Helper().add_points((0, 0), (0, 0))
        (0, 0)
        >>> Helper().add_points((1, -4), (-2, 5))
        (-1, 1)
        """
        l_x, l_y = lhs
        r_x, r_y = rhs

        return l_x + r_x, l_y + r_y

    def iterable_length(self, iterable):
        return sum(1 for _ in iterable)

    @contextmanager
    def time_it(self):
        start = timeit.default_timer()
        stats = {'start': start, 'end': None, 'duration': None}
        yield stats
        end = timeit.default_timer()
        stats.update({'end': end, 'duration': end - start})


class BasePointMeta(type):
    @classmethod
    def auto_assign_to(mcs, attribute):
        def decorator(method):
            method.auto_assign_to = attribute
            return method

        return decorator

    def __new__(mcs, *args, **kwargs):
        # noinspection PyPep8Naming
        Point = super().__new__(mcs, *args, **kwargs)

        mcs.assign_auto_attributes(mcs, Point)

        return Point

    # noinspection PyPep8Naming
    def assign_auto_attributes(cls, Point):
        if Point.__name__ == 'BasePoint':
            return
        for name in dir(Point):
            attribute = getattr(Point, name)
            if attribute == cls:
                continue
            auto_assign_to = getattr(attribute, 'auto_assign_to', None)
            if auto_assign_to is None:
                continue
            setattr(Point, auto_assign_to, attribute())


class BasePoint(metaclass=BasePointMeta):
    _fields: Tuple[str, ...]
    coordinates_names: Tuple[str, ...]

    @classmethod
    def from_comma_delimited_text(cls, point_text):
        """
        >>> Point4D.from_comma_delimited_text("0,-8,-4,-6")
        Point4D(x=0, y=-8, z=-4, t=-6)
        """
        parts = map(str.strip, point_text.split(","))
        return cls.from_int_texts(*parts)

    @classmethod
    def from_int_texts(cls, *coordinate_strs, **named_coordinate_strs):
        """
        >>> Point3D.from_int_texts("1", "2", "3")
        Point3D(x=1, y=2, z=3)
        >>> Point3D.from_int_texts(x="1", y="2", z="3")
        Point3D(x=1, y=2, z=3)
        >>> Point3D.from_int_texts("1", y="2", z="3")
        Point3D(x=1, y=2, z=3)
        >>> Point3D.from_int_texts("1", z="3", y="2")
        Point3D(x=1, y=2, z=3)
        """
        coordinate_strs = coordinate_strs + tuple(
            named_coordinate_strs.pop(name)
            for name in cls.coordinates_names[len(coordinate_strs):]
        )
        if named_coordinate_strs:
            raise Exception(
                f"Too many arguments: {sorted(named_coordinate_strs)}")
        if len(coordinate_strs) != len(cls.coordinates_names):
            raise Exception(
                f"Expected {len(cls.coordinates_names)} coordinates but got "
                f"{len(coordinate_strs)}")
        # noinspection PyArgumentList
        return cls(*map(int, coordinate_strs))

    @classmethod
    def get_zero_point(cls):
        """
        >>> Point2D.get_zero_point()
        Point2D(x=0, y=0)
        >>> Point2D(-3, 4).get_zero_point()
        Point2D(x=0, y=0)
        """
        # noinspection PyArgumentList
        return cls(*(0,) * len(cls.coordinates_names))

    @property
    def coordinates(self):
        """
        >>> Point3D(1, 2, 3).coordinates
        Point3D(x=1, y=2, z=3)
        >>> tuple(zip(
        ...     Point3D(1, 2, 3).coordinates, Point3D(4, 5, 6).coordinates))
        ((1, 4), (2, 5), (3, 6))
        """
        if self.coordinates_names is NotImplemented:
            raise Exception(
                f"{type(self).__name__} did not specify 'coordinates_names'")
        # noinspection PyUnresolvedReferences
        if self.coordinates_names == self._fields:
            return self
        # noinspection PyTypeChecker
        return tuple(
            getattr(self, coordinate_name)
            for coordinate_name in self.coordinates_names
        )

    def distance(self, other):
        """
        >>> Point3D(0, 0, 0).distance(Point3D(0, 0, 0))
        0.0
        >>> Point3D(0, 0, 0).distance(Point3D(2, 3, -4))
        5.385164807134504
        >>> Point3D(0, 0, 0).distance(Point3D(0, 3, -4))
        5.0
        """
        return math.sqrt(sum(
            (my_coordinate - other_coordinate) ** 2
            for my_coordinate, other_coordinate
            in zip(self.coordinates, other.coordinates)
        ))

    def manhattan_distance(self, other):
        """
        >>> Point3D(0, 0, 0).manhattan_distance(Point3D(0, 0, 0))
        0
        >>> Point3D(0, 0, 0).manhattan_distance(Point3D(2, 3, -4))
        9
        """
        return sum(
            abs(my_coordinate - other_coordinate)
            for my_coordinate, other_coordinate
            in zip(self.coordinates, other.coordinates)
        )

    def offset(self, offsets):
        """
        >>> Point3D(3, -2, 4).offset((-2, -5, 3))
        Point3D(x=1, y=-7, z=7)
        """
        cls = type(self)
        # noinspection PyArgumentList
        return cls(**{
            name: coordinate + offset
            for name, coordinate, offset
            in zip(self.coordinates_names, self.coordinates, offsets)
        })

    def get_manhattan_neighbours(self):
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbours())
        [Point2D(x=-1, y=0), Point2D(x=0, y=-1), Point2D(x=0, y=1),
            Point2D(x=1, y=0)]
        """
        return (
            self.offset(offset)
            for offset in self.MANHATTAN_OFFSETS
        )

    MANHATTAN_OFFSETS: List[Tuple[int, ...]]

    @classmethod
    @BasePointMeta.auto_assign_to('MANHATTAN_OFFSETS')
    def get_manhattan_offsets(cls):
        """
        >>> sorted(Point2D.MANHATTAN_OFFSETS)
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        >>> sorted(Point2D(0, 0).get_manhattan_offsets())
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        >>> # We run it twice to make sure we didn't use a read-once iterator
        >>> sorted(Point2D.MANHATTAN_OFFSETS)
        [(-1, 0), (0, -1), (0, 1), (1, 0)]
        """
        coordinate_count = len(cls.coordinates_names)
        return [
            (0,) * index + (delta,) + (0,) * (coordinate_count - index - 1)
            for index in range(coordinate_count)
            for delta in (-1, 1)
        ]

    def get_manhattan_neighbourhood(self, size):
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood(0))
        [Point2D(x=0, y=0)]
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood(1))
        [Point2D(x=-1, y=0), Point2D(x=0, y=-1), Point2D(x=0, y=0),
            Point2D(x=0, y=1), Point2D(x=1, y=0)]
        """
        return (
            self.offset(offset)
            for offset in self.get_manhattan_neighbourhood_offsets(size)
        )

    MANHATTAN_NEIGHBOUR_OFFSETS = {}

    def get_manhattan_neighbourhood_offsets(self, size):
        """
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood_offsets(0))
        [(0, 0)]
        >>> sorted(Point2D(0, 0).get_manhattan_neighbourhood_offsets(1))
        [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0)]
        """
        if size not in self.MANHATTAN_NEIGHBOUR_OFFSETS:
            zero_point = self.get_zero_point()
            neighbourhood = {zero_point}
            previous_layer = [zero_point]
            for distance in range(1, size + 1):
                current_layer = []
                for point in previous_layer:
                    neighbours = \
                        set(point.get_manhattan_neighbours()) - neighbourhood
                    neighbourhood.update(neighbours)
                    current_layer.extend(neighbours)
                previous_layer = current_layer
            self.MANHATTAN_NEIGHBOUR_OFFSETS[size] = tuple(
                tuple(point.coordinates)
                for point in neighbourhood
            )

        return self.MANHATTAN_NEIGHBOUR_OFFSETS[size]


class Point2D(namedtuple("Point2D", ("x", "y")), BasePoint):
    coordinates_names = ("x", "y")


class Point3D(namedtuple("Point3D", ("x", "y", "z")), BasePoint):
    coordinates_names = ("x", "y", "z")


class Point4D(namedtuple("Point4D", ("x", "y", "z", "t")), BasePoint):
    coordinates_names = ("x", "y", "z", "t")


helper = Helper()


if __name__ == "__main__":
    if doctest.testmod(optionflags=BaseChallenge.optionflags).failed:
        print("Tests failed")
    else:
        print("Tests passed")
