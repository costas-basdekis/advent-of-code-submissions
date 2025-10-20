#!/usr/bin/env python3
from dataclasses import dataclass, field
import re
from enum import Enum
from functools import reduce
from itertools import groupby
from pathlib import Path
from typing import (
    Any, cast, Callable, ClassVar, Dict, Generic, Iterable, List, Optional, Set,
    Tuple, Type, Union, TypeVar, Iterator, Sized, Collection,
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
        return "\n".join(
            "yes" if feasible else "no"
            for feasible in check_cats_feasibility_from_text_many(_input)
        )
        # cat_sets = CatSet.from_text_many(_input)
        # if debugger:
        #     answers = []
        #     for index, cat_set in enumerate(cat_sets, start=1):
        #         debugger.report(f"Case #{index}/{len(cat_sets)}:")
        #         constraint = cat_set.get_constraint(keep_reasons=True, debugger=debugger)
        #         debugger.report(str(constraint))
        #         answers.append("yes" if constraint.possible else "no")
        #     return "\n".join(answers)
        # return CatSet.get_answers(cat_sets)
    
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
        # print("Case 4:\n" + str(CatSet.from_text_many((Path(__file__).parent / "data" / "F-herdingcats" / "secret-07-rmo.in").read_text())[0].get_constraint(keep_reasons=True)))


def check_cats_feasibility_from_text_many(text: str) -> List[bool]:
    lines = map(str.strip, text.strip().splitlines())
    next(lines)
    results = []
    while True:
        try:
            case_lines = [next(lines)]
        except StopIteration:
            break
        cat_count, _ = map(int, case_lines[0].strip().split(" "))
        for _ in range(cat_count):
            try:
                case_lines.append(next(lines))
            except StopIteration:
                raise Exception(f"There were supposed to be {cat_count} lines, but got only {len(case_lines) - 1}")
        results.append(check_cats_feasibility(case_lines))
    return results


def check_cats_feasibility_from_text(cat_text: str) -> bool:
    lines = cat_text.strip().splitlines()
    return check_cats_feasibility(lines)


SimpleCat = Tuple[int, List[int]]


def check_cats_feasibility(cat_lines: Iterable[str]) -> bool:
    cat_lines = iter(cat_lines)
    _, plant_count = map(int, next(cat_lines).strip().split(" "))
    cats: Iterable[SimpleCat] = (
        (pot, plants)
        for line in cat_lines
        for pot, _, *plants in [map(int, line.strip().split(" "))]
    )
    cat_groups: Iterable[Tuple[int, Iterable[SimpleCat]]] = groupby(sorted(cats, key=lambda _cat: _cat[0], reverse=True), key=lambda _cat: _cat[0])
    excluded_plants = set()
    for index, (pot, pot_cats) in enumerate(cat_groups, start=1):
        pot_cats = iter(pot_cats)
        try:
            cats_plants = set(next(pot_cats)[1])
        except StopIteration:
            raise Exception(f"Got not cats for pot {pot}")
        inclusive_cats_plants = set(cats_plants)
        for _, cat_plants in pot_cats:
            cats_plants.intersection_update(cat_plants)
            if not cats_plants:
                return False
            inclusive_cats_plants.update(cat_plants)
        pot_plants = cats_plants - excluded_plants
        if not pot_plants:
            return False
        excluded_plants |= inclusive_cats_plants
        excluded_plants_count = len(excluded_plants)
        if (plant_count - excluded_plants_count) < (pot - 1):
            return False
    return True


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
        return PotConstraint.from_cat_set_constructively(self, keep_reasons=keep_reasons, debugger=debugger)


@dataclass
class Cat:
    pot: int
    plants: Set[int]

    @classmethod
    def from_text(cls, text: str) -> "Cat":
        """
        >>> Cat.from_text("2 2 1 5")
        Cat(pot=2, plants=[1, 5])
        """
        values = list(map(int, text.strip().split(" ")))
        return cls(pot=values[0], plants=set(values[2:]))


@dataclass
class PotConstraint:
    plants_per_pot: Dict[int, Set[int]]
    plant_count: int
    possible: bool
    reasons: Optional[Set[str]]
    pots_per_plant: Dict[int, Set[int]]
    plants_per_pot_counts: Dict[int, int]
    pots_per_plant_counts: Dict[int, int]
    single_plant_pots: Set[int]
    single_pot_plants: Set[int]

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
    def from_plants_per_pot_list(cls, plants_per_pot_list: List[Union[Set[int], Set[int]]], plant_count: Optional[int] = None, keep_reasons: bool = False, possible: bool = True) -> "PotConstraint":
        return cls.from_plants_per_pot(
            {
                pot: (
                    plants_per_pot
                    if isinstance(plants_per_pot, set) else
                    set(plants_per_pot)
                )
                for pot, plants_per_pot in enumerate(plants_per_pot_list, start=1)
            },
            plant_count=plant_count,
            keep_reasons=keep_reasons,
            possible=possible,
        )

    @classmethod
    def from_plants_per_pot(cls, plants_per_pot: Dict[int, Set[int]], plant_count: Optional[int] = None, keep_reasons: bool = False, possible: bool = True) -> "PotConstraint":
        if plant_count is None:
            plant_count = max(map(max, plants_per_pot.values()))
        pots_per_plant = cls.get_pots_per_plant(plants_per_pot, plant_count)
        return cls(
            plants_per_pot=plants_per_pot,
            plant_count=plant_count,
            possible=possible,
            reasons=set() if keep_reasons else None,
            pots_per_plant=pots_per_plant,
            plants_per_pot_counts={pot: len(plants) for pot, plants in plants_per_pot.items()},
            pots_per_plant_counts={plant: len(pots) for plant, pots in pots_per_plant.items()},
            single_plant_pots={pot for pot, plants in plants_per_pot.items() if len(plants) == 1},
            single_pot_plants={plant for plant, pots in pots_per_plant.items() if len(pots) == 1},
        )

    @classmethod
    def get_pots_per_plant(cls, plants_per_pot: Dict[int, Set[int]], plant_count: int) -> Dict[int, Set[int]]:
        pots_per_plant = {plant: set() for plant in range(1, plant_count + 1)}
        for pot, plants in plants_per_pot.items():
            for plant in plants:
                pots_per_plant[plant].add(pot)
        return pots_per_plant

    @classmethod
    def from_cat_set_constructively(cls, cat_set: CatSet, keep_reasons: bool = False, debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        return cls.empty(cat_set.plant_count, keep_reasons)\
            .apply_cats_constructively(cat_set.cats, debugger=debugger)\
            # .apply_optimisations(debugger=debugger)

    @classmethod
    def empty(cls, plant_count: int = None, keep_reasons: bool = False) -> "PotConstraint":
        return cls(
            plants_per_pot={plant: set() for plant in range(1, plant_count + 1)},
            plant_count=plant_count,
            possible=True,
            reasons=set() if keep_reasons else None,
            pots_per_plant={pot: set() for pot in range(1, plant_count + 1)},
            plants_per_pot_counts={pot: 0 for pot in range(1, plant_count + 1)},
            pots_per_plant_counts={plant: 0 for plant in range(1, plant_count + 1)},
            single_plant_pots=set(),
            single_pot_plants=set(),
        )

    def __str__(self) -> str:
        return "{}\n{}{}".format(
            "\n".join(
                f"#{pot} ({self.plants_per_pot_counts[pot]}): {', '.join(map(str, sorted(plants)))}"
                for pot, plants in self.plants_per_pot.items()
            ),
            f"Possible: {self.possible}",
            "\nReasons:\n{}".format(
                "\n".join(map(" - {}".format, sorted(self.reasons)))
            )
            if self.reasons else "",
        )

    def add(self, pot: int, plant: int) -> None:
        plants = self.plants_per_pot[pot]
        if plant in plants:
            return
        plants.add(plant)
        self.pots_per_plant[plant].add(pot)
        self.plants_per_pot_counts[pot] += 1
        plant_count = self.plants_per_pot_counts[pot]
        if plant_count == 1:
            self.single_plant_pots.add(pot)
        elif plant_count == 2:
            self.single_plant_pots.discard(pot)
        self.pots_per_plant_counts[plant] += 1
        pot_count = self.pots_per_plant_counts[plant]
        if pot_count == 1:
            self.single_pot_plants.add(plant)
        elif pot_count == 2:
            self.single_pot_plants.discard(plant)

    def discard(self, pot: int, plant: int) -> None:
        plants = self.plants_per_pot[pot]
        if plant not in plants:
            return
        plants.discard(plant)
        self.pots_per_plant[plant].discard(pot)
        self.plants_per_pot_counts[pot] -= 1
        plant_count = self.plants_per_pot_counts[pot]
        if plant_count == 1:
            self.single_plant_pots.add(pot)
        elif plant_count ==0:
            self.single_plant_pots.discard(pot)
        self.pots_per_plant_counts[plant] -= 1
        pot_count = self.pots_per_plant_counts[plant]
        if pot_count == 1:
            self.single_pot_plants.add(plant)
        elif pot_count == 0:
            self.single_pot_plants.discard(plant)

    def fail(self, reason_format_or_func: Union[str, Callable], *args, **kwargs) -> bool:
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
                for plant in plants & cat.plants:
                    self.pots_per_plant[plant].discard(pot)
                plants -= cat.plants
                if not plants:
                    if self.fail("Cat in pot {cat_pot} excludes all plants from pot {pot}", cat_pot=cat.pot, pot=pot):
                        break
            plants = self.plants_per_pot[cat.pot]
            for plant in plants - cat.plants:
                self.pots_per_plant[plant].discard(cat.pot)
            plants &= cat.plants
            if not plants:
                if self.fail("Cat in pot {cat_pot} requires plants {cat_plants}, none possible", cat_pot=cat.pot, cat_plants=cat.plants):
                    break
            if debugger.should_report():
                debugger.default_report_if(f"Applied {index}/{len(cats)} cats")
        self.plants_per_pot_counts = {pot: len(plants) for pot, plants in self.plants_per_pot.items()}
        self.pots_per_plant_counts = {plant: len(pots) for plant, pots in self.pots_per_plant.items()}
        self.single_plant_pots = {pot for pot, count in self.plants_per_pot_counts.items() if count == 1}
        self.single_pot_plants = {plant for plant, count in self.pots_per_plant_counts.items() if count == 1}
        return self.check_feasibility_after_applying_cats(cats, debugger=debugger)

    def check_feasibility_after_applying_cats(self, cats: List[Cat], debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        cat_pots = sorted(cat.pot for cat in cats)
        previous_plants = None
        total_plants = set()
        plant_count = 0
        for pot_count, (pot, plants) in enumerate(debugger.stepping(self.plants_per_pot.items()), start=1):
            if plants is not previous_plants:
                previous_plants = plants
                total_plants |= plants
                plant_count = len(total_plants)
            if pot_count > plant_count:
                if self.fail("Pots 1-{pot_count} have only {plant_count} plants", pot_count=pot_count, plant_count=plant_count):
                    break
            if debugger.should_report():
                debugger.default_report_if(f"Checked feasibility after applying {pot_count}/{len(cat_pots)}")
        # for index, pot_end in enumerate(debugger.stepping(cat_pots), start=1):
        #     pot_count = pot_end - 1
        #     total_plants = set()
        #     for pot in range(1, pot_end):
        #         total_plants |= self.plants_per_pot[pot]
        #     plant_count = len(total_plants)
        #     if pot_count > plant_count:
        #         if self.fail("Pots {pot_start}-{pot_end_minus_1} have only {plant_count} plants, but need {pot_count} plants", pot_start=1, pot_end_minus_1=pot_end - 1, plant_count=plant_count, pot_count=pot_count):
        #             break
        #     if debugger.should_report():
        #         debugger.default_report_if(f"Checked feasibility after applying {index}/{len(cat_pots)}")
        return self

    def apply_cats_constructively(self, cats: List[Cat], debugger: Debugger = Debugger(enabled=False)) -> "PotConstraint":
        # cat_groups: List[Tuple[int, List[Cat]]] = [
        #     (pot, list(cats))
        #     for pot, cats
        #     in groupby(sorted(cats, key=lambda _cat: _cat.pot, reverse=True), key=lambda _cat: _cat.pot)
        # ] # + [(0, [])]
        cat_groups: Iterable[Tuple[int, Iterable[Cat]]] = groupby(sorted(cats, key=lambda _cat: _cat.pot, reverse=True), key=lambda _cat: _cat.pot)
        excluded_plants = set()
        excluded_plants_count = 0
        previous_pot = self.plant_count + 1
        cat_count = 0
        non_restricted_pot_count = 0
        # debugger.default_report(
        #     f"Applied {0}/{len(cat_groups)} cat groups ({cat_count}/{len(cats)} cats), "
        #     f"{len(excluded_plants)} excluded plants, "
        #     f"{sum(self.plants_per_pot_counts.values())} total plants in pots, "
        #     f"{non_restricted_pot_count} non-restricted pots"
        # )
        for index, (pot, pot_cats) in enumerate(debugger.stepping(cat_groups), start=1):
            # if previous_pot - pot > 1:
            #     # other_plants = {
            #     #     plant
            #     #     for plant in range(1, self.plant_count + 1)
            #     #     if plant not in excluded_plants
            #     # }
            #     other_plants_count = self.plant_count - excluded_plants_count
            #     other_pots = range(pot + 1, previous_pot)
            #     # other_pots_count = len(other_pots)
            #     for other_pot in other_pots:
            #     #     # self.plants_per_pot[other_pot] |= other_plants
            #         self.plants_per_pot_counts[other_pot] += other_plants_count
            #     # for other_plant in other_plants:
            #     #     # self.pots_per_plant[other_plant].update(other_pots)
            #     #     self.pots_per_plant_counts[other_plant] += other_pots_count
            #     if debugger:
            #         # non_restricted_pot_count += other_pots_count
            #         non_restricted_pot_count += self.plant_count - excluded_plants_count
            # if pot == 0 and not pot_cats:
            #     break
            # previous_pot = pot
            pot_cats = iter(pot_cats)
            try:
                cats_plants = set(next(pot_cats).plants)
            except StopIteration:
                raise Exception(f"Got not cats for pot {pot}")
            inclusive_cats_plants = set(cats_plants)
            stop_due_to_no_cats = False
            for cat in pot_cats:
                cats_plants.intersection_update(cat.plants)
                if not cats_plants:
                    if self.fail("Cats in pot {pot} require plants {cats_plants}, none possible", pot=pot, cats_plants=cats_plants):
                        stop_due_to_no_cats = True
                        break
                inclusive_cats_plants.update(cat.plants)
            if stop_due_to_no_cats:
                break
            # noinspection PyTypeChecker
            # cats_plants: Set[int] = reduce(set.__and__, (cat.plants for cat in pot_cats))
            # if not cats_plants:
            #     if self.fail("Cats in pot {pot} require plants {cats_plants}, none possible", pot=pot, cats_plants=cats_plants):
            #         break
            pot_plants = cats_plants - excluded_plants
            if not pot_plants:
                if self.fail("Cats in pot {pot} require plants {cats_plants}, none possible", pot=pot, cats_plants=cats_plants):
                    break
            # self.plants_per_pot[pot] |= pot_plants
            # self.plants_per_pot_counts[pot] += len(pot_plants)
            # for plant in pot_plants:
                # self.pots_per_plant[plant].add(pot)
                # self.pots_per_plant_counts[plant] += 1
            # noinspection PyTypeChecker
            # inclusive_cats_plants = reduce(set.__or__, (cat.plants for cat in pot_cats))
            excluded_plants |= inclusive_cats_plants
            excluded_plants_count = len(excluded_plants)
            if (self.plant_count - excluded_plants_count) < (pot - 1):
                if self.fail(
                    "Cats in pots 1-{next_pot} can only have up to {available_plant_count} (plant count={plant_count}, "
                    "excluded count={excluded_plants_count}), too few plants",
                    next_pot=pot - 1, available_plant_count=self.plant_count - excluded_plants_count,
                    plant_count=self.plant_count, excluded_plants_count=excluded_plants_count,
                ):
                    break
            # if debugger:
            #     cat_count += len(pot_cats)
            # if debugger.should_report():
            #     debugger.default_report_if(
            #         f"Applied {index}/{len(cat_groups)} cat groups ({cat_count}/{len(cats)} cats, current pot is {pot}), "
            #         f"{len(excluded_plants)} excluded plants, "
            #         f"{sum(self.plants_per_pot_counts.values())} total plants in pots, "
            #         f"{non_restricted_pot_count} non-restricted pots"
            #     )
        self.single_plant_pots.update(pot for pot, count in self.plants_per_pot_counts.items() if count == 1)
        self.single_pot_plants.update(plant for plant, count in self.pots_per_plant_counts.items() if count == 1)
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
            # | self.check_too_few_or_too_many_plants()
        )

    def apply_one_plant(self) -> bool:
        # for pot, plants in self.plants_per_pot.items():
        for pot in self.single_plant_pots:
            plants = self.plants_per_pot[pot]
            # if len(plants) != 1:
            # if self.plants_per_pot_counts[pot] != 1:
            #     continue
            plant, = plants
            pots = self.pots_per_plant[plant]
            if self.pots_per_plant_counts[plant] == 1:
                continue
            for other_pot in list(pots):
                if other_pot == pot:
                    continue
                self.discard(other_pot, plant)
                if not self.plants_per_pot[other_pot]:
                    if self.fail("Pot {pot} has only plant {plant}, excludes all plants from pot {other_pot}", pot=pot, plant=plant, other_pot=other_pot):
                        break
            self.single_plant_pots.discard(pot)
            return True
            # self.pots_per_plant[plant] = {pot}
        return False

    def apply_plant_only_once(self) -> bool:
        # for plant, pots in list(self.pots_per_plant.items()):
        for plant in self.single_pot_plants:
            pots = self.pots_per_plant[plant]
            # if len(pots) != 1:
            # if self.pots_per_plant_counts[plant] != 1:
            #     continue
            pot, = pots
            plants = self.plants_per_pot[pot]
            # if len(plants) == 1:
            if self.plants_per_pot_counts[pot] == 1:
                continue
            for other_plant in list(plants):
                if other_plant == plant:
                    continue
                self.discard(pot, other_plant)
                if not self.pots_per_plant[other_plant]:
                    if self.fail("Plant {plant} has only pot {pot}, excludes all pots from plant {other_plant}", pot=pot, plant=plant, other_plant=other_plant):
                        break
            self.single_pot_plants.discard(plant)
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
