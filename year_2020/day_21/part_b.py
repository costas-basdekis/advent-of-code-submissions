#!/usr/bin/env python3
import utils
from year_2020.day_21 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        'jzzjz,bxkrd,pllzxb,gjddl,xfqnss,dzkb,vspv,dxvsp'
        """
        recipe_set = RecipeSetExtended.from_recipes_text(_input)
        return recipe_set.get_canonical_dangerous_ingredient_list()


class RecipeSetExtended(part_a.RecipeSet):
    def get_canonical_dangerous_ingredient_list(self):
        """
        >>> RecipeSetExtended.from_recipes_text(
        ...     "mxmxvkd kfcds sqjhc nhms (contains dairy, fish)\\n"
        ...     "trh fvjkl sbzzf mxmxvkd (contains dairy)\\n"
        ...     "sqjhc fvjkl (contains soy)\\n"
        ...     "sqjhc mxmxvkd sbzzf (contains fish)\\n"
        ... ).get_canonical_dangerous_ingredient_list()
        'mxmxvkd,sqjhc,fvjkl'
        """
        ingredients = self.get_all_ingredients()
        allergens_by_ingredient = self\
            .get_allergens_by_ingredient(ingredients)
        allergen_by_allergenic_ingredient = \
            self.get_definitive_allergen_by_ingredient(allergens_by_ingredient)
        return ",".join(sorted(
            allergen_by_allergenic_ingredient,
            key=allergen_by_allergenic_ingredient.__getitem__))

    def get_definitive_allergen_by_ingredient(self, allergens_by_ingredient):
        possible_allergens_by_ingredient = {
            ingredient: allergens
            for ingredient, allergens
            in allergens_by_ingredient.items()
            if allergens
        }
        allergen_by_allergenic_ingredient = {}
        remaining_possible_allergens_by_ingredient =\
            dict(possible_allergens_by_ingredient)
        while remaining_possible_allergens_by_ingredient:
            single_allergen_ingredients = {
                ingredient
                for ingredient, possible_allergens
                in remaining_possible_allergens_by_ingredient.items()
                if len(possible_allergens) == 1
            }
            if not single_allergen_ingredients:
                raise Exception(
                    f"Could not find ingredients with a single allergen: "
                    f"{remaining_possible_allergens_by_ingredient}")
            ingredient = next(iter(single_allergen_ingredients))
            allergen, = remaining_possible_allergens_by_ingredient\
                .pop(ingredient)
            for possible_allergens\
                    in remaining_possible_allergens_by_ingredient.values():
                possible_allergens -= {allergen}
            allergen_by_allergenic_ingredient[ingredient] = allergen
        return allergen_by_allergenic_ingredient


Challenge.main()
challenge = Challenge()
