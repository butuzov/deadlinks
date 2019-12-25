"""
tests.runners.utils.driver.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Driver Class for standalone applications.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

import subprocess


class Driver:

    def __init__(self, init, destroy, cmd):

        self._cmds_init = init
        self._cmds_destroy = destroy
        self.cmd = cmd

        for command in self._cmds_init:
            self.execute(command)

    def execute(self, command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
        return subprocess.run(command, stdout=stdout, stderr=stderr)

    def __del__(self):
        for command in self._cmds_destroy:
            self.execute(command)
