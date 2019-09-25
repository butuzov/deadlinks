import pytest

from deadlinks.url import URL


@pytest.fixture(scope="module")
def url():
    """return valid config object"""

    return URL("https://google.com")


@pytest.mark.parametrize(
    'base, url, expected', [
        *[
            (
                "http://localhost:1313/documentation/", "part1.html",
                "http://localhost:1313/documentation/part1.html"
            ),
            (
                "http://localhost:1313/documentation", "part1.html",
                "http://localhost:1313/part1.html"
            ),
            (
                "http://localhost:1313/documentation", "../part1.html",
                "http://localhost:1313/part1.html"
            ),
            (
                "http://localhost:1313/documentation/", "../part1.html",
                "http://localhost:1313/part1.html"
            ),
        ]
    ]
)
def test_url_link(base, url, expected):
    assert URL(base).link(url) == expected


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
    ]
)
def test_is_external(base, url):
    assert URL(base).is_external(URL(url))
    assert URL(url).is_external(URL(base))


@pytest.mark.parametrize(
    'base, url', [
        *[
            ("http://www.google.com/", "http://google.com"),
            ("http://www.www.google.com/", "http://www.www.google.com"),
            ("http://www.google.com/", "http://google.com:80"),
            ("https://www.google.com/", "https://google.com:443"),
            ("https://www.google.com:443/", "https://google.com"),
        ]
    ]
)
def test_is_interal(base, url):
    assert not (URL(base).is_external(URL(url)))
    assert not (URL(url).is_external(URL(base)))


# def test_links():
#     u = URL("https://example.com/")
#     assert u.exists()
#     assert len(u.get_links()) == 1

#     expected = "https://example.com"
#     assert str(u) == expected and u.url() == expected


@pytest.mark.parametrize(
    "url",
    [
        "localhost",                # no scheme
        "http://localhost:4040404", # no existsing domain
        "http://:4040404",          # no existsing domain
    ]
)
def test_bad_links(url):
    assert not URL(url).exists()


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
    ]
)
def test_ignored(ignore_domains, ignore_pathes, url):
    assert URL(url).match_domains(ignore_domains)
    assert URL(url).match_pathes(ignore_pathes)


@pytest.mark.parametrize("url", [
    "https://google.com",
    "http://github.com",
])
def test_is_valid(url):
    """ tests URL for valid (for crawler) format"""

    assert URL(url).is_valid()


def test_links(server):
    """ checks for a perticular number of links, not caring about quality """

    u = URL("http://{}:{}".format(*server))

    assert u.exists()
    assert len(u.get_links()) == 24


def test_retries(server):
    """ retrys cehcking """
    u = URL("http://{}:{}/limk-20".format(*server))
    assert not u.exists(retries=0)
    print(u._error)
