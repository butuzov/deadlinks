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

from requests import Session, Response
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .__version__ import __app_version__ as version
from .__version__ import __app_website__ as website
from .__version__ import __app_package__ as package


def request(url: str, is_external: bool = False, retries_attempts: int = 1) -> Response:
    """Request a web resource and return Response

    Perform GET  - for the local resource
            HEAD - for the remote resource
    Return Response of the request.
    """

    _headers = {
        'User-agent': "{}/v{} ( {} )".format(package, version, website),
    }
    _settings = {
        'allow_redirects': False,
    }

    _retry = Retry(
        total=retries_attempts,
        backoff_factor=1,
        status_forcelist=[502, 503, 504],
    )

    session = Session()
    session.mount(url, HTTPAdapter(max_retries=_retry))

    method_to_call = (session.head if is_external else session.get)
    return method_to_call(url, headers=_headers, **_settings)
