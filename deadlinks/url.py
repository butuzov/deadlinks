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
deadlinks.url
~~~~~~~~~~~~~

URL representation with benefits

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (List, Optional) #pylint: disable-msg=W0611

from urllib.parse import (urlparse, urljoin)
from html import unescape
from re import compile as _compile

from requests import RequestException

from .request import request
from .status import Status
from .exceptions import (
    DeadlinksIgnoredURL,
    DeadlinksRedirectionURL,
)

# -- Constants -----------------------------------------------------------------

__RE_LINKS__ = _compile(r'<a\s{1}([^>]+)>') # pylint: disable=W1401

# filters
CLEANER = lambda x: x.strip("\"'\n ") # removes quotes, spaces and new lines
ANCHORS = lambda x: x.split("#")[0] # removed part after anchor
UNESCPE = lambda x: unescape(x) # pylint: disable=W0108


class URL:
    """ URL abstraction representation. """

    def __init__(self, location: str) -> None:
        self._url = urlparse(location)
        self._status = Status.UNDEFINED # type: Status

        # some predefined states
        self._referrers = [] # type: List[str]
        self._text = None # type: Optional[str]
        self._links = [] # type: List[str]

        # internal error or mesage field, used to store ignore message
        # or error or status code.
        # TODO - rethink logic behind this value.
        self._message = "" # type: str

    # Basic properties of the URL Link
    @property
    def domain(self) -> str:
        """ Short netlocation prop. """
        return self._url.netloc

    @property
    def scheme(self) -> str:
        """ Short scheme prop. """
        return self._url.scheme

    @property
    def path(self) -> str:
        """ Short path prop. """
        return self._url.path

    @property
    def status(self) -> Status:
        """ Return one of 4 statuses of the URL ."""
        return self._status

    @status.setter
    def status(self, value: Status) -> None:
        """ Setter for status property. """
        if not isinstance(value, Status):
            raise TypeError("URL Status value can have only Status type ")
        self._status = value

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("message can be only string")
        self._message = value

    def is_valid(self) -> bool:
        """ Check if url looks "valid". """

        return (self.domain != "" and self.scheme in {"http", "https"})

    def add_referrer(self, url: str) -> None:
        """ Add a page that links (referrer) to self object. """
        if url in self._referrers:
            return
        self._referrers.append(url)

    def get_referrers(self) -> List[str]:
        """ Return URL refferers list. """
        return self._referrers

    def match_domains(self, domains: List[str]) -> bool:
        """ Match ignored pathes (argument pathes) to `url.netloc`. """
        for domain in domains:
            if domain in self._url.netloc:
                return True
        return False

    def match_pathes(self, pathes: List[str]) -> bool:
        """ Match ignored pathes (argument pathes) to `url.path`. """
        for path in pathes:
            if path in self._url.path:
                return True
        return False

    def exists(self, is_external: bool = False, retries: int = 0) -> bool:
        """ Return "found" (or "not found") status of the page as bool. """

        if self.status == Status.FOUND:
            return True

        if self.status == Status.NOT_FOUND:
            return False

        if self.status == Status.IGNORED:
            error = "This URL <{}> ignored"
            raise DeadlinksIgnoredURL(error.format(self.url()))

        try:
            response = request(self.url(), is_external, retries)
        except RequestException as exception:
            self.message = str(exception)
            return False

        # Group of 2XX responses. In general we think its OK to mark URL as
        # reachable and exists
        if response.status_code // 100 == 2:
            self._text = response.text
            return True

        # redirections catching.
        if response.status_code // 100 == 3:
            raise DeadlinksRedirectionURL(response.headers['location'])

        self.message = str(response.status_code)
        return False

    def url(self) -> str:
        """ Return url based on abstraction, minus ending slash. """
        return self._url.geturl()

    def __str__(self) -> str:
        """ Converts URL object to string (actual URL). """
        return self.url()

    def __repr__(self) -> str:
        """ Object stringer representation. """

        return "{}<{}>".format(self.__class__.__name__, self.url())

    def _consume_links(self) -> None:
        """ Parse response text into list of links. """

        links = []
        for attr in __RE_LINKS__.findall(self._text):
            pos = attr.find("href=")
            if pos == -1:
                "href not found"
                continue

            href = attr[pos + 5:].strip()

            if not href:
                continue

            link = "" # type: str

            quoted = href[0] in {'"', "'"}
            if quoted:
                end_pos = href[1:].find(href[0])
                if end_pos == -1:
                    "unquoted link"
                    continue
                link = href[1:end_pos + 1]
            else:
                end_pos = href[0:].find(" ")
                link = href if end_pos == -1 else href[:end_pos + 1]

            if not link:
                "empty link"
                continue

            links.append(link)

        self._links = list(links)
        self._links = list(map(CLEANER, self._links))
        self._links = list(map(ANCHORS, self._links))
        self._links = list(map(UNESCPE, self._links))

    @property
    def links(self) -> List[str]:
        """ Return links found at the page. """

        if not self._text or self._links:
            return self._links

        self._consume_links()

        return list(set(self._links))

    def link(self, href: str) -> str:
        """
        Construct a full (“absolute”) URL by combining a
        “URL” object as base with another URL (url).

        avoiding using urljoin if self._url and href are same.
        """

        if self._url.geturl() == href:
            return href

        return urljoin(self._url.geturl(), href)


if __name__ == "__main__": # pragma: no cover
    urls = set()
    urls.add(URL("http://google.com"))
    urls.add(URL("http://google.com"))
    urls.add(URL("https://google.com"))

    print(len(urls), urls)
