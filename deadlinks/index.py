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
deadlinks.index
~~~~~~~~~~~~~~~

Provides a collection interface

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (Set, List, Iterator)

from deadlinks.link import Link


class Index:
    r""" Links collection """

    def __init__(self) -> None:
        self._index = set() # type: Set[Link]

    def __len__(self) -> int:
        """ Find out how many links in this index."""
        return len(self._index)

    def __iter__(self) -> Iterator[Link]:
        """ Iterating over a index. """
        return iter(self._index)

    def __contains__(self, link: Link) -> bool:
        """ Checks links existance in the index. """
        return link in self._index

    def put(self, link: Link) -> None:
        """ Puts a link to the index. """
        self._index.add(link)

    def add(self, link: Link) -> None:
        """ Alias of the puts method. """
        return self.put(link)

    def all(self) -> List[Link]:
        """ Return links in the index. """
        return list(self._index)

    def succeed(self) -> List[Link]:
        """ Filters succeed urls from index. """
        return list(filter(lambda x: x.exists(), self))

    def failed(self) -> List[Link]:
        """ Filters failed urls from index. """
        return list(filter(lambda x: not x.exists(), self))
