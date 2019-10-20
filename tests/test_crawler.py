"""
test_server.py
--------------

    New webServer logic tests implementation, done in order to introduce new
    concepts to crawler (noindex, nofollow, sitemaps.xml, robots.txt, etc) as
    long as testing currently implemented things.

"""

import pytest

from tests.helpers import Page

from deadlinks import (Settings, Crawler)
from deadlinks import (
    DeadlinksIgnoredURL,
    DeadlinksSettingsBase,
)


@pytest.mark.parametrize(
    'stay_within_path, check_external, results', [
        (True, False, (1, 1, 5)),
        (True, True, (4, 1, 2)),
        (False, False, (3, 1, 5)),
        (False, True, (8, 1, 0)),
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
    (True, 10, [], [], (30, 6, 21, 0, 3)),
    (False, 10, [], [], (27, 2, 17, 8, 0)),
    (True, 10, [], ["limk"], (30, 4, 21, 2, 3)),
    (False, 10, [], ["limk"], (27, 0, 17, 10, 0)),
    (True, 10, ["google.com"], [], (28, 6, 19, 2, 1)),
    (False, 10, ["google.com"], [], (27, 2, 17, 8, 0)),
    (True, 10, ["google.com"], ["limk"], (28, 4, 19, 4, 1)),
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

    HTML_FORMATTER = lambda x: "<a href='{}-{{0}}'>{{0}}</a>".format(x)
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


def test_redirection(servers):

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
    """ extra mailto test """
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
