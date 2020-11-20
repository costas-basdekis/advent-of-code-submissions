#!/usr/bin/env python3
import doctest

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    3035
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return Schedule.from_schedule_text(_input).get_earliest_bus_hash()


class Schedule:
    @classmethod
    def from_schedule_text(cls, schedule_text):
        """
        >>> schedule = Schedule.from_schedule_text(
        ...     "939\\n"
        ...     "7,13,x,x,59,x,31,19\\n"
        ... )
        >>> schedule.min_departure_time, schedule.bus_numbers, schedule.discontinued_buses_indexes
        (939, (7, 13, 59, 31, 19), (2, 3, 5))
        """
        min_departure_time_text, buses_text = \
            filter(None, schedule_text.splitlines())
        min_departure_time = int(min_departure_time_text)
        bus_numbers = tuple(
            int(number_text)
            for number_text in buses_text.split(",")
            if number_text != 'x'
        )
        discontinued_buses_indexes = tuple(
            index
            for index, number_text in enumerate(buses_text.split(","))
            if number_text == 'x'
        )

        return cls(min_departure_time, bus_numbers, discontinued_buses_indexes)

    def __init__(self, min_departure_time, bus_numbers,
                 discontinued_buses_indexes):
        self.min_departure_time = min_departure_time
        self.bus_numbers = bus_numbers
        self.discontinued_buses_indexes = discontinued_buses_indexes

    def get_earliest_bus_hash(self):
        """
        >>> Schedule.from_schedule_text(
        ...     "939\\n"
        ...     "7,13,x,x,59,x,31,19\\n"
        ... ).get_earliest_bus_hash()
        295
        """
        earliest_bus_number, earliest_bus_time = \
            self.get_earliest_bus_and_time()
        waiting_time = earliest_bus_time - self.min_departure_time
        return waiting_time * earliest_bus_number

    def get_earliest_bus_and_time(self):
        """
        >>> Schedule.from_schedule_text(
        ...     "939\\n"
        ...     "7,13,x,x,59,x,31,19\\n"
        ... ).get_earliest_bus_and_time()
        (59, 944)
        """
        modulo_by_bus_number = {
            bus_number: self.min_departure_time % bus_number
            for bus_number in self.bus_numbers
        }
        immediate_bus_numbers = [
            bus_number
            for bus_number, modulo in modulo_by_bus_number.items()
            if modulo == 0
        ]
        if len(immediate_bus_numbers) > 1:
            raise Exception(
                f"Got too many immediate bus numbers: {immediate_bus_numbers}")
        if len(immediate_bus_numbers) == 1:
            earliest_bus_number, = immediate_bus_numbers
            return earliest_bus_number, self.min_departure_time

        next_departure_by_bus_time = {
            bus_number: bus_number - modulo + self.min_departure_time
            for bus_number, modulo in modulo_by_bus_number.items()
        }
        earlier_bus_time = min(next_departure_by_bus_time.values())
        earliest_bus_numbers = [
            bus_number
            for bus_number, departure_time
            in next_departure_by_bus_time.items()
            if departure_time == earlier_bus_time
        ]
        if len(earliest_bus_numbers) > 1:
            raise Exception(
                f"Got too many next bus numbers at {earlier_bus_time}: "
                f"{earliest_bus_numbers}")
        earliest_bus_number, = earliest_bus_numbers
        return earliest_bus_number, earlier_bus_time


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
