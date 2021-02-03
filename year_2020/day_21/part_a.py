#!/usr/bin/env python3
import re
from collections import namedtuple

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2423
        """
        recipe_set = RecipeSet.from_recipes_text(_input)
        return recipe_set.get_non_allergenic_ingredient_occurrence_count()


class RecipeSet:
    @classmethod
    def from_recipes_text(cls, recipes_text):
        """
        >>> RecipeSet.from_recipes_text(
        ...     "mxmxvkd kfcds sqjhc nhms (contains dairy, fish)\\n"
        ...     "trh fvjkl sbzzf mxmxvkd (contains dairy)\\n"
        ...     "sqjhc fvjkl (contains soy)\\n"
        ...     "sqjhc mxmxvkd sbzzf (contains fish)\\n"
        ... ).recipes
        [Recipe(ingredients=('mxmxvkd', 'kfcds', 'sqjhc', 'nhms'),
            allergens=('dairy', 'fish')),
            Recipe(ingredients=('trh', 'fvjkl', 'sbzzf', 'mxmxvkd'),
                allergens=('dairy',)),
            Recipe(ingredients=('sqjhc', 'fvjkl'),
                allergens=('soy',)),
            Recipe(ingredients=('sqjhc', 'mxmxvkd', 'sbzzf'),
                allergens=('fish',))]
        """
        return cls(list(map(
            Recipe.from_recipe_text, recipes_text.splitlines())))

    def __init__(self, recipes):
        self.recipes = recipes

    def get_non_allergenic_ingredient_occurrence_count(self):
        """
        >>> RecipeSet.from_recipes_text(
        ...     "mxmxvkd kfcds sqjhc nhms (contains dairy, fish)\\n"
        ...     "trh fvjkl sbzzf mxmxvkd (contains dairy)\\n"
        ...     "sqjhc fvjkl (contains soy)\\n"
        ...     "sqjhc mxmxvkd sbzzf (contains fish)\\n"
        ... ).get_non_allergenic_ingredient_occurrence_count()
        5
        """
        ingredients = self.get_all_ingredients()
        allergens_by_ingredient = self.get_allergens_by_ingredient(ingredients)
        non_allergenic_ingredients = \
            self.get_non_allergenic_ingredients(allergens_by_ingredient)
        return sum(
            len(non_allergenic_ingredients & set(recipe.ingredients))
            for recipe in self.recipes
        )

    def get_non_allergenic_ingredients(self, allergens_by_ingredient):
        return {
            ingredient
            for ingredient, allergens in allergens_by_ingredient.items()
            if not allergens
        }

    def get_allergens_by_ingredient(self, ingredients):
        return {
            ingredient: ({
                allergen
                for recipe in self.recipes
                if ingredient in recipe.ingredients
                for allergen in recipe.allergens
            } - {
                allergen
                for recipe in self.recipes
                if ingredient not in recipe.ingredients
                for allergen in recipe.allergens
            })
            for ingredient in ingredients
        }

    def get_all_ingredients(self):
        return {
            ingredient
            for recipe in self.recipes
            for ingredient in recipe.ingredients
        }


class Recipe(namedtuple("Recipe", ("ingredients", "allergens"))):
    re_recipe = re.compile(r"^(\w+(?: \w+)*) \(contains (\w+(?:, \w+)*)\)$")

    @classmethod
    def from_recipe_text(cls, recipe_text):
        """
        >>> Recipe.from_recipe_text(
        ...     "mxmxvkd kfcds sqjhc nhms (contains dairy, fish)")
        Recipe(ingredients=('mxmxvkd', 'kfcds', 'sqjhc', 'nhms'),
            allergens=('dairy', 'fish'))
        >>> Recipe.from_recipe_text(
        ...     "sqjhc (contains soy)")
        Recipe(ingredients=('sqjhc',), allergens=('soy',))
        """
        ingredients_text, allergens_text = \
            cls.re_recipe.match(recipe_text).groups()
        ingredients = tuple(ingredients_text.split(' '))
        allergens = tuple(allergens_text.split(', '))

        return cls(ingredients, allergens)


Challenge.main()
challenge = Challenge()
