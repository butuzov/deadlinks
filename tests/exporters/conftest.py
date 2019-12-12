"""
exporters/conftest.py
~~~~~~~~~~~~~~~~~~~~~
Provides fixtures used in cli/experters testing.
"""

import pytest

from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()
