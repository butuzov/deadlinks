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

    assert f"Error: URL {dsn} is not valid" in result['output']


def test_default_url_no_scheme_issue(server, runner):
    """ no domain cli execution test """

    address = server.router({'^/$': Page("").exists()})

    scheme, address = address.split("//")
    args = [address, '-r1', '-s', 'failed', '--no-progress', '--fiff']
    result = runner(args)

    assert result['code'] == 0
    assert f"{scheme}//{address}" in result['output']


def test_help(runner):
    result = runner(['--help'])

    from deadlinks.exporters import Default

    section, _ = Default.options()
    assert section in result['output']
