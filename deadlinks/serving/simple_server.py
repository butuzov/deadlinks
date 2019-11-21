# Copyright 2019 Oleg Butuzov. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
deadlinks.main
~~~~~~~~~~~~~~

Main (cli interface)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (Union, Optional)

from functools import partial
from http.server import HTTPServer
from socket import (socket, SOCK_STREAM, AF_INET)
from threading import Thread
from pathlib import Path

from .handler import Handler
from .router import Router

# -- Implementation ------------------------------------------------------------


class SimpleServer:

    def __init__(self, web_root: Union[str, Path], web_path: Optional[str]) -> None:
        """ Starts simple webserver and handles requests to local folder. """
        self.web_path = "/" if not web_path else web_path
        if not self.web_path.startswith("/"):
            self.web_path = "/" + self.web_path

        if not isinstance(web_root, Path):
            web_root = Path(web_root)

        _router = Router(web_root.resolve(), self.web_path)

        _socket = socket(AF_INET, type=SOCK_STREAM)
        _socket.bind(('localhost', 0))
        self._sa = _socket.getsockname()
        _socket.close()

        # implement correct type annotation, when change
        # https://github.com/python/mypy/issues/1484

        self._server = HTTPServer(self._sa, partial(Handler, _router)) # type: ignore
        server_thread = Thread(target=self._server.serve_forever)
        server_thread.setDaemon(True)
        server_thread.start()

    def __str__(self) -> str:
        """ Instance as browsable URL. """

        return self.url()

    def url(self) -> str:
        """ Return URL of running server (including path). """
        return "http://{}:{}{}".format(self._sa[0], self._sa[1], self.web_path)
