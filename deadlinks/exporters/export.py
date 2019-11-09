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
deadlinks.exporters.export
~~~~~~~~~~~~~~~~~~~~~~~~~

Abstract Interface we will ask to implemnt child classes.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from abc import ABC, abstractmethod
from typing import (Dict, List, Tuple, Any)

from ..crawler import Crawler
"""
class Sample(Export):

    def __init__(self, crawler: Crawler, **opts: Dict) -> None:
        self._crawler = crawler
        self._opts = opts

    def report(self) -> None:
        print("Total", len(self._crawler.index))

"""


class Export(ABC):

    @abstractmethod
    def __init__(self, crawler: Crawler, **opts: Dict) -> None:
        """ you need to implement init method """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def options() -> Tuple[str, List[Tuple[Tuple[str], Dict[str, Any]]]]:
        """ you need to implement report method """
        raise NotImplementedError

    @abstractmethod
    def report(self) -> None:
        """ you need to implement report method """
        raise NotImplementedError
