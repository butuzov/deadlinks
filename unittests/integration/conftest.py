"""
integration/conftest.py
~~~~~~~~~~~
Provides fixtures for integration tests.
"""

import pytest

import sys
from subprocess import (run, DEVNULL)


class Driver:

    def __init__(self, init, destroy, cmd):

        self._cmds_init = init
        self._cmds_destroy = destroy
        self.cmd = cmd

        for command in self._cmds_init:
            self.execute(command)

    def execute(self, command):
        run(command, stdout=DEVNULL, stderr=DEVNULL)

    def __del__(self):
        for command in self._cmds_destroy:
            self.execute(command)

    @classmethod
    def brew(cls):
        return cls(
            [
                ["make", "brew-pytest-start"],
                ["make", "brew-web-stop"],
            ],
            [
                ["make", "brew-pytest-final"],
            ],
            ["/usr/local/bin/deadlinks"],
        )

    @classmethod
    def docker(cls):
        return cls(
            [
                ["make", "docker-build"],
            ],
            [
                ["make", "docker-clean"],
            ],
            [
                "docker",
                "run",
                "--rm",
                "-it",
                "--network=host",
                "butuzov/deadlinks:local",
            ],
        )


# Defining all interfaces
params = [
    pytest.param(Driver.docker),
    pytest.param(
        Driver.brew, marks=pytest.mark.skipif(
            sys.platform != "darwin",
            reason="Not Mac",
        )),
]


@pytest.fixture(scope="session", params=params)
def interface(request):
    """ Invoke resource creation and destroy it. """

    runner = request.param()
    yield runner
    del runner
