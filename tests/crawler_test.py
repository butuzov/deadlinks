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


@pytest.mark.timeout(5)
def test_single_thread_timeout(server):
    """ testing for whilte True condition of the indexer """
    c = Crawler(Settings(
        "http://{}:{}/".format(*server),
        check_external_urls=False,
        threads=1,
    ))
    c.crawl()


@pytest.mark.timeout(12)
@pytest.mark.parametrize(
    "succeed_retries, do_retries, expect_exists, expect_failed",
    [
        (0, 0, 1, 0), # 0 retry attempts to unlock page. 1 (1 req + 0 retry) req. done - res. 200
        (4, 3, 1, 0), # 4 retry attempts to unlock page. 4 (1 req + 3 retry) req. done - res. 200
        (4, 2, 0, 1), # 4 retry attempts to unlock page. 3 (1 req + 2 retry) req. done - res. 503
        (2, 1, 1, 0), # 2 retry attempts to unlock page. 2 (1 req + 1 retry) req. done - res. 200
        (2, 0, 0, 1), # 2 retry attempts to unlock page. 1 (1 req + 0 retry) req. done - res. 503
    ])
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

        def log_message(self, *args):
            pass

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


@pytest.mark.timeout(5)
def test_crawler_crawring(server):
    c = Crawler(Settings(
        "http://{}:{}/".format(*server),
        check_external_urls=True,
        threads=5,
    ))
    c.crawl()
    c.crawl()


@pytest.mark.timeout(5)
@pytest.mark.parametrize(
    "external, domains, pathes, indexed, failed, succeed, ignored", [
        (True, [], [], 27, 6, 21, 0),
        (True, ["google.com"], [], 25, 6, 19, 2),
        (True, [], ["limk"], 25, 4, 21, 2),
        (True, ["google.com"], ["limk"], 23, 4, 19, 4),
        (False, [], [], 19, 2, 17, 0),
    ])
def test_crawler(server, external, domains, pathes, indexed, failed, succeed, ignored):
    """ testing for whilte True condition of the indexer """
    c = Crawler(
        Settings(
            "http://{}:{}/".format(*server),
            check_external_urls=external,
            threads=10,
            ignore_domains=domains,
            ignore_pathes=pathes,
        ))

    c.crawl()

    # indexed
    assert len(c.index) == indexed

    # failed urls
    assert len(c.index.failed()) == failed

    # succeed urls
    assert len(c.index.succeed()) == succeed

    # ignored
    assert len(c.ignored()) == ignored
