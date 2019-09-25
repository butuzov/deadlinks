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

r"""
deadlinks.index

"""

from typing import Set, List
from deadlinks.url import URL


class Index:

    _index: Set[URL] = set()


    def __init__(self):

        self._index: Set[URL] = set()


    def __len__(self):
        return len(self._index)


    def __iter__(self):
        return iter(self._index)


    def __contains__(self, link: URL) -> bool:
        return link in self._index


    def put(self, link: URL) -> None:
        r""" puts new links into the index """

        self._index.add(link)


    def add(self, link: URL) -> None:
        r""" alias of the put """

        return self.put(link)


    def all(self) -> Set[URL]:
        r""" return all index urls """

        return self._index


    def succeed(self) -> List[URL]:
        """filters failed urls from all db"""

        return list(filter(lambda x: x.exists(), self._index))


    def failed(self) -> List[URL]:
        """filters failed urls from all db"""

        return list(filter(lambda x: not x.exists(), self._index))
