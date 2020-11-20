__all__ = ['KeyedDefaultDict']


class KeyedDefaultDict(dict):
    def __init__(self, default_factory, **kwargs):
        self.default_factory = default_factory
        super().__init__(kwargs)

    def __missing__(self, key):
        """
        >>> _dict = KeyedDefaultDict(lambda _key: _key)
        >>> _dict[5]
        5
        >>> _dict
        {5: 5}
        >>> _dict = KeyedDefaultDict(lambda _key: [_key])
        >>> _dict[5]
        [5]
        >>> _dict
        {5: [5]}
        >>> _dict[6] is _dict[6]
        True
        >>> _dict[7] = 10
        >>> _dict[7]
        10
        >>> _dict
        {5: [5], 6: [6], 7: 10}
        """
        value = self[key] = self.default_factory(key)
        return value
