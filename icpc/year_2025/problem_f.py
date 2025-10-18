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
    BaseIcpcChallenge, Point2D, get_type_argument_class, helper, Cls, Self,
)


class Challenge(BaseIcpcChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> print(Challenge().default_solve())
        yes
        no
        """
        cat_sets = CatSet.from_text_many(_input)
        if debugger:
            for index, cat_set in enumerate(cat_sets, start=1):
                debugger.report(f"Case #{index}:")
                debugger.report(str(cat_set.get_constraint(keep_reasons=True, debugger=debugger)))
        return CatSet.get_answers(cat_sets)
    
    def split_cases(self, _input: str) -> List[str]:
        return CatSet.split_cases(_input)
    
    def join_cases(self, cases: List[str]) -> str:
        return CatSet.join_cases(cases)

    def play(self):
        print("Case 1:\n" + str(CatSet.from_text('''
            3 5
            2 2 1 5
            2 3 1 4 5
            4 2 3 4
        ''').get_constraint(keep_reasons=True)))
        print("Case 2:\n" + str(CatSet.from_text('''
            3 5
            2 2 1 5
            2 3 1 4 5
            5 2 3 4
        ''').get_constraint(keep_reasons=True)))
        print("Case 3:\n" + str(CatSet.from_text('''
            3 100
            76 12 9 27 30 47 54 55 57 66 67 86 94 99
            68 18 3 6 22 29 31 32 40 41 50 51 53 55 61 76 83 85 87 88
            77 13 9 10 12 19 22 25 33 56 73 82 85 95 100
        ''').get_constraint(keep_reasons=True)))


@dataclass
class CatSet:
    cats: List["Cat"]
    plant_count: int

    @classmethod
    def get_answers_from_text(cls, text: str) -> str:
        """
        >>> print(CatSet.get_answers_from_text('''
        ...     2
        ...     3 5
        ...     2 2 1 5
        ...     2 3 1 4 5
        ...     4 2 3 4
        ...     3 5
        ...     2 2 1 5
        ...     2 3 1 4 5
        ...     5 2 3 4
        ... '''))
        yes
        no
        """
        return cls.get_answers(cls.from_text_many(text))
    
    @classmethod
    def get_answers(cls, cat_sets: List["CatSet"]) -> str:
        return "\n".join(
            cat_set.get_answer() 
            for cat_set in cat_sets
        )

    @classmethod
    def from_text_many(cls, text: str) -> List["CatSet"]:
        """
        >>> _cat_sets = CatSet.from_text_many('''
        ...     2
        ...     3 5
        ...     2 2 1 5
        ...     2 3 1 4 5
        ...     4 2 3 4
        ...     3 5
        ...     2 2 1 5
        ...     2 3 1 4 5
        ...     5 2 3 4
        ... ''')
        >>> [(len(_cat_set.cats), _cat_set.plant_count) for _cat_set in _cat_sets]
        [(3, 5), (3, 5)]
        """
        cases = cls.split_cases(text)
        return list(map(cls.from_text, cases))
    
    @classmethod
    def split_cases(cls, text: str) -> List[str]:
        lines = list(map(str.strip, text.strip().splitlines()))
        lines.pop(0)
        case_texts = []
        while lines:
            cat_count, _ = map(int, lines[0].split(" "))
            case_text = "\n".join(lines[:cat_count + 1])
            case_texts.append(case_text)
            lines = lines[cat_count + 1:]
        return case_texts
    
    @classmethod
    def join_cases(cls, cases: List[str]) -> str:
        return "\n".join([str(len(cases))] + cases)

    @classmethod
    def from_text(cls, text: str) -> "CatSet":
        """
        >>> _cat_set = CatSet.from_text('''
        ...     3 5
        ...     2 2 1 5
        ...     2 3 1 4 5
        ...     4 2 3 4
        ... ''')
        >>> len(_cat_set.cats), _cat_set.plant_count
        (3, 5)
        """
        lines = list(map(str.strip, text.strip().splitlines()))
        return cls.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: List[str]) -> "CatSet":
        cat_count, plant_count = map(int, lines[0].split(" "))
        return cls(cats=list(map(Cat.from_text, lines[1:1 + cat_count])), plant_count=plant_count)
    
    def get_answer(self) -> str:
        return (
            "yes"
            if self.get_constraint().possible
            else "no"
        )

    def get_constraint(self, keep_reasons: bool = False, debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        return PotConstraint.from_cat_set(self, keep_reasons=keep_reasons, debugger=debugger)


@dataclass
class Cat:
    pot: int
    plants: List[int]

    @classmethod
    def from_text(cls, text: str) -> "Cat":
        """
        >>> Cat.from_text("2 2 1 5")
        Cat(pot=2, plants=[1, 5])
        """
        values = list(map(int, text.strip().split(" ")))
        return cls(pot=values[0], plants=values[2:])


@dataclass
class PotConstraint:
    plants_per_pot: Dict[int, Set[int]]
    plant_count: int
    possible: bool
    reasons: Optional[Set[str]]
    pots_per_plant: Dict[int, Set[int]]

    @classmethod
    def from_cat_set(cls, cat_set: CatSet, keep_reasons: bool = False, debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        return cls.from_plant_count(cat_set.plant_count, keep_reasons)\
            .apply_cats(cat_set.cats, debugger=debugger)\
            .apply_optimisations(debugger=debugger)

    @classmethod
    def from_plant_count(cls, plant_count: int, keep_reasons: bool = False) -> "PotConstraint":
        return cls.from_plants_per_pot(
            {plant: set(range(1, plant_count + 1)) for plant in range(1, plant_count + 1)},
            plant_count=plant_count,
            keep_reasons=keep_reasons,
        )

    @classmethod
    def from_plants_per_pot_list(cls, plants_per_pot_list: List[Set[int]], plant_count: Optional[int] = None, keep_reasons: bool = False, possible: bool = True) -> "PotConstraint":
        return cls.from_plants_per_pot(
            {pot: plants_per_pot for pot, plants_per_pot in enumerate(plants_per_pot_list, start=1)},
            plant_count=plant_count,
            keep_reasons=keep_reasons,
            possible=possible,
        )

    @classmethod
    def from_plants_per_pot(cls, plants_per_pot: Dict[int, Set[int]], plant_count: Optional[int] = None, keep_reasons: bool = False, possible: bool = True) -> "PotConstraint":
        if plant_count is None:
            plant_count = max(map(max, plants_per_pot.values()))
        return cls(
            plants_per_pot=plants_per_pot,
            plant_count=plant_count,
            possible=possible,
            reasons=set() if keep_reasons else None,
            pots_per_plant=cls.get_pots_per_plant(plants_per_pot, plant_count),
        )

    @classmethod
    def get_pots_per_plant(cls, plants_per_pot: Dict[int, Set[int]], plant_count: int) -> Dict[int, Set[int]]:
        pots_per_plant = {plant: set() for plant in range(1, plant_count + 1)}
        for pot, plants in plants_per_pot.items():
            for plant in plants:
                pots_per_plant[plant].add(pot)
        return pots_per_plant

    def __str__(self) -> str:
        return "{}\n{}{}".format(
            "\n".join(
                f"#{pot} ({len(plants)}): {', '.join(map(str, sorted(plants)))}"
                for pot, plants in self.plants_per_pot.items()
            ),
            f"Possible: {self.possible}",
            "\nReasons:\n{}".format(
                "\n".join(map(" - {}".format, sorted(self.reasons)))
            )
            if self.reasons else "",
        )

    def fail(self, reason_format_or_func: Union[str, Callable], *args, **kwargs) -> None:
        self.possible = False
        if self.reasons is None:
            return True
        if args and kwargs:
            raise Exception("Cannot have both args and kwargs")
        if isinstance(reason_format_or_func, str):
            if args or kwargs:
                reason = reason_format_or_func.format(*args, **kwargs)
            else:
                reason = reason_format_or_func
        else:
            reason = reason_format_or_func(*args, **kwargs)
        self.reasons.add(reason)
        return False

    def apply_cats(self, cats: List[Cat], debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        for index, cat in enumerate(debugger.stepping(cats), start=1):
            for pot in range(1, cat.pot):
                plants = self.plants_per_pot[pot]
                for plant in plants & set(cat.plants):
                    self.pots_per_plant[plant].discard(pot)
                plants -= set(cat.plants)
                if not plants:
                    if self.fail("Cat in pot {cat_pot} excludes all plants from pot {pot}", cat_pot=cat.pot, pot=pot):
                        break
            plants = self.plants_per_pot[cat.pot]
            for plant in plants - set(cat.plants):
                self.pots_per_plant[plant].discard(cat.pot)
            plants &= set(cat.plants)
            if not plants:
                if self.fail("Cat in pot {cat_pot} requires plants {cat_plants}, none possible", cat_pot=cat.pot, cat_plants=cat.plants):
                    break
            if debugger.should_report():
                debugger.default_report_if(f"Applied {index}/{len(cats)} cats")
        return self.check_feasibility_after_applying_cats(cats, debugger=debugger)
    
    def check_feasibility_after_applying_cats(self, cats: List[Cat], debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        cat_pots = sorted(cat.pot for cat in cats)
        for index, pot_end in enumerate(debugger.stepping(cat_pots), start=1):
            pot_count = pot_end - 1
            total_plants = set()
            for pot in range(1, pot_end):
                total_plants |= self.plants_per_pot[pot]
            plant_count = len(total_plants)
            if pot_count > plant_count:
                if self.fail("Pots {pot_start}-{pot_end_minus_1} have only {plant_count} plants, but need {pot_count} plants", pot_start=1, pot_end_minus_1=pot_end - 1, plant_count=plant_count, pot_count=pot_count):
                    break
            if debugger.should_report():
                debugger.default_report_if(f"Checked feasibility after applying {index}/{len(cat_pots)}")
        return self

    def apply_optimisations(self, debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        count = 0
        while debugger.step_if(self.possible and self.apply_optimisations_once()):
            count += 1
            if debugger.should_report():
                plant_count = sum(map(len, self.plants_per_pot.values()))
                debugger.default_report_if(f"Applied optimisations {count} times, {plant_count} possible plants remain")
        return self

    def apply_optimisations_once(self) -> bool:
        return (
            self.apply_one_plant()
            | self.apply_plant_only_once()
            | self.check_every_plant_at_least_once()
            | self.check_too_few_or_too_many_plants()
        )
    
    def discard(self, pot: int, plant: int) -> None:
        plants = self.plants_per_pot[pot]
        if plant not in plants:
            return
        plants.discard(plant)
        self.pots_per_plant[plant].discard(pot)

    def apply_one_plant(self) -> bool:
        for pot, plants in self.plants_per_pot.items():
            if len(plants) != 1:
                continue
            plant, = plants
            for other_pot in self.pots_per_plant[plant]:
                if other_pot == pot:
                    continue
                self.discard(other_pot, plant)
                if not self.plants_per_pot[other_pot]:
                    if self.fail("Pot {pot} has only plant {plant}, excludes all plants from pot {other_pot}", pot=pot, plant=plant, other_pot=other_pot):
                        break
                return True
            self.pots_per_plant[plant] = {pot}
        return False

    def apply_plant_only_once(self) -> bool:
        for plant, pots in self.pots_per_plant.items():
            if len(pots) != 1:
                continue
            pot, = pots
            plants = self.plants_per_pot[pot]
            if len(plants) == 1:
                continue
            for other_plant in list(plants):
                if other_plant == plant:
                    continue
                self.discard(pot, other_plant)
            return True
        return False

    def check_every_plant_at_least_once(self) -> bool:
        if not self.possible and self.reasons is None:
            return False
        changed_any = False
        for plant, pots_with_plant in self.pots_per_plant.items():
            if not pots_with_plant:
                if self.fail("Plant {plant} cannot go to any pot", plant=plant):
                    break
        return changed_any

    def check_too_few_or_too_many_plants(self) -> bool:
        fellow_plants_by_plant = self.get_fellow_plants_by_plant()
        if len(fellow_plants_by_plant[1]) == self.plant_count:
            return False
        return (
            self.check_too_few_plants(fellow_plants_by_plant)
            | self.check_too_many_plants(fellow_plants_by_plant)
        )

    def check_too_few_plants(self, fellow_plants_by_plant: Optional[Dict[int, Set[int]]] = None) -> bool:
        """
        >>> PotConstraint.from_plants_per_pot_list(
        ...     [{3, 4}, {1, 2, 5}, {1, 5}, {1, 5}, {3, 4}]).check_too_few_plants()
        False
        >>> PotConstraint.from_plants_per_pot_list(
        ...     [{3, 4}, {1, 2, 5}, {1, 5}, {1, 5}, {3, 4}]).check_too_few_plants()
        False
        >>> PotConstraint.from_plants_per_pot_list(
        ...     [{3, 4}, {1, 5}, {1, 5}, {1, 5}, {3, 4}]).check_too_few_plants()
        True
        >>> PotConstraint.from_plants_per_pot_list(
        ...     [{2}, {1, 5}, {1, 5}, {1, 5}, {3, 4}]).check_too_few_plants()
        True
        """
        if not self.possible and self.reasons is None:
            return False
        changed_any = False
        checked_plants = set()
        if fellow_plants_by_plant is None:
            fellow_plants_by_plant = self.get_fellow_plants_by_plant()
        for plant, fellow_plants in fellow_plants_by_plant.items():
            if plant in checked_plants:
                continue
            checked_plants |= fellow_plants
            if len(fellow_plants) == self.plant_count:
                break
            pots_with_only_plants = [
                pot
                for pot, plants in self.plants_per_pot.items()
                if plants <= fellow_plants
            ]
            if len(pots_with_only_plants) > len(fellow_plants):
                if self.possible:
                    changed_any = True
                if self.fail(lambda: f"Pots {sorted(pots_with_only_plants)} can only have plants {sorted(fellow_plants)}, too few plants"):
                    break
        return changed_any

    def check_too_many_plants(self, fellow_plants_by_plant: Optional[Dict[int, Set[int]]] = None) -> bool:
        """
        >>> PotConstraint.from_plants_per_pot_list(
        ...     [{2}, {1, 5}, {1, 5}, {1, 5}, {3, 4}]).check_too_many_plants()
        True
        """
        if not self.possible and self.reasons is None:
            return False
        changed_any = False
        checked_plants = set()
        if fellow_plants_by_plant is None:
            fellow_plants_by_plant = self.get_fellow_plants_by_plant()
        for plant, fellow_plants in fellow_plants_by_plant.items():
            if plant in checked_plants:
                continue
            checked_plants |= fellow_plants
            if len(fellow_plants) == self.plant_count:
                break
            pots_with_plants = [
                pot
                for pot, plants in self.plants_per_pot.items()
                if plants & fellow_plants
            ]
            if len(pots_with_plants) < len(fellow_plants):
                if self.possible:
                    changed_any = True
                if self.fail(lambda: f"Plants {sorted(fellow_plants)} can only go to pots {pots_with_plants}, too many plants"):
                    break
        return changed_any

    def get_fellow_plants_by_plant(self) -> Dict[int, Set[int]]:
        if len(self.plants_per_pot[self.plant_count]) == self.plant_count:
            fellow_plants = self.plants_per_pot[self.plant_count]
            return {plant: fellow_plants for plant in self.pots_per_plant}
        fellow_plants_by_plant = {
            plant: {plant}
            for plant in range(1, self.plant_count + 1)
        }
        for plants in self.plants_per_pot.values():
            if not plants:
                continue
            first_plant = next(iter(plants))
            fellow_plants = fellow_plants_by_plant[first_plant]
            new_fellow_plants = plants - fellow_plants
            fellow_plants |= new_fellow_plants
            for plant in new_fellow_plants:
                fellow_plants_by_plant[plant] = fellow_plants
        return fellow_plants_by_plant


Challenge.main()
challenge = Challenge()
