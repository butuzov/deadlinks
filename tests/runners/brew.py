"""
tests.runners.brew.py
~~~~~~~~~~~~~~~~~~~~~

UI for running deadlinks in the docker container.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

import sys
from typing import List
from functools import partial
from subprocess import PIPE

from .utils.runner import Runner
from .utils.driver import Driver

# -- Implementation ------------------------------------------------------------


class brewRunner(Runner, Driver):
    name = "brew"

    def __call__(self, args: List[str]):

        result = super().execute(self.cmd + args, stdout=PIPE, stderr=PIPE)

        return {
            'code': result.returncode,
            'output': result.stdout.decode() + result.stderr.decode(),
        }

    def async_call(self, args, queue):
        result = self.__call__(args)
        queue.put(('code', result['code']))
        queue.put(('output'), result['output'])

    def supports(self, what: str) -> bool:
        return True


BrewRunner = pytest.param(
    partial(brewRunner, **{
        'init': [],
        'destroy': [],
        'cmd': ["/usr/local/bin/deadlinks"],
    }),
    marks=[
        pytest.mark.brew(),
        pytest.mark.e2e(),
        pytest.mark.skipif(sys.platform != "darwin", reason="!macOS"),
    ])
