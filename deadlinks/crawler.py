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

What it should be doing

:copyright: (c) 2019 by Oleg Butuziv.
:license:   Apache2, see LICENSE for more details.
"""

from typing import Set

from threading import Thread
from queue import Queue
import time

from deadlinks.url import URL
from deadlinks.index import Index
from deadlinks.settings import Settings


class Crawler:

    r"""Runs Crawler logic"""


    def __init__(self, settings: Settings):
        r"""
        Accepts settings and assign them to the members
        in order to start crawling.
        """

        self.settings = settings
        self.index = Index()

        self.crawling = False
        self.queue = Queue()

        # Initialization of the Queue and Index
        self.add(settings.get_base_url())
        self.queue.put(settings.get_base_url())

        self.threads = settings.threads()
        self.retry = settings.retries()


    def crawl(self):
        r""" Starts the crawling process """

        if self.crawling:
            return

        self.crawling = True
        if self.threads > 1:
            for i in range(1, 1 + self.threads):
                t = Thread(target=self.indexer, args=[i], daemon=True)
                t.start()
            self.queue.join()
        else:
            self.indexer()


    def add(self, link: URL):
        r""" add link to indexed urls db in order to keep links state """

        self.index.add(link)


    def update(self, url):
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

            # so we building here a URL object for combined urls of
            # url and additional part suplied by href
            link = URL(url.link(href))

            # if checking external links disabled, we return to next link in the loop
            if (not self.settings.index_external() and
                    link.is_external(self.settings.base)):
                continue

            # if any ignored patterns found, we return to next link in the loop
            match_domains = link.match_domains(self.settings.ignored("domains"))
            match_pathes = link.match_pathes(self.settings.ignored("pathes"))
            if match_domains or match_pathes:
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
