import pytest

from deadlinks import (Link, Index)


def test_indexer():
    i = Index()

    assert len(i) == 0

    links = [] # List[Link]

    links.append(Link("https://google.com"))
    links.append(Link("https://google.com"))
    links.append(Link("https://google.com"))
    links.append(Link("http://google.com"))
    links.append(Link("https://google.de"))
    links.append(Link("http://google.de"))
    links.append(Link("https://google.es"))
    links.append(Link("http://google.es"))

    assert len(i) == 0

    for k, l in enumerate(links):
        i.add(l) if k % 2 else i.put(l)

    assert len(i) == 6

    # all items are in index
    assert len(set(links) - i.all()) == 0

    # __iter__ and __contain__
    for l in i:
        assert l in i
