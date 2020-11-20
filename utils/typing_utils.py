import sys
from typing import TypeVar, Type, ForwardRef, get_args, Generic, Union, \
    Optional, Dict, Any
# noinspection PyUnresolvedReferences,PyProtectedMember
from typing import _type_check

from utils.collections_utils import KeyedDefaultDict

__all__ = [
    'Cls', 'Self',
    'get_type_argument_class',
    'resolve_type_argument',
    'get_type_argument',
    'get_type_argument_index',
]


def create_named_self(bound):
    """
    >>> create_named_self('SomeClass')
    ~Self
    >>> class SomeClass: pass
    >>> create_named_self(SomeClass)
    ~Self
    >>> create_named_self(SomeClass) != create_named_self(SomeClass)
    True
    >>> Self['SomeClass']
    ~Self
    >>> Self[SomeClass]
    ~Self
    >>> Self[SomeClass] is Self[SomeClass]
    True
    """
    # noinspection PyTypeHints
    return TypeVar('Self', bound=bound)


def create_named_cls(bound):
    """
    >>> create_named_cls('SomeClass')
    typing.Type[~Self]
    >>> class SomeClass: pass
    >>> create_named_cls(SomeClass)
    typing.Type[~Self]
    >>> create_named_cls(SomeClass) != create_named_self(SomeClass)
    True
    >>> Cls['SomeClass']
    typing.Type[~Self]
    >>> Cls[SomeClass]
    typing.Type[~Self]
    >>> Cls[SomeClass] is Cls[SomeClass]
    True
    """
    return Type[Self[bound]]


Self = KeyedDefaultDict(create_named_self)
Cls = KeyedDefaultDict(create_named_cls)


TypeArgument = Union[TypeVar, ForwardRef, Type]


def get_type_argument_class(
        cls: Type['Generic'], argument_type_var: TypeVar,
        class_globals: Optional[Dict[str, Any]] = None) -> Type:
    """
    Get the subclassed type argument, eg for `T2` in `B(A[E, F, G])` it's F,
    where `A(Generic[T1, T2, T3])`, and for `A` it's `D` where
    `T2 = TypeVar('T2', bound=D)`.

    >>> # noinspection PyTypeChecker
    >>> T1 = TypeVar('T1', bound='B')
    >>> class B: pass
    >>> _class_globals: Dict[str, Any] = {'B': B}
    >>> class A(Generic[T1]): pass
    >>> get_type_argument_class(A, T1, _class_globals)
    <class '....B'>
    >>> # noinspection PyTypeChecker
    >>> T2 = TypeVar('T2', bound='B')
    >>> class A(Generic[T1, T2]): pass
    >>> get_type_argument_class(A, T1, _class_globals)
    <class '....B'>
    >>> class A(Generic[T2, T1]): pass
    >>> get_type_argument_class(A, T1, _class_globals)
    <class '....B'>
    >>> class B1: pass
    >>> class B2: pass
    >>> _class_globals.update({'B1': B1, 'B2': B2})
    >>> class A(Generic[T1, T2]): pass
    >>> class C(A[B1, B2]): pass
    >>> get_type_argument_class(C, T1, _class_globals)
    <class '....B1'>
    >>> class D(C): pass
    >>> get_type_argument_class(D, T1, _class_globals)
    <class '....B1'>
    >>> class A(Generic[T2, T1]): pass
    >>> class C(A[B1, B2]): pass
    >>> get_type_argument_class(C, T1, _class_globals)
    <class '....B2'>
    >>> class D(C): pass
    >>> get_type_argument_class(D, T1, _class_globals)
    <class '....B2'>
    """
    type_or_var = get_type_argument(cls, argument_type_var)
    return resolve_type_argument(cls, type_or_var, class_globals=class_globals)


