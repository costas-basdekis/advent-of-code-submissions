#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Generic, Type, List, Tuple, Iterable

from aox.challenge import Debugger
from utils import BaseChallenge, TV, get_type_argument_class, product, \
    all_possible_quantity_splits


class Challenge(BaseChallenge):
    def solve(self, _input, debugger: Debugger):
        """
        >>> Challenge().default_solve()
        21367368
        """
        return IngredientSet.from_ingredients_text(_input).get_highest_score()


IngredientT = TV['Ingredient']


@dataclass
class IngredientSet(Generic[IngredientT]):
    ingredients: List[IngredientT]

    @classmethod
    def get_ingredient_class(cls) -> Type[IngredientT]:
        return get_type_argument_class(cls, IngredientT)

    @classmethod
    def from_ingredients_text(cls, ingredients_text: str):
        """
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... )
        IngredientSet(ingredients=[Ingredient(name='Butterscotch', capacity=-1,
            durability=-2, flavour=6, texture=3, calories=8),
            Ingredient(name='Cinnamon', capacity=2, durability=3,
                flavour=-2, texture=-1, calories=3)])
        """
        ingredient_class = cls.get_ingredient_class()
        return cls(list(map(
            ingredient_class.from_ingredient_text,
            ingredients_text.splitlines())))

    def get_highest_score(self, total: int = 100) -> int:
        """
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_highest_score(2)
        8
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_highest_score()
        62842880
        """
        return self.get_quantities_score(
            self.get_highest_scoring_quantities(total))

    def get_highest_scoring_quantities(self, total: int = 100,
                                       ) -> Tuple[int, ...]:
        """
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_highest_scoring_quantities(2)
        (1, 1)
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_highest_scoring_quantities()
        (44, 56)
        """
        return max(self.get_possible_quantities(total),
                   key=self.get_quantities_score)

    def get_possible_quantities(self, total: int = 100,
                                ) -> Iterable[Tuple[int, ...]]:
        """
        >>> sorted(IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_possible_quantities(2))
        [(0, 2), (1, 1), (2, 0)]
        """
        return all_possible_quantity_splits(total, len(self.ingredients))

    SCORE_PROPERTIES = ["capacity", "durability", "flavour", "texture"]

    def get_quantities_score(self, quantities: Tuple[int, ...]) -> int:
        """
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_quantities_score((44, 56))
        62842880
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_quantities_score((10, 90))
        0
        """
        if len(quantities) != len(self.ingredients):
            raise Exception(
                f"Expected {len(self.ingredients)} quantities, but got "
                f"{len(quantities)}")
        return product(
            max(0, sum(
                getattr(ingredient, _property) * quantity
                for quantity, ingredient in zip(quantities, self.ingredients)
            ))
            for _property in self.SCORE_PROPERTIES
        )


@dataclass
class Ingredient:
    name: str
    capacity: int
    durability: int
    flavour: int
    texture: int
    calories: int

    re_ingredient = re.compile(
        r"^(\w+): capacity (-?\d+), durability (-?\d+), flavor (-?\d+), "
        r"texture (-?\d+), calories (-?\d+)$")

    @classmethod
    def from_ingredient_text(cls, ingredient_text: str):
        """
        >>> Ingredient.from_ingredient_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8")
        Ingredient(name='Butterscotch', capacity=-1, durability=-2, flavour=6,
            texture=3, calories=8)
        """
        match = cls.re_ingredient.match(ingredient_text)
        if not match:
            raise Exception(f"Could not parse {repr(ingredient_text)}")
        name, capacity_str, durability_str, flavour_str, texture_str, \
            calories_str = match.groups()
        return cls(
            name, int(capacity_str), int(durability_str), int(flavour_str),
            int(texture_str), int(calories_str))


Challenge.main()
challenge = Challenge()
