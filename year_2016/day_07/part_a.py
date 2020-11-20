#!/usr/bin/env python3
import re
from dataclasses import dataclass
from typing import List, TypeVar, Generic, Type, Iterable

from utils import BaseChallenge, Cls, Self, get_type_argument_class, helper


class Challenge(BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        118
        """
        return Ip7Set.from_ips_text(_input).get_ip_count_with_tls()


# noinspection PyTypeChecker
Ip7T = TypeVar('Ip7T', bound='Ip7')


@dataclass
class Ip7Set(Generic[Ip7T]):
    ips: List[Ip7T]

    @classmethod
    def get_ip_7_class(cls) -> Type[Ip7T]:
        # noinspection PyTypeChecker
        return get_type_argument_class(cls, Ip7T)

    @classmethod
    def from_ips_text(cls: Cls['Ip7Set'], ips_text: str) -> Self['Ip7Set']:
        """
        >>> Ip7Set.from_ips_text(
        ...     'abba[mnop]qrst\\nabcd[bddb]xyyx\\naaaa[qwer]tyui\\n'
        ...     'ioxxoj[asdfgh]zxcvbn\\n')
        Ip7Set(ips=[Ip7(parts=['abba', 'qrst'], hypernets=['mnop']),
            Ip7(parts=['abcd', 'xyyx'], hypernets=['bddb']),
            Ip7(parts=['aaaa', 'tyui'], hypernets=['qwer']),
            Ip7(parts=['ioxxoj', 'zxcvbn'], hypernets=['asdfgh'])])
        """
        ip_7_class = cls.get_ip_7_class()
        return cls(list(map(ip_7_class.from_ip_text, ips_text.splitlines())))

    def get_ip_count_with_tls(self) -> int:
        """
        >>> Ip7Set.from_ips_text(
        ...     'abba[mnop]qrst\\nabcd[bddb]xyyx\\naaaa[qwer]tyui\\n'
        ...     'ioxxoj[asdfgh]zxcvbn\\n').get_ip_count_with_tls()
        2
        """
        return helper.iterable_length(self.get_ips_with_tls())

    def get_ips_with_tls(self) -> Iterable[Ip7T]:
        """
        >>> list(Ip7Set.from_ips_text(
        ...     'abba[mnop]qrst\\nabcd[bddb]xyyx\\naaaa[qwer]tyui\\n'
        ...     'ioxxoj[asdfgh]zxcvbn\\n').get_ips_with_tls())
        [Ip7(parts=['abba', 'qrst'], hypernets=['mnop']),
            Ip7(parts=['ioxxoj', 'zxcvbn'], hypernets=['asdfgh'])]
        """
        return (
            ip
            for ip in self.ips
            if ip.supports_tls()
        )


@dataclass
class Ip7:
    parts: List[str]
    hypernets: List[str]

    re_hypernet = re.compile(r"\[[a-z]+]")
    re_abba = re.compile(r'.*(.)(?!\1)(.)(\2)(\1)')

    @classmethod
    def from_ip_text(cls: Cls['Ip7'], ip_text: str) -> Self['Ip7']:
        """
        >>> Ip7.from_ip_text('')
        Ip7(parts=[], hypernets=[])
        >>> Ip7.from_ip_text('abba')
        Ip7(parts=['abba'], hypernets=[])
        >>> Ip7.from_ip_text('[abba]')
        Ip7(parts=[], hypernets=['abba'])
        >>> Ip7.from_ip_text('abba[mnop]qrst')
        Ip7(parts=['abba', 'qrst'], hypernets=['mnop'])
        >>> Ip7.from_ip_text('[mnop]qrst[abba]')
        Ip7(parts=['qrst'], hypernets=['mnop', 'abba'])
        >>> Ip7.from_ip_text('aa[bb]cc[dd]ee')
        Ip7(parts=['aa', 'cc', 'ee'], hypernets=['bb', 'dd'])
        >>> Ip7.from_ip_text('[bb]cc[dd]ee[ff]')
        Ip7(parts=['cc', 'ee'], hypernets=['bb', 'dd', 'ff'])
        """
        hypernet_texts = cls.re_hypernet.findall(ip_text)
        hypernets = [
            text.replace('[', '').replace(']', '')
            for text in hypernet_texts
        ]
        parts = list(filter(None, cls.re_hypernet.split(ip_text)))

        return cls(parts, hypernets)

    def supports_tls(self) -> bool:
        """
        >>> Ip7.from_ip_text('abba[mnop]qrst').supports_tls()
        True
        >>> Ip7.from_ip_text('abcd[bddb]xyyx').supports_tls()
        False
        >>> Ip7.from_ip_text('abba[bddb]xyyx').supports_tls()
        False
        >>> Ip7.from_ip_text('aaaa[qwer]tyui').supports_tls()
        False
        >>> Ip7.from_ip_text('ioxxoj[asdfgh]zxcvbn').supports_tls()
        True
        >>> Ip7.from_ip_text(
        ...     'abcd[efgh]ijkl[mnop]ioxxoj[asdfgh]zxcvbn').supports_tls()
        True
        """
        return (
            any(map(self.is_abba, self.parts))
            and not any(map(self.is_abba, self.hypernets))
        )

    def is_abba(self, text) -> bool:
        """
        >>> Ip7([], []).is_abba('abba')
        True
        >>> Ip7([], []).is_abba('asdasdabbaasdadas')
        True
        >>> Ip7([], []).is_abba('mnop')
        False
        >>> Ip7([], []).is_abba('aaaa')
        False
        >>> Ip7([], []).is_abba('asdasdaaaaasdsad')
        False
        >>> Ip7([], []).is_abba('aaaabba')
        True
        """
        return bool(self.re_abba.match(text))


Challenge.main()
challenge = Challenge()
