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
deadlinks.serving.options
~~~~~~~~~~~~~~~~~~~~~~~~~

Default options to be consumed by click if `internal` domain passed.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from typing import List

from click import Path

from ..clicker import OptionRaw, Options #pylint: disable-msg=W0611

# -- Code ----------------------------------------------------------------------

default_options = [] # type: List[OptionRaw]
# root, in case of URL<internal>, defaults to . (pwd or current directory)
default_options.append((
    ('root', '-R', '--root'),
    {
        'help': 'Path to the documentation\'s Document Root',
        'metavar': '',
        'type': Path()
    },
))
