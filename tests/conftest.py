"""
conftest.py
~~~~~~~~~~~

Provides Default fixtures for deadlinks tests

:copyright: (c) 2019 by Oleg Butuzov.
:license:   Apache2, see LICENSE for more details.
"""

import pytest

from textwrap import dedent
from collections import OrderedDict

from .utils import Server, Page
from .runners.click import ClickRunner
from .runners.docker import DockerRunner
from .runners.brew import BrewRunner

runners = OrderedDict({
    'click': ClickRunner,
    'docker': DockerRunner,
    'brew': BrewRunner,
})


@pytest.fixture(scope="session", params=list(runners.values()), ids=list(runners.keys()))
def runner(request):
    """ Invoke standalone/internal cli interface(s) """

    runner = request.param()
    yield runner
    del runner


@pytest.fixture
def server():
    s = Server()
    yield s
    s.destroy()


@pytest.fixture
def servers():
    s1 = Server()
    s2 = Server()
    yield (s1, s2)
    s1.destroy()
    s2.destroy()


@pytest.fixture
def simple_site(server):
    """ simple configuration for routing and indexation testing
        easy to calculate what addresses will work and whats not.
        path       status        external       internal
        /           200          0              2
        /about      200          2              0
        /projects   200          3              1 (not existing)
    """
    INDEX_PAGE = dedent(
        """\
            <h1>~ <a href="/">/index</a> - <a href="/about/">/about</a> - <a href="/projects/">/projects</a></h1>
            <h1>hello all</h1>
        """)

    ABOUT_PAGE = dedent(
        """\
        <h1>~ <a href="/">/index</a> - <strong>/about</strong> - <a href="/projects/">/projects</a></h1>
        <hr>
        <a href="https://github.com/butuzov">github.com</a> -
        <a href="http://made.ua">made.ua</a>
        </ul>
        """)

    PROJECTS_PAGE = dedent(
        """\
        <h1>~ <a href="/">/index</a> - <a href="/about/">/about</a> - <strong>/projects</strong></h1>
        <hr>
        <a href="https://github.com/butuzov/deadlinks">deadlinks</a> -
        <a href="https://gobyexample.com">gobyexample</a> -
        <a href="http://gobyexample.com.ua">gobyexample</a> -
        <a href="https://wordpress.org/plugins/debug-bar-rewrite-rules">(wordpress) debug bar rewrite rules</a> -
        <a href="nope-no-such-page">secret project</a>
        </ul>
        """)

    return server.router({
        '^/$': Page(INDEX_PAGE).exists(),
        "^/about/?$": Page(ABOUT_PAGE).exists(),
        "^/projects/?$": Page(PROJECTS_PAGE).exists(),
    })


@pytest.fixture
def site_with_links(server):
    INDEX_PAGE = dedent(
        """\
            <b>arguments</b><br/>
            <a href="link-01">(1) existing link</a>
            <a style="color:#f00;"href="link-02">(2)existing link</a>
            <a href="link-03"style="background:#f00;">(3) existing link</a>
            <hr>
            <a href='link-04'>(5) existing link</a>
            <a style='background:#f00;'href='link-05'>(5) existing link</a>
            <a href="link-06"style='background:#f00;'>(6) existing link</a>
            <hr>
            <a href=link-07>(7) existing link</a>
            <a style=background:#f00; href=link-08>(8) existing link</a>
            <a href=link-09 style=background:#f00;>(9) existing link</a>
            <hr>coverage run --source jedi -m py.test
            <b>relative links</b><br/>
            <a href=/link-10>(10)existing link</a>
            <a href="/link-11">(11)existing link</a>
            <a href='/link-12'>(12)existing link</a>
            <hr>
            <b>two in one out</b><br/>
            <a href='/link-13'href='/link-13.1'>(13)existing link #10</a>
            <a href='/link-14' href='/link-14.1'>(14)existing link #10</a>
            <hr>
            <b>not existing links</b><br/>
            <ahref=link-6 style=background:#f00;>this isn't a link at all</a>
            <a onclick="this.location=http://google.com">js</a>
            <a href>just href</a>
            <a href=''>just href</a>
            <a href=''>just href</a>
            <a href="">just href</a>
            <a href=">just href</a>
            <a href=' >just href</a>
            <a href= >just href</a>
            <hr>
            <b>external links</b><br/>
            <a href="http://google.com/search/about">(15) http google</a>
            <a href=https://www.example.org>(16) google org</a>
            <a href="http://example.net:80">(17) example net (port 80)</a>
            <a href="http://example.com/">(18) example.com</a>
            <hr>
            <b>external dead links</b><br/>
            <a href="http://loclahost:21">(19) localhost: 21</a>
            <a href="https://lolhost:90">(20) lolhost: 90</a>
            <a href="https://this site isn't existing.de">(21) spaces in domain</a>
            <a href="http://lol/">(22) hostname (lol)</a>
            <a href='/limk-19'>(23) mistyped  link</a>
            <hr>
            <b>more links</b><br/>
            <a href="more/links">(24) more link</a>
        """)

    OTHER_PAGE = dedent(
        """\
            more links for crawler
            <a href="/link-01">(1) seen link</a>
            <a href="/link-15">(24) unseen link</a>
            <a href='/limk-20'>(25) mistyped  link 2</a>
        """)

    site_with_links = server.router({
        '^/$': Page(INDEX_PAGE).exists(),
        'link-\d{1,}': Page("ok").exists(),
        'limk-\d{1,}': Page("typo in path").not_exists(),
        '^/more/links/?$': Page(OTHER_PAGE).exists(),
    })
    return site_with_links
