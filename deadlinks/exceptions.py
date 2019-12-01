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
deadlinks.exceptions
~~~~~~~~~~~~~~~~~~~~

Exceptions used for deadlinks package.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Exceptions ----------------------------------------------------------------


class DeadlinksException(BaseException):
    """ General Exception. """


class DeadlinksRedirectionURL(DeadlinksException):
    """ Redicrection URL. """


class DeadlinksIgnoredURL(DeadlinksException):
    """ Error when we trying to index ignored URL. """


class DeadlinksSettings(DeadlinksException):
    """ Error on Settings object. """


class DeadlinksSettingsBase(DeadlinksSettings):
    """ Error on Settings object related to `BaseUrl` property. """


class DeadlinksSettingsRoot(DeadlinksSettings):
    """ Error on Setting Root directory """


class DeadlinksSettingsThreads(DeadlinksSettings):
    """ Error on Settings object related to `threads` property. """


class DeadlinksSettingsRetry(DeadlinksSettings):
    """ Error on Settings object related to `retry` property. """


class DeadlinksSettingsChange(DeadlinksSettings):
    """ Error on Settings object related to settings change. """


class DeadlinksSettingsDomains(DeadlinksSettings):
    """ Error on Settings object related to `IgnoredDomains` property """


class DeadlinksSettingsPathes(DeadlinksSettings):
    """ Error on Settings object related to `IgnoredPathes` property """


class DeadlinksSettingsPath(DeadlinksSettings):
    """ Error on Settings object related to `StayWithinPath` property """
