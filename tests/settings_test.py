import pytest

from deadlinks import (Settings, Link)
from deadlinks.exceptions import *

# from deadlinks.exceptions import (
#     URLIsNotValid,
#     UnknownIgnoreType,
#     MatchedIgnorePatterns,
#     SettingsOutOfTheRange,
#     SettingsNotANumber,
# )

#  50,  67, 72-76, 88, 49->50, 55->63, 56->59, 66->67, 68->76, 69->72, 85->88


@pytest.fixture
def settings():
    return Settings("http://localhost")


# --- Base Url -----------------------------------------------------------------
@pytest.mark.parametrize('base', ["localhost", "1012031023"])
def test_base_bad(base):
    with pytest.raises(DeadlinksSettinsBase):
        Settings(base)


@pytest.mark.parametrize('base', ["http://google.com", "http://bing.com"])
def test_base_ok(base):
    s = Settings(base)
    assert s.base == base


def test_base_defaults():
    with pytest.raises(TypeError):
        Settings()


def test_base_delete(settings):
    with pytest.raises(DeadlinksSettinsChange):
        del settings.base


def test_base_update(settings):
    with pytest.raises(DeadlinksSettinsBase):
        settings.base = Link("http://google.com")


# --- Ignore Domains ----------------------------------------------------------
def test_domains_default(settings):
    assert isinstance(settings.domains, list)
    assert not settings.domains


def test_domains_ok():
    domains = ["google.com", "nbc.com", "gmx.de", "nv.ua", "github.com"]
    s = Settings("http://localhost", ignore_domains=domains)

    with pytest.raises(DeadlinksSettinsDomain):
        s.domains = []

    with pytest.raises(DeadlinksSettinsChange):
        del s.domains

    for domain in domains:
        assert domain in s.domains


@pytest.mark.parametrize(
    'domains',
    [
        [
            "google1.com",
            "", # empty
            "google2.com",
        ],
        [
            "google1.com",
            "ssss"*250 + ".com", # long long
            "google2.com",
        ],
        [
            "google1.com",
            20, # type
            "google2.com",
        ],
    ])
def test_domain_bad(domains):
    with pytest.raises(DeadlinksSettinsDomain):
        Settings("http://localhost", ignore_domains=domains)


# --- Ignore Pathes -----------------------------------------------------------
def test_pathes_default(settings):
    assert isinstance(settings.pathes, list)
    assert not settings.pathes


def test_pathes_change(settings):
    with pytest.raises(DeadlinksSettinsPathes):
        settings.pathes = ["/new"]


def test_pathes_delete(settings):
    with pytest.raises(DeadlinksSettinsChange):
        del settings.pathes


@pytest.mark.parametrize(
    'pathes',
    [
        [
            "do/not/follow",
            "",
        ], # empty
        [
            "do/not/follow",
            1,
        ], # number
    ])
def test_pathes_bad(pathes):
    with pytest.raises(DeadlinksSettinsPathes):
        Settings("http://localhost", ignore_pathes=pathes)


@pytest.mark.parametrize('pathes', [
    [
        "do/not/follow",
    ],
    [
        "do/not/follow",
    ],
])
def test_pathes_ok(pathes):
    s = Settings("http://localhost", ignore_pathes=pathes)


# --- Thread -------------------------------------------------------------------
@pytest.mark.parametrize('threads', [11, 5.0, 0, "ten", "10"])
def test_threads_exception(threads):
    with pytest.raises(DeadlinksSettinsThreads):
        Settings("http://google.com", threads=threads)


@pytest.mark.parametrize('threads', list(range(1, 11)))
def test_threads(threads):
    s = Settings("http://google.com", threads=threads)
    assert s.threads == threads
    with pytest.raises(DeadlinksSettinsChange):
        s.threads = 10 - threads
    assert s.threads == threads


def test_threads_defaults(settings):
    assert isinstance(settings.threads, int)
    assert settings.threads == 1


def test_threads_update(settings):
    with pytest.raises(DeadlinksSettinsChange):
        settings.threads = 12


def test_threads_delete(settings):
    with pytest.raises(DeadlinksSettinsChange):
        del settings.threads


# --- External -----------------------------------------------------------------
@pytest.mark.parametrize('value', [True, False])
def test_external_true(value):
    s = Settings("http://google.com", check_external_urls=value)
    assert s.external is value

    with pytest.raises(DeadlinksSettinsChange):
        s.external = not value

    assert s.external is value


def test_external_update(settings):
    with pytest.raises(DeadlinksSettinsChange):
        settings.external = not settings.external


def test_external_delete(settings):
    with pytest.raises(DeadlinksSettinsChange):
        del settings.external


def test_external_defaults(settings):
    assert not settings.external


# --- Retry -------------------------------------------------------------------
@pytest.mark.parametrize('retry', range(0, 11))
def test_retry(retry):
    s = Settings("http://google.com", retry=retry)
    assert s.retry == retry


def test_retry_change(settings):
    with pytest.raises(DeadlinksSettinsChange):
        settings.retry = 8


def test_retry_delete(settings):
    with pytest.raises(DeadlinksSettinsChange):
        del settings.retry


def test_retry_wrong_type():
    with pytest.raises(DeadlinksSettinsRetry):
        Settings("http://google.com", retry=5.0)


@pytest.mark.parametrize('retry', [-20, 20])
def test_retry_error_values(retry):
    with pytest.raises(DeadlinksSettinsRetry):
        Settings("http://google.com", retry=retry)
