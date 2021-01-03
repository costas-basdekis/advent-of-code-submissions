#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        3035
        """
        return Schedule.from_schedule_text(_input).get_earliest_bus_hash()


class Schedule:
    @classmethod
    def from_schedule_text(cls, schedule_text):
        """
        >>> schedule = Schedule.from_schedule_text(
        ...     "939\\n"
        ...     "7,13,x,x,59,x,31,19\\n"
        ... )
        >>> schedule.min_departure_time, schedule.bus_numbers_and_indexes
        (939, {7: 0, 13: 1, 59: 4, 31: 6, 19: 7})
        """
        min_departure_time_text, buses_text = \
            filter(None, schedule_text.splitlines())
        min_departure_time = int(min_departure_time_text)
        return cls.from_buses_text(buses_text, min_departure_time)

    @classmethod
    def from_buses_text(cls, buses_text, min_departure_time=0):
        """
        >>> schedule = Schedule.from_buses_text("7,13,x,x,59,x,31,19")
        >>> schedule.min_departure_time, schedule.bus_numbers_and_indexes
        (0, {7: 0, 13: 1, 59: 4, 31: 6, 19: 7})
        """
        bus_numbers_and_indexes = {
            int(number_text): index
            for index, number_text in enumerate(buses_text.split(","))
            if number_text != 'x'
        }

        return cls(min_departure_time, bus_numbers_and_indexes)

    def __init__(self, min_departure_time, bus_numbers_and_indexes):
        self.min_departure_time = min_departure_time
        self.bus_numbers_and_indexes = bus_numbers_and_indexes

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
            for bus_number in self.bus_numbers_and_indexes
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


challenge = Challenge()
challenge.main()
