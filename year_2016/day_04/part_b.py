#!/usr/bin/env python3
from string import ascii_lowercase
from typing import Dict

from utils import BaseChallenge
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        991
        """
        room_set = RoomSetExtended.from_rooms_text(_input)
        if debug:
            real_rooms = list(room_set.get_real_rooms())
            print("\n".join(
                name
                for name in (
                    room.get_name()
                    for room in real_rooms
                )
                if 'pole' in name
                or 'north' in name
            ))

        return room_set.get_north_pole_object_storage_sector_id()


class RoomSetExtended(part_a.RoomSet['RoomExtended']):
    NORTH_POLE_NAME = 'northpole object storage'

    def get_north_pole_object_storage_sector_id(self):
        room, = (
            room
            for room in self.get_real_rooms()
            if room.get_name() == self.NORTH_POLE_NAME
        )

        return room.sector_id


class RoomExtended(part_a.Room):
    def get_name(self) -> str:
        """
        >>> RoomExtended('qzmt-zixmtkozy-ivhz', 343, '').get_name()
        'very encrypted name'
        """
        return self.decrypt_name(self.encrypted_name, self.sector_id)

    def decrypt_name(self, name: str, right_shift: int) -> str:
        """
        >>> RoomExtended('', 0, '').decrypt_name('qzmt-zixmtkozy-ivhz', 343)
        'very encrypted name'
        """
        decryption_map = self.get_decryption_map(right_shift)
        return "".join(
            decryption_map[letter]
            for letter in name
        )

    def get_decryption_map(self, right_shift: int,
                           letters: str = ascii_lowercase) -> Dict[str, str]:
        """
        >>> RoomExtended('', 0, '').get_decryption_map(0, 'abc')
        {'-': ' ', 'a': 'a', 'b': 'b', 'c': 'c'}
        >>> RoomExtended('', 0, '').get_decryption_map(1, 'abc')
        {'-': ' ', 'a': 'b', 'b': 'c', 'c': 'a'}
        >>> RoomExtended('', 0, '').get_decryption_map(-2, 'abc')
        {'-': ' ', 'a': 'b', 'b': 'c', 'c': 'a'}
        >>> RoomExtended('', 0, '').get_decryption_map(4, 'abc')
        {'-': ' ', 'a': 'b', 'b': 'c', 'c': 'a'}
        >>> RoomExtended('', 0, '').get_decryption_map(2, 'abc')
        {'-': ' ', 'a': 'c', 'b': 'a', 'c': 'b'}
        >>> RoomExtended('', 0, '').get_decryption_map(-1, 'abc')
        {'-': ' ', 'a': 'c', 'b': 'a', 'c': 'b'}
        >>> RoomExtended('', 0, '').get_decryption_map(5, 'abc')
        {'-': ' ', 'a': 'c', 'b': 'a', 'c': 'b'}
        >>> RoomExtended('', 0, '').get_decryption_map(3, 'abc')
        {'-': ' ', 'a': 'a', 'b': 'b', 'c': 'c'}
        >>> RoomExtended('', 0, '').get_decryption_map(-3, 'abc')
        {'-': ' ', 'a': 'a', 'b': 'b', 'c': 'c'}
        >>> RoomExtended('', 0, '').get_decryption_map(6, 'abc')
        {'-': ' ', 'a': 'a', 'b': 'b', 'c': 'c'}
        """
        return {
            '-': ' ',
            **{
                letter: letters[(index + right_shift) % len(letters)]
                for index, letter in enumerate(letters)
            },
        }


Challenge.main()
challenge = Challenge()
