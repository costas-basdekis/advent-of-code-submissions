#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Union

from aox.challenge import Debugger
from utils import BaseChallenge


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        1809
        """
        viewer = ForestViewer.from_forest_text(_input).update_visible()
        debugger.report(viewer)
        return viewer.get_visible_count()


@dataclass
class ForestViewer:
    forest: "Forest"
    visible_trees: [[bool]]

    @classmethod
    def from_forest_text(cls, forest_text: str) -> "ForestViewer":
        return cls.from_forest(Forest.from_forest_text(forest_text))

    @classmethod
    def from_forest(cls, forest: "Forest") -> "ForestViewer":
        return cls(
            forest=forest,
            visible_trees=[
                [False] * len(row)
                for row in forest.trees
            ],
        )

    def get_visible_count(self) -> int:
        """
        >>> ForestViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... ).update_visible().get_visible_count()
        21
        """
        return sum(
            1
            for row in self.visible_trees
            for visible in row
            if visible
        )

    def update_visible(self) -> "ForestViewer":
        """
        >>> print(ForestViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... ).update_visible())
        30373
        255 2
        65 32
        3 5 9
        35390
        """
        visible_from_top = self.get_visible_from_top()
        visible_from_bottom = self.get_visible_from_bottom()
        visible_from_left = self.get_visible_from_left()
        visible_from_right = self.get_visible_from_right()

        for row_index in range(self.forest.height):
            for column_index in range(self.forest.width):
                self.visible_trees[row_index][column_index] = (
                    visible_from_top[row_index][column_index]
                    or visible_from_bottom[row_index][column_index]
                    or visible_from_left[row_index][column_index]
                    or visible_from_right[row_index][column_index]
                )

        return self

    def get_visible_from_top(self) -> [[bool]]:
        """
        >>> ForestViewer.from_forest_text("0\\n2\\n0\\n0")\\
        ...     .get_visible_from_top()
        [[True], [True], [False], [False]]
        >>> ForestViewer.from_forest_text("0\\n2\\n0\\n1")\\
        ...     .get_visible_from_top()
        [[True], [True], [False], [False]]
        >>> ForestViewer.from_forest_text("0\\n2\\n1\\n1")\\
        ...     .get_visible_from_top()
        [[True], [True], [False], [False]]
        >>> ForestViewer.from_forest_text("0\\n2\\n1\\n3\\n2")\\
        ...     .get_visible_from_top()
        [[True], [True], [False], [True], [False]]
        """
        return self.get_visible_from_side_horizontal(False)

    def get_visible_from_bottom(self) -> [[bool]]:
        return self.get_visible_from_side_horizontal(True)

    def get_visible_from_side_horizontal(self, reverse: bool) -> [[bool]]:
        min_visible_heights_from_side = [-1] * self.forest.width
        visible_from_side: [[bool]] = [
            [False] * self.forest.width
            for _ in range(self.forest.height)
        ]
        row_indexes = range(self.forest.height)
        if reverse:
            row_indexes = reversed(row_indexes)
        for row_index in row_indexes:
            for column_index in range(self.forest.width):
                if (height := self.forest.trees[row_index][column_index]) \
                        > min_visible_heights_from_side[column_index]:
                    visible_from_side[row_index][column_index] = True
                    min_visible_heights_from_side[column_index] = height

        return visible_from_side

    def get_visible_from_left(self) -> [[bool]]:
        return self.get_visible_from_side_vertical(False)

    def get_visible_from_right(self) -> [[bool]]:
        return self.get_visible_from_side_vertical(True)

    def get_visible_from_side_vertical(self, reverse: bool) -> [[bool]]:
        min_visible_heights_from_side = [-1] * self.forest.height
        visible_from_side: [[bool]] = [
            [False] * self.forest.width
            for _ in range(self.forest.height)
        ]
        column_indexes = range(self.forest.width)
        if reverse:
            column_indexes = reversed(column_indexes)
        for column_index in column_indexes:
            for row_index in range(self.forest.height):
                if (height := self.forest.trees[row_index][column_index]) \
                        > min_visible_heights_from_side[row_index]:
                    visible_from_side[row_index][column_index] = True
                    min_visible_heights_from_side[row_index] = height

        return visible_from_side

    def __str__(self) -> str:
        """
        >>> print(ForestViewer.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... ))





        """
        return "\n".join(
            "".join(
                str(tree) if visible else " "
                for tree, visible in zip(tree_row, visible_row)
            )
            for tree_row, visible_row
            in zip(self.forest.trees, self.visible_trees)
        )


@dataclass
class Forest:
    trees: [[int]]

    @classmethod
    def from_forest_text(cls, forest_text: str) -> "Forest":
        """
        >>> Forest.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... )
        Forest(trees=[[3, 0, 3, 7, 3], [2, 5, 5, 1, 2], [6, 5, 3, 3, 2],
            [3, 3, 5, 4, 9], [3, 5, 3, 9, 0]])
        """
        return cls(
            trees=[
                list(map(int, line))
                for line in forest_text.strip().splitlines()
            ],
        )

    def __str__(self) -> str:
        """
        >>> print(Forest.from_forest_text(
        ...     "30373\\n"
        ...     "25512\\n"
        ...     "65332\\n"
        ...     "33549\\n"
        ...     "35390\\n"
        ... ))
        30373
        25512
        65332
        33549
        35390
        """
        return "\n".join("".join(map(str, row)) for row in self.trees)

    @property
    def is_square(self) -> bool:
        return self.width == self.height

    @property
    def width(self) -> int:
        return len(self.trees[0])

    @property
    def height(self) -> int:
        return len(self.trees)


Challenge.main()
challenge = Challenge()
