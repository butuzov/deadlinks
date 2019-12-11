"""
tests.test_links.py
~~~~~~~~~~~~~~~~~~~~~~~

Links object test coverage

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# pylint: disable=redefined-outer-name

# -- Imports -------------------------------------------------------------------

import pytest

from .helpers import Page

from deadlinks import (Link, URL)
from deadlinks.status import Status
from deadlinks.exceptions import (
    DeadlinksIgnoredURL,
    DeadlinksRedirectionURL,
)

# -- Tests ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def link():
    """ Return valid config object. """
    return Link("https://google.com")


@pytest.mark.parametrize(
    'base, url, expected',
    [
        (
            "http://localhost:1313/documentation/",
            "part1.html",
            "http://localhost:1313/documentation/part1.html",
        ),
        (
            "http://localhost:1313/documentation",
            "part1.html",
            "http://localhost:1313/part1.html",
        ),
        (
            "http://localhost:1313/documentation",
            "../part1.html",
            "http://localhost:1313/part1.html",
        ),
        (
            "http://localhost:1313/documentation/",
            "../part1.html",
            "http://localhost:1313/part1.html",
        ),
    ],
)
def test_url_link(base, url, expected):
    """ Relative link generation. """
    assert Link(base).link(url) == expected


@pytest.mark.parametrize(
    'base, url',
    [
        ("http://localhost:1313/", "http://localhost:3000/"),
        ("http://google.com/", "http://bing.com/"),
        ("http://google.com/", "http://google.com.ua/"),
        ("http://google.com.ua/", "http://google.com"),
        ("http://google.com/", "http://ww1.google.com"),
        ("http://ww1.google.com/", "http://www.www.google.com"),
    ],
)
def test_is_external(base, url):
    """ External links. """

    assert Link(base).is_external(URL(url))
    assert Link(url).is_external(URL(base))
    assert Link(base).is_external(Link(url))
    assert Link(url).is_external(Link(base))
    assert Link(base).is_external(url)
    assert Link(url).is_external(base)


@pytest.mark.parametrize(
    'base, url', [*[
        ("http://localhost:1313/", 2222),
        ("http://localhost:1313/", 2222.1),
    ]])
def test_is_external_of_wrong_type(base, url):
    """ (Mis)Typed external links """

    with pytest.raises(TypeError):
        assert Link(base).is_external(url)


def test_non_string_message():
    """ (Mis)Typed external links """

    with pytest.raises(TypeError):
        Link("http://google.com/").message = 404


@pytest.mark.parametrize(
    'base, url',
    [
        ("http://www.google.com/", "http://google.com"),
        ("http://www.www.google.com/", "http://www.www.google.com"),
        ("http://www.google.com/", "http://google.com:80"),
        ("https://www.google.com/", "https://google.com:443"),
        ("https://www.google.com:443/", "https://google.com"),
    ],
)
def test_is_internal_links(base, url):
    """ Are this links internal to url? """

    assert not Link(base).is_external(url)
    assert not Link(url).is_external(base)
    assert not Link(base).is_external(URL(url))
    assert not Link(url).is_external(URL(base))


def test_links(server):
    """ General testing for link. """

    url = server.router({
        '^/$': Page('<a href="https://google.com/">google</a>').exists(),
    })

    l = Link(url)

    assert l.exists()
    assert len(l.links) == 1
    assert str(l) == url
    assert l.url() == url


@pytest.mark.parametrize(
    "url",
    [
        "localhost", # no scheme
        "http://localhost:4040404", # no existsing domain
        "http://:4040404", # no existsing domain
    ],
)
def test_bad_links(url):
    assert not Link(url).exists()


@pytest.fixture(scope="function")
def ignore_domains():
    """ Fixture for domains """
    return ["github.com"]


@pytest.fixture(scope="function")
def ignore_pathes():
    """ Fixture for pathes. """
    return ["issues/new", "edit/master", "commit"]


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/kubeflow/website/issues/new?title",
        "https://github.com/kubeflow/website/commit/d26bed8d8",
        "https://github.com/kubeflow/website/edit/master/content/docs/",
    ],
)
def test_ignored(ignore_domains, ignore_pathes, url):
    """ Ignored domains and pathes matching. """

    assert Link(url).match_domains(ignore_domains)
    assert Link(url).match_pathes(ignore_pathes)


@pytest.mark.parametrize("url", [
    "https://google.com",
    "http://github.com",
])
def test_is_valid(url):
    """ Tests URL for valid (for crawler) format. """
    assert Link(url).is_valid()


def test_eq():
    """ Compare two objects. """

    assert Link("http://google.com") == Link("http://google.com")
    assert Link("http://google.com") == "http://google.com"
    assert "http://google.com" == Link("http://google.com")

    with pytest.raises(TypeError):
        Link('http://google.com') == 1 # pylint: disable=expression-not-assigned


def test_referrer():
    """ Test referrer. """

    l = Link("https://made.ua")
    referrer = "https://google.com"
    l.add_referrer(referrer)
    l.add_referrer(referrer)

    assert referrer in l.get_referrers()


def test_match_domain():
    """ Domain matching. """

    l = Link("https://made.ua")
    assert l.match_domains(["made.ua"])
    assert not l.match_domains(["google.com"])


@pytest.mark.timeout(2)
def test_existing_page(server):
    """ emulating slow server (responds after 1s) """

    address = server.router({
        '^/$': Page("").slow().exists(),
    })

    l = Link(address)
    assert l.status == Status.UNDEFINED
    assert l.exists()
    l.status = Status.FOUND
    assert l.exists()

    with pytest.raises(TypeError):
        l.status = 1


@pytest.mark.timeout(3)
def test_not_existing_page(server):
    """ emulating slow broken server """

    address = server.router({
        '^/$': Page("").unlock_after(3).slow().exists(),
    })

    l = Link(address)
    assert l.status == Status.UNDEFINED

    # timed out
    assert not l.exists(retries=2)
    # setting new status
    l.status = Status.NOT_FOUND

    # page is unlocked, but response is cached!
    assert not l.exists()

    with pytest.raises(TypeError):
        l.status = 2


def test_redirected_page(server):
    """ Should raise IgnoredURL if Ignored """
    address = server.router({
        '^/$': Page("").redirects(pattern="https://google.com/?%s"),
    })

    l = Link(address)
    assert l.status == Status.UNDEFINED
    with pytest.raises(DeadlinksRedirectionURL):
        l.exists()

    with pytest.raises(TypeError):
        l.status = 0


def test_ignored_page(server):
    """ Should raise IgnoredURL if Ignored """
    address = server.router({
        '^/$': Page("").exists(),
    })

    l = Link(address)
    assert l.status == Status.UNDEFINED
    l.status = Status.IGNORED
    assert l.status == Status.IGNORED
    with pytest.raises(DeadlinksIgnoredURL):
        l.exists()

    with pytest.raises(TypeError):
        l.status = 3


def test_same_url(server):
    page = "<a href='http://{}:{}'>same link</a>, <a href='/'>a</a>"
    address = server.router({
        '^/$': Page(page.format(*server.sa)).exists(),
        '^/link$': Page("ok").exists(),
    })
    l = Link(address)
    assert l.exists()
    assert address in l.links


def test_not_available_page():
    """ ok server, but ip with error """

    l = Link("http://127.0.0.1:79")
    assert l.status == Status.UNDEFINED
    assert not l.exists()
    assert "Failed to establish a new connection" in l.message
