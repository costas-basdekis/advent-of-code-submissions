from typing import Dict, Type, Optional

from utils.typing_utils import Cls, Self

__all__ = ['PolymorphicParser']


class PolymorphicParser:
    name: str = NotImplemented

    sub_classes: Dict[str, Type['PolymorphicParser']]

    def __init_subclass__(cls, **kwargs):
        """
        >>> # noinspection PyAbstractClass
        >>> class A1(PolymorphicParser, root=True): pass
        >>> # noinspection PyAbstractClass
        >>> @A1.register
        ... class B1(A1): name = 'b'
        >>> # noinspection PyAbstractClass
        >>> class A2(PolymorphicParser, root=True): pass
        >>> # noinspection PyAbstractClass
        >>> @A2.register
        ... class C1(A2): name = 'c'
        >>> A1.sub_classes
        {'b': <class 'utils.polymorphic.B1'>}
        >>> A2.sub_classes
        {'c': <class 'utils.polymorphic.C1'>}
        >>> A1.sub_classes is not A2.sub_classes
        True
        >>> B1.sub_classes is A1.sub_classes
        True
        >>> C1.sub_classes is A2.sub_classes
        True
        """
        if kwargs.get('root', False):
            cls.sub_classes = {}

    @classmethod
    def register(cls, sub_class: Type['PolymorphicParser'],
                 override: bool = False) -> Type['PolymorphicParser']:
        """
        >>> # noinspection PyAbstractClass
        >>> class A(PolymorphicParser, root=True): pass
        >>> # noinspection PyAbstractClass
        >>> @A.register
        ... class B(A): pass
        Traceback (most recent call last):
        ...
        Exception: Tried to register B, but it hadn't set the name
        >>> # noinspection PyAbstractClass
        >>> @A.register
        ... class B1(A): name = 'b'
        >>> A.sub_classes
        {'b': <class 'utils.polymorphic.B1'>}
        >>> # noinspection PyAbstractClass
        >>> @A.register
        ... class B2(A): name = 'b'
        Traceback (most recent call last):
        ...
        Exception: Tried to register B2 under b, but B1 was already registered
        """
        name = sub_class.name
        class_name = sub_class.__name__
        if name is NotImplemented:
            raise Exception(
                f"Tried to register {class_name}, but it hadn't set the name")
        if not override:
            existing_instruction_class = cls.sub_classes.get(name)
            if existing_instruction_class:
                raise Exception(
                    f"Tried to register {class_name} under {name}, but "
                    f"{existing_instruction_class.__name__} was already "
                    f"registered")
        cls.sub_classes[name] = sub_class
        return sub_class

    @classmethod
    def override(cls, sub_class: Type['PolymorphicParser']
                 ) -> Type['PolymorphicParser']:
        """
        >>> # noinspection PyAbstractClass
        >>> class A(PolymorphicParser, root=True): pass
        >>> # noinspection PyAbstractClass
        >>> @A.register
        ... class B1(A): name = 'b'
        >>> # noinspection PyAbstractClass
        >>> @A.override
        ... class B2(A): name = 'b'
        """
        return cls.register(sub_class, override=True)

    @classmethod
    def parse(cls: Cls['PolymorphicParser'], text: str
              ) -> Self['PolymorphicParser']:
        """
        >>> from abc import ABC
        >>> class A(PolymorphicParser, ABC, root=True):
        ...     def __repr__(self):
        ...         return f"<{type(self).__name__}>"
        >>> @A.register
        ... class B1(A):
        ...     name = 'b1'
        ...     @classmethod
        ...     def try_parse(cls, _text):
        ...         if _text != 'b1':
        ...             return None
        ...         return cls()
        >>> @A.register
        ... class B2(A):
        ...     name = 'b2'
        ...     @classmethod
        ...     def try_parse(cls, _text):
        ...         if _text != 'b2':
        ...             return None
        ...         return cls()
        >>> A.parse('b1')
        <B1>
        """
        for instruction_class in cls.sub_classes.values():
            if not issubclass(instruction_class, cls):
                continue
            instruction = instruction_class.try_parse(text)
            if instruction:
                return instruction

        raise Exception(f"Could not parse '{text}'")

    @classmethod
    def try_parse(cls: Cls['PolymorphicParser'], text: str
                  ) -> Optional[Self['PolymorphicParser']]:
        raise NotImplementedError()
