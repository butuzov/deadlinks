import pytest

from deadlinks.link import Link
from deadlinks.url import URL


@pytest.fixture(scope="module")
def link():
    """return valid config object"""

    return Link("https://google.com")


@pytest.mark.parametrize(
    'base, url, expected', [
        *[
            (
                "http://localhost:1313/documentation/", "part1.html",
                "http://localhost:1313/documentation/part1.html"),
            (
                "http://localhost:1313/documentation", "part1.html",
                "http://localhost:1313/part1.html"),
            (
                "http://localhost:1313/documentation", "../part1.html",
                "http://localhost:1313/part1.html"),
            (
                "http://localhost:1313/documentation/", "../part1.html",
                "http://localhost:1313/part1.html"),
        ]
    ])
def test_url_link(base, url, expected):
    assert Link(base).link(url) == expected


@pytest.mark.parametrize(
    'base, url', [
        *[
            ("http://localhost:1313/", "http://localhost:3000/"),
            ("http://google.com/", "http://bing.com/"),
            ("http://google.com/", "http://google.com.ua/"),
            ("http://google.com.ua/", "http://google.com"),
            ("http://google.com/", "http://ww1.google.com"),
            ("http://ww1.google.com/", "http://www.www .google.com"),
        ]
    ])
def test_is_external(base, url):
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
    with pytest.raises(TypeError):
        assert Link(base).is_external(url)


@pytest.mark.parametrize(
    'base, url', [
        *[
            ("http://www.google.com/", "http://google.com"),
            ("http://www.www.google.com/", "http://www.www.google.com"),
            ("http://www.google.com/", "http://google.com:80"),
            ("https://www.google.com/", "https://google.com:443"),
            ("https://www.google.com:443/", "https://google.com"),
        ]
    ])
def test_is_interal_links(base, url):
    """are this links internal to url?"""
    assert not Link(base).is_external(url)
    assert not Link(url).is_external(base)
    assert not Link(base).is_external(URL(url))
    assert not Link(url).is_external(URL(base))


def test_links(server):
    """general testing for link"""

    url = "http://{}:{}".format(*server)
    l = Link(url)
    assert l.exists()
    assert len(l.get_links()) == 24
    assert str(l) == url
    assert l.url() == url


@pytest.mark.parametrize(
    "url",
    [
        "localhost", # no scheme
        "http://localhost:4040404", # no existsing domain
        "http://:4040404", # no existsing domain
    ])
def test_bad_links(url):
    assert not Link(url).exists()


@pytest.fixture(scope="function")
def ignore_domains():
    return [
        "github.com",
    ]


@pytest.fixture(scope="function")
def ignore_pathes():
    return [
        "issues/new",
        "edit/master",
        "commit",
    ]


@pytest.mark.parametrize(
    "url", [
        "https://github.com/kubeflow/website/issues/new?title",
        "https://github.com/kubeflow/website/commit/d26bed8d8",
        "https://github.com/kubeflow/website/edit/master/content/docs/",
    ])
def test_ignored(ignore_domains, ignore_pathes, url):
    assert Link(url).match_domains(ignore_domains)
    assert Link(url).match_pathes(ignore_pathes)


@pytest.mark.parametrize("url", [
    "https://google.com",
    "http://github.com",
])
def test_is_valid(url):
    """ tests URL for valid (for crawler) format"""

    assert Link(url).is_valid()


def test_refferer():
    l = Link("https://made.ua")

    refferer = "https://google.com"
    l.add_referrer(refferer)
    l.add_referrer(refferer)

    assert refferer in l.get_refferers()


def test_match_domain():
    l = Link("https://made.ua")
    assert l.match_domains(["made.ua"])
    assert not l.match_domains(["google.com"])


def test_error():
    l = Link("http://asdasdasa/")
    assert not l.exists()
    assert "Failed to establish a new connection" in l.error()
    assert len(l.get_links()) == 0
