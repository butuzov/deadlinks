"""
tests.exporters.test_cli.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Testing cli functionality.


:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

import sys

from deadlinks.__main__ import main

# -- Tests ---------------------------------------------------------------------


def test_internal_200(tmp_path, runner):

    d = tmp_path
    p = d / "index.html"
    p.write_text("<h1>Hallo World!</h1>")

    args = ["internal", '--no-colors', '--no-progress', "-R", str(d), "-s", "all"]
    result = runner.invoke(main, args)

    assert result.exit_code == 0
    assert "http://internal/" in result.output


@pytest.mark.skipif(sys.version_info < (3, 6), reason="requires python3.6 or higher")
def test_internal_404(tmp_path, runner):
    d = tmp_path / "html"
    d.mkdir()
    p = d / "index.html"
    p.write_text("<h1>Hallo World!</h1>")

    args = ["internal", '--no-colors', '--no-progress', "-R", str(d / "www-root")]
    result = runner.invoke(main, args)

    assert result.exit_code == 2
    assert "Document Root" in result.output
    assert "not found" in result.output
    assert str(d / "www-root") in result.output
