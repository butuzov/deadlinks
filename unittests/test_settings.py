"""
settings_test.py
~~~~~~~~~~~~~~~~

These tests are covers Settings API.
"""

# pylint: disable=redefined-outer-name

import pytest

from deadlinks import (Settings, Link)
from deadlinks.exceptions import (
    DeadlinksSettingsPathes,
    DeadlinksSettingsPath,
    DeadlinksSettingsThreads,
    DeadlinksSettingsBase,
    DeadlinksSettingsRetry,
    DeadlinksSettingsChange,
    DeadlinksSettingsDomains,
)


@pytest.fixture
def settings():
    """ defaults """
    return Settings("http://localhost")


# --- Base Url -----------------------------------------------------------------
@pytest.mark.parametrize('base', ["localhost", "1012031023"])
def test_base_bad(base):
    """ Bad Url form, no scheme """
    with pytest.raises(DeadlinksSettingsBase):
        Settings(base)


@pytest.mark.parametrize('base', ["http://google.com", "http://bing.com"])
def test_base_ok(base):
    """ Base URL looks OK """
    s = Settings(base)
    assert s.base == base


def test_base_defaults():
    """ Default settings with no URL provided. """
    with pytest.raises(TypeError):
        Settings() # pylint: disable=no-value-for-parameter

    with pytest.raises(AttributeError):
        del settings.base


def test_base_update(settings):
    """ Attempts to update baseurl property """
    with pytest.raises(DeadlinksSettingsBase):
        settings.base = Link("http://google.com")


# --- Ignore Domains ----------------------------------------------------------
def test_domains_default(settings):
    """ Default values for ignored domains is empty list """
    assert isinstance(settings.domains, list)
    assert not settings.domains

    # delete domain
    with pytest.raises(AttributeError):
        del settings.domains


def test_domains_ok():
    """ General tests for ignored domains """
    domains = ["google.com", "nbc.com", "gmx.de", "nv.ua", "github.com"]
    s = Settings("http://localhost", ignore_domains=domains)

    # domains update
    with pytest.raises(DeadlinksSettingsDomains):
        s.domains = []

    for domain in domains:
        assert domain in s.domains


@pytest.mark.parametrize(
    'domains',
    [
        ["google1.com", "", "google2.com"], # empty
        ["google1.com", "ssss"*250 + ".com", "google2.com"], # long long
        ["google1.com", 20, "google2.com"], # type
    ])
def test_domain_bad(domains):
    """ Values that causing throwing exception while setting ignored domains """
    with pytest.raises(DeadlinksSettingsDomains):
        Settings("http://localhost", ignore_domains=domains)


# --- Ignore Pathes -----------------------------------------------------------
def test_pathes_default(settings):
    """ Default values for ignored pathes is empty list """
    assert isinstance(settings.pathes, list)
    assert not settings.pathes

    # deleting property
    with pytest.raises(AttributeError):
        del settings.pathes


def test_pathes_change(settings):
    """ Attempts to update ignored pathes information """
    with pytest.raises(DeadlinksSettingsPathes):
        settings.pathes = ["/new"]


@pytest.mark.parametrize(
    'pathes',
    [
        ["do/not/follow", ""], # empty string
        ["do/not/follow", 10], # int number
    ])
def test_pathes_bad(pathes):
    """ General test for `ignored pathes` property with wrong type passed """
    with pytest.raises(DeadlinksSettingsPathes):
        Settings("http://localhost", ignore_pathes=pathes)


@pytest.mark.parametrize('pathes', [
    ["do/not/follow"],
    ["issues/new"],
])
def test_pathes_ok(pathes):
    """ General test for `ignored pathes` property """
    s = Settings("http://localhost", ignore_pathes=pathes)
    assert s.pathes == pathes


# --- Stay within path --------------------------------------------------------
def test_stay_within_path(settings):
    assert settings.stay_within_path

    # changeing it?
    with pytest.raises(DeadlinksSettingsPath):
        settings.stay_within_path = False


@pytest.mark.parametrize('stay', ["Yes", 1.1, 1, None])
def test_stay_within_path_exception(stay):
    """ Breaking threads property with wrong values """
    with pytest.raises(DeadlinksSettingsPath):
        Settings("http://google.com", stay_within_path=stay)


# --- Thread -------------------------------------------------------------------
@pytest.mark.parametrize('threads', [11, 5.0, 0, "ten", "10"])
def test_threads_exception(threads):
    """ Breaking threads property with wrong values """
    with pytest.raises(DeadlinksSettingsThreads):
        Settings("http://google.com", threads=threads)


@pytest.mark.parametrize('threads', range(1, 11))
def test_threads(threads):
    """ Setting threads value within valid range"""
    s = Settings("http://google.com", threads=threads)
    assert s.threads == threads


def test_threads_defaults(settings):
    """ Default of the threads property """
    assert isinstance(settings.threads, int)
    assert settings.threads == 1

    with pytest.raises(AttributeError):
        del settings.threads


def test_threads_update(settings):
    """ Attempts to update threads information """
    with pytest.raises(DeadlinksSettingsChange):
        settings.threads = 12


# --- External Urls Checking ---------------------------------------------------
@pytest.mark.parametrize('value', [True, False])
def test_external_true(value):
    """ General test for `external` property """
    s = Settings("http://google.com", check_external_urls=value)
    assert s.external is value


def test_external_update(settings):
    """ Attempt to update External property """
    with pytest.raises(DeadlinksSettingsChange):
        settings.external = not settings.external


def test_external_defaults(settings):
    """ Checking external urls by default is: False """
    assert not settings.external

    with pytest.raises(AttributeError):
        del settings.external


# --- Retry -------------------------------------------------------------------
@pytest.mark.parametrize('retry', range(0, 11))
def test_retry(retry):
    """ Setting retry within valid range """
    s = Settings("http://google.com", retry=retry)
    assert s.retry == retry


def test_retry_change(settings):
    """ Attempts to change retry property """
    with pytest.raises(DeadlinksSettingsChange):
        settings.retry = 8

    with pytest.raises(AttributeError):
        del settings.retry


def test_retry_wrong_type():
    """ Wrong type provided for retry """
    with pytest.raises(DeadlinksSettingsRetry):
        Settings("http://google.com", retry=5.0)


@pytest.mark.parametrize('retry', [-20, 20])
def test_retry_error_values(retry):
    """ Out of range values provided for retry """
    with pytest.raises(DeadlinksSettingsRetry):
        Settings("http://google.com", retry=retry)
