"""
tests.components.tests_crawler.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

New webServer logic tests implementation, done in order to introduce new
concepts to crawler (noindex, nofollow, sitemaps.xml, robots.txt, etc) as
long as testing currently implemented things.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest
from flaky import flaky

from ..utils import Page

from deadlinks import (Settings, Crawler)
from deadlinks import (
    DeadlinksIgnoredURL,
    DeadlinksSettingsBase,
)

# -- Tests ---------------------------------------------------------------------


def test_redirections(server):

    address = server.router({
        '^/$': Page("<a href='/link-1'></a>").exists(),
        '^/link-\d{1,}$': Page("ok").exists().redirects(pattern='%s/'),
        '^/link-\d{1,}/$': Page("ok").exists(),
    })

    c = Crawler(Settings(address))
    c.start()

    assert len(c.redirected) == 1, "NOT"
    assert len(c.succeed) == 2, "OK"


def test_crawler_update_link(server):

    address = server.router({
        '^/$': Page("ok").exists().unlock_after(2),
        '^/link-\d{1,2}$': Page("").exists().redirects(pattern='%s/'),
    })

    c = Crawler(Settings(address, retry=1))
    c.start()

    assert len(c.failed) == 1
    url = c.failed[0]
    # print("OUT", url, url.status)
    c.update(url)
    assert len(c.failed) == 1

    # доадати в тест url p редіректоv раніше не бачений
    with pytest.raises(TypeError):
        c.update(address + 1)

    url = address + "/link-1"
    c.update(url)
    assert len(c.failed) == 1
    assert len(c.index) == 2
    assert len(c.undefined) == 1


# todo: find issue later
@pytest.mark.parametrize(
    'stay_within_path, check_external, results',
    [
        (True, False, (1, 1, 6)),
        # (True, True, (2, 2, 4)),
        (False, False, (3, 1, 6)),
        # (False, True, (5, 2, 3)),
    ])
def test_index_within_path(simple_site, stay_within_path, check_external, results):

    baseurl = "{}/{}".format(simple_site.rstrip("/"), "projects/")
    options = {
        'stay_within_path': stay_within_path,
        'check_external_urls': check_external,
        'threads': 10,
    }
    c = Crawler(Settings(baseurl, **options))
    c.start()

    exists, failed, ignored = results

    assert len(c.succeed) == exists
    assert len(c.failed) == failed
    assert len(c.ignored) == ignored


# Once you change value here copy/paste it to the test_cli
# ------------------------------------------------------------------
# parameters used in pair with site_with_links fixture
# Tuple
#   1st arg: External Indexation (bool)
#   2nd arg: Threads (int)
#   3rd arg: Ignored Domains (List[str])
#   4th arg: Ignored Path (List[str])
#   5th arg: Result (total_links_in_index, failed, succeed, ignored)

site_with_links_defaults = [
    (False, 10, [], [], (27, 2, 17, 8, 0)),
    (False, 10, [], ["limk"], (27, 0, 17, 10, 0)),
    (False, 10, ["google.com"], [], (27, 2, 17, 8, 0)),
    (True, 10, [], [], (29, 6, 21, 0, 2)),
    (True, 10, [], ["limk"], (29, 4, 21, 2, 2)),
    (True, 10, ["google.com"], [], (27, 6, 20, 1, 0)),
    (True, 10, ["google.com"], ["limk"], (27, 4, 20, 3, 0)),
]


@pytest.mark.parametrize(
    'check_external, threads, ignore_domains, ignore_pathes, results', site_with_links_defaults)
def test_crawling_advanced(
    site_with_links,
    check_external,
    threads,
    ignore_domains,
    ignore_pathes,
    results,
):
    options = {
        'check_external_urls': check_external,
        'stay_within_path': False,
        'threads': threads,
        'ignore_domains': ignore_domains,
        'ignore_pathes': ignore_pathes,
    }
    c = Crawler(Settings(site_with_links, **options))
    c.start()

    indexed, failed, succeed, ignored, redirected = results

    assert len(c.index) == indexed
    assert len(c.redirected) == redirected
    assert len(c.failed) == failed
    assert len(c.succeed) == succeed
    assert len(c.ignored) == ignored


@pytest.mark.parametrize(
    'unlocked_after, do_retries, fails',
    [
        (0, 0, 0), # no fails
        (1, 0, 1), # not available page
        (2, 1, 1), # not available page
        (2, 0, 1), # not available page
        (1, 1, 0), # no fails
        (3, 3, 0), # no fails
    ])
def test_crawling_retry(server, unlocked_after, do_retries, fails):
    address = server.router({
        '^/$': Page("ok").exists().unlock_after(unlocked_after),
    })

    c = Crawler(Settings(address, retry=do_retries))
    c.start()

    assert len(c.failed) == fails


@pytest.mark.parametrize(
    'url',
    [
        'localhost', # no scheme
        'ws://example.org', # web socket not indexated.
        'httpd://example.org', # typo in https
        'mailto:me@example.org', # mialto link?
    ])
def test_base_url_badurl(url):
    """ Testing bad urls to start API crawling """

    with pytest.raises(DeadlinksSettingsBase):
        Crawler(Settings(url))


def test_base_url_ignored(server):
    """ Starting URL is Ignored Domain (ip:port pair) """

    address = server.router({'^/$': Page('ok').exists()})
    with pytest.raises(DeadlinksIgnoredURL):
        Crawler(Settings(address, ignore_domains=[address.split("//")[1]]))


@pytest.mark.timeout(1)
@pytest.mark.parametrize('threads', [1, 7])
def test_defaults(server, threads):
    """ Solo/Multi - Threading with default settings """

    # there are 2*3 links on the page, and half of them are working
    links_number = 3

    HTML_FORMATTER = lambda x: "<a href='{}-{{0}}'>{{0}}</a>".format(x) #pylint: disable-msg=W0108
    LINK_FORMATTER = lambda x: HTML_FORMATTER("link").format(x)
    LIMK_FORMATTER = lambda x: HTML_FORMATTER("limk").format(x)

    index_html = "<!-- index page -->"
    index_html += " - ".join(map(LINK_FORMATTER, range(links_number))) # 10 good links
    index_html += " - ".join(map(LIMK_FORMATTER, range(links_number))) # 10 bad links

    address = server.router({
        '^/$': Page(index_html).exists(),
        'link-\d{1,}': Page("ok").exists(),
        'limk-\d{1,}': Page("error").not_exists(),
    })

    c = Crawler(Settings(address, threads=threads))
    c.start()

    assert len(c.index) == (1 + 2*links_number)
    assert len(c.failed) == links_number
    assert len(c.succeed) == (1 + links_number)
    assert not c.ignored


def test_external_external(servers):
    """ Redirections tested via added 2nd domain and extra external domains. """

    CONTENT = """ Example of the index page
        <a href="{}">external link 1</a> | <a href="{}">external link 2</a>
    """

    # this urls not suppose to be found in index
    external_urls = (
        "http://example.com",
        "http://example.org",
    )

    # external domain with catfished urls
    linked_domain = servers[0].router({
        '^/$': Page(CONTENT.format(*external_urls)).exists(),
    })

    site_to_index = servers[1].router({
        '^/$': Page("<a href='{0}'>{0}</a>".format(linked_domain)).exists(),
    })

    c = Crawler(Settings(site_to_index, check_external_urls=True))
    c.start()

    # convert index to list
    links = [link.url() for link in c.index]

    assert linked_domain in links
    assert external_urls[0] not in links
    assert external_urls[1] not in links


def test_mailto(server):
    """ Extra mailto test. """

    MAILTO = "mailto:name@example.org"
    CONTENT = """  <a href="{}">mail link</a>""".format(MAILTO)

    address = server.router({
        '^/$': Page(CONTENT).exists(),
    })

    c = Crawler(Settings(address, check_external_urls=True))
    c.start()

    assert len(c.ignored) == 1
    assert MAILTO in c.ignored

    assert len(c.failed) == 0
    assert len(c.index) == 2


# TODO: Fix it later.
# def test_double_start(simple_site):

#     c = Crawler(Settings(simple_site, threads=10))
#     c.start()

#     # should not take same time again.
#     c.start()


@flaky(max_runs=3)
@pytest.mark.timeout(3)
def test_redirected_links(server):

    from random import sample

    pages = list(range(1, 51))
    format_link = lambda x: "<a href='/link-%s'>link</a>" % x

    routes = {
        '^/$': Page(" / ".join(map(format_link, sample(pages, 4)))).exists(),
        '^/link-\d{1,2}$': Page("").exists().redirects(pattern='%s/'),
    }

    for step in pages:
        route_key = '^/link-%s/$' % step
        route_contents = Page(" / ".join(map(format_link, sample(pages, 4)))).exists()
        routes.update({route_key: route_contents})

    address = server.router(routes)

    settings = Settings(address, threads=10)
    c = Crawler(settings)
    c.start()

    assert 1 < len(c.index) <= (2 * len(pages) + 1)
    assert 1 < len(c.redirected) <= len(pages)
    assert len(c.failed) == 0


@pytest.mark.timeout(3)
def test_no_index_page(server):

    from random import sample

    pages = list(range(1, 51))
    format_link = lambda x: "<a href='/link-%s'>link</a>" % x

    routes = {
        '^/$': Page("").exists(),
    }

    for step in pages:
        route_key = '^/link-%s/$' % step
        route_contents = Page(" / ".join(map(format_link, sample(pages, 4)))).exists()
        routes.update({route_key: route_contents})

    address = server.router(routes)

    settings = Settings(address, threads=10)
    c = Crawler(settings)
    c.start()

    assert len(c.index) == 1


def test_within_site_root(server):
    """
        This Test checks a case when url without trailing slash is ignored
        because it's not stays within path.
    """
    CONTENT = """
        <a href="http://{0}:{1}">link</a>
        <a href="http://{0}:{1}/">link</a>
    """.format(*server.sa)

    CONTENT_DOCS = CONTENT.replace('">', '/docs/">').replace('//docs/', '/docs')

    address = server.router({
        '^/$': Page(CONTENT).exists(),
        '^/docs/?$': Page(CONTENT_DOCS).exists(),
    })

    for base in {address.rstrip("/") + "/", address.rstrip("/") + "/docs/"}:
        settings = Settings(base, stay_within_path=True)
        c = Crawler(settings)
        c.start()

        assert len(c.ignored) == 0
