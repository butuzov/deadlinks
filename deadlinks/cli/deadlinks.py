#!/usr/bin/env python

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
deadlinks.cli.deadlinks
~~~~~~~~~~~~~~~~~~~~

Actual planned CLI.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

from sys import version_info
from sys import exit as _exit

_PYTHON_MIN = version_info[:2] >= (3, 5)

if not _PYTHON_MIN:
    _PYTHON_VER = ".".join(map(str, version_info[:2]))
    _ERROR = "ERROR: deadlinks requires a minimum of Python3 version 3.5. Current version: {}"
    raise SystemExit(_ERROR.format(_PYTHON_VER))


# -- app -------------------------------------------------------------------
def main():
    """ TODO """
    raise NotImplementedError("TODO: implement CLI")


if __name__ == "__main__":
    _exit(main())
