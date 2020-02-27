"""
tests.components.features.tests_terminition.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terminition (ctrl+C or ^c)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

import multiprocessing as mp
from threading import Timer
from os import kill
from signal import SIGINT
from time import sleep

from click.testing import CliRunner
from deadlinks.__main__ import main

from ..utils import Page

# -- Bootstrap -----------------------------------------------------------------

# -- Test 1 --------------------------------------------------------------------


def background_cli_runner(args, queue):
    runner = CliRunner()
    result = runner.invoke(main, args)
    queue.put(('exit_code', result.exit_code))
    queue.put(('output', result.output))


@flaky(max_runs=3)
def test_terminition_click(server):

    url = server.router({'^/$': Page("").slow().exists()})
    args = [url, '--no-colors', '--no-progress']

    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass

    queue = mp.Queue()

    proc = mp.Process(target=background_cli_runner, args=(args, queue))

    Timer(1, lambda: kill(proc.pid, SIGINT)).start()
    proc.start()

    results = {}
    while proc.is_alive():
        sleep(0.1)
    else:
        while not queue.empty():
            key, value = queue.get()
            results[key] = value

    assert results['exit_code'] == 0
    assert "Results can be inconsistent, as execution was terminated" in results['output']


# -- Test 2 - End 3 End tests --------------------------------------------------

# def test_terminition_e2e(server):

#     url = server.router({'^/$': Page("").slow().exists()})
#     args = [url, '--no-colors', '--no-progress']

#     mp.set_start_method('spawn')
#     queue = mp.Queue()

#     proc = mp.Process(target=runner_example, args=(args, queue))
#     Timer(1, lambda: kill(proc.pid, SIGINT)).start()
#     proc.start()

# results = {}
# while proc.is_alive():
#     sleep(0.1)
# else:
#     while not queue.empty():
#         key, value = queue.get()
#         results[key] = value
