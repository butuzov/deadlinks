"""
tests.utils.handler.py
~~~~~~~~~~~~~~~~~~~~~~

Provides Default fixtures for deadlinks tests

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from http.server import BaseHTTPRequestHandler

# -- Implementation ------------------------------------------------------------


class Handler(BaseHTTPRequestHandler):

    def __init__(self, logic, *args, **kwargs) -> None:
        self.logic = logic
        super().__init__(*args, **kwargs)

    def log_message(self, *args):
        """ Ignoring logging. """

    def do_HEAD(self):
        """ HEAD, but GET. """
        return self.do_GET()

    def do_GET(self):
        """handling request"""

        response_code, mime_type, content = self.logic.handler(self.path)

        if response_code == 301:
            self.send_response(301)
            self.send_header('Location', content % self.path)
            self.end_headers()
            return

        self.send_response(response_code)
        self.send_header('Content-type', mime_type)
        self.end_headers()
        self.wfile.write(bytes(content, "utf8"))
