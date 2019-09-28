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

r"""
deadlinks.request

"""

import requests

from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def request(url: str, is_external: bool = False, total_retries_attempts: int = 1):
    r"""request a internet resourse N times using get or head methods


    """
    session = Session()

    session.mount(
        url,
        HTTPAdapter(
            max_retries=Retry(
                total=total_retries_attempts, backoff_factor=1, status_forcelist=[502, 503, 504])))

    return (session.head if is_external else session.get)(url, allow_redirects=True)
