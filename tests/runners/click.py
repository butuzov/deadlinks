"""
tests.runners.click.py
~~~~~~~~~~~~~~~~~~~~~~

Click runner (using testing.CliRunner)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""
# -- Imports -------------------------------------------------------------------

import pytest

from typing import List
from functools import partial

from click.testing import CliRunner
from .utils.runner import Runner

from deadlinks.__main__ import main

# -- Implementation -------------------------------------------------------------------


class clickRunner(Runner, CliRunner):
    name = "click"

    def __init__(self, main: List[str], params: List[str], *args, **kwargs):
        self._main = main
        self._params = params
        super().__init__(*args, **kwargs)

    def __call__(self, args):
        result = super().invoke(self._main, self._params + args)

        return {
            'code': result.exit_code,
            'output': result.output,
        }

    def supports(self, what: str) -> bool:
        return True


ClickRunner = pytest.param(
    partial(
        clickRunner,
        **{
            'main': main,
            'params': list()
        },
    ), marks=[
        pytest.mark.click(),
    ])
