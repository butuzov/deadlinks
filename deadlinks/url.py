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

:copyright: (c) 2019 by Oleg Butuziv.
:license:   Apache2, see LICENSE for more details.
"""

# try:
#     from __future__ import annotations
# except SyntaxError:
#     URL = 'URL'

from typing import List

from urllib.parse import urlparse, urljoin
import re

# libraryr
from deadlinks.request import request

__RE_LINKS__ = re.compile("<a\s{1}([^>]+)>") # pylint: disable=W1401

# filters
CLEANER = lambda x: x.strip("\"'\n ") # removes quotes, spaces and new lines
ANCHORS = lambda x: x.split("#")[0] # removed part after anchor


class URL:
    r"""
    URL abstraction representation.
    """

    def __init__(self, location):
        self._url = urlparse(location)
        self._exists = False

        # some predefined states
        self._exists = None # Is URL exists (assume 200 response)?
        self._text = None # taxt place holder.
        self._referrers = [] # type: List[str]
        self._attempts = 0 # type: int
        self._links = [] # type: List[str]
        self._error = "" # type: str

    def is_valid(self):
        r"""checks if scheme and domain exists in url"""
        return self._url.scheme and self._url.netloc

    def add_referrer(self, url: str) -> None:
        r"""add a page that links to self object"""
        if url in self._referrers:
            return
        self._referrers.append(url)

    def get_refferers(self) -> List:
        return self._referrers

    def match_domains(self, domains) -> bool:
        """ match ignored pathes (argument pathes) to url.netloc"""
        for domain in domains:
            if domain in self._url.netloc:
                return True
        return False

    def match_pathes(self, pathes: List[str]) -> bool:
        """ match ignored pathes (argument pathes) to url.path"""
        for path in pathes:
            if path in self._url.path:
                return True
        return False

    def exists(self, is_external: bool = False, retries: int = 0):
        """ return "found" status of the page """

        if self._exists is not None:
            return self._exists

        self._attempts += 1

        try:
            response = request(self.url(), is_external, retries)
        except Exception as exception:
            self._exists = False
            self._error = exception
            return False

        # Group of 2XX responses. In general we think its OK to mark URL as
        # reachable and exists
        if response.status_code // 100 == 2:
            self._exists = True
            self._links = self._consume_links(response.text)
            return True

        self._exists = False
        self._error = response.status_code
        return False

    def error(self) -> str:
        """error to string"""
        return str(self._error)

    def url(self) -> str:
        """return url based on abstraction, minus ending slash"""

        return self._url.geturl().rstrip("/")

    def __str__(self) -> str:
        """stringer"""

        return self.url()

    def __repr__(self) -> str:
        """object stringer representation"""

        return "{}#{}<{}>".format(self.__class__.__name__, id(self), self.url())

    def _consume_links(self, text) -> List[str]:
        """ parse response text into list of links """

        links = []
        for attr in __RE_LINKS__.findall(text):
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

        return list(map(ANCHORS, map(CLEANER, links)))

    def get_links(self):
        """ return links found at the page """
        if not self._exists:
            return []
        return self._links

    def link(self, href: str) -> str:
        """
        Construct a full (“absolute”) URL by combining a
        “URL” object as base with another URL (url).

        note: we not going to use self.url() as it removes ending slash.
        """

        return urljoin(self._url.geturl(), href)


if __name__ == "__main__": # pragma: no cover
    urls = set()
    urls.add(URL("http://google.com"))
    urls.add(URL("http://google.com"))
    urls.add(URL("https://google.com"))

    print(len(urls), urls)
