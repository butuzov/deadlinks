r"""
deadlinks.request

"""

import requests

from requests import Session
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


def request(
        url: str, is_external: bool = False, total_retries_attempts: int = 1
):
    r"""request a internet resourse N times using get or head methods


    """
    session = Session()

    session.mount(
        url,
        HTTPAdapter(
            max_retries=Retry(
                total=total_retries_attempts,
                backoff_factor=1,
                status_forcelist=[502, 503, 504]
            )
        )
    )

    return (session.head if is_external else session.get
            )(url, allow_redirects=True)
