"""
tests.utils.server.py
~~~~~~~~~~~~~~~~~~~~~

Simple page emulator.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports ------------------------------------------------------------------

from typing import (Optional, Dict)

from functools import partial
from time import sleep
from http.server import HTTPServer

import socket

from threading import Thread

from .router import Router
from .handler import Handler
from .page import Page

# -- Implementation -----------------------------------------------------------

RouterConfig = Optional[Dict[str, Page]]


def defaults() -> RouterConfig:
    """ return new instance of default rules """
    return {'.*': Page("ok").exists()}


class Server:

    def __init__(self):
        self.address = socket.gethostbyname(socket.gethostname())
        self.port = 0

    def __str__(self):
        return "http://{0}:{1}".format(*self.s.server_address)

    def acquire_new_addr(self):
        _socket = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
        _socket.bind((socket.gethostbyname(socket.gethostname()), 0))
        addr = _socket.getsockname()

        _socket.close()

        self.address, self.port = addr[0], addr[1]

        return self.address, self.port,

    def router(self, config: RouterConfig = None):

        self.rules = config or defaults()
        handler = partial(Handler, Router(self.rules))
        self.s = HTTPServer((self.address, self.port), handler)
        self.s.allow_reuse_address = True

        thread = Thread(target=self.s.serve_forever)
        thread.setDaemon(True)
        thread.start()

        return str(self)

    def destroy(self):
        self.s.shutdown()
        # self.s.server_close()
