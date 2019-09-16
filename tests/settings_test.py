import pytest

from deadlinks.settings import Settings
from deadlinks.exceptions import (
    URLIsNotValid,
    UnknownIgnoreType,
    MatchedIgnorePatterns,
    SettingsOutOfTheRange,
    SettingsNotANumber,
)


@pytest.mark.xfail(raises=URLIsNotValid)
@pytest.mark.parametrize('malformed_url', [
    *["localhost", "1012031023"],
])
def test_settings_url_bad(malformed_url):
    Settings(malformed_url)


@pytest.mark.parametrize(
    'base_url', [
        *["http://google.com", "http://bing.com"],
    ]
)
def test_settings_url_ok(base_url):
    Settings(base_url)
