#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar,
)

from aox.challenge import Debugger
from utils import (
    BaseChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)
from year_2022.day_19 import part_a


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        10336
        """
        return BlueprintSetExtended\
            .get_product_of_first_3_blueprints_for_longer_from_blueprints_text(
                _input, debugger=debugger,
            )


class BlueprintSetExtended(part_a.BlueprintSet):
    @classmethod
    def get_product_of_first_3_blueprints_for_longer_from_blueprints_text(
        cls, blueprint_text: str, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        return cls.from_blueprints_text(blueprint_text)\
            .get_product_of_first_3_blueprints_for_longer(debugger=debugger)

    def get_product_of_first_3_blueprints_for_longer(
        self, debugger: Debugger = Debugger(enabled=False),
    ) -> int:
        total = 1
        for index, blueprint in enumerate(self.blueprints[:3], 1):
            debugger.report(
                f"Blueprint {index}/{len(self.blueprints[:3])}, "
                f"product is {total}"
            )
            finder = part_a.GeodeFinder\
                .from_blueprint(blueprint)
            finder.max_time = 32
            best_geode_count = finder\
                .search(debugger=debugger)
            total *= best_geode_count
            debugger.report(
                f"Blueprint {index}/{len(self.blueprints[:3])}: "
                f"gave {best_geode_count}, "
                f"product is {total}"
            )
        return total


Challenge.main()
challenge = Challenge()
