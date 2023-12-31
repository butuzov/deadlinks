"""
tests.utils.server.py
~~~~~~~~~~~~~~~~~~~~~

Simple page emulator.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports ------------------------------------------------------------------

import socket
from functools import partial
from http.server import HTTPServer
from threading import Thread
from typing import Dict, Optional

from .handler import Handler
from .page import Page
from .router import Router

# -- Implementation -----------------------------------------------------------

RouterConfig = Optional[Dict[str, Page]]


def defaults() -> RouterConfig:
    """ return new instance of default rules """
    return {'.*': Page("ok").exists()}


class Server:

    def __init__(self):
        self.address = self.host()
        self.port = 0

    def __str__(self):
        return "http://{0}:{1}".format(*self.s.server_address)

    def acquire_new_addr(self):
        _socket = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)

        _socket.bind((self.host(), 0))
        addr = _socket.getsockname()

        _socket.close()

        self.address, self.port = addr[0], addr[1]

        return self.address, self.port,

    def host(self):
        return socket.gethostbyname(socket.gethostname())

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
