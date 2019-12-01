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
deadlinks.baseurl
~~~~~~~~~~~~~~~~~

Starting Point URL or BaseURL

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

from .link import Link


class BaseURL(Link):
    """ BaseURL propose to allow subpath check for provided link

        Having this class allow us to pass responsibility for
        "checking" of within class to it, instead adding this functionality
        to crawler or Link.
    """

    def __init__(self, url: str) -> None:
        super().__init__(url)
        self._path = self.get_base_path()

    def get_base_path(self) -> str:
        file = self.path.split("/")[-1]
        if "." in file:
            return self.path[:(len(self.path) - len(file))]

        return self.path

    def within(self, link: Link) -> bool:
        """ determite is `link` argument stays within path of baseurl """

        if link.is_external(self):
            return False

        return link.path.startswith(self._path.rstrip("/"))


if __name__ == "__main__":

    b1 = BaseURL("http://google.com/somepath/index.html")
    print(b1.within(Link("http://google.com/somepath/specs.html")))

    b2 = BaseURL("http://google.com/index.html")
    print(b2.within(Link("http://google.com/somepath/specs.html")))

    b3 = BaseURL("http://google.com/")
    print(b3.within(Link("http://google.com/somepath/specs.html")))
