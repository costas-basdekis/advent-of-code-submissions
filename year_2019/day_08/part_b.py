#!/usr/bin/env python3
from copy import deepcopy

import utils

from year_2019.day_08.part_a import split_text_into_layers


class Challenge(utils.BaseChallenge):
    def solve(self, _input):
        """
        >>> Challenge().default_solve()
        1    1111   11 1  1  11
        1    1       1 1 1  1  1
        1    111     1 11   1
        1    1       1 1 1  1
        1    1    1  1 1 1  1  1
        1111 1111  11  1  1  11
        """
        print(serialise_image(parse_image(_input, 25, 6)))


def serialise_image(image):
    """
    >>> serialise_image([['0', '1'], ['1', '0']])
    ' 1\\n1'
    """
    return "\n".join("".join(line).replace('0', ' ').rstrip() for line in image)


def parse_image(text, width, height):
    """
    >>> parse_image('0222112222120000', 2, 2)
    [['0', '1'], ['1', '0']]
    """
    layer_texts = split_text_into_layers(text, width, height)
    layers = [
        parse_layer(layer_text, width, height)
        for layer_text in layer_texts
    ]
    composite = composite_layers(layers)

    return composite


COLOR_TRANSPARENT = '2'


def composite_layers(layers):
    """
    >>> composite_layers([[['1']]])
    [['1']]
    >>> composite_layers([[['2']], [['1']]])
    [['1']]
    >>> composite_layers([[['0']], [['1']]])
    [['0']]
    """
    result = deepcopy(layers[-1])

    for layer in reversed(layers):
        for y, line in enumerate(layer):
            for x, pixel in enumerate(line):
                if pixel != COLOR_TRANSPARENT:
                    result[y][x] = pixel

    return result


def parse_layer(text, width, height):
    """
    >>> parse_layer('123456', 3, 2)
    [['1', '2', '3'], ['4', '5', '6']]
    >>> parse_layer('123456', 2, 3)
    [['1', '2'], ['3', '4'], ['5', '6']]
    """
    return [
        list(text[layer_start:layer_start + width])
        for layer_start in range(0, width * height, width)
    ]


challenge = Challenge()
challenge.main()
