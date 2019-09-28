# std lib
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread

# mocking
import pytest
import re, textwrap
from collections import Counter

from deadlinks import (Crawler, Settings)


class RequestHandler(BaseHTTPRequestHandler):
    r"""
    Process simple website link structure we use to crawling
    please see to link expectations matrix to check the number of
    failed and succeed links in the appropriate tests.

    requuests
        /           -> 200
        /link       -> 200
        /more/links -> 200
        /limk-10    -> 404


    Links expectations
                Dead    Live    ALL
    Internal    2       17      19
    External    4       4       8
    ALL         6       21      27
    """

    EXISTING_LINK = re.compile(r'link-(\d{1,})')

    INDEX_PAGE_CONTENTS = textwrap.dedent(
        """\
            <b>arguments</b><br/>
            <a href="link-1">(0) existing link</a>
            <a style="color:#f00;"href="link-2">(1)existing link</a>
            <a href="link-3"style="background:#f00;">(2) existing link</a>
            <hr>
            <a href='link-4'>(3) existing link</a>
            <a style='background:#f00;'href='link-5'>(4) existing link</a>
            <a href="link-6"style='background:#f00;'>(5) existing link</a>
            <hr>
            <a href=link-7>(6) existing link</a>
            <a style=background:#f00; href=link-8>(7) existing link</a>
            <a href=link-9 style=background:#f00;>(8) existing link</a>

            <hr>coverage run --source jedi -m py.test
            <b>relative links</b><br/>
            <a href=/link-10>(9)existing link</a>
            <a href="/link-11">(10)existing link</a>
            <a href='/link-12'>(11)existing link</a>

            <hr>
            <b>two in one out</b><br/>
            <a href='/link-13'href='/link-13.1'>(12)existing link #10</a>
            <a href='/link-14' href='/link-14.1'>(13)existing link #10</a>

            <hr>
            <b>not existing links</b><br/>
            <ahref=link-6 style=background:#f00;>this isn't a link at all</a>
            <a onlick="this.location=http://google.com">js</a>
            <a href>just href</a>
            <a href=''>just href</a>
            <a href=''>just href</a>
            <a href="">just href</a>
            <a href=">just href</a>
            <a href=' >just href</a>
            <a href= >just href</a>

            <hr>
            <b>external links</b><br/>
            <a href="http://google.com">(14) http google</a>
            <a href=https://google.de>(15) google germany</a>
            <a href="http://google.com.ua:80/">(16) google ukraine (port 80)</a>
            <a href="http://example.com/">(17) example.com</a>

            <hr>
            <b>external dead links</b><br/>
            <a href="http://loclahost:21">(18) localhost: 21</a>
            <a href="https://lolhost:90">(19) lolhost: 90</a>
            <a href="https://this site isnt exitng.de">(20) spaces in domain</a>
            <a href="http://lol/">(21) hostname (lol)</a>
            <a href='/limk-19'>mistyped  link</a>

            <hr>
            <b>more links</b><br/>
            <a href="more/links">(22) more link</a>
        """)

    OTHER_PAGE_CONTENTS = textwrap.dedent(
        """\
            more links for crawler
            <a href="/link-1">(0) seen link</a>
            <a href="/link-20">(23) unseen link</a>
            <a href='/limk-20'>mistyped  link 2</a>
        """)

    def log_message(self, *args):
        pass

    def do_GET(self):
        r"""handling request"""

        message = ""

        if self.path == "/":
            message = self.INDEX_PAGE_CONTENTS
        elif self.path == "/more/links":
            message = self.OTHER_PAGE_CONTENTS
        elif self.EXISTING_LINK.search(self.path):
            message = "Page Found"
        else:
            self.send_response(404)
            self.end_headers()
            return

        # Add response status code.
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(message, "utf8"))


@pytest.fixture
def server():
    """ starts a server for testing web crawling """

    # getting free port
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    sa = s.getsockname()
    s.close()

    # starting web service and yealding port

    mock_server = HTTPServer((sa[0], sa[1]), RequestHandler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()

    yield sa

    # teardown webservice
    mock_server.shutdown()
