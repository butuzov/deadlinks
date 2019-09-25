#
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
from threading import Thread
from functools import partial

# tested modules
from deadlinks.settings import Settings
from deadlinks.crawler import Crawler
from deadlinks.url import URL

import pytest


def test_crawler_external_links(server):
    """
    checking external links
    """

    c = Crawler(Settings(
        "http://{}:{}/".format(*server),
        check_external_urls=True,
        threads=5,
    ))
    c.crawl()

    # 24 links at index page
    # 2 more links at /more/links page, and 1 start page
    assert len(c.index) == 27

    # failed urls
    # 2 internal and 5 external
    assert len(c.index.failed()) == 6

    # succeed urls
    # 18 internal urls of link-DIGIT(s)
    # 1 homepage
    # 1 /more/links
    assert len(c.index.succeed()) == 21


def test_crawler_internal_links(server):
    """
    checking internal links only
    """

    # check_external_urls=True,
    # threads=1,
    # retry=None,

    c = Crawler(Settings(
        "http://{}:{}/".format(*server),
        check_external_urls=False,
        threads=5,
    ))
    c.crawl()

    # 16 links at index page
    # 2 more links at /more/links page, and 1 start page
    assert len(c.index) == 19

    # failed urls
    # 2 internal and 5 external
    assert len(c.index.failed()) == 2

    # succeed urls
    # 16 internal urls of link-DIGIT(s)
    # 1 homepage
    assert len(c.index.succeed()) == 17


@pytest.mark.timeout(2)
def test_single_thread_timeout(server):
    """ testing for whilte True condition of the indexer """
    c = Crawler(Settings(
        "http://{}:{}/".format(*server),
        check_external_urls=False,
        threads=1,
    ))
    c.crawl()


@pytest.mark.slow
@pytest.mark.parametrize(
    "succeed_retries, do_retries, expect_exists, expect_failed",
    [
        (0, 0, 1, 0), # 0 retry attempts to unlock page. 1 (1 request + 0 retry) requests done - result 200
        (4, 3, 1, 0), # 4 retry attempts to unlock page. 4 (1 request + 3 retry) requests done - result 200
        (4, 2, 0, 1), # 4 retry attempts to unlock page. 4 (1 request + 2 retry) requests done - result 503
        (2, 1, 1, 0), # 2 retry attempts to unlock page. 2 (1 request + 1 retry) requests done - result 200
        (2, 0, 0, 1), # 2 retry attempts to unlock page. 1 (1 request + 0 retry) requests done - result 503
    ]
)
def test_retry(succeed_retries, do_retries, expect_exists, expect_failed):
    # allocate port
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    sa = s.getsockname()
    s.close()

    # passing state to handler
    retry_attempts = 0
    def counter():
        nonlocal retry_attempts
        retry_attempts += 1
        return retry_attempts


    class RetryRequestHandler(BaseHTTPRequestHandler):


        def __init__(self, retry, succeed_retries, *args, **kwargs):
            self.requests_counter = retry
            self.succeed_retries = succeed_retries
            super().__init__(*args, **kwargs)

        def log_message(self, format, *args): pass

        def do_GET(self):
            deny = self.requests_counter() < self.succeed_retries
            answer = (503, "don't") if deny else (200, "ok")

            self.send_response(answer[0])
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(answer[1], "utf8"))


    handler = partial(RetryRequestHandler, counter, succeed_retries)
    server = HTTPServer((sa[0], sa[1]), handler)
    server_thread = Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    c = Crawler(Settings(
        "http://{}:{}/".format(*sa),
        threads=1,
        retry=do_retries,
    ))
    c.crawl()

    assert expect_failed == len(c.index.failed())
    assert expect_exists == len(c.index.succeed())

    server.shutdown()
