"""
tests.components.features.tests_robots.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests robots.txt integration.

:copyright: (c) 2020 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest
from flaky import flaky

from copy import deepcopy as copy
from typing import (Optional, Dict)

from ..utils import Page

from deadlinks import (Settings, Crawler)
from deadlinks import user_agent

from deadlinks import (
    DeadlinksIgnoredURL,
    DeadlinksSettingsBase,
)

server_pages = {
    '^/$': Page("".join(["<a href='/link-%s'>%s</a>" % (x, x) for x in range(1, 101)])).exists(),
    '^/link-\d{1,}$': Page("ok").exists().redirects(pattern='%s/'),
    '^/link-\d{1,}/$': Page("ok").exists(),
}

# '^/robots.txt': Page("User-agent: *\nDisallow: /").mime('text/plain').exists(),


def pages(robots_page: Page) -> Dict[str, Page]:
    _pages = copy(server_pages)
    _pages['^/robots.txt'] = robots_page
    return _pages


def test_robots_txt_reject_all(server):

    robots_txt = Page("User-agent: *\nDisallow: /").mime('text/plain').exists()
    address = server.router(pages(robots_txt))

    with pytest.raises(DeadlinksIgnoredURL):
        c = Crawler(Settings(address))
        c.start()


def test_robots_txt_option_is_off_user_agent_reject(server):

    robots_txt = Page("User-agent: *\nDisallow: /").mime('text/plain').exists()
    address = server.router(pages(robots_txt))

    try:
        c = Crawler(Settings(address, check_robots_txt=False))
        c.start()
    except DeadlinksIgnoredURL:
        pytest.fail("User agent chcked by robots.txt")


def test_robots_txt_reject_user_agent(server):

    robots_txt = Page("User-agent: deadlinks\nDisallow: /").mime('text/plain').exists()
    address = server.router(pages(robots_txt))

    with pytest.raises(DeadlinksIgnoredURL):
        c = Crawler(Settings(address))
        c.start()


def test_robots_txt_option_is_off_user_agent_reject_specified(server):

    robots_txt = Page("User-agent: deadlinks\nDisallow: /").mime('text/plain').exists()
    address = server.router(pages(robots_txt))

    c = Crawler(Settings(address, check_robots_txt=False))
    c.start()
    try:
        c = Crawler(Settings(address, check_robots_txt=False))
        c.start()
    except DeadlinksIgnoredURL:
        pytest.fail("User agent chcked by robots.txt")


def test_robots_txt_allow_user_agent(server):

    robots_txt = Page("User-agent: *\nDisallow: /link").mime('text/plain').exists()
    address = server.router(pages(robots_txt))

    c = Crawler(Settings(address))
    c.start()

    assert len(c.ignored) == 100


@pytest.mark.timeout(1)
def test_failed_domain():
    """ Some random domain should fails (robots.txt fails to be retrived)"""

    from random import choice
    from string import ascii_lowercase

    domain = "http://%s.com/" % ''.join([choice(ascii_lowercase) for x in range(42)])
    c = Crawler(Settings(domain))
    c.start()

    assert len(c.failed) == 1


def test_failed_google():

    c = Crawler(
        Settings(
            "http://google.com/search/about/",
            **{
                'stay_within_path': True,
                'check_external_urls': False,
            },
        ))
    c.start()

    assert len(c.succeed) == 1


def test_gobyexample():
    """ special case - aws substitute robots.txt """

    with pytest.raises(DeadlinksIgnoredURL):
        c = Crawler(Settings("https://gobyexample.com"))
        c.start()
