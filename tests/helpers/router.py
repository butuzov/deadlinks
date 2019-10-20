from collections import defaultdict
from re import compile as _compile

PAGE_TEMPLATE = "<!DOCTYPE HTML><html><head>{0}</head><body>{1}</body></html>"


class Router:

    def __init__(self, router):
        self._pathes = defaultdict(lambda: 0)
        self._router = {}

        for path, data in router.items():
            self._router[_compile(path)] = data

    def handler(self, url):

        self._pathes[url] += 1

        for reg, _page in self._router.items():
            if not reg.search(url):
                continue

            param = _page()

            if self._pathes[url] <= param['unlocks']:
                return 503, 'text/html', '<h1>Service Unavailable</h1>'

            if param['redirects']:
                return 301, None, param['redirects']

            if param['exists']:
                return 200, param['mime_type'], param['content']

            return 404, param['mime_type'], param['content']

        return 404, 'text/html', '<h1>Page Not Found</h1>'
