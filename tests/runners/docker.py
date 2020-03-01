"""
tests.runners.docker.py
~~~~~~~~~~~~~~~~~~~~~~~

UI for running deadlinks in the docker container.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""
# -- Imports -------------------------------------------------------------------

import pytest

from typing import List
from functools import partial
from subprocess import PIPE

from .utils.runner import Runner
from .utils.driver import Driver

# -- Implementation ------------------------------------------------------------


class dockerRunner(Runner, Driver):
    name = "docker"

    does_not_supports = ['fs']

    def __call__(self, args: List[str]):
        result = super().execute(self.cmd + args, stdout=PIPE, stderr=PIPE)

        return {
            'code': result.returncode,
            'output': result.stdout.decode() + result.stderr.decode(),
        }

    def supports(self, what: str) -> bool:
        return what not in self.does_not_supports


# docker run suppose to be runned outside default virtual environment.

DockerRunner = pytest.param(
    partial(
        dockerRunner, **{
            'init': [],
            'destroy': [],
            'cmd': ["docker", "run", "--rm", "--network=host", "deadlinks:local"],
        }),
    marks=[
        pytest.mark.docker(),
        pytest.mark.e2e(),
    ])
