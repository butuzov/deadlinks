"""
serving/conftest.py
~~~~~~~~~~~~~~~~~~~
Provides fixtures used in self serving testings.
"""

import pytest

from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()
