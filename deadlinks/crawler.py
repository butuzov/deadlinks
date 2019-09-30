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
from queue import Queue
import time

from typing import List

from deadlinks.link import Link
from deadlinks.index import Index
from deadlinks.settings import Settings


class Crawler:
    """ Crawler/Spider Application """

    def __init__(self, settings: Settings) -> None:
        r"""
        Accepts settings and assign them to the members
        in order to start crawling.
        """

        self.settings = settings
        self.index = Index()
        self._ignored = [] # type: List[Link]

        self.crawling = False
        self.queue = Queue() # type: Queue

        # Initialization of the Queue and Index
        self.add(settings.base)
        self.queue.put(settings.base)

        self.retry = settings.retry

    def start(self) -> None:
        r""" Starts the crawling process """

        if self.crawling:
            return

        self.crawling = True

        if self.settings.threads > 1:
            for idx in range(1, 1 + self.settings.threads):
                thread = Thread(target=self.indexer, args=[idx], daemon=True)
                thread.start()
            self.queue.join()
        else:
            self.indexer()

    def add(self, link: Link) -> None:
        """ Add link to index in order to keep links state. """
        self.index.add(link)

    def update(self, url: Link) -> None:
        """ Update state or the url by checking it's data. """

        # Is it external to website url?
        is_external = url.is_external(self.settings.base)

        # Add to index
        self.add(url)

        # item not exists, fallback.
        if not url.exists(is_external, retries=self.retry):
            return

        # no indexation for external resources
        if is_external:
            return

        for href in url.get_links():

            # Creating relative url
            link = Link(url.link(href)) # type: Link

            # If checking external links disabled, we return to next link in the loop
            if (not self.settings.external and \
                link.is_external(self.settings.base)):
                continue

            # If any ignored patterns found, we return to next link in the loop
            match_domains = link.match_domains(self.settings.domains)
            match_pathes = link.match_pathes(self.settings.pathes)
            if match_domains or match_pathes:
                self._ignored.append(link)
                continue

            # check if link is already indexed and update source of the link

            if link in self.index:
                continue

            # Add to index
            self.add(link)

            # add to index queue
            self.queue.put(link)

            # Update link source
            link.add_referrer(url.url())

    def ignores(self) -> bool:
        """ return "ignore" state of the crawler """
        ignore_domains = len(self.settings.domains) > 0
        ignore_pathes = len(self.settings.pathes) > 0
        return ignore_domains or ignore_pathes

    @property
    def ignored(self) -> List[Link]:
        """ Return URLs we have ignore to check. """
        return self._ignored

    @property
    def succeed(self) -> List[Link]:
        """ Return URLs we exists. """
        return self.index.succeed()

    @property
    def failed(self) -> List[Link]:
        """ Return URLs failed to exist. """
        return self.index.failed()

    def indexer(self, thread_number: int = 0) -> None:
        """ Runs indexation operation using piped source. """

        while True:
            while not self.queue.empty():
                url = self.queue.get()
                self.update(url)
                self.queue.task_done()
            else:

                if thread_number == 0:
                    break

                time.sleep(thread_number / 10)


if __name__ == "__main__":

    crawler = Crawler(
        Settings(
            "http://localhost:1313",
            check_external_urls=True,
            ignore_pathes=["issues/new", "edit/master", "commit/"],
            threads=10,
            retry=None,
        ),
    )
    crawler.start()
    print("added")
    print("RESULTS - TOTAL (", len(crawler.index), ")")

    print("Failed")
    for k, item in enumerate(crawler.index.failed()):
        print(k, " ", end=' ')
        print("{0!s:^8}\t{1}".format(item.exists(), item.url()))
        print(item.error())

    # print("Sussecced")
    # for k, item in enumerate(c.index.succeed()):
    #     print(k, " ", end=' ')
    #     print("{0!s:^8}\t{1}".format(item.exists(), item.url()))
