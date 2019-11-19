"""
exporter/test_cli_default.py
-----------

Testing General/Default Exporter of cli.

"""

from collections import Counter
from random import choice

import pytest

from click.testing import CliRunner
from click import unstyle
from ..helpers import Page

from deadlinks.__main__ import main
from deadlinks.exporters import Default


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
    (True, 10, [], [], (30, 6, 21, 0, 3)),
    (False, 10, [], [], (27, 2, 17, 8, 0)),
    (True, 10, [], ["limk"], (30, 4, 21, 2, 3)),
    (False, 10, [], ["limk"], (27, 0, 17, 10, 0)),
    (True, 10, ["google.com"], [], (28, 6, 19, 2, 1)),
    (False, 10, ["google.com"], [], (27, 2, 17, 8, 0)),
    (True, 10, ["google.com"], ["limk"], (28, 4, 19, 4, 1)),
]


def make_params(external, threads, domains, pathes):
    args = ['-n', threads, '--no-progress', '--no-colors']

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

    result = runner.invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    assert result.exit_code == 0

    # -- SETTINGS ----------------------------------------------------------
    FIRST_LINE = 'URL=<{}>; External Checks={}; Threads={}; Retry=0'.format(
        site_with_links,
        "On" if external else "Off",
        threads,
    )
    assert output[1] == FIRST_LINE

    # -- SHORT REPORT ----------------------------------------------------------
    Message = "Links Total: {}; Found: {}; Not Found: {}; Ignored: {}; Redirects: {}"
    _, failed, succeed, ignored, redirects = results
    total = succeed + failed + ignored + redirects
    message = Message.format(total, succeed, failed, ignored, redirects)

    assert message == output[3]


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
    _, failed, succeed, ignored, _ = results

    stats = Counter()

    for line in output[5:]:
        params = line.split(" ")
        assert len(params) >= 3
        stats[params[1]] += 1

    if show == 'none':
        assert len(output) == 5

    if show in {'failed', 'all'}:
        assert stats['failed'] == failed

    if show in {'ok', 'all'}:
        assert stats['succeed'] == succeed

    if show in {'ignored', 'all'}:
        assert stats['ignored'] == ignored


def test_help(runner):
    result = runner.invoke(main, ['--help'])
    section, options = Default.options()
    assert section in result.output


# TODO - Fix this bug issue and fix tests.
# https://github.com/butuzov/deadlinks/issues/33
@pytest.mark.parametrize(
    'stay_within_path, check_external, results', [
        (True, False, (1, 1, 5)),
        (True, True, (3, 2, 2)),
        (False, False, (3, 1, 5)),
        (False, True, (7, 2, 0)),
    ])
def test_full_site(simple_site, runner, stay_within_path, check_external, results):

    # parameters
    url = "{}/{}".format(simple_site.rstrip("/"), "projects/")

    args = [url, '-s', 'all']
    args += make_params(check_external, 10, [], [])
    if not stay_within_path:
        args += ['--full-site-check']

    result = runner.invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    # -- SHORT REPORT ----------------------------------------------------------
    exists, failed, ignored = results

    stats = Counter()

    for line in output[5:]:
        params = line.split(" ")
        assert len(params) >= 3
        stats[params[1]] += 1

    assert stats['failed'] == failed
    assert stats['succeed'] == exists
    assert stats['ignored'] == ignored


def test_redirection(servers, runner):

    CONTENT = """ Example of the index page
        <a href="{}">external link 1</a> | <a href="{}">external link 2</a>
    """

    # this urls not suppose to be found in index
    external_urls = (
        "http://example.com",
        "http://example.org",
    )

    # external domain with catfished urls
    linked_domain = servers[0].router({
        '^/$': Page(CONTENT.format(*external_urls)).exists(),
    })

    site_to_index = servers[1].router({
        '^/$': Page("<a href='{0}'>{0}</a>".format(linked_domain)).exists(),
    })

    args = [site_to_index, '-e', '-s', 'all']

    result = runner.invoke(main, args)

    assert linked_domain in result.output
    assert external_urls[0] not in result.output
    assert external_urls[1] not in result.output


def test_default__no_colors(server, runner):

    address = server.router({
        '^/$': Page("").exists(),
    })

    args = [address, '-s', 'none', '--no-progress']

    result = runner.invoke(main, args)
    output_color = result.output.rstrip("\n").split("\n")

    args.append('--no-colors')
    result = runner.invoke(main, args)
    output_plain = result.output.rstrip("\n").split("\n")

    assert len(output_color) == len(output_plain)
    assert output_color[0] == output_plain[0]
    assert output_color[1] == output_plain[1]
    assert output_color[2] == output_plain[2]
    assert output_color[4] == output_plain[4]

    # colored lines.
    assert output_plain[3] != output_color[3]
    assert output_plain[3] == unstyle(output_color[3])


def test_default_progress_on(server):
    address = server.router({
        '^/$': Page("").slow().exists().unlock_after(2),
    })
    args = [address, '-s', 'none', '--no-colors', '-r', '2']
    result = CliRunner(echo_stdin=True).invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    returns = output[0].split("\r")
    assert len(returns) > 1


def test_default_progress_off(server):
    address = server.router({
        '^/$': Page("").slow().exists().unlock_after(2),
    })
    args = [address, '-s', 'none', '--no-colors', '--no-progress', '-r', '2']
    result = CliRunner(echo_stdin=True).invoke(main, args)
    output = result.output.rstrip("\n").split("\n")

    returns = output[0].split("\r")
    assert len(returns) == 1
