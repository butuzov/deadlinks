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
deadlinks.serving.handler
~~~~~~~~~~~~~~~~~~~~~~~~~

Handles requests responses via simple webserver.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import Any

try:
    from http.server import BaseHTTPRequestHandler
except ModuleNotFoundError:
    from BaseHTTPServer import BaseHTTPRequestHandler # type: ignore

from .router import Router

# -- Implementation ------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):

    def __init__(self, router: Router, *args: Any, **kwargs: Any) -> None:
        """ Defined logic for responding on static files requests. """
        self._router = router

        super().__init__(*args, **kwargs)

    def log_message(self, *args: Any) -> None:
        """ Ignoring logging """

    def do_GET(self) -> None:
        """ SuperSimple GET handler.

        Responds with (addording router results for requested path):
            Code 200 -> Content
            Code 301 -> New Location
            Code 404 -> Nothing (None)
        """

        code, response = self._router(self.path)

        if code == 301:
            self.send_response(code)
            self.send_header('Location', response)
            self.end_headers()
            return

        if code == 404:
            self.send_response(code)
            self.end_headers()
            return

        try:

            with open(response, "r") as f:

                try:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(f.read().encode())
                except UnicodeDecodeError:
                    pass

        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            return
