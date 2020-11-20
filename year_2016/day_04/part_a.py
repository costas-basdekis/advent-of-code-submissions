#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Generic, TypeVar, List, Type, Iterable

from utils import BaseChallenge, Cls, Self, helper, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        409147
        """
        return RoomSet.from_rooms_text(_input).get_real_rooms_hash()


# noinspection PyTypeChecker
RoomT = TypeVar('RoomT', bound='Room')


@dataclass
class RoomSet(Generic[RoomT]):
    rooms: List[RoomT]

    @classmethod
    def get_room_class(cls) -> Type[RoomT]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, RoomT)

    @classmethod
    def from_rooms_text(cls: Cls['RoomSet'], rooms_text: str
                        ) -> Self['RoomSet']:
        """
        >>> RoomSet.from_rooms_text(
        ...     "aaaaa-bbb-z-y-x-123[abxyz]\\n"
        ...     "a-b-c-d-e-f-g-h-987[abcde]\\n"
        ...     "not-a-real-room-404[oarel]\\n"
        ...     "totally-real-room-200[decoy]\\n"
        ... )
        RoomSet(rooms=[Room(encrypted_name='aaaaa-bbb-z-y-x', sector_id=123,
            attached_encrypted_checksum='abxyz'),
            Room(encrypted_name='a-b-c-d-e-f-g-h', sector_id=987,
                attached_encrypted_checksum='abcde'),
            Room(encrypted_name='not-a-real-room', sector_id=404,
                attached_encrypted_checksum='oarel'),
            Room(encrypted_name='totally-real-room', sector_id=200,
                attached_encrypted_checksum='decoy')])
        """
        return cls(list(map(
            cls.get_room_class().from_room_text, rooms_text.splitlines())))

    def get_real_rooms_hash(self) -> int:
        """
        >>> RoomSet.from_rooms_text(
        ...     "aaaaa-bbb-z-y-x-123[abxyz]\\n"
        ...     "a-b-c-d-e-f-g-h-987[abcde]\\n"
        ...     "not-a-real-room-404[oarel]\\n"
        ...     "totally-real-room-200[decoy]\\n"
        ... ).get_real_rooms_hash()
        1514
        """
        return sum(
            room.sector_id
            for room in self.get_real_rooms()
        )

    def get_real_rooms(self) -> Iterable[RoomT]:
        """
        >>> list(RoomSet.from_rooms_text(
        ...     "aaaaa-bbb-z-y-x-123[abxyz]\\n"
        ...     "a-b-c-d-e-f-g-h-987[abcde]\\n"
        ...     "not-a-real-room-404[oarel]\\n"
        ...     "totally-real-room-200[decoy]\\n"
        ... ).get_real_rooms())
        [Room(encrypted_name='aaaaa-bbb-z-y-x', sector_id=123,
            attached_encrypted_checksum='abxyz'),
            Room(encrypted_name='a-b-c-d-e-f-g-h', sector_id=987,
                attached_encrypted_checksum='abcde'),
            Room(encrypted_name='not-a-real-room', sector_id=404,
                attached_encrypted_checksum='oarel')]
        """
        return (
            room
            for room in self.rooms
            if room.is_real()
        )


@dataclass
class Room:
    encrypted_name: str
    sector_id: int
    attached_encrypted_checksum: str

    re_room = re.compile(r"^([a-z]+(?:-[a-z]+)*)-(\d+)\[([a-z]+)]$")

    @classmethod
    def from_room_text(cls: Cls['Room'], room_text: str) -> Self['Room']:
        """
        >>> Room.from_room_text('aaaaa-bbb-z-y-x-123[abxyz]')
        Room(encrypted_name='aaaaa-bbb-z-y-x', sector_id=123,
            attached_encrypted_checksum='abxyz')
        """
        encrypted_name, sector_id_str, attached_encrypted_checksum = \
            cls.re_room.match(room_text).groups()

        return cls(
            encrypted_name, int(sector_id_str), attached_encrypted_checksum)

    def is_real(self):
        """
        >>> Room.from_room_text('aaaaa-bbb-z-y-x-123[abxyz]').is_real()
        True
        >>> Room.from_room_text('a-b-c-d-e-f-g-h-987[abcde]').is_real()
        True
        >>> Room.from_room_text('a-b-c-d-e-f-g-h-987[abcde]').is_real()
        True
        >>> Room.from_room_text('totally-real-room-200[decoy]').is_real()
        False
        """
        return self.attached_encrypted_checksum == self.get_encrypted_checksum()

    def get_encrypted_checksum(self):
        """
        >>> Room.from_room_text(
        ...     'aaaaa-bbb-z-y-x-123[abxyz]').get_encrypted_checksum()
        'abxyz'
        >>> Room.from_room_text(
        ...     'totally-real-room-200[decoy]').get_encrypted_checksum()
        'loart'
        """
        return self.calculate_checksum(self.encrypted_name)

    def calculate_checksum(self, name):
        """
        >>> Room('', 0, '').calculate_checksum('aaaaa-bbb-z-y-x')
        'abxyz'
        >>> Room('', 0, '').calculate_checksum('a-b-c-d-e-f-g-h')
        'abcde'
        >>> Room('', 0, '').calculate_checksum('not-a-real-room')
        'oarel'
        >>> Room('', 0, '').calculate_checksum('totally-real-room')
        'loart'
        """
        letter_count = {
            letter: len(items)
            for letter, items in helper.group_by(name.replace('-', '')).items()
        }
        sorted_letters = sorted(
            letter_count, key=lambda letter: (-letter_count[letter], letter))
        return "".join(sorted_letters[:5])


Challenge.main()
challenge = Challenge()
