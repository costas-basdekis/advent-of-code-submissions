#!/usr/bin/env python3

import utils

from year_2020.day_13 import part_a


class Challenge(utils.BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        725169163285238
        """

        return ScheduleExtended.from_schedule_text(_input)\
            .get_earliest_timestamp_with_dotted_departures()


class ScheduleExtended(part_a.Schedule):
    def get_earliest_timestamp_with_dotted_departures(self):
        """
        >>> ScheduleExtended.from_buses_text("7,13,x,x,59,x,31,19")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        1068781
        >>> ScheduleExtended.from_buses_text("17,x,13,19")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        3417
        >>> ScheduleExtended.from_buses_text("67,7,59,61")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        754018
        >>> ScheduleExtended.from_buses_text("67,x,7,59,61")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        779210
        >>> ScheduleExtended.from_buses_text("67,7,x,59,61")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        1261476
        >>> ScheduleExtended.from_buses_text("1789,37,47,1889")\\
        ...     .get_earliest_timestamp_with_dotted_departures()
        1202161486
        """
        return utils.solve_linear_congruence_system([
            (bus_number, bus_number - index)
            for bus_number, index in self.bus_numbers_and_indexes.items()
        ])


Challenge.main()
challenge = Challenge()
