"""
index_test.py
--------------

test for Index (indexed links collection) object.

TODO
- [ ] Better way to test __iter__ and __contains__
"""

from typing import (List)

from deadlinks import (Link, Index)


def test_index():
    """ general and only index test """
    index = Index()

    assert len(index) == 0

    links = [] # type: List[Link]

    links.append(Link("https://google.com"))
    links.append(Link("https://google.com"))
    links.append(Link("https://google.com"))
    links.append(Link("http://google.com"))
    links.append(Link("https://google.de"))
    links.append(Link("http://google.de"))
    links.append(Link("https://google.es"))
    links.append(Link("http://google.es"))

    for idx, link in enumerate(links):
        if idx % 2 == 1:
            index.add(link)
            continue
        index.put(link)

    # total uniq links
    assert len(index) == 6

    # all items in the index and in the list are same.
    set_index = set(links)
    set_links = set(index.all())
    assert (set_links - set_index) == (set_index - set_links)

    # __iter__ and __contains__ test.
    for link in index:
        assert link in index # __contains__
