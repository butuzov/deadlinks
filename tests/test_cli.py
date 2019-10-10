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

from deadlinks.__main__ import main


@pytest.fixture
def runner():
    return CliRunner()


# Once you change value here copy/paste it to the test_crawler
# ------------------------------------------------------------------
# parameters used in pair with site_with_links fixture
# Tuple
#   1st arg: External Indexation (bool)
#   2nd arg: Threads (int)
#   3rd arg: Ignored Domains (List[str])
#   4th arg: Ignored Path (List[str])
#   5th arg: Result (total_links_in_index, failed, succeed, ignored)

site_with_links_defaults = [
    (True, 10, [], [], (27, 6, 21, 0)),
    (False, 10, [], [], (27, 2, 17, 8)),
    (True, 10, [], ["limk"], (27, 4, 21, 2)),
    (False, 10, [], ["limk"], (27, 0, 17, 10)),
    (True, 10, ["google.com"], [], (27, 6, 19, 2)),
    (False, 10, ["google.com"], [], (27, 2, 17, 8)),
    (True, 10, ["google.com"], ["limk"], (27, 4, 19, 4)),
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
@pytest.mark.parametrize("external, threads, domains, pathes, results", site_with_links_defaults)
def test_cli(site_with_links, runner, external, threads, domains, pathes, results):

    # parameters
    show_key = choice(['-s', '--show'])
    args = [site_with_links] + make_params(external, threads, domains, pathes) + [show_key, 'none']
    args += ["--no-colors"]

    result = runner.invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    assert result.exit_code == 0

    # -- SETTINGS ----------------------------------------------------------
    FIRST_LINE = 'URL=<{}>; External Cheks={}; Threads={}; Retry=0'.format(
        site_with_links,
        "On" if external else "Off",
        threads,
    )
    assert output[0] == FIRST_LINE

    # -- SHORT REPORT ----------------------------------------------------------
    _, failed, succeed, ignored = results
    message = "Stats: Found {}; Not Found {}; Ignored {}".format(succeed, failed, ignored)

    assert message == output[2]


@pytest.mark.timeout(15)
@pytest.mark.parametrize("external, threads, domains, pathes, results", site_with_links_defaults)
@pytest.mark.parametrize("show", ['failed', 'ok', 'ignored', 'all', 'none'])
def test_cli_details(site_with_links, runner, external, threads, domains, pathes, results, show):
    """ tests detailed report of default export """

    # parameters
    show_key = choice(['-s', '--show'])
    args = [site_with_links] + make_params(external, threads, domains, pathes) + [show_key, show]
    args += ["--no-colors"]

    result = runner.invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    # -- SHORT REPORT ----------------------------------------------------------
    _, failed, succeed, ignored = results

    stats = Counter()

    for line in output[4:]:
        params = line.split(" ")
        assert len(params) >= 3
        stats[params[1]] += 1

    if show == 'none':
        assert len(output) == 4

    if show in {'failed', 'all'}:
        assert stats['failed'] == failed

    if show in {'ok', 'all'}:
        assert stats['succeed'] == succeed

    if show in {'ignored', 'all'}:
        assert stats['ignored'] == ignored


def test_help(runner):

    result = runner.invoke(main, ['--help'])

    assert result.exit_code == 0

    for word in {'Usage', 'Examples', 'Options'}:
        assert word in result.output


def test_version(runner):

    result = runner.invoke(main, ['--version'])

    assert result.exit_code == 0

    from deadlinks.__init__ import __app_version__, __app_package__

    assert result.output.rstrip("\n") == "{}: v{}".format(__app_package__, __app_version__)


@pytest.mark.parametrize(
    'stay_within_path, check_external, results', [
        (True, False, (1, 1, 5)),
        (True, True, (4, 1, 2)),
        (False, False, (3, 1, 5)),
        (False, True, (8, 1, 0)),
    ])
def test_full_site(simple_site, runner, stay_within_path, check_external, results):

    # parameters
    url = "{}/{}".format(simple_site.rstrip("/"), "projects/")

    args = [url, '-s', 'all', '--no-colors']
    args += make_params(check_external, 10, [], [])
    if not stay_within_path:
        args += ['--full-site-check']

    result = runner.invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    # -- SHORT REPORT ----------------------------------------------------------
    exists, failed, ignored = results

    stats = Counter()

    for line in output[4:]:
        params = line.split(" ")
        assert len(params) >= 3
        stats[params[1]] += 1

    assert stats['failed'] == failed
    assert stats['succeed'] == exists
    assert stats['ignored'] == ignored
