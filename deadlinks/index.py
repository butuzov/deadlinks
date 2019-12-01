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

from .link import Link
from .status import Status

# -- Implementation ------------------------------------------------------------


class Index:
    """ Links collection """

    def __init__(self) -> None:
        self._index = dict() # type: Dict[str, Link]
        self._stats = dict({
            Status.FOUND: 0,
            Status.NOT_FOUND: 0,
            Status.IGNORED: 0,
            Status.REDIRECTION: 0,
        })

    def __len__(self) -> int:
        """ Find out how many links in this index."""
        return len(self._index)

    def __iter__(self) -> Iterator[Link]:
        """ Iterating over a index. """
        return self._index.values().__iter__()

    def __contains__(self, link: Link) -> bool:
        """ Checks links existence in the index. """
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

        lmbd = lambda x: x.status != Status.UNDEFINED
        return self._filter(lmbd)

    def succeed(self) -> List[Link]:
        """ Filters succeed urls from index. """

        lmbd = lambda x: x.status == Status.FOUND
        return self._filter(lmbd)

    def redirected(self) -> List[Link]:
        """ Filters succeed urls from index. """

        lmbd = lambda x: x.status == Status.REDIRECTION
        return self._filter(lmbd)

    def failed(self) -> List[Link]:
        """ Filters failed urls from index. """

        lmbd = lambda x: x.status == Status.NOT_FOUND
        return self._filter(lmbd)

    def ignored(self) -> List[Link]:
        """ Filters failed urls from index. """

        lmbd = lambda x: x.status == Status.IGNORED
        return self._filter(lmbd)

    def undefined(self) -> List[Link]:
        """ Filters undefined urls from index. """

        lmbd = lambda x: x.status == Status.UNDEFINED
        return self._filter(lmbd)

    def update(self, url: Link, status: Status, message: str) -> None:
        """ wraps access to updating url status and gathering stats """

        if url not in self:
            return

        url.status = status
        url.message = message

        self._stats[status] += 1

    def get_stats(self) -> Dict[Status, int]:
        return self._stats

    def _filter(self, lambda_func: Callable[[Link], bool]) -> List[Link]:
        """ Filters  values according lambda. """
        return list(filter(lambda_func, self._index.values()))
