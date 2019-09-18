r"""
deadlinks.request

"""

import requests


def request(url: str, is_external: bool = False, retries: int = 1):
    r"""request a internet resourse N times using get or head methods


    """
    session = requests.Session()
    session.mount(url, requests.adapters.HTTPAdapter(max_retries=retries))

    return (session.head if is_external else session.get)(url, allow_redirects=True)
