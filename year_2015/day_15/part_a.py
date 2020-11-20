#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import Generic, Type, List, Tuple, Iterable, Optional

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

    def get_highest_score(self, total: int = 100,
                          exact_calories: Optional[int] = None) -> int:
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
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_highest_score(exact_calories=500)
        57600000
        """
        return self.get_quantities_score(
            self.get_highest_scoring_quantities(
                total, exact_calories=exact_calories))

    def get_highest_scoring_quantities(self, total: int = 100,
                                       exact_calories: Optional[int] = None,
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
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_highest_scoring_quantities(exact_calories=500)
        (40, 60)
        """
        return max(self.get_possible_quantities(
            total, exact_calories=exact_calories),
            key=self.get_quantities_score)

    def get_possible_quantities(self, total: int = 100,
                                exact_calories: Optional[int] = None,
                                ) -> Iterable[Tuple[int, ...]]:
        """
        >>> sorted(IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_possible_quantities(2))
        [(0, 2), (1, 1), (2, 0)]
        >>> sorted(IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_possible_quantities(2, 500))
        []
        >>> sorted(IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_possible_quantities(2, 11))
        [(1, 1)]
        """
        all_possible_quantities = all_possible_quantity_splits(
            total, len(self.ingredients))
        if exact_calories is not None:
            all_possible_quantities = (
                quantities
                for quantities in all_possible_quantities
                if self.get_quantities_calories(quantities) == exact_calories
            )

        return all_possible_quantities

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

    def get_quantities_calories(self, quantities: Tuple[int, ...]) -> int:
        """
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_quantities_calories((44, 56))
        520
        >>> IngredientSet.from_ingredients_text(
        ...     "Butterscotch: capacity -1, durability -2, flavor 6, "
        ...     "texture 3, calories 8\\n"
        ...     "Cinnamon: capacity 2, durability 3, flavor -2, texture -1, "
        ...     "calories 3\\n"
        ... ).get_quantities_calories((40, 60))
        500
        """
        if len(quantities) != len(self.ingredients):
            raise Exception(
                f"Expected {len(self.ingredients)} quantities, but got "
                f"{len(quantities)}")
        return sum(
            ingredient.calories * quantity
            for quantity, ingredient in zip(quantities, self.ingredients)
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
