"""
exporter/test_cli.py
-----------

Testing cli frunctionality.
"""

import pytest

from click.testing import CliRunner
from tests.helpers import Page

from deadlinks.__main__ import main


@pytest.fixture
def runner():
    return CliRunner()


def test_help(runner):
    """ will check if section and main title are present in help """

    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0

    assert main.help.rstrip() in result.output

    for word in {'Usage Examples:', 'Examples', 'Other:', 'Default Options'}:
        assert word in result.output


def test_version(runner):
    """ simple version test """
    result = runner.invoke(main, ['--version'])

    assert result.exit_code == 0

    from deadlinks.__version__ import __app_version__ as version
    from deadlinks.__version__ import __app_package__ as package

    assert result.output.rstrip("\n") == "{}: v{}".format(package, version)


def test_default_fail_if_failed_found(server, runner):
    """ checks genra fiff option """

    # adress exists, page isn't
    address = server.router({'^/$': Page("")})

    args = [address, '-s', 'none', '--no-progress']
    result = runner.invoke(main, args)

    # no fails
    assert result.exit_code == 0

    args.append("--fiff")
    result = runner.invoke(main, args)

    # failed
    assert result.exit_code == 1


@pytest.mark.parametrize('dsn', [
    "ssh://127.0.0.1:21",
    "mailto:example@exmaple.org",
])
def test_default_url_issue(runner, dsn):

    result = runner.invoke(main, [dsn])

    assert result.exit_code == 2
    MESSAGE = "Error: URL {} is not valid"
    assert MESSAGE.format(dsn) in result.output
