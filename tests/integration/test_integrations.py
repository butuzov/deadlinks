import pytest

import subprocess as sp
from ..helpers import Page


def test_help(interface):
    """ Simple version test. """

    result = sp.run(interface.cmd + ['--help'], stdout=sp.PIPE)
    output = result.stdout.decode()

    assert result.returncode == 0

    for word in {'Usage Examples', 'Examples', 'Other', 'Default Options'}:
        assert word in output


def test_default_fail_if_failed_found(server, interface):
    """ Checks general `fiff` option. """

    # address exists, page isn't
    address = server.router({'^/$': Page("")})

    args = [address, '-s', 'none', '--no-progress']
    result = sp.run(interface.cmd + args, stdout=sp.PIPE)

    # no fails
    assert result.returncode == 0

    args.append("--fiff")
    result = sp.run(interface.cmd + args, stdout=sp.PIPE)

    # failed
    assert result.returncode == 1
