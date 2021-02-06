import itertools
from typing import Dict, Type, Iterable, Tuple, Union, Any


__all__ = ['Helper', 'helper']


class Helper:
    def iterable_length(self, iterable):
        return sum(1 for _ in iterable)

    def find_smallest_required_value(self, min_value, is_value_enough,
                                     debug=False):
        """
        >>> is_more_than_10 = lambda _value, **_: _value > 10
        >>> Helper().find_smallest_required_value(1, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(0, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(-2, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(-3, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(3, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(9, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(10, is_more_than_10)
        11
        >>> Helper().find_smallest_required_value(11, is_more_than_10)
        Traceback (most recent call last):
        ...
        Exception: Tried ... already enough
        >>> Helper().find_smallest_required_value(12, is_more_than_10)
        Traceback (most recent call last):
        ...
        Exception: Tried ... already enough
        """
        if is_value_enough(min_value):
            raise Exception(
                f"Tried to bisect value, but provided min_value {min_value} "
                f"was already enough")
        max_value = self.get_big_enough_value(
            start=min_value + 1, is_value_enough=is_value_enough, debug=debug)
        if debug:
            print(f"Value must be between {min_value} and {max_value}")

        while max_value > min_value + 1:
            mid_value = (max_value + min_value) // 2
            if is_value_enough(mid_value, debug=debug):
                max_value = mid_value
                if debug:
                    print(
                        f"Value {mid_value} is too much: checking between "
                        f"{min_value} and {max_value}")
            else:
                min_value = mid_value
                if debug:
                    print(
                        f"Value {mid_value} is not enough: checking between "
                        f"{min_value} and {max_value}")

        return max_value

    def get_big_enough_value(self, start, is_value_enough, debug=False):
        """
        >>> is_more_than_10 = lambda _value, **_: _value > 10
        >>> Helper().get_big_enough_value(1, is_more_than_10)
        16
        >>> Helper().get_big_enough_value(0, is_more_than_10)
        16
        >>> Helper().get_big_enough_value(-2, is_more_than_10)
        16
        >>> Helper().get_big_enough_value(-3, is_more_than_10)
        12
        >>> Helper().get_big_enough_value(3, is_more_than_10)
        12
        """
        value = start
        while not is_value_enough(value, debug=debug):
            if debug:
                print(f"Value {value} was not enough")
            if value > 0:
                value *= 2
            elif value == 0:
                value = 1
            else:
                value = -value
        if debug:
            print(f"Value {value} was enough")

        return value

    def reverse_dict(self, _dict: Dict,
                     values_container: Type[Iterable] = list):
        """
        >>> Helper().reverse_dict({'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 2})
        {1: ['a', 'c'], 2: ['b', 'e'], 3: ['d']}
        >>> Helper().reverse_dict(
        ...     {'a': 1, 'b': 2, 'c': 1, 'd': 3, 'e': 2},
        ...     values_container=tuple)
        {1: ('a', 'c'), 2: ('b', 'e'), 3: ('d',)}
        """
        # noinspection PyTypeChecker
        return self.group_by(
            _dict.items(),
            key=lambda item: item[1],
            value='auto',
            values_container=values_container,
        )

    def group_by(self, iterable, key=None, value=None,
                 values_container: Type[Iterable] = list):
        """
        >>> Helper().group_by([1, 2, 1, 3, 2, 4, 1, 2])
        {1: [1, 1, 1], 2: [2, 2, 2], 3: [3], 4: [4]}
        >>> Helper().group_by([1, 2, 1, 3, 2, 4, 1, 2], values_container=tuple)
        {1: (1, 1, 1), 2: (2, 2, 2), 3: (3,), 4: (4,)}
        >>> Helper().group_by(
        ...     [1, 2, 1, 3, 2, 4, 1, 2], key=lambda item: item % 2)
        {0: [2, 2, 4, 2], 1: [1, 1, 3, 1]}
        >>> Helper().group_by(
        ...     [('a', 1), ('b', 2), ('a', 3), ('a', 4), ('c', 5)],
        ...     key=lambda item: item[0])
        {'a': [('a', 1), ('a', 3), ('a', 4)], 'b': [('b', 2)], 'c': [('c', 5)]}
        >>> Helper().group_by(
        ...     [('a', 1), ('b', 2), ('a', 3), ('a', 4), ('c', 5)],
        ...     key=lambda item: item[0], value='auto')
        {'a': [1, 3, 4], 'b': [2], 'c': [5]}
        """
        # noinspection PyArgumentList
        return {
            _key: values_container(
                (
                    item
                    if value is None else
                    self.auto_group_by_value(item, _key)
                    if value == 'auto' else
                    value(item)
                )
                for item in items
            )
            for _key, items
            in itertools.groupby(sorted(iterable, key=key), key=key)
        }

    def auto_group_by_value(self, item: Tuple, key: Union[Tuple, Any]):
        """
        >>> Helper().auto_group_by_value(('a', 'b'), 'a')
        'b'
        >>> Helper().auto_group_by_value(('a', 'b'), 'b')
        'a'
        >>> Helper().auto_group_by_value(('a', 'b'), 'b')
        'a'
        >>> Helper().auto_group_by_value(('a', 'b'), 'ab')
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), 'a')
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), 'c')
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), ('a',))
        ('b', 'c')
        >>> Helper().auto_group_by_value(('a', 'b', 'c'), ('c',))
        ('a', 'b')
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('a', 'b'))
        ('c', 'd')
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('c', 'd'))
        ('a', 'b')
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('a', 'd'))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value((('a', 'b'), ('c', 'd')), ('a',))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b'), ('a',))
        ('b',)
        >>> Helper().auto_group_by_value(('a', 'b'), ('b',))
        ('a',)
        >>> Helper().auto_group_by_value(('a', 'b'), ('c',))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('a',))
        ('b', 'c', 'd')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('d',))
        ('a', 'b', 'c')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('b',))
        Traceback (most recent call last):
        ...
        ValueError: ...
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('a', 'b'))
        ('c', 'd')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('c', 'd'))
        ('a', 'b')
        >>> Helper().auto_group_by_value(('a', 'b', 'c', 'd'), ('a', 'd'))
        Traceback (most recent call last):
        ...
        ValueError: ...
        """
        if not isinstance(item, tuple):
            raise ValueError(f"Item must be a tuple")
        key_is_tuple = (
                isinstance(key, tuple)
                and item[1:] != (key,)
                and item[:1] != (key,)
        )
        if not key_is_tuple:
            key_tuple = (key,)
            if len(item) != 2:
                raise ValueError(
                    f"If key is not a tuple ({key}), then item needs to be a "
                    f"2-tuple, not a {len(item)}-tuple ({item})")
        else:
            key_tuple = key

        if item[:len(key_tuple)] == key_tuple:
            value_tuple = item[len(key_tuple):]
        elif item[-len(key_tuple):] == key_tuple:
            value_tuple = item[:-len(key_tuple)]
        else:
            raise ValueError(
                f"Key {key_tuple} is not a prefix or a suffix of item {item}")

        if key_is_tuple:
            return value_tuple
        else:
            value, = value_tuple
            return value


helper = Helper()
