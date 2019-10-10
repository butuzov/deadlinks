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

from typing import (Dict, List, Iterator, Callable) #pylint: disable-msg=W0611

from deadlinks.link import Link
from deadlinks.status import Status


class Index:
    r""" Links collection """

    def __init__(self) -> None:
        self._index = dict() # type: Dict[str, Link]

    def __len__(self) -> int:
        """ Find out how many links in this index."""
        return len(self._index)

    def __iter__(self) -> Iterator[Link]:
        """ Iterating over a index. """
        return self._index.values().__iter__()

    def __contains__(self, link: Link) -> bool:
        """ Checks links existance in the index. """
        return link.url() in self._index

    def __getitem__(self, link: Link) -> Link:
        """ """
        return self._index[link.url()]

    def put(self, link: Link) -> None:
        """ Puts a link to the index. """
        if link.url() in self._index:
            return
        self._index[link.url()] = link

    def all(self) -> List[Link]:
        """ Return links in the index (but not UNDEFINED). """
        return self._filter(lambda x: x.status != Status.UNDEFINED)

    def succeed(self) -> List[Link]:
        """ Filters succeed urls from index. """
        return self._filter(lambda x: x.status == Status.FOUND)

    def failed(self) -> List[Link]:
        """ Filters failed urls from index. """
        return self._filter(lambda x: x.status == Status.NOT_FOUND)

    def ignored(self) -> List[Link]:
        """ Filters failed urls from index. """
        return self._filter(lambda x: x.status == Status.IGNORED)

    def undefined(self) -> List[Link]:
        """ Filters undefined urls from index. """
        return self._filter(lambda x: x.status == Status.UNDEFINED)

    def _filter(self, lambda_func: Callable[[Link], bool]) -> List[Link]:
        """ Filters  values according lambda. """
        return list(filter(lambda_func, self._index.values()))
