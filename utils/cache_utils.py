from functools import wraps
from typing import Callable, Any, Optional, TypeVar

__all__ = ["cached"]

Return = TypeVar('Return')
Func = Callable[..., Return]


def cached(
    func: Optional[Func] = None,
    *,
    key: Optional[Callable[..., Any]] = None,
) -> Callable:
    """
    >>> @cached
    ... def f1(a: int) -> int:
    ...     print(a)
    ...     return a * 2
    >>> f1(1)
    1
    2
    >>> f1(1)
    2
    >>> f1(2)
    2
    4
    >>> f1(1), f1(2)
    (2, 4)
    >>> @cached
    ... def f2(a: int, b: int, c: int) -> int:
    ...     print(a, b, c)
    ...     return a + b + c
    >>> f2(1, 2, 3)
    1 2 3
    6
    >>> f2(1, 2, 3)
    6
    >>> f2(1, 2, 4)
    1 2 4
    7
    >>> f2(1, 2, 3), f2(1, 2, 4)
    (6, 7)
    >>> @cached(key=lambda a, b, c: a + b + c)
    ... def f3(a: int, b: int, c: int) -> int:
    ...     print(a, b, c)
    ...     return a + b + c
    >>> f3(1, 2, 3)
    1 2 3
    6
    >>> f3(1, 2, 3)
    6
    >>> f3(1, 3, 2)
    6
    >>> f3(1, 2, 3), f3(1, 3, 2)
    (6, 6)
    """
    def decorator(_func: Func) -> Func:
        __cache__ = _func.__cache__ = {}

        @wraps(_func)
        def decorated(*args, **kwargs) -> Return:
            if key is None:
                call_key = (args, tuple(sorted(kwargs)))
            else:
                call_key = key(*args, **kwargs)

            if call_key not in __cache__:
                __cache__[call_key] = _func(*args, **kwargs)

            return __cache__[call_key]

        return decorated

    if func is not None:
        return decorator(func)
    else:
        return decorator
