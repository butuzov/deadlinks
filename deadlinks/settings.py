from urllib.parse import urlparse
from deadlinks.url import URL


class Settings:

    """ handles general settings for """

    def __init__(
            self,
            url,
            check_external_urls=False,
            mirror=None,
            ignore_domains=[],
            ignore_pathes=[],
            retry=None,
            threads=None,
    ):

        # general settings
        self.index_external_urls = check_external_urls
        self._ignore_domains = ignore_domains
        self._ignore_pathes = ignore_pathes
        self._mirror = mirror

        # baseurl
        self.base = URL(url)
        if not self.base.is_valid():
            raise Exception("fuck")

        match_domains = self.base.match_domains(self.ignored("domains"))
        match_pathes = self.base.match_pathes(self.ignored("pathes"))
        if match_domains or match_pathes:
            raise Exception(
                "Baseurl {} matchs one of the ignore pattern".format(self.base)
            )

        # retry validation
        if retry is None:
            self._retry = 0
        elif isinstance(retry, int):
            if 0 <= retry <= 10:
                self._retry = retry
            else:
                raise Exception((
                    'Setting "retry" out of the allowed range. '
                    'allowed value from 0 to 10'
                ).format(retry))
        else:
            raise Exception(
                'Setting "retry" isn\'t a number ({})'.format(retry)
            )

        # threads
        if threads is None:
            self._threads = 1
        elif isinstance(threads, int):
            if 1 <= threads <= 10:
                self._threads = threads
            else:
                raise Exception((
                    'Setting "threads" out of the allowed range. '
                    'allowed value from 1 to 10'
                ).format(threads))
        else:
            raise Exception(
                'Setting "threads" isn\'t a number ({})'.format(threads)
            )

    def index_external(self):
        return self.index_external_urls

    def ignored(self, what="domains"):
        if what == "domains":
            return self._ignore_domains

        if what == "pathes":
            return self._ignore_pathes

        raise UnknownIgnoreType('"Uknown ignore setting - "{}"'.format(what))

    def threads(self):
        return self._threads

    def retries(self):
        return self._retry

    def get_base_url(self):
        return self.base


if __name__ == "__main__":
    s = Settings(
        "http://localhost:1313/data/new",
        retry=None,
        ignore_domains=[],
        ignore_pathes=[],
        threads=2,
    )
    print("Base Url", s.get_base_url())
    print("External_Urls", s.index_external())
    print("Ignore_Domains", s.ignored("domains"))
    print("Ignore_Pathes", s.ignored("pathes"))
    print("Threads", s.threads())
    print("Retries", s.retries())
