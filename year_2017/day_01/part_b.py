#!/usr/bin/env python3
import utils
from year_2017.day_01 import part_a


class Challenge(utils.BaseChallenge):
    def solve(self, _input, debug=False):
        """
        >>> Challenge().default_solve()
        1420
        """
        return CaptchaExtended.from_text(_input).get_even_captcha()


class CaptchaExtended(part_a.Captcha):
    def get_even_captcha(self):
        """
        >>> CaptchaExtended.from_text('1212').get_even_captcha()
        6
        >>> CaptchaExtended.from_text('1221').get_even_captcha()
        0
        >>> CaptchaExtended.from_text('123425').get_even_captcha()
        4
        >>> CaptchaExtended.from_text('123123').get_even_captcha()
        12
        >>> CaptchaExtended.from_text('12131415').get_even_captcha()
        4
        """
        length = len(self.digits)
        return sum(
            self.digits[index]
            for index in range(length)
            if self.digits[index] == self.digits[(index + length // 2) % length]
        )


Challenge.main()
challenge = Challenge()
