#!/usr/bin/env python3
import doctest
import string

from utils import get_current_directory


def solve(_input=None):
    """
    >>> solve()
    9390
    """
    if _input is None:
        _input = get_current_directory(__file__)\
            .joinpath("part_a_input.txt")\
            .read_text()
    return len(Polymer(_input.strip()).simplify())


class Polymer(str):
    def simplify(self):
        return self.simplify_intelligent()

    def simplify_replace(self):
        """
        >>> Polymer('aA').simplify_replace()
        ''
        >>> Polymer('abBA').simplify_replace()
        ''
        >>> Polymer('abAB').simplify_replace()
        'abAB'
        >>> Polymer('aabAAB').simplify_replace()
        'aabAAB'
        >>> Polymer('dabAcCaCBAcCcaDA').simplify_replace()
        'dabCBAcaDA'
        >>> Polymer('wNnJZzjXxlLrbBaARdaADWfmMZzFDdKCcQTCaActfEeFqkKkpxXdPpDPEejbBCcuqQUFfQqJMmNnL').simplify_replace()
        'L'
        >>> Polymer('abcdefFEDCBA').simplify_replace()
        ''
        >>> Polymer('abcdefFEDCBA').simplify_replace()
        ''
        >>> Polymer('abcdefGgHhIIKJJjjkiiFEDCBA').simplify_replace()
        ''
        """
        previous, simplified = self, self.simplify_replace_once()
        while previous != simplified:
            previous, simplified = simplified, simplified.simplify_replace_once()

        return simplified

    SIMPLIFICATION_REPLACEMENTS = [
        f"{lower}{lower.upper()}"
        for lower in string.ascii_lowercase
    ] + [
        f"{lower.upper()}{lower}"
        for lower in string.ascii_lowercase
    ]

    def simplify_replace_once(self):
        simplified = self
        for replacement in self.SIMPLIFICATION_REPLACEMENTS:
            simplified = simplified.replace(replacement, '')
        return type(self)(simplified)

    def simplify_intelligent(self):
        """
        >>> Polymer('aA').simplify_intelligent()
        ''
        >>> Polymer('abBA').simplify_intelligent()
        ''
        >>> Polymer('abAB').simplify_intelligent()
        'abAB'
        >>> Polymer('aabAAB').simplify_intelligent()
        'aabAAB'
        >>> Polymer('dabAcCaCBAcCcaDA').simplify_intelligent()
        'dabCBAcaDA'
        >>> Polymer('wNnJZzjXxlLrbBaARdaADWfmMZzFDdKCcQTCaActfEeFqkKkpxXdPpDPEejbBCcuqQUFfQqJMmNnL').simplify_intelligent()
        'L'
        >>> Polymer('abcdefFEDCBA').simplify_intelligent()
        ''
        >>> Polymer('abcdefFEDCBA').simplify_intelligent()
        ''
        >>> Polymer('abcdefGgHhIIKJJjjkiiFEDCBA').simplify_intelligent()
        ''
        """
        result = ''
        for _, result in self.simplify_intelligent_all_steps():
            pass

        return result

    def simplify_intelligent_all_steps(self):
        """
        >>> [_result for _, _result in Polymer('dabAcCaCBAcCcaDA').simplify_intelligent_all_steps()]
        ['', 'd', 'da', 'dab', 'dabA', 'dabAc', 'dabA', 'dab', 'dabC', \
'dabCB', 'dabCBA', 'dabCBAc', 'dabCBA', 'dabCBAc', 'dabCBAca', 'dabCBAcaD', \
'dabCBAcaDA']
        """
        result = ''
        position = 0
        length = len(self)
        yield position, result
        while position < length:
            position, result = self.simplify_intelligent_step(position, result)
            yield position, result

    def simplify_intelligent_step(self, position, result):
        """
        >>> Polymer('aA').simplify_intelligent_step(0, '')
        (1, 'a')
        >>> Polymer('aA').simplify_intelligent_step(1, 'a')
        (2, '')
        >>> Polymer('abBA').simplify_intelligent_step(0, '')
        (1, 'a')
        >>> Polymer('abBA').simplify_intelligent_step(1, 'a')
        (2, 'ab')
        >>> Polymer('abBA').simplify_intelligent_step(2, 'ab')
        (3, 'a')
        >>> Polymer('abBA').simplify_intelligent_step(3, 'a')
        (4, '')
        """
        if not result:
            result += self[position]
        elif self.should_react(result[-1], self[position]):
            result = result[:-1]
        else:
            result += self[position]
        position += 1
        return position, result

    def simplify_naive(self):
        """
        >>> Polymer('aA').simplify_naive()
        ''
        >>> Polymer('abBA').simplify_naive()
        ''
        >>> Polymer('abAB').simplify_naive()
        'abAB'
        >>> Polymer('aabAAB').simplify_naive()
        'aabAAB'
        >>> Polymer('dabAcCaCBAcCcaDA').simplify_naive()
        'dabCBAcaDA'
        >>> Polymer('wNnJZzjXxlLrbBaARdaADWfmMZzFDdKCcQTCaActfEeFqkKkpxXdPpDPEejbBCcuqQUFfQqJMmNnL').simplify_naive()
        'L'
        >>> Polymer('abcdefFEDCBA').simplify_naive()
        ''
        >>> Polymer('abcdefGgHhIIKJJjjkiiFEDCBA').simplify_naive()
        ''
        """
        previous, simplified = self, self.simplify_naive_once()
        while simplified != previous:
            previous, simplified = simplified, simplified.simplify_naive_once()

        return simplified

    def simplify_naive_once(self):
        """
        >>> Polymer('aA').simplify_naive_once()
        ''
        >>> Polymer('abBA').simplify_naive_once()
        'aA'
        >>> Polymer('abAB').simplify_naive_once()
        'abAB'
        >>> Polymer('aabAAB').simplify_naive_once()
        'aabAAB'
        >>> Polymer('dabAcCaCBAcCcaDA').simplify_naive_once()
        'dabAaCBAcCcaDA'
        """
        for index, (previous, char) \
                in enumerate(zip(self, self[1:])):
            if self.should_react(previous, char):
                return type(self)(self.react_at(index))

        return self

    def react_at(self, index):
        """
        >>> Polymer('aA').react_at(0)
        ''
        """
        return self[:index] + self[index + 2:]

    def should_react(self, lhs, rhs):
        """
        >>> Polymer('').should_react('a', 'A')
        True
        >>> Polymer('').should_react('A', 'a')
        True
        >>> Polymer('').should_react('a', 'a')
        False
        >>> Polymer('').should_react('A', 'A')
        False
        """
        return lhs.lower() == rhs.lower() and lhs != rhs


if __name__ == '__main__':
    if doctest.testmod().failed:
        print("Tests failed")
    else:
        print("Tests passed")
    print("Solution:", solve())
