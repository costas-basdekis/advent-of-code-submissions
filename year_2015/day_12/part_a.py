#!/usr/bin/env python3
import json
from typing import Union, Iterable, Type, Tuple

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        111754
        """
        return JsonWalker().get_numbers_sum_from_json(_input)


JsonValue = Union[None, bool, int, float, str]
JsonStructure = Union[dict, list]
Json = Union[JsonValue, JsonStructure]


class JsonWalker:
    def get_numbers_sum_from_json(self, json_string: str) -> float:
        """
        >>> JsonWalker().get_numbers_sum_from_json('{"a":{"b":4},"c":-1}')
        3
        """
        return self.get_numbers_sum(json.loads(json_string))

    def get_numbers_sum(self, data: Json) -> float:
        """
        >>> JsonWalker().get_numbers_sum([1, 2, 3])
        6
        >>> JsonWalker().get_numbers_sum({"a": 2, "b": 4})
        6
        >>> JsonWalker().get_numbers_sum([[[3]]])
        3
        >>> JsonWalker().get_numbers_sum({"a": {"b": 4}, "c": -1})
        3
        >>> JsonWalker().get_numbers_sum({"a": [-1, 1]})
        0
        >>> JsonWalker().get_numbers_sum([-1, {"a": 1}])
        0
        >>> JsonWalker().get_numbers_sum([])
        0
        >>> JsonWalker().get_numbers_sum({})
        0
        """
        return sum(self.walk_values_of_type(data, (int, float)))

    def walk_values_of_type(self, data: Json,
                            _type: Union[Type, Tuple[Type, ...]],
                            ) -> Iterable[JsonValue]:
        """
        >>> list(JsonWalker().walk_values_of_type([1, 2.0, 3], int))
        [1, 3]
        >>> list(JsonWalker().walk_values_of_type([1, 2.0, 3], (int, float)))
        [1, 2.0, 3]
        >>> list(JsonWalker().walk_values_of_type(
        ...     {"a": {"b": 4, "d": [1, "f", {"e": 5}]},"c": True}, int))
        [4, 1, 5]
        >>> list(JsonWalker().walk_values_of_type(
        ...     {"a": {"b": 4, "d": [1, "f", {"e": 5}]},"c": True}, bool))
        [True]
        """
        if _type is bool or (isinstance(_type, tuple) and bool in _type):
            for value in self.walk_values(data):
                if isinstance(value, _type):
                    yield value
        else:
            for value in self.walk_values(data):
                if isinstance(value, _type) and not isinstance(value, bool):
                    yield value

    def walk_values(self, data: Json) -> Iterable[JsonValue]:
        """
        >>> list(JsonWalker().walk_values([1, 2, 3]))
        [1, 2, 3]
        >>> list(JsonWalker().walk_values(
        ...     {"a": {"b": 4, "d": [1, "f", {"e": 5}]},"c": -1}))
        [4, 1, 'f', 5, -1]
        >>> list(JsonWalker().walk_values([[[3]]]))
        [3]
        """
        if data is None:
            yield data
        elif isinstance(data, (bool, int, float, str)):
            yield data
        elif isinstance(data, list):
            for value in data:
                yield from self.walk_values(value)
        elif isinstance(data, dict):
            for value in data.values():
                yield from self.walk_values(value)
        else:
            raise TypeError(f"Expected JSON type, but got {type(data)}")


Challenge.main()
challenge = Challenge()
