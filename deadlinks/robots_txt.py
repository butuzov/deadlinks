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
from typing import Dict, Optional
from collections import defaultdict

from reppy.robots import Robots
from reppy.exceptions import ReppyException

from .url import URL


class RobotsTxt:

    def __init__(self, *, user_agent: str) -> None:
        self._robots = defaultdict(Robots) # type: Dict[str, Optional[Robots]]
        self._user_agent = user_agent # type: str
        # self._robots = None # type: Robots

    def allowed(self, url: URL) -> bool:

        if url.domain not in self._robots:
            self._retrieve(url)

        return bool(self._robots[url.domain].allowed(str(url), self._user_agent))

    def _retrieve(self, url: URL) -> None:
        """ Perform robots.txt request """
        robots_txt_link = url.link("/robots.txt")
        try:
            self._robots[url.domain] = Robots.fetch(robots_txt_link)
        except ReppyException:
            self._robots[url.domain] = Robots.parse(robots_txt_link, "")
