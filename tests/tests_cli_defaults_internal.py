"""
tests.tests_cli_defaults_internal.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Testing local files serving using default exporter

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

import sys
from textwrap import dedent

# -- Tests -------------------------------------------------------------------

# TODO - Do same tests for updated docker runner with shared volume.


def test_internal_200(tmpdir, runner):

    if not runner.supports('fs'):
        pytest.skip("required: Local File System Support")

    p = tmpdir.mkdir("html").join("index.html")
    p.write("<h1>Hallo World!</h1>")

    args = ["internal", '--no-colors', '--no-progress', "-R", p.dirname, "-s", "all"]
    result = runner(args)

    print(result['output'])

    assert result['code'] == 0
    assert "http://internal" in result['output']


# @pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_internal_404(tmpdir, runner):

    if not runner.supports('fs'):
        pytest.skip("required: Local File System Support")

    p = tmpdir.mkdir("html").join("index.html")
    p.write("<h1>Hallo World!</h1>")

    result = runner(["internal", '--no-colors', '--no-progress', "-R", str(tmpdir + '/www-root')])

    assert result['code'] == 2
    assert "Document Root" in result['output']
    assert "not found" in result['output']
    assert str(tmpdir + '/www-root') in result['output']


def test_internal_handler(tmpdir, runner):
    """ redirections tests """

    if not runner.supports('fs'):
        pytest.skip("required: Local File System Support")

    root = tmpdir.mkdir("html")
    root.join("_redirects").write(
        "\n".join([
            "/page-1.html /page-2.html 301",
            "# comment",
            "/index.html / 301",
        ]))

    root.join("index.html").write(
        dedent(
            """\
            <h1><a href='/page-1.html'>Page 1</a></h1>
            <h1><a href='/no-page.html'>No such page</a></h1>
        """))
    root.join("page-2.html").write("<h1><a href='/index.html'>Index</a></h1>")

    r = runner(["internal", "-R", str(root), "--no-progress", "--no-colors", "--fiff", '-s', 'all'])

    assert r['code'] == 1
