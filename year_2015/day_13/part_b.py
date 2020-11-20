#!/usr/bin/env python3
from aox.challenge import Debugger
from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    part_a_for_testing = part_a

    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        668
        """
        return AttendeeSetExtended.from_happiness_listings_text(_input)\
            .insert_apathetic()\
            .get_happiest_arrangement_happiness()


class AttendeeSetExtended(part_a.AttendeeSet):
    def insert_apathetic(self, name: str = 'me'):
        attendees = self.get_attendees()
        if name in attendees:
            raise Exception(
                f"Name {repr(name)} already in list of attendees "
                f"{sorted(attendees)}")
        for other in attendees:
            self.happiness_map[(name, other)] = 0
            self.happiness_map[(other, name)] = 0

        return self


Challenge.main()
challenge = Challenge()
