#!/usr/bin/env python3
from dataclasses import dataclass
import re
from typing import (
    Callable, Dict, Generic, Iterable, List, Optional, Set, Tuple, Type, Union,
)

from aox.challenge import Debugger
from utils import BaseChallenge, Point2D, TV, get_type_argument_class


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        42
        """


Challenge.main()
challenge = Challenge()
