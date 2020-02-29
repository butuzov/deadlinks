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
from typing import (Any)

from reppy.robots import Robots
from reppy.exceptions import ReppyException

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
        if self.state is False:
            return True

        return bool(self.state.allowed(str(url), user_agent))

    def request(self, url: str) -> None:
        """ Perform robots.txt request """
        if not (self.state is None):
            return

        try:
            self.state = Robots.fetch(url)

        except ReppyException:
            self.state = False
