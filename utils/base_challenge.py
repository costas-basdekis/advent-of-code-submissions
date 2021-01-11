from abc import ABC

import aox

import utils


__all__ = ['BaseChallenge']


class BaseChallenge(aox.BaseChallenge, ABC):
    def get_test_modules(self):
        return super().get_test_modules() + utils.test_modules
