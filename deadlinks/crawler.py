from urllib.parse import urlparse, urljoin
from threading import Thread
from queue import Queue

from deadlinks.url import URL
from deadlinks.settings import Settings


class Crawler:
    """
    Crawler - achives crawling logic
    """

    indexing = False
    queue = Queue()
    indexed_links = dict()

    def __init__(self, settings: Settings):
        self.settings = settings
        self.queue.put(settings.get_base_url())
        self.threads = settings.threads()
        self.retry = settings.retries()

    def index(self):
        if self.indexing:
            return

        self.indexing = True
        if self.threads > 1:
            self._start()
        else:
            self.indexer()

    def indexed(self, url: URL) -> bool:
        return url.url() in self.indexed_links

    def add_to_index(self, url: URL) -> URL:
        data = {'href': url, 'source': [], 'attempt': 0}
        self.indexed_links.update({url.url(): data})
        return data["href"]

    def update_link_source(self, link, source_page):
        data = self.indexed_links.get(link.url())
        data['source'].append(source_page)
        self.indexed_links.update({link.url(): data})

    def update(self, url):

        # we not going to check links of external links
        # print("is_external", url.url(), url.is_external(self.settings.base))
        if url.is_external(self.settings.base):
            return

        for href in url.get_links():
            link = URL(url.link(href))

            # checking external links is disabled, and current link
            # is external, so we skipping it.
            if not self.settings.index_external() and \
                link.is_external(self.settings.base):
                continue

            # does this url match a ignored patterns?
            match_domains = link.match_domains(self.settings.ignored("domains"))
            match_pathes = link.match_pathes(self.settings.ignored("pathes"))
            if match_domains or match_pathes:
                continue

            # check if link is already indexed and update source of the link
            if not self.indexed(link):
                self.add_to_index(link)
                print(url.url(), "=>", link.url())
                self.queue.put(link)

            # update link source
            self.update_link_source(link, url.url())

    def get_index(self):
        """ return index information """
        return self.indexed_links

    def remove(self, url):
        """ removes or reschedule url """
        # check if retries are limited
        if not self.settings.retries():
            return

        # check data we have in indexed links
        data = self.indexed_links.get(url.url())
        data['attempt'] += 1
        self.indexed_links.update({url.url(): data})

        # TODO = make more elegant reschedule, maybe with time intervals.
        if data['attempt'] < self.settings.retries():
            self.queue.put(url)

    def indexer(self) -> None:
        """ actual indexer, run untill queue is empty """

        while not self.queue.empty():
            url = self.queue.get()

            is_external = url.is_external(self.settings.base)

            if url.exists(is_external):
                self.update(url)
            else:
                self.remove(url)

            self.queue.task_done()

    def _start(self) -> None:
        """ multi threaded indexer """

        for _ in range(self.threads):
            t = Thread(target=self.indexer, daemon=True)
            t.start()
        self.queue.join()


if __name__ == "__main__":
    settings = Settings(
        "http://localhost:1313",
        check_external_urls=True,
        ignore_pathes=["issues/new", "edit/master", "commit/"],
        threads=10,
        retry=0,
    )
    c = Crawler(settings)
    c.index()
    print("recheck", len(c.get_index()))
    for link, data in c.get_index().items():
        if not data["href"].exists():
            print(data["href"].exists(), link)
