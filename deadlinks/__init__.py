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

from deadlinks.url import URL
from deadlinks.help import CLI
from deadlinks.link import Link
from deadlinks.index import Index
from deadlinks.crawler import Crawler
from deadlinks.request import request
from deadlinks.settings import Settings

from deadlinks.exceptions import (
    DeadlinksIgnoredURL,
    DeadlinksSettingsThreads,
    DeadlinksSettingsBase,
    DeadlinksSettingsRetry,
    DeadlinksSettingsChange,
    DeadlinksSettingsDomains,
    DeadlinksSettingsPathes,
    DeadlinksSettingsPath,
)

# package meta data
__app_version__ = "0.0.1"
__app_package__ = "deadlinks"
__app_license__ = "Apache License 2.0"
__app_website__ = "https://github.com/butuzov/deadlinks"
__description__ = "CLI/API for links liveness checking."
__author_name__ = "Oleg Butuzov"
__author_mail__ = "butuzov@made.ua"

# backwards compatibility
__version__ = __app_version__

__all__ = [
    "URL",
    "CLI",
    "Link",
    "Index",
    "Crawler",
    "request",
    "Settings",

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
