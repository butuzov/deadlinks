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
            [["make", "brew-pytest-start"], ["make", "brew-web-stop"]],
            [["make", "brew-pytest-final"]],
            ["/usr/local/bin/deadlinks"],
        )

    @classmethod
    def docker(cls):
        return cls(
            [["make", "docker-build"]],
            [["make", "docker-clean"]],
            ["docker", "run", "--rm", "--network=host", "butuzov/deadlinks:local"],
        )


# Same but, no resources creation or destroy.
class FastDriver(Driver):

    def __init__(self, *args):
        self.cmd = args[-1]

    def __del__(self):
        pass
