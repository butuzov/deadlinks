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
deadlinks.main
~~~~~~~~~~~~~~~~~

main (cli interface)

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# package meta data
__app_version__ = "0.2.0"
__app_package__ = "deadlinks"
__app_license__ = "Apache License 2.0"
__app_website__ = "https://github.com/butuzov/deadlinks"
__description__ = "CLI/API for links liveness checking."
__author_name__ = "Oleg Butuzov"
__author_mail__ = "butuzov@made.ua"

# for development proposes (docker butuzov/deadlinks:dev images)

try:
    from .__develop__ import version
    __app_version__ += version
except ImportError:
    pass

# backwards compatibility
__version__ = __app_version__
