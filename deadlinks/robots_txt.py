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
deadlinks.request
~~~~~~~~~~~~~~~~~

`requests` wrapper for getting requests.Response

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------
from typing import Any, List, Tuple
from urllib.robotparser import RobotFileParser

from .request import user_agent
from .url import URL


class RobotsTxt:

    def __init__(self) -> None:
        self.state = None # type: Any

    def allowed(self, url: URL) -> bool:

        # We don't have info about this domain for now, so we going to request
        # robots.txt
        if self.state is None:
            self.request(url.link("/robots.txt"))

        # We actually can't find out is there robots.txt or not
        # so we going to allow all in this case.
        if self.state is False or self.state.allow_all:
            return True

        if not self.state.last_checked and self.state.disallow_all:
            return False

        # find entry
        return allowed(matched_rules(self._entry(), url))

    def request(self, url: str) -> None:
        """ Perform robots.txt request """
        if self.state is not None:
            return

        try:
            self.state = RobotFileParser()
            self.state.set_url(url)
            self.state.read()

        except Exception:
            self.state = False

    # This is mostly transferred logics from robotparser.py,
    # but we trying to follow 2019 extension of the Google's Robots Txt
    # protocol and allow, disallowed pathes.
    # https://www.contentkingapp.com/blog/implications-of-new-robots-txt-rfc/
    # https://tools.ietf.org/html/draft-koster-rep-04

    def _entry(self) -> Any:

        for entry in self.state.entries:
            if entry.applies_to(user_agent):
                return entry

        return self.state.default_entry


def matched_rules(entry: Any, url: URL) -> List[Tuple[bool, str]]:
    result: List[Tuple[bool, str]] = []

    path = url.path
    if not path:
        path = "/"

    for line in entry.rulelines:
        if not line.applies_to(path):
            continue

        if len(line.path) > len(path):
            continue

        result.append((
            line.allowance,
            line.path,
        ))

    return sorted(result, key=lambda x: x[1])


def allowed(rules: List[Tuple[bool, str]]) -> bool:

    if not rules:
        return True

    return rules[-1][0]