def resolve_type_argument(cls: Type['Generic'], type_or_var: TypeArgument,
                          class_globals: Optional[Dict[str, Any]] = None) \
        -> Type:
    """
    Convert a `TypeVar` or a `ForwardRef` to their actual type.

    >>> # noinspection PyTypeChecker
    >>> T1 = TypeVar('T1', bound='B')
    >>> class B: pass
    >>> _class_globals: Dict[str, Any] = {'B': B}
    >>> class A(Generic[T1]): pass
    >>> resolve_type_argument(A, T1, _class_globals)
    <class '....B'>
    >>> class B1: pass
    >>> class B2: pass
    >>> _class_globals.update({'B1': B1, 'B2': B2})
    >>> resolve_type_argument(A, B1, _class_globals)
    <class '....B1'>
    """
    if isinstance(type_or_var, TypeVar):
        type_var: TypeVar = type_or_var
        type_or_ref = type_var.__bound__
    else:
        type_or_ref = type_or_var
    if isinstance(type_or_ref, ForwardRef):
        ref: ForwardRef = type_or_ref
        if class_globals is None:
            class_module = sys.modules[cls.__module__]
            class_globals = class_module.__dict__
        # noinspection PyProtectedMember,PyArgumentList
        _type = ref._evaluate(class_globals, None, set())
    else:
        _type = type_or_ref
    if not isinstance(_type, type):
        raise Exception(
            f"Could not get instruction class for {cls.__name__}, got "
            f"{_type}")

    return _type


def get_type_argument(cls: Type['Generic'], type_var: TypeVar) -> TypeArgument:
    """
    Get the raw type argument, eg for `T2` in `B(A[E, F, G])` it's F,
    where `A(Generic[T1, T2, T3])`, and for `A` it's `T2`.

    >>> # noinspection PyTypeChecker
    >>> T1 = TypeVar('T1', bound='B')
    >>> class A(Generic[T1]): pass
    >>> get_type_argument(A, T1)
    ~T1
    >>> # noinspection PyTypeChecker
    >>> T2 = TypeVar('T2', bound='B')
    >>> class A(Generic[T1, T2]): pass
    >>> get_type_argument(A, T1)
    ~T1
    >>> class A(Generic[T2, T1]): pass
    >>> get_type_argument(A, T1)
    ~T1
    >>> class B1: pass
    >>> class B2: pass
    >>> class A(Generic[T1, T2]): pass
    >>> class C(A[B1, B2]): pass
    >>> get_type_argument(C, T1)
    <class '....B1'>
    >>> class D(C): pass
    >>> get_type_argument(D, T1)
    <class '....B1'>
    >>> class A(Generic[T2, T1]): pass
    >>> class C(A[B1, B2]): pass
    >>> get_type_argument(C, T1)
    <class '....B2'>
    >>> class D(C): pass
    >>> get_type_argument(D, T1)
    <class '....B2'>
    """
    index = get_type_argument_index(cls, type_var)
    arguments = get_args(cls.__orig_bases__[0])
    return arguments[index]


def get_type_argument_index(cls: Type['Generic'], type_var: TypeVar) -> int:
    """
    Find the index of a type argument, eg `T2` in `A(Generic[T1, T2, T3])` has
    index 1.

    >>> # noinspection PyTypeChecker
    >>> T1 = TypeVar('T1', bound='B')
    >>> class A(Generic[T1]): pass
    >>> get_type_argument_index(A, T1)
    0
    >>> # noinspection PyTypeChecker
    >>> T2 = TypeVar('T2', bound='B')
    >>> class A(Generic[T1, T2]): pass
    >>> get_type_argument_index(A, T1)
    0
    >>> class A(Generic[T2, T1]): pass
    >>> get_type_argument_index(A, T1)
    1
    >>> class B1: pass
    >>> class B2: pass
    >>> class A(Generic[T1, T2]): pass
    >>> class C(A[B1, B2]): pass
    >>> get_type_argument_index(C, T1)
    0
    >>> class D(C): pass
    >>> get_type_argument_index(D, T1)
    0
    >>> class A(Generic[T2, T1]): pass
    >>> class C(A[B1, B2]): pass
    >>> get_type_argument_index(C, T1)
    1
    >>> class D(C): pass
    >>> get_type_argument_index(D, T1)
    1
    """
    for parent in cls.mro():
        if not hasattr(parent, '__orig_bases__'):
            continue
        type_vars = get_args(parent.__orig_bases__[0])
        if type_var in type_vars:
            return type_vars.index(type_var)

    raise Exception(
        f"Cannot find type argument {type_var.__name__} in {cls.__name__}")
