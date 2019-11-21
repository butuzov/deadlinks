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
deadlinks.serving.router
~~~~~~~~~~~~~~~~~~~~~~~~

Implements simple file system lookups for web requests on generated docs.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (Union, Dict, Optional, Tuple)

from pathlib import Path
from collections import OrderedDict

from ..exceptions import DeadlinksSettingsRoot

# -- Implementation ------------------------------------------------------------

root_web_files = [
    '/robots.txt',
    '/favicon.ico',
    '/sitemap.xml',
]


class Router():
    """ Router for the static site  """

    def __init__(self, siteroot: Union[Path, str], sitepath: str) -> None:
        """ Transform startup params and load redirections. """

        if isinstance(siteroot, str):
            siteroot = Path(siteroot)

        self._siteroot = siteroot
        self._sitepath = sitepath

        # handle not found error.
        if not self._siteroot.exists():
            raise DeadlinksSettingsRoot("DocumentRoot not found")

        if not self._siteroot.is_dir():
            raise DeadlinksSettingsRoot("This is not a directory")

        # redirects
        self._redirects = OrderedDict() # type: Dict[str, str]
        self.load_redirects()

    def load_redirects(self) -> None:
        """  Supports only _redirects - docs.netlify.com/routing/redirects . """

        self._redirects_file = self._siteroot / "_redirects"

        if not self._redirects_file.exists():
            return

        with open(str(self._redirects_file)) as file:
            for line in file:
                if not line or line.strip() == "" or line[0] == "#":
                    continue

                p = line.split()
                if len(p) < 2:
                    continue

                self._redirects[p[0]] = p[1]

    def __call__(self, request_url: str) -> Tuple[int, Optional[str]]:
        """ Implements router logic. """

        # request_url is redirect
        if request_url in self._redirects:
            return (301, self._redirects[request_url])

        # requests for favicon, robots.txt and sitemap.xml
        if request_url in root_web_files:
            request_file = self._siteroot / request_url.lstrip("/")
            if request_file.is_file():
                return (200, str(request_file.resolve()))

            return (404, None)

        if request_url.startswith(self._sitepath):
            request_url = request_url[len(self._sitepath):]

        request_file = self._siteroot / request_url.lstrip("/")

        try_files = []

        if request_file.is_dir():
            try_files.append(request_file / "index.html")
            try_files.append(request_file / "index.htm")
        else:
            _path = str(request_file)
            try_files.append(Path(_path + ".html"))
            try_files.append(Path(_path + ".htm"))
            try_files.append(request_file)

        for file in try_files:
            if file.is_file():
                return (200, str(file))

        return (404, None)
