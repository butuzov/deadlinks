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
deadlinks.__init__
~~~~~~~~~~~~~~~~~~

deadlinks module __init__ file

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from .url import URL
from .link import Link
from .index import Index
from .baseurl import BaseURL
from .crawler import Crawler
from .request import request
from .settings import Settings

from .__version__ import __version__ as version

# -- Exports  ------------------------------------------------------------------

from .exceptions import (
    DeadlinksIgnoredURL,
    DeadlinksSettingsThreads,
    DeadlinksSettingsBase,
    DeadlinksSettingsRetry,
    DeadlinksSettingsChange,
    DeadlinksSettingsDomains,
    DeadlinksSettingsPathes,
    DeadlinksSettingsPath,
)

__all__ = [
    'version',

    # App
    'URL',
    'Link',
    'BaseURL',
    'Index',
    'Crawler',
    'request',
    'Settings',

    # Exceptions
    'DeadlinksIgnoredURL',
    'DeadlinksSettingsThreads',
    'DeadlinksSettingsBase',
    'DeadlinksSettingsRetry',
    'DeadlinksSettingsChange',
    'DeadlinksSettingsDomains',
    'DeadlinksSettingsPathes',
    'DeadlinksSettingsPath',
]
