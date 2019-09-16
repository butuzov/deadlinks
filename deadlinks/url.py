from urllib.parse import urlparse, urljoin
from re import compile
from typing import List, Callable

import requests


class URL:

    def __init__(self, location):
        self._url = urlparse(location)
        self._exists = False
        # do i really need it?
        self._reachable = False
        self._text = None
        # url cleaners

        self.filter_clean = lambda x: x.strip("\"'\n ")
        self.filter_noachor = lambda x: x.strip("\"'\n ")
        self.re_links: Callable = compile("<a([^>]+)>")

    def is_valid(self):
        """deines url valid if scheme and netloc present"""
        return self._url.scheme and self._url.netloc

    def match_domains(self, domains):
        """ match ignored pathes (argument pathes) to url.netloc"""

        for domain in domains:
            if domain in self._url.netloc:
                return True
        return False

    def match_pathes(self, pathes: List[str]):
        """ match ignored pathes (argument pathes) to url.path"""

        for path in pathes:
            if path in self._url.path:
                return True
        return False

    def exists(self, is_external: bool = False):
        """ return "found" status of the page """

        if self._exists:
            return self._exists

        print("after check", self.url())

        # TODO - more flexible try catch strategy
        try:
            resp = (requests.head if is_external else requests.get)(self.url())
            response_group = resp.status_code // 100
        except requests.exceptions.SSLError:
            self._exists = False
            return False
        except requests.exceptions.MissingSchema:
            self._exists = False
            return False
        except requests.exceptions.ConnectionError:
            self._exists = False
            return False
        except requests.exceptions.InvalidURL:
            self._exists = False
            return False

        # Group 20X, OK
        # - change status to Found.
        # - grab links if internal url
        if response_group == 2:
            self._exists = True
            self._reachable = True
            if resp.text:
                self._links = self._consume_links(resp.text)
            return True

        # dummy
        self._exists = False
        return self._exists

    def url(self) -> str:
        """return url based on abstraction, minus ending slash"""
        return self._url.geturl().rstrip("/")

    def __str__(self) -> str:
        """stringer"""
        return self.url()

    def _consume_links(self, text) -> List[str]:
        """ parse response text into list of links """

        links = []
        for attr in self.re_links.findall(text):
            links += [
                s.split("=")[1:][0]
                for s in attr.split(" ")
                if s[0:5] == "href="
            ]

        return list(map(self.filter_noachor, map(self.filter_clean, links)))

    def get_links(self):
        """ return links found at the page """
        if not self._exists:
            return []
        return self._links

    def is_external(self, url) -> bool:
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

    def link(self, url) -> str:
        """
        Construct a full (“absolute”) URL by combining a
        “URL” object as base with another URL (url).

        note: we not going to use self.url() as it removes ending slash.
        """

        return urljoin(self._url.geturl(), url)
