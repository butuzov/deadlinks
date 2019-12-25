"""
tests.runners.utils.runner.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Abstract class of runner.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

import abc


class Runner(abc.ABC):

    @abc.abstractmethod
    def __call__(self, args):
        pass

    @abc.abstractmethod
    def supports(self, what) -> bool:
        pass
