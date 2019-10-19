from http.server import BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):

    def __init__(self, logic, *args, **kwargs) -> None:
        self.logic = logic
        super().__init__(*args, **kwargs)

    def log_message(self, *args):
        """ Ignoring logging """

    def do_HEAD(self):
        """ Additionaly we need to cover head for tests. """
        return self.do_GET()

    def do_GET(self):
        """handling request"""

        response_code, mime_type, content = self.logic.handler(self.path)

        self.send_response(response_code)
        self.send_header('Content-type', mime_type)
        self.end_headers()
        self.wfile.write(bytes(content, "utf8"))
