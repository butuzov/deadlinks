"""
tests.tests_cli_defaults.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Default Exporter of the deadlinks (CLI)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

from collections import Counter
from random import choice

from .utils import Page

from click import unstyle


# -- Helpers  ------------------------------------------------------------------
def make_params(external, threads, domains, pathes):
    args = ['-n', str(threads), '--no-progress', '--no-colors']

    for domain in domains:
        args.append('-d')
        args.append(domain)

    for path in pathes:
        args.append('-p')
        args.append(path)

    if external:
        args.append('-e')

    return args


# -- Tests -------------------------------------------------------------------


def test_version(runner):
    """ Simple version test. """

    result = runner(['--version'])

    assert result['code'] == 0

    from deadlinks.__version__ import __app_version__ as version
    from deadlinks.__version__ import __app_package__ as package

    expected_main_version = "{}: v{}".format(package, version)

    assert result["output"].rstrip("\n").startswith(expected_main_version)


def test_help(runner):
    """ Simple version test. """

    result = runner(['--help'])
    assert result['code'] == 0

    for word in {'Usage Examples', 'Examples', 'Other', 'Default Options'}:
        assert word in result['output']


def test_default_option__fail_if_failed_found(server, runner):
    """ Tested Option `--fiff` : fail if fails found. """

    address = server.router({'^/$': Page("")})

    args = [address, '-s', 'none', '--no-progress']
    result = runner(args)
    assert result['code'] == 0

    args = [address, '-s', 'none', '--no-progress', '--fiff']
    result = runner(args)
    assert result['code'] == 1


def test_default_option__no_colors(server, runner):
    """ Tested Option `--no-colors` """

    address = server.router({'^/$': Page("").exists()})

    args = [address, '-s', 'none', '--no-progress']

    result = runner(args)
    output_color = result["output"].rstrip("\n").split("\n")

    args.append('--no-colors')
    result = runner(args)
    output_plain = result["output"].rstrip("\n").split("\n")

    assert len(output_color) == len(output_plain)
    assert output_color[0] == output_plain[0]
    assert output_color[1] == output_plain[1]
    assert output_color[2] == output_plain[2]
    assert output_color[4] == output_plain[4]

    # colored lines.
    assert output_plain[3] != output_color[3]
    assert output_plain[3] == unstyle(output_color[3])


@pytest.mark.parametrize('no_progress', [True, False])
def test_default_option__no_progress(server, runner, no_progress):
    """ Tested Option `--no-progress` """
    address = server.router({
        '^/$': Page("").slow().exists().unlock_after(2),
    })

    args = [address, '-s', 'none', '-r', '2']
    if no_progress:
        args.append("--no-progress")

    result = runner(args)

    output = result["output"].rstrip("\n").split("\n")
    progress_updates = output[0].split("\r")

    if no_progress:
        assert len(progress_updates) == 1
    else:
        assert len(progress_updates) > 1


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
    linked_domain = servers[0].router({'^/$': Page(CONTENT.format(*external_urls)).exists()})

    site_to_index = servers[1].router({
        '^/$': Page("<a href='{0}'>{0}</a>".format(linked_domain)).exists(),
    })

    # TODO - fix for docker
    if not runner.supports("localnet"):
        pytest.skip("required: Local Network Support")

    args = [site_to_index, '-e', '-s', 'all']

    result = runner(args)

    assert linked_domain in result["output"]
    assert external_urls[0] not in result["output"]
    assert external_urls[1] not in result["output"]


@pytest.mark.parametrize(
    'stay_within_path, check_external, results', [
        (True, False, (1, 1, 6)),
        (True, True, (2, 2, 4)),
        (False, False, (3, 1, 6)),
        (False, True, (5, 2, 3)),
    ])
def test_full_site(simple_site, runner, stay_within_path, check_external, results):

    # TODO - fix for docker
    if not runner.supports("localnet"):
        pytest.skip("required: Local Network Support")

    # parameters
    url = "{}/{}".format(simple_site.rstrip("/"), "projects/")

    args = [url, '-s', 'all']
    args += make_params(check_external, "10", [], [])

    if not stay_within_path:
        args += ['--full-site-check']

    result = runner(args)
    output = result["output"].rstrip("\n").split("\n")

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
    (False, 10, [], [], (27, 2, 17, 8, 0)),
    (False, 10, [], ["limk"], (27, 0, 17, 10, 0)),
    (False, 10, ["google.com"], [], (27, 2, 17, 8, 0)),
    (True, 10, [], [], (29, 6, 21, 0, 2)),
    (True, 10, [], ["limk"], (29, 4, 21, 2, 2)),
    (True, 10, ["google.com"], [], (27, 6, 20, 1, 0)),
    (True, 10, ["google.com"], ["limk"], (27, 4, 20, 3, 0)),
]


@pytest.mark.timeout(15)
@pytest.mark.parametrize("external, threads, domains, pathes, results", site_with_links_defaults)
def test_cli(site_with_links, runner, external, threads, domains, pathes, results):

    # TODO - fix for docker
    if not runner.supports("localnet"):
        pytest.skip("required: Local Network Support")

    # parameters
    show_key = choice(['-s', '--show'])
    args = [site_with_links] + make_params(external, threads, domains, pathes) + [show_key, 'none']

    result = runner(args)
    output = result["output"].rstrip("\n").split("\n")

    assert result['code'] == 0

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

    # TODO - fix for docker
    if not runner.supports("localnet"):
        pytest.skip("required: Local Network Support")

    # parameters
    show_key = choice(['-s', '--show'])
    args = [site_with_links] + make_params(external, threads, domains, pathes) + [show_key, show]
    args += ["--no-colors"]

    result = runner(args)
    output = result["output"].rstrip("\n").split("\n")

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
