from functools import wraps
from typing import TypeVar, Callable

__all__ = ["CallableT", "cached_classmethod"]


CallableT = TypeVar("CallableT", bound=Callable)


def cached_classmethod(func: CallableT) -> CallableT:
    default_context = {
        "value": None,
        "is_value_set": False,
    }
    context_by_class = {}
    @wraps(func)
    def decorated(cls, *args, **kwargs):
        if cls not in context_by_class:
            context_by_class[cls] = dict(default_context)
        context = context_by_class[cls]
        if not context["is_value_set"]:
            context["value"] = func(cls, *args, **kwargs)
            context["is_value_set"] = True
        return context["value"]

    return decorated
