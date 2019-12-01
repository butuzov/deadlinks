"""
utils.setup.py
~~~~~~~~~~~~~~

Setup utilities used by setup.py

"""

from typing import (Dict, Tuple, Optional, List) #pylint: disable-msg=W0611

from pathlib import Path
from re import compile as _compile
from collections import defaultdict

# -- Common Functions ----------------------------------------------------------

DUNDER_REGEXP = _compile(r'(__(.*?)__ = "(.*?)")\n')


def read_data() -> Dict[str, str]:
    """ Read data from __versions__ py """

    init = Path(".").parent / "deadlinks" / "__version__.py"

    if not Path(init).is_file():
        raise RuntimeError("Can not find source for deadlinks/__version__.py")

    values = dict() # type: Dict[str, str]
    with open(str(init)) as fh:
        content = "".join(fh.readlines())
        for match in DUNDER_REGEXP.findall(content):
            values[match[1]] = match[2]

    return values


def require(section: str = "install") -> List[str]:
    """ Requirements txt parser. """

    require_txt = Path(".").parent / "requirements.txt"
    if not Path(require_txt).is_file():
        return []

    requires = defaultdict(list) # type: Dict[str, List[str]]
    with open(str(require_txt), "rb") as fh:
        key = "" # type: str
        for line in fh.read().decode("utf-8").split("\n"):

            if not line.strip():
                " empty line "
                continue

            if line[0] == "#":
                " section key "
                key = line[2:]
                continue

            # actual package
            requires[key].append(line.strip())

    return requires[section]


def readme() -> str:
    """ different version of readme changed for pypi """
    readme = Path(".").parent / "README.md"

    if not Path(readme).is_file():
        return ""

    contents = " "
    with open("README.md", encoding="utf8") as f:
        contents = f.read()

    # cutout first header
    return contents.replace("# deadlinks", "", 1).lstrip()
