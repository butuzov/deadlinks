"""
tests.tests_cli_common.py
~~~~~~~~~~~~~~~~~~~~~~~~~

Testing common cli functionality.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

from .utils import Page

# -- Tests ---------------------------------------------------------------------


@pytest.mark.parametrize('dsn', [
    "ssh://127.0.0.1:21",
    "mailto:example@example.org",
])
def test_default_dsn_with_issues(runner, dsn):
    """ Passing unsupported DSN string. """
    result = runner([dsn])

    assert result['code'] == 2

    assert "Error: URL {} is not valid".format(dsn) in result['output']


def test_default_url_no_scheme_issue(server, runner):
    """ no domain cli execution test """

    address = server.router({'^/$': Page("").exists()})

    # TODO - fix for docker
    if not runner.supports("localnet"):
        pytest.skip("required: Local Network Support")

    scheme, address = address.split("//")
    result = runner([address, '-r1', '-s', 'failed', '--no-progress', '--fiff'])

    assert result['code'] == 0
    assert "{}//{}".format(scheme, address) in result['output']


def test_help(runner):
    result = runner(['--help'])

    from deadlinks.exporters import Default

    section, _ = Default.options()
    assert section in result['output']
