#!/usr/bin/env python3
import re
from functools import reduce
from typing import Set, Iterable

from utils import BaseChallenge, helper
from utils.collections_utils import get_fixed_length_substrings
from . import part_a


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        260
        """
        return Ip7SetExtended.from_ips_text(_input).get_ip_count_with_ssl()


class Ip7SetExtended(part_a.Ip7Set['Ip7Extended']):
    def get_ip_count_with_ssl(self) -> int:
        """
        >>> Ip7SetExtended.from_ips_text(
        ...     'aba[bab]xyz\\nxyx[xyx]xyx\\naaa[kek]eke\\n'
        ...     'zazbz[bzb]cdb\\n').get_ip_count_with_ssl()
        3
        """
        return helper.iterable_length(self.get_ips_with_ssl())

    def get_ips_with_ssl(self) -> Iterable[part_a.Ip7T]:
        """
        >>> list(Ip7SetExtended.from_ips_text(
        ...     'aba[bab]xyz\\nxyx[xyx]xyx\\naaa[kek]eke\\n'
        ...     'zazbz[bzb]cdb\\n').get_ips_with_ssl())
        [Ip7Extended(parts=['aba', 'xyz'], hypernets=['bab']),
            Ip7Extended(parts=['aaa', 'eke'], hypernets=['kek']),
            Ip7Extended(parts=['zazbz', 'cdb'], hypernets=['bzb'])]
        """
        return (
            ip
            for ip in self.ips
            if ip.supports_ssl()
        )


class Ip7Extended(part_a.Ip7):
    re_aba = re.compile(r'(.)(?!\1)(.)(\1)')

    def supports_ssl(self) -> bool:
        """
        >>> Ip7Extended.from_ip_text('aba[bab]xyz').supports_ssl()
        True
        >>> Ip7Extended.from_ip_text('xyx[xyx]xyx').supports_ssl()
        False
        >>> Ip7Extended.from_ip_text('aaa[kek]eke').supports_ssl()
        True
        >>> Ip7Extended.from_ip_text('zazbz[bzb]cdb').supports_ssl()
        True
        """
        return any(
            any(
                bab in hypernet
                for hypernet in self.hypernets
            )
            for bab in self.get_all_bab_strings()
        )

    def get_all_bab_strings(self) -> Set[str]:
        """
        >>> sorted(Ip7Extended.from_ip_text(
        ...     'aba[bab]xyz').get_all_bab_strings())
        ['bab']
        >>> sorted(Ip7Extended.from_ip_text(
        ...     'xyx[xyx]xyx').get_all_bab_strings())
        ['yxy']
        >>> sorted(Ip7Extended.from_ip_text(
        ...     'aaa[kek]eke').get_all_bab_strings())
        ['kek']
        >>> sorted(Ip7Extended.from_ip_text(
        ...     'zazbz[bzb]cdb').get_all_bab_strings())
        ['aza', 'bzb']
        """
        return reduce(set.__or__, map(self.get_bab_strings, self.parts), set())

    def get_bab_strings(self, text: str) -> Set[str]:
        """
        >>> sorted(Ip7Extended([], []).get_bab_strings('aba'))
        ['bab']
        >>> sorted(Ip7Extended([], []).get_bab_strings('dddddddaba'))
        ['bab']
        >>> sorted(Ip7Extended([], []).get_bab_strings('abada'))
        ['bab', 'dad']
        >>> sorted(Ip7Extended([], []).get_bab_strings('abababa'))
        ['aba', 'bab']
        >>> sorted(Ip7Extended([], []).get_bab_strings('abababaaaaaa'))
        ['aba', 'bab']
        >>> sorted(Ip7Extended([], []).get_bab_strings('aaa'))
        []
        """
        return set(map(self.aba_to_bab, self.get_aba_strings(text)))

    def aba_to_bab(self, aba: str) -> str:
        """
        >>> Ip7Extended([], []).aba_to_bab('aba')
        'bab'
        """
        outer, middle, _ = aba
        return f"{middle}{outer}{middle}"

    def get_aba_strings(self, text: str) -> Set[str]:
        """
        >>> sorted(Ip7Extended([], []).get_aba_strings('aba'))
        ['aba']
        >>> sorted(Ip7Extended([], []).get_aba_strings('dddddddaba'))
        ['aba']
        >>> sorted(Ip7Extended([], []).get_aba_strings('abada'))
        ['aba', 'ada']
        >>> sorted(Ip7Extended([], []).get_aba_strings('abababa'))
        ['aba', 'bab']
        >>> sorted(Ip7Extended([], []).get_aba_strings('abababaaaaaa'))
        ['aba', 'bab']
        >>> sorted(Ip7Extended([], []).get_aba_strings('aaa'))
        []
        """
        return set(filter(
            self.re_aba.match, get_fixed_length_substrings(text, 3)))


Challenge.main()
challenge = Challenge()
