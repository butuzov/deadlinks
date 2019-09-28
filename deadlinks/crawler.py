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

from threading import Thread
from queue import Queue
import time

from typing import List

from .link import Link
from .index import Index
from .settings import Settings


class Crawler:
    r"""Runs Crawler logic"""

    def __init__(self, settings: Settings):
        r"""
        Accepts settings and assign them to the members
        in order to start crawling.
        """

        self.settings = settings
        self.index = Index()
        self._ignored = [] # type: List[Link]

        self.crawling = False
        self.queue = Queue()

        # Initialization of the Queue and Index
        self.add(settings.base)
        self.queue.put(settings.base)

        self.retry = settings.retry

    def crawl(self):
        r""" Starts the crawling process """

        if self.crawling:
            return

        self.crawling = True

        if self.settings.threads > 1:
            for i in range(1, 1 + self.settings.threads):
                t = Thread(target=self.indexer, args=[i], daemon=True)
                t.start()
            self.queue.join()
        else:
            self.indexer()

    def add(self, link: Link):
        r""" add link to indexed urls db in order to keep links state """

        self.index.add(link)

    def update(self, url: Link):
        r""" update state or the url by checking its data and other details."""

        # is it external to website url?
        is_external = url.is_external(self.settings.base)

        # add to index
        self.add(url)

        # item not exists, fallback.
        if not url.exists(is_external, retries=self.retry):
            return

        # no indexation for external resources
        if is_external:
            return

        for href in url.get_links():

            # creating relative url
            link = Link(url.link(href))

            # if checking external links disabled, we return to next link in the loop
            if (not self.settings.external and \
                link.is_external(self.settings.base)):
                continue

            # if any ignored patterns found, we return to next link in the loop
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

            # # update link source
            link.add_referrer(url.url())

    def ignored(self) -> List[Link]:
        return self._ignored

    def indexer(self, n=0) -> None:
        r""" runs indexation operation using piped source. """

        while True:
            while not self.queue.empty():
                url = self.queue.get()
                self.update(url)
                self.queue.task_done()
            else:

                if n == 0:
                    break

                time.sleep(n / 10)


if __name__ == "__main__":
    settings = Settings(
        "http://localhost:1313",
        check_external_urls=True,
        ignore_pathes=["issues/new", "edit/master", "commit/"],
        threads=10,
        retry=None,
    )
    c = Crawler(settings)
    c.crawl()
    print("added")
    print("RESULTS - TOTAL (", len(c.index), ")")

    print("Failed")
    for k, item in enumerate(c.index.failed()):
        print(k, " ", end=' ')
        print("{0!s:^8}\t{1}".format(item.exists(), item.url()))
        print(item.error())

    # print("Sussecced")
    # for k, item in enumerate(c.index.succeed()):
    #     print(k, " ", end=' ')
    #     print("{0!s:^8}\t{1}".format(item.exists(), item.url()))
