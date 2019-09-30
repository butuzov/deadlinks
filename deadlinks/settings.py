# Copyright 2019 Oleg Butuzov. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
deadlinks.settings
~~~~~~~~~~~~~~~~~~

Handles settings passed to crawler.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (Optional, List, Dict, Any, Union)

from deadlinks.link import Link
from deadlinks.exceptions import (
    DeadlinksSettingsPathes,
    DeadlinksSettingsThreads,
    DeadlinksSettingsBase,
    DeadlinksSettingsRetry,
    DeadlinksSettingsChange,
    DeadlinksSettingsDomains,
)


class Settings:
    """ handles general settings for """

    # pylint: disable=R0902
    _external = None # type: bool
    _threads = None # type: Optional[int]
    _domains = None # type: Optional[List[str]]
    _pathes = None # type: Optional[List[str]]
    _retry = None # type: Optional[int]
    _base = None # type: Optional[Link]

    def __init__(self, url: str, **kwargs: Any) -> None:
        """ Instantiate settings class """

        defaults = Settings.defaults(kwargs)

        # first we adding misc properties
        self.threads = defaults['threads']
        self.external = defaults['check_external_urls']
        self.retry = defaults['retry']

        self.domains = defaults['ignore_domains']
        self.pathes = defaults['ignore_pathes']

        # next we create base url and check for ignore patterns
        self.base = Link(url)

    @staticmethod
    def defaults(kwargs: Dict) -> Dict[str, Union[bool, List[str], Optional[int]]]:
        """ Return default arguments merged with user provided data. """

        _defaults = {
            'check_external_urls': False,
            'ignore_domains': [],
            'ignore_pathes': [],
            'retry': None,
            'threads': None,
        }

        return {**_defaults, **kwargs}

    # -- Base URL --------------------------------------------------------------
    @property
    def base(self) -> Link:
        """ Getter for BaseURl """
        return self._base

    @base.setter
    def base(self, value: Link) -> None:
        if not (self._base is None): #pylint: disable-msg=C0325
            error = "BaseUrl is already set to {}"
            raise DeadlinksSettingsBase(error.format(self._base))

        if not value.is_valid():
            raise DeadlinksSettingsBase("URL {} is not valid".format(value))

        self._base = value

    @base.deleter
    def base(self) -> None: #pylint: disable-msg=R0201
        raise DeadlinksSettingsChange("Change not allowed")

    # -- Ignored Domains -------------------------------------------------------
    @property
    def domains(self) -> List[str]:
        """ Getter for Ignored Domains """
        return self._domains

    @domains.setter
    def domains(self, values: List[str]) -> None:
        if not (self._domains is None): #pylint: disable-msg=C0325
            error = "Ignored Domains is already defined"
            raise DeadlinksSettingsDomains(error)

        for domain in values:
            if not isinstance(domain, str):
                error = 'Domain "{}" is not a string'
                raise DeadlinksSettingsDomains(error.format(domain))

            # TODO - Should I add a better check for 3986 ?
            if not domain:
                error = 'Empty Domain is not accepted.'
                raise DeadlinksSettingsDomains(error.format(domain))

            if len(domain) > 255:
                error = 'Domain "{}" should conform to rfc3986.'
                raise DeadlinksSettingsDomains(error.format(domain))

        self._domains = values

    @domains.deleter
    def domains(self) -> None: #pylint: disable-msg=R0201
        raise DeadlinksSettingsChange("Change not allowed.")

    # -- Ignored Pathes --------------------------------------------------------
    @property
    def pathes(self) -> List[str]:
        """ Getter for Ignored Pathes """
        return self._pathes

    @pathes.setter
    def pathes(self, values: List[str]) -> None:
        if not (self._pathes is None): #pylint: disable-msg=C0325
            error = "Ignored Pathes is already defined."
            raise DeadlinksSettingsPathes(error)

        for path in values:
            if not isinstance(path, str):
                error = 'Path "{}" is not a string.'
                raise DeadlinksSettingsPathes(error.format(path))

            if not path:
                error = 'Empty Path is not accepted.'
                raise DeadlinksSettingsPathes(error.format(path))

        self._pathes = list(set(values)) # only uniq values

    @pathes.deleter
    def pathes(self) -> None: #pylint: disable-msg=R0201
        raise DeadlinksSettingsChange("Change not allowed.")

    # -- Retries ---------------------------------------------------------------

    """
    Retry is additional requests we going to send to url in case if it responds
    with 502,503,504. Delay between requests exponential.

        Value | Delay (seconds)
        1     | 1
        2     | 2
        3     | 4
        4     | 8
        5     | 16
        6     | 32
        7     | 64
        8     | 108
        9     | 216
        10    | 432

       Beware of setting values above 5.
    """

    @property
    def retry(self) -> int:
        """ Getter for retry information """
        return self._retry

    @retry.setter
    def retry(self, value: Optional[int]) -> None:
        if not (self._retry is None): #pylint: disable-msg=C0325
            raise DeadlinksSettingsChange("Change not allowed")

        # retry validation
        if value is None:
            self._retry = 0
            return

        if isinstance(value, int):
            if 0 <= value <= 10:
                self._retry = value
                return

            error = 'Setting "retry" value out of the allowed range (0...10).'
            raise DeadlinksSettingsRetry(error)

        raise DeadlinksSettingsRetry('Setting "retry" is not a number')

    @retry.deleter
    def retry(self) -> None: #pylint: disable-msg=R0201
        raise DeadlinksSettingsChange("Change not allowed")

    # -- External -------------------------------------------------------------

    """
    Should crawler check external urls existense?
        True - Check existance of external urls
        False - Ignore external urls while indexing website
    """

    @property
    def external(self) -> bool:
        """ Getter for External Indexation State """
        return self._external

    @external.setter
    def external(self, value: bool) -> None:
        if not (self._external is None): #pylint: disable-msg=C0325
            raise DeadlinksSettingsChange("Change not allowed")

        self._external = bool(value)

    @external.deleter
    def external(self) -> None: #pylint: disable-msg=R0201
        raise DeadlinksSettingsChange("Change not allowed")

    # -- Threads -------------------------------------------------------------

    """
    Concurrent execution of indexation. "Off" by default.
    """

    @property
    def threads(self) -> int:
        """ Getter for number of threads to run """
        return int(self._threads)

    @threads.setter
    def threads(self, value: Optional[int]) -> None:
        if not (self._threads is None): #pylint: disable-msg=C0325
            raise DeadlinksSettingsChange("Change not allowed")

        if value is None:
            self._threads = 1
            return

        if isinstance(value, int):
            if 1 <= value <= 10:
                self._threads = value
                return

            error = 'Setting "threads" value out of the allowed range (1...10).'
            raise DeadlinksSettingsThreads(error)

        raise DeadlinksSettingsThreads('Setting "threads" is not a number')

    @threads.deleter
    def threads(self) -> None: #pylint: disable-msg=R0201
        raise DeadlinksSettingsChange("Change not allowed")


if __name__ == "__main__":
    s = Settings(
        "http://localhost:1313/data/new",
        retry=None,
        ignore_domains=[],
        ignore_pathes=[],
        threads=2,
    )
    # print("Base Url", s.get_base_url())
    # print("External_Urls", s.index_external())
    # print("Ignore_Domains", s.ignored("domains"))
    # print("Ignore_Pathes", s.ignored("pathes"))
    print("Threads", s.threads)

    # print("Retries", s.retries())
