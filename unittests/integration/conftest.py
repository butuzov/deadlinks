"""
integration/conftest.py
~~~~~~~~~~~
Provides fixtures for integration tests.
"""

import pytest

import sys
from .driver import Driver, FastDriver

IS_DARWIN = sys.platform == "darwin"
IS_NOT_DAWRIN = not IS_DARWIN
REASON_IS_NOT_DAWRIN = "Is Not Darwin"

# Defining all testable interfaces
params = [
    pytest.param(
        Driver.docker,
        marks=[
            pytest.mark.slow(),
            pytest.mark.integration(),
        ],
    ),
    pytest.param(
        FastDriver.docker,
        marks=[
            pytest.mark.fast(),
            pytest.mark.integration(),
        ],
    ),
    pytest.param(
        Driver.brew,
        marks=[
            pytest.mark.slow(),
            pytest.mark.integration(),
            pytest.mark.skipif(IS_NOT_DAWRIN, reason=REASON_IS_NOT_DAWRIN),
        ],
    ),
    pytest.param(
        FastDriver.brew,
        marks=[
            pytest.mark.fast(),
            pytest.mark.integration(),
            pytest.mark.skipif(IS_NOT_DAWRIN, reason=REASON_IS_NOT_DAWRIN),
        ],
    ),
]


@pytest.fixture(scope="session", params=params)
def interface(request):
    """ Invoke resource creation and destroy it. """

    runner = request.param()
    yield runner
    del runner
