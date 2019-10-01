"""
cli_test.py
-----------

Testing cli app

TODO
- [ ] Reports tests
- [ ] Fails tests
"""

import pytest

from click.testing import CliRunner

from deadlinks.main import cli


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.timeout(15)
@pytest.mark.parametrize(
    "external, threads, domains, pathes, failed, succeed, ignored",
    [
        (True, 1, [], [], 6, 21, 0),
        (True, 2, ["google.com"], [], 6, 19, 2),
        (True, 3, [], ["limk"], 4, 21, 2),
        (True, 4, ["google.com"], ["limk"], 4, 19, 4),
        (False, 5, [], [], 2, 17, 0),
    ],
)
def test_cli(server, runner, external, threads, domains, pathes, failed, succeed, ignored):

    url = "http://{}:{}".format(*server)
    args = [url, "-n", threads]
    if external:
        args.append('-e')

    is_ignored = (domains or pathes)

    for domain in domains:
        args.append('-d')
        args.append(domain)

    for path in pathes:
        args.append('-p')
        args.append(path)

    result = runner.invoke(cli, args)

    assert result.exit_code == 0

    output = result.output.split("\n")

    # We testing general settings.
    FIRST_LINE = 'URL=<{}>; External Cheks={}; Threads={}; Retry=0'.format(
        url,
        "On" if external else "Off",
        threads,
    )
    assert output[0] == FIRST_LINE

    # Ignored/Found/Not Found
    message = "Found {}; Not Found {}".format(succeed, failed)
    message += "; Ignored {}".format(ignored) if is_ignored else ""

    assert message == output[2]
