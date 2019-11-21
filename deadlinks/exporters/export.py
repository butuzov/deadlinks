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
~~~~~~~~~~~~~~~~~~~~~~~~~~

Abstract Interface we will ask to implement child classes.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import (Dict, Tuple)
from abc import ABC, abstractmethod

from ..crawler import Crawler
from ..clicker import OptionsList

# -- Abstract ------------------------------------------------------------------


class Export(ABC):

    @abstractmethod
    def __init__(self, crawler: Crawler, **opts: Dict) -> None:
        """ you need to implement init method """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def options() -> Tuple[str, OptionsList]:
        """ you need to implement report method """
        raise NotImplementedError

    @abstractmethod
    def report(self) -> None:
        """ you need to implement report method """
        raise NotImplementedError
