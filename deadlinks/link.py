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
deadlinks.link
~~~~~~~~~~~~~~

Link representation based on URL object.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import Union

from .url import URL


class Link(URL):
    """
    Link URL with benefits

    Real reason why this exists, it's impossible situation on using class as
    type definition, in one (two) of the methods.

    In Python 3.5 its OK to use quoted class name.
    In Python 3.6 we can import annotations from __future__
    What we can't do is to try catch, python version handling or
    `__future__ import` as this is compile time operation. Therefore,
    lets use Link.
    """

    def is_external(self, url: Union[URL, str]) -> bool:
        """ Check if url is external to Link object. """

        if isinstance(url, str):
            url = URL(url)
        elif not isinstance(url, URL):
            raise TypeError("url of type {}".format(type(url)))

        base_scheme, this_scheme = url.scheme, self.scheme
        base, this = url.domain, self.domain

        # we assuming that www.domain.com and domain.com are same
        pattern = "www."
        base = base[len(pattern):] if base.startswith(pattern) else base
        this = this[len(pattern):] if this.startswith(pattern) else this

        # we assume that http://domain.com and http://domain.com:80/ are same
        if this_scheme == "http" and base_scheme == "http":
            pattern = ":80"
            base = base[:-(len(pattern))] if base.endswith(pattern) else base
            this = this[:-(len(pattern))] if this.endswith(pattern) else this
        elif this_scheme == "https" and base_scheme == "https":
            pattern = ":443"
            base = base[:-(len(pattern))] if base.endswith(pattern) else base
            this = this[:-(len(pattern))] if this.endswith(pattern) else this

        return base != this

    def __eq__(self, other: object) -> bool:
        """ Compare two links. """

        if isinstance(other, str):
            other = Link(other)

        if not isinstance(other, URL):
            raise TypeError("`url` expected to be str or Link ")

        return self.url() == other.url()
