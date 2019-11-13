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
deadlinks.crawler
~~~~~~~~~~~~~~~~~

Crawl the links on from the provided start point.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from threading import Thread
from signal import (signal, SIGINT)
from queue import Queue
import time

from typing import (List, Tuple, Optional, Dict)
from types import FrameType

from deadlinks.link import Link
from deadlinks.status import Status
from deadlinks.index import Index
from deadlinks.settings import Settings
from deadlinks.exceptions import (
    DeadlinksIgnoredURL,
    DeadlinksRedicrectionURL,
)


class Crawler:
    """ Crawler/Spider Application """

    def __init__(self, settings: Settings) -> None:
        r"""
        Accepts settings and assign them to the members
        in order to start crawling.
        """

        self.settings = settings
        self.retry = settings.retry
        self.index = Index()

        # Application state
        self.terminated = False # type: bool
        self.crawling = False # type: bool
        self.crawled = False # type: bool
        self.queue = Queue() # type: Queue

        # Initialization of the Queue and Index
        self._base = settings.base

        # Checking if this is Ignored URL
        is_ignored, message = self.is_ignored(settings.base)
        if is_ignored:
            self._base.status = Status.IGNORED
            self._base.message = message
            error = "Issue with Base URL <{}>: {}"
            raise DeadlinksIgnoredURL(error.format(self._base.url(), message))

        self.add(self._base)

    def stop(self, sig: int, frame: FrameType) -> None:
        """ Capturs SIGINT signal and and change terminition state """
        self.terminated = True

    def terminition_watcher(self) -> None:
        """ Clears queue on teminated execution

        TODO: Test long term waiting page and terminition
        """

        while not self.terminated:
            time.sleep(0.01)

        while True:
            try:
                while not self.queue.empty():
                    self.queue.task_done()
                time.sleep(0.01)
            except ValueError:
                break

    def start(self) -> None:
        """ Starts the crawling process """

        if self.crawling or self.crawled or self.terminated:
            return

        self.crawling = True

        # catching kill signal.
        signal(SIGINT, self.stop)

        if self.settings.threads > 1:

            thread = Thread(target=self.terminition_watcher, daemon=True)
            thread.start()

            for idx in range(1, 1 + self.settings.threads):
                thread = Thread(target=self.indexer, args=[idx], daemon=True)
                thread.start()

            self.queue.join()
        else:
            self.indexer()

        self.crawling = False
        self.crawled = True

    def indexer(self, thread_number: int = 0) -> None:
        """ Indexation process """

        while True:
            while not self.terminated and not self.queue.empty():

                url = self.queue.get()
                self.update(url)
                self.queue.task_done()

            else:

                # catching terminated
                if self.terminated:
                    return

                # in case is its only 1 thread we NOT waiting for
                # new url to come.
                if thread_number == 0:
                    break

                # and we wait for fraction of second, if there are many threads.
                time.sleep(thread_number / 10)

    def add(self, link: Link) -> None:
        """ Queue URL """
        if link in self.index:
            return

        self.index.put(link)
        self.queue.put(link)

    def is_ignored(self, url: Link) -> Tuple[bool, Optional[str]]:
        """ Check if url can be ignored """

        # We can have few different cases when URL is ignored.

        # ok, checking for valid link first
        if not url.is_valid():
            return (True, "URL isn't valid")

        # TODO - Site Owner Ask (via meta tag) to ignore this URL
        # https://support.google.com/webmasters/answer/93710?hl=en

        # TODO - Site Owner Ask (via robota.txt) to ignore this URL
        # https://www.robotstxt.org/robotstxt.html

        # We have an external URL and cheking external URL are Off
        if url.is_external(self.settings.base) and not self.settings.external:
            return (True, "External indexation is Off")

        # This is a URL that fits to one of the ignored domains
        if url.match_domains(self.settings.domains):
            return (True, "Matching ignored domain")

        # This is a URL that fits to one of the ignored pathes
        if url.match_pathes(self.settings.pathes):
            return (True, "Matching ignored path")

        # FORBIDDEN: This is a local URL that located outside indexed path.
        if not url.is_external(self.settings.base) and  \
            self.settings.stay_within_path and not self._base.within(url):
            return (True, "URL outside of the allowed path")

        return (False, None)

    def update(self, url: Link) -> None:
        """ Update state or the url by checking it's data."""

        # We assume that URL Link that passed to this method is in status
        # Status.UNDEFINED, therefor we can perform required checks.
        if url in self.index:
            url = self.index[url]

        if url.status != Status.UNDEFINED:
            return

        # Adding URL to index so we can track its state.
        is_ignored, message = self.is_ignored(url)

        if is_ignored:
            self.index.update(url, Status.IGNORED, str(message))
            return

        try:
            # TODO - rething short calls implementation.
            is_external = url.is_external(self.settings.base)
            if not url.exists(is_external, retries=self.retry):
                self.index.update(url, Status.NOT_FOUND, url.message)
                return
        except DeadlinksRedicrectionURL as _href:
            # ok, so next time we looking for this
            # we will need to make lookup to redirected URL.
            self.index.update(url, Status.REDIRECTION, "")
            self.add_and_go(url, str(_href))
            return
        except DeadlinksIgnoredURL:
            # we catching this exception jic, but "it should never happen"
            return

        # we defining status of this url as FOUND
        self.index.update(url, Status.FOUND, "")

        for href in url.links:
            self.add_and_go(url, href)

    def add_and_go(self, url: Link, href: str) -> None:
        """ reducing code duplication"""

        # Create link variable of type Link that represent a new
        #    relative to URL link that has href
        link = Link(url.link(href)) # type: Link

        # adding it to queue
        self.add(link)

        # Update link by adding url as link referrer
        link.add_referrer(url.url())

    @property
    def ignored(self) -> List[Link]:
        """ Return URLs we have ignore to check. """
        return self.index.ignored()

    @property
    def succeed(self) -> List[Link]:
        """ Return URLs we exists. """
        return self.index.succeed()

    @property
    def failed(self) -> List[Link]:
        """ Return URLs failed to exist. """
        return self.index.failed()

    @property
    def redirected(self) -> List[Link]:
        """ Return URLs failed to exist. """
        return self.index.redirected()

    @property
    def stats(self) -> Dict[Status, int]:
        """ return crawler stats """
        return self.index.get_stats()


if __name__ == "__main__":

    crawler = Crawler(
        Settings(
            "http://localhost:1313/docs/azure/",
            check_external_urls=False,
            ignore_pathes=["issues/new", "edit/master", "commit/"],
            threads=10,
            retry=None,
        ),
    )
    crawler.start()
    print("RESULTS - TOTAL (", len(crawler.index), ")")

    print("All")
    for k, item in enumerate(crawler.index.succeed()):
        print("{0!s:^8}\t{1!s:^8}\t{2}\t{3}".format(k, item.status, item.url(), item.message))
