#!/usr/bin/env python3
import utils


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1119
        """
        return Captcha.from_text(_input).get_captcha()


class Captcha:
    @classmethod
    def from_text(cls, text):
        return cls(tuple(map(int, text.strip())))

    def __init__(self, digits):
        self.digits = digits

    def get_captcha(self):
        """
        >>> Captcha.from_text('1122').get_captcha()
        3
        >>> Captcha.from_text('1111').get_captcha()
        4
        >>> Captcha.from_text('1234').get_captcha()
        0
        >>> Captcha.from_text('91212129').get_captcha()
        9
        """
        return sum(
            self.digits[index]
            for index in range(len(self.digits))
            if self.digits[index] == self.digits[(index + 1) % len(self.digits)]
        )


Challenge.main()
challenge = Challenge()
