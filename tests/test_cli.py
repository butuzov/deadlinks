"""
cli_test.py
-----------

Testing cli app

TODO
- [ ] Reports tests
- [ ] Fails tests
"""

from collections import Counter
from random import choice

import pytest

from click.testing import CliRunner

from deadlinks.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def url(server):
    return "http://{}:{}".format(*server)


CLI_PARAMS = [
    (True, 1, [], [], (6, 21, 0)),
    (True, 2, ["google.com"], [], (6, 19, 2)),
    (True, 3, [], ["limk"], (4, 21, 2)),
    (True, 4, ["google.com"], ["limk"], (4, 19, 4)),
    (True, 1, ["facebook.com"], ["404.html"], (6, 21, 0)),
    (False, 5, [], [], (2, 17, 0)),
]


def make_params(external, threads, domains, pathes):
    args = ['-n', threads]

    for domain in domains:
        args.append('-d')
        args.append(domain)

    for path in pathes:
        args.append('-p')
        args.append(path)

    if external:
        args.append('-e')

    return args


@pytest.mark.timeout(15)
@pytest.mark.parametrize("external, threads, domains, pathes, results", CLI_PARAMS)
def test_cli(url, runner, external, threads, domains, pathes, results):

    # parameters
    show_key = choice(['-s', '--show'])
    args = [url] + make_params(external, threads, domains, pathes) + [show_key, 'none']

    result = runner.invoke(cli, args)
    output = result.output.rstrip("\n").split("\n")

    assert result.exit_code == 0

    # -- SETTINGS ----------------------------------------------------------
    FIRST_LINE = 'URL=<{}>; External Cheks={}; Threads={}; Retry=0'.format(
        url,
        "On" if external else "Off",
        threads,
    )
    assert output[0] == FIRST_LINE

    # -- SHORT REPORT ----------------------------------------------------------
    failed, succeed, ignored = results
    message = "Found {}; Not Found {}".format(succeed, failed)
    message += "; Ignored {}".format(ignored) if (domains or pathes) else ""
    assert message == output[2]


@pytest.mark.timeout(15)
@pytest.mark.parametrize("external, threads, domains, pathes, results", CLI_PARAMS)
@pytest.mark.parametrize("show", ['failed', 'ok', 'ignored', 'all', 'none'])
def test_cli_details(url, runner, external, threads, domains, pathes, results, show):
    """ tests detailed report of default export """
    # parameters
    show_key = choice(['-s', '--show'])
    args = [url] + make_params(external, threads, domains, pathes) + [show_key, show]

    result = runner.invoke(cli, args)
    output = result.output.rstrip("\n").split("\n")

    # -- SHORT REPORT ----------------------------------------------------------
    failed, succeed, ignored = results

    stats = Counter()

    for line in output[3:]:
        stats[line.split(" ")[1]] += 1

    if show == 'none':
        assert len(output) == 3

    if show in {'failed', 'all'}:
        assert stats['failed'] == failed

    if show in {'ok', 'all'}:
        assert stats['succeed'] == succeed

    if show in {'ignored', 'all'}:
        assert stats['ignored'] == ignored


def test_help(runner):

    result = runner.invoke(cli, ['--help'])

    assert result.exit_code == 0

    for word in {'Usage', 'Examples', 'Options'}:
        assert word in result.output


def test_version(runner):

    result = runner.invoke(cli, ['--version'])

    assert result.exit_code == 0

    from deadlinks.__init__ import __app_version__, __app_package__

    assert result.output.rstrip("\n") == "{}: v{}".format(__app_package__, __app_version__)
