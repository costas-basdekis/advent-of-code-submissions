#!/usr/bin/env python3
import itertools
import re
from dataclasses import dataclass
from typing import Dict

import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        2508
        """
        _, total_severity = Firewall.from_firewall_text(_input).step_many()

        return total_severity


@dataclass
class Firewall:
    layers: Dict[int, int]
    scanners: Dict[int, int]
    packet: int

    re_layer = re.compile(r"^(\d+): (\d+)$")

    @classmethod
    def from_firewall_text(cls, firewall_text):
        """
        >>> Firewall.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... )
        Firewall(layers={0: 3, 1: 2, 4: 4, 6: 4},
            scanners={0: 0, 1: 0, 4: 0, 6: 0}, packet=-1)
        """
        layers = {
            int(depth_str): int(range_str)
            for depth_str, range_str in (
                cls.re_layer.match(line).groups()
                for line in firewall_text.strip().splitlines()
            )
        }
        scanners = {
            depth: 0
            for depth in layers
        }
        return cls(layers, scanners, -1)

    def step_many(self, count=None):
        """
        >>> firewall = Firewall.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... )
        >>> firewall.step_many()
        (True, 24)
        >>> print(firewall.show())
         0   1   2   3   4   5   6
        [ ] [ ] ... ... [ ] ... ( )
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        """
        if count is None:
            steps = itertools.count()
        else:
            steps = range(count)
        total_severity = 0
        for _ in steps:
            finished, severity = self.step()
            total_severity += severity
            if finished:
                break

        return self.has_finished(), total_severity

    def step(self):
        """
        >>> firewall = Firewall.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... )
        >>> firewall.step()
        (False, 0)
        >>> print(firewall.show())
         0   1   2   3   4   5   6
        ( ) [ ] ... ... [ ] ... [ ]
        [S] [S]         [S]     [S]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        """
        if self.has_finished():
            return True, 0

        self.packet += 1
        if self.scanners.get(self.packet) == 0:
            severity = self.packet * self.layers[self.packet]
        else:
            severity = 0

        for layer, _range in self.layers.items():
            layer_length = self.get_scanner_length(_range)
            self.scanners[layer] = (self.scanners[layer] + 1) % layer_length

        return self.has_finished(), severity

    def get_scanner_length(self, _range):
        """
        >>> Firewall.from_firewall_text('').get_scanner_length(1)
        1
        >>> Firewall.from_firewall_text('').get_scanner_length(2)
        2
        >>> Firewall.from_firewall_text('').get_scanner_length(3)
        4
        >>> Firewall.from_firewall_text('').get_scanner_length(4)
        6
        >>> Firewall.from_firewall_text('').get_scanner_length(5)
        8
        """
        if _range <= 2:
            return _range
        else:
            return _range * 2 - 2

    def has_finished(self):
        return self.packet >= max(self.layers)

    def get_scanner_position(self, layer):
        if layer not in self.scanners:
            return None

        scanner = self.scanners[layer]
        _range = self.layers[layer]

        return self.get_scanner_position_for_scanner(scanner, _range)

    def get_scanner_position_for_scanner(self, scanner, _range):
        """
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(0, 4)
        0
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(1, 4)
        1
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(2, 4)
        2
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(3, 4)
        3
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(4, 4)
        2
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(5, 4)
        1
        >>> Firewall.from_firewall_text('')\\
        ...     .get_scanner_position_for_scanner(6, 4)
        0
        """
        if scanner >= _range:
            scanner = _range - 1 - (scanner - _range + 1)

        return scanner

    def show(self):
        """
        >>> print(Firewall.from_firewall_text(
        ...     "0: 3\\n"
        ...     "1: 2\\n"
        ...     "4: 4\\n"
        ...     "6: 4\\n"
        ... ).show())
         0   1   2   3   4   5   6
        [S] [S] ... ... [S] ... [S]
        [ ] [ ]         [ ]     [ ]
        [ ]             [ ]     [ ]
                        [ ]     [ ]
        """
        max_layer = max(self.layers)
        max_range = max(self.layers.values())
        return "\n".join(map(str.rstrip, [
            " ".join(
                f" {layer} "
                for layer in range(max_layer + 1)
            ),
        ] + [
            " ".join(
                (
                    "({})"
                    if distance == 0 and self.packet == layer else
                    (
                        "[{}]"
                        if distance < self.layers[layer] else
                        " {} "
                    )
                    if layer in self.scanners else
                    (
                        ".{}."
                        if distance == 0 else
                        " {} "
                    )
                ).format(
                    (
                        "."
                        if distance == 0 else
                        " "
                    )
                    if layer not in self.scanners else
                    "S"
                    if self.get_scanner_position(layer) == distance else
                    " "
                )
                for layer in range(max_layer + 1)
            )
            for distance in range(max_range)
        ]))


Challenge.main()
challenge = Challenge()
