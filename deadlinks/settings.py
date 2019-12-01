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

from pathlib import Path

from .baseurl import BaseURL
from .serving import Server

from .exceptions import (
    DeadlinksSettingsThreads,
    DeadlinksSettingsBase,
    DeadlinksSettingsRetry,
    DeadlinksSettingsChange,
    DeadlinksSettingsDomains,
    DeadlinksSettingsPathes,
    DeadlinksSettingsPath,
    DeadlinksSettingsRoot,
)

# -- Implementation ------------------------------------------------------------
# TODO - Review, and may be somehow simplify arguments


class Settings:
    """ Handles general settings. """
    # pylint: disable=R0902
    _stay_within_path = None # type: Optional[bool]
    _external = None # type: Optional[bool]
    _threads = None # type: Optional[int]
    _domains = None # type: Optional[List[str]]
    _pathes = None # type: Optional[List[str]]
    _retry = None # type: Optional[int]
    _base = None # type: Optional[BaseURL]
    _root = None # type: Optional[Path]

    def __init__(self, url: str, **kwargs: Any) -> None:
        """ Instantiate settings class. """

        defaults = Settings.defaults(kwargs)

        # first we adding misc properties
        self.threads = defaults['threads']
        self.external = defaults['check_external_urls']
        self.retry = defaults['retry']

        # ignoring pathes.
        self.domains = defaults['ignore_domains']
        self.pathes = defaults['ignore_pathes']

        self.stay_within_path = defaults['stay_within_path']

        # next we create base url and check for ignore patterns
        self._is_masked = False
        # special case of baseurl is internal
        base = BaseURL(url)
        if base.domain == "internal":
            self._is_masked = True
            self.root = Path(defaults['root']) # type: ignore
            web_server = Server(self.root, base.path)
            base = BaseURL(web_server.url())

        self.base = base

    @staticmethod
    def defaults(kwargs: Dict) -> Dict[str, Union[str, bool, List[str], Optional[int]]]:
        """ Return default arguments merged with user provided data. """

        _defaults = {
            'root': '.',
            'check_external_urls': False,
            'ignore_domains': [],
            'ignore_pathes': [],
            'stay_within_path': True,
            'retry': None,
            'threads': None,
        }

        return {**_defaults, **kwargs}

    # -- Root ------------------------------------------------------------------

    @property
    def masked(self) -> bool:
        """ Is Base url masked? """

        return self._is_masked

    @property
    def root(self) -> str:
        """ Getter for Document Root value. """
        return self._root

    @root.setter
    def root(self, value: Path) -> None:
        if not (self._root is None): #pylint: disable-msg=C0325
            error = "root is already set to {}"
            raise DeadlinksSettingsRoot(error.format(self._root))

        if value is None:
            error = "For URL<internal> checks, Document Root is required."
            raise DeadlinksSettingsRoot(error)

        if not isinstance(value, Path):
            raise DeadlinksSettingsRoot("Document Root required to be Path-type.")

        if not value.is_dir():
            error = "Document Root ({}) not found."
            raise DeadlinksSettingsRoot(error.format(value.resolve()))

        self._root = value

    # -- Base URL --------------------------------------------------------------
    @property
    def base(self) -> BaseURL:
        """ Getter for BaseURL ."""
        return self._base

    @base.setter
    def base(self, value: BaseURL) -> None:
        if not (self._base is None): #pylint: disable-msg=C0325
            error = "BaseUrl is already set to {}"
            raise DeadlinksSettingsBase(error.format(self._base))

        if not value.is_valid():
            raise DeadlinksSettingsBase("URL {} is not valid".format(value))

        self._base = value

    # -- Ignored Domains -------------------------------------------------------
    @property
    def domains(self) -> List[str]:
        """ Getter for Ignored Domains. """
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

            # TODO - Should I add a better check for rfc 3986 ?
            if not domain:
                error = 'Empty Domain is not accepted.'
                raise DeadlinksSettingsDomains(error.format(domain))

            if len(domain) > 255:
                error = 'Domain "{}" should conform to rfc3986.'
                raise DeadlinksSettingsDomains(error.format(domain))

        self._domains = values

    # -- Ignored Pathes --------------------------------------------------------
    @property
    def pathes(self) -> List[str]:
        """ Getter for Ignored Pathes. """
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

    # -- Stay with in path setting ---------------------------------------------
    @property
    def stay_within_path(self) -> bool:
        """ Default value of stay within path setting. """
        return self._stay_within_path

    @stay_within_path.setter
    def stay_within_path(self, value: bool) -> None:
        """ Getter for stay_within_path setting. """
        if not (self._stay_within_path is None): #pylint: disable-msg=C0325
            error = "Stay within path is already defined."
            raise DeadlinksSettingsPath(error)

        if not isinstance(value, bool):
            error = 'stay_within_path can\'t be anything but bool.'
            raise DeadlinksSettingsPath(error)

        self._stay_within_path = value

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
        """ Getter for retry information. """
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

    # -- External -------------------------------------------------------------

    """
    Should crawler check external urls existence?
        True  - Check existence of external urls
        False - Ignore external urls while indexing website
    """

    @property
    def external(self) -> bool:
        """ Getter for External Indexation State. """
        return self._external

    @external.setter
    def external(self, value: bool) -> None:
        if not (self._external is None): #pylint: disable-msg=C0325
            raise DeadlinksSettingsChange("Change not allowed")

        self._external = bool(value)

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
