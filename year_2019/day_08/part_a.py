#!/usr/bin/env python3
import itertools

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        1340
        """
        layers = split_text_into_layers(_input, 25, 6)
        layer_digit_counts = [
            {
                digit: len(list(digits))
                for digit, digits in itertools.groupby(sorted(layer))
            }
            for layer in layers
        ]
        min_layer_on_0_digit_count = \
            min(layer_digit_counts, key=lambda digit_counts: digit_counts['0'])

        return min_layer_on_0_digit_count['1'] * min_layer_on_0_digit_count['2']


def split_text_into_layers(text, width, height):
    """
    >>> split_text_into_layers('123456789012', 3, 2)
    ['123456', '789012']
    >>> split_text_into_layers('123456789012', 3, 1)
    ['123', '456', '789', '012']
    >>> split_text_into_layers('12345678901', 3, 1)
    Traceback (most recent call last):
    ...
    Exception: Text of length 11 can't be for an image of 3 * 1
    >>> split_text_into_layers('1234567890123', 3, 1)
    Traceback (most recent call last):
    ...
    Exception: Text of length 13 can't be for an image of 3 * 1
    """
    text = text.strip()
    text_length = len(text)
    layer_length = (width * height)
    if text_length % layer_length:
        raise Exception(
            f"Text of length {text_length} can't be for an image of "
            f"{width} * {height}")

    return [
        text[layer_start:layer_start + layer_length]
        for layer_start in range(0, text_length, layer_length)
    ]


challenge = Challenge()
challenge.main()
