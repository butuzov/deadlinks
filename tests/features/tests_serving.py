"""
tests.components.features.tests_serving.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Serving local files.

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

# -- Imports -------------------------------------------------------------------

import pytest

from deadlinks import DeadlinksSettingsRoot
from deadlinks.serving.router import Router
from deadlinks.serving.simple_server import SimpleServer

# -- Tests ---------------------------------------------------------------------


def test_servering(tmpdir):

    root = tmpdir.mkdir("html")
    s = SimpleServer(web_root=str(root))
    assert s.url() == str(s)


def test_router(tmpdir):
    root = tmpdir.mkdir("html")
    root.join("index.html").write("hola")
    root.join("_redirects").write(
        "\n".join([
            "/page-1.html /page-2.html 301",
            "# comment",
            "bad_url_forgotten",
            "/index.html / 301",
        ]))

    r = Router(str(root))

    robots_txt = root.join("robots.txt")
    robots_txt.write("User-agent: *\nDisallow: /")
    robots_txt_request = r('robots.txt')
    assert robots_txt_request[0] == 200
    assert robots_txt_request[1] == str(robots_txt)

    sitemap_txt_request = r('/sitemap.xml')
    assert sitemap_txt_request[0] == 404
    assert sitemap_txt_request[1] is None

    index_request = r('/index.html')
    assert index_request[0] == 301
    assert index_request[1] == '/'

    section_request = r('/section')
    assert section_request[0] == 301
    assert section_request[1] == '/section/'

    none_request = r('/nope.html')
    assert none_request[0] == 404
    assert none_request[1] is None


def test_router_dir_non_exists(tmpdir):
    tmpdir.remove()
    with pytest.raises(DeadlinksSettingsRoot):
        Router(tmpdir)


def test_router_dir_is_not_dir(tmpdir):
    index = tmpdir.join("index.html")
    index.write("hola")
    with pytest.raises(DeadlinksSettingsRoot):
        Router(str(index))
