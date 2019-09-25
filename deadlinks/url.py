# standard library
from __future__ import annotations
from typing import List
from urllib.parse import urlparse, urljoin
import re

# library
from deadlinks.request import request

__RE_LINKS__ = re.compile("<a\s{1}([^>]+)>")   # pylint: disable=W1401

# filters
CLEANER = lambda x: x.strip("\"'\n ")   # removes quotes, spaces and new lines
ANCHORS = lambda x: x.split("#")[0]   # removed part after anchor


class URL:
    r""" URL provides URL abstraction

    """


    def __init__(self, location):
        self._url = urlparse(location)
        self._exists = False

        # some predefined states
        self._exists = None   # Is URL exists (assume 200 response)?
        self._text = None   # taxt place holder.
        self._referrers: List[str] = []   # list of refferers
        self._attempts: int = 0   # number of attempts we tryied to reach page.

        self._links: List[str] = []
        self._error: str = ""


    def is_valid(self):
        r"""checks if scheme and domain exists in url"""
        return self._url.scheme and self._url.netloc


    def add_referrer(self, url: str) -> None:
        r"""add a page that links to self object"""
        if url not in self._referrers:
            self._referrers.append(url)


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
            if isinstance(response.text, str):
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

            href = attr[pos + 5:]
            if not href:
                "empty href"
                continue

            link: str
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


    def is_external(self, url: URL) -> bool:
        """ compare domain and port """

        base_scheme, this_scheme = url._url.scheme, self._url.scheme
        base, this = url._url.netloc, self._url.netloc

        # we assiming that www.domain.com and domain.com are same
        ptrn = "www."
        base = base[len(ptrn):] if base.startswith(ptrn) else base
        this = this[len(ptrn):] if this.startswith(ptrn) else this

        # we assume that http://domain.com and http://domain.com:80/ are same
        if this_scheme == "http" and base_scheme == "http":
            ptrn = ":80"
            base = base[:-(len(ptrn))] if base.endswith(ptrn) else base
            this = this[:-(len(ptrn))] if this.endswith(ptrn) else this

        if this_scheme == "https" and base_scheme == "https":
            ptrn = ":443"
            base = base[:-(len(ptrn))] if base.endswith(ptrn) else base
            this = this[:-(len(ptrn))] if this.endswith(ptrn) else this

        return base != this


    def link(self, href: str) -> str:
        """
        Construct a full (“absolute”) URL by combining a
        “URL” object as base with another URL (url).

        note: we not going to use self.url() as it removes ending slash.
        """

        return urljoin(self._url.geturl(), href)


    def __hash__(self) -> int:
        """return hash of url object - url converted to string"""

        return hash(self.url())


    def __eq__(self, other: URL) -> bool:
        """compare two links"""

        return self.url() == other.url()


if __name__ == "__main__":   # pragma: no cover
    urls = set()
    urls.add(URL("http://google.com"))
    urls.add(URL("http://google.com"))
    urls.add(URL("https://google.com"))

    print(len(urls), urls)
