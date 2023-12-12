from typing import Dict, Optional, Tuple, Callable, Union, Any, List, Iterable

import click

from .math_utils import min_and_max_tuples
from .point import Point2D


__all__ = [
    'make_and_show_string_table',
    'make_string_table',
    'show_string_table',
]


def make_and_show_string_table(
    points: Iterable[Point2D],
    get_value: Callable[[Point2D], Any],
    boundaries: Optional[Tuple[Point2D, Point2D]] = None,
    justify_func: Callable = str.rjust,
    auto_separator: Union[str, bool] = True,
) -> str:
    """
    >>> def _make(items: List[List[Any]]) -> Dict[Point2D, Any]:
    ...     return {Point2D(x, y): item for y, line in enumerate(items) for x, item in enumerate(line)}
    >>> print(make_and_show_string_table(_make([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), lambda point: point.x + point.y))
    012
    123
    234
    """
    if boundaries is None:
        boundaries = min_and_max_tuples(points)
    return show_string_table(
        make_string_table(points, get_value=get_value, boundaries=boundaries),
        boundaries=boundaries,
        justify_func=justify_func,
        auto_separator=auto_separator,
    )


def make_string_table(points: Iterable[Point2D], get_value: Callable[[Point2D], Any], boundaries: Optional[Tuple[Point2D, Point2D]] = None) -> Dict[Point2D, str]:
    """
    >>> def _make(items: List[List[Any]]) -> Dict[Point2D, Any]:
    ...     return {Point2D(x, y): item for y, line in enumerate(items) for x, item in enumerate(line)}
    >>> print(show_string_table(make_string_table(_make([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), lambda point: point.x + point.y)))
    012
    123
    234
    """
    if boundaries is None:
        boundaries = min_and_max_tuples(points)
    (min_x, min_y), (max_x, max_y) = boundaries
    return {
        point: str(get_value(point))
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        for point in [Point2D(x, y)]
    }


def show_string_table(table: Dict[Point2D, str], boundaries: Optional[Tuple[Point2D, Point2D]] = None, justify_func: Callable = str.rjust, auto_separator: Union[str, bool] = True) -> str:
    """
    >>> def _make(items: List[List[Any]]) -> Dict[Point2D, str]:
    ...     return {Point2D(x, y): str(item) for y, line in enumerate(items) for x, item in enumerate(line)}
    >>> print(show_string_table(_make([[1, 2, 3], [4, 5, 6], [7, 8, 9]])))
    123
    456
    789
    >>> print(show_string_table(_make([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), auto_separator=False))
    1 2 3
    4 5 6
    7 8 9
    >>> print(show_string_table(_make([[10, 2, 3], [4, 5, 6], [7, 8, 9]])))
    10  2  3
     4  5  6
     7  8  9
    >>> print(show_string_table(_make([[10, 2, 3], [4, 5, 6], [7, 8, 9]]), justify_func=str.ljust))
    10 2  3
    4  5  6
    7  8  9
    """
    if not table:
        return ""
    if boundaries is None:
        boundaries = min_and_max_tuples(table)
    (min_x, min_y), (max_x, max_y) = boundaries
    max_length = max(map(len, map(lambda text: click.unstyle(text), table.values()))) if table else 0

    def justify_styled(text: str) -> str:
        unstyled = click.unstyle(text)
        justified = justify_func(unstyled, max_length)
        if text != unstyled:
            styled = justified.replace(unstyled, text)
        else:
            styled = justified
        return styled

    if isinstance(auto_separator, bool):
        if auto_separator:
            separator = " " if max_length > 1 else ""
        else:
            separator = " "
    else:
        separator = auto_separator
    return "\n".join(
        separator.join(
            justify_styled(table.get(point, ""))
            for x in range(min_x, max_x + 1)
            for point in [Point2D(x, y)]
        )
        for y in range(min_y, max_y + 1)
    )
