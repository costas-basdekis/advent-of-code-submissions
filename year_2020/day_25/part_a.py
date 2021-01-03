#!/usr/bin/env python3
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        17032383
        """
        public_key_a_str, public_key_b_str = _input.strip().splitlines()
        public_key_a = int(public_key_a_str)
        public_key_b = int(public_key_b_str)
        return get_encryption_key(public_key_a, public_key_b)


def get_encryption_key(public_key_a, public_key_b):
    """
    >>> get_encryption_key(17807724, 5764801)
    14897079
    """
    if public_key_b < public_key_a:
        public_key_a, public_key_b = public_key_b, public_key_a

    loop_size_a = find_loop_size(7, public_key_a)
    return transform_subject_number(public_key_b, loop_size_a)


def transform_subject_number(subject_number, loop_size):
    """
    >>> transform_subject_number(7, 8)
    5764801
    """
    for value_loop_size, value in iterate_subject_number(subject_number):
        if value_loop_size == loop_size:
            return value

    raise Exception(f"Finished endless loop")


def iterate_subject_number(subject_number):
    value = 1
    for loop_size in itertools.count():
        yield loop_size, value
        value *= subject_number
        value = value % 20201227


def unlock(card_loop_size, door_loop_size):
    card_public_key = transform_subject_number(7, card_loop_size)
    door_public_key = transform_subject_number(7, door_loop_size)
    encryption_key = transform_subject_number(door_public_key, card_loop_size)
    verified_encryption_key = transform_subject_number(
        card_public_key, door_loop_size)

    assert encryption_key == verified_encryption_key


def find_loop_size(subject_number, public_key):
    """
    >>> find_loop_size(7, 5764801)
    8
    """
    for loop_size, value in iterate_subject_number(subject_number):
        if value == public_key:
            return loop_size


challenge = Challenge()
challenge.main()
